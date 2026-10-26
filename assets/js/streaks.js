/* Crisp live light on <canvas>, vector only (canvas 2D strokes and rects, plain source-over: 'lighter' doubles the
   raster cost on machines without a GPU).
   <canvas data-streaks="reel">   the reel: a swarm of amber tracers rushing a precise shield arc; each one is stopped
                                   at the line, flares white for a moment and dies. The shield's hairlines and ticks
                                   are an SVG and its base and rim light are CSS gradients (set once per resize).
   <canvas data-streaks="hero">   over the home hero image: a swarm of crisp sparks flying along the image's own spark
                                   streaks into its arc of light and winking out there, fine tracers riding the arc;
                                   the dark bottom left (headline) stays clean.
                                   ("accent" is an alias.)
   <canvas data-streaks="pinch">  over the 404 image: tracers converging into the pinch and stopping there.
   Crisp by construction (Axel, 2026-10-26: the long-exposure reel "gives the illusion that it's blurry"): every
   moving line is a hard-edged stroke 1 to 2 device px wide, no blur, no per-frame pixel work (no getImageData /
   putImageData, no JS pixel loops). Soft light is static only (CSS gradients).
   Light on cheap hardware: DPR capped at 2 (1.5 on weak devices); quality steps down (DPR, then density, then
   30 fps) when frames run long, measured as script time per frame and main-thread time from rAF to the end of the
   frame; pauses offscreen, in hidden tabs and on the reel toggle; one static frame under reduced motion.
   Optional controls: a [data-streaks-scope] ancestor with a [data-streaks-toggle] button; the scope gets
   .is-paused and the button aria-pressed. Optional data-seed changes the layout. */

const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const outCubic = (p) => 1 - (1 - p) * (1 - p) * (1 - p);

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${Math.max(0, Math.min(1, a)).toFixed(3)})`;
// a tail drawn as k hard-edged pieces, alpha rising to the head (one stroke per piece for every tracer at once)
const ramp = (c, a, k, pow = 1.7) => Array.from({ length: k }, (_, i) => rgba(c, a * Math.pow((i + 1) / k, pow)));

const AMBER = [255, 191, 0];     // brand #FFBF00
const DEEP = [255, 166, 32];     // warm amber
const GOLD = [255, 216, 128];    // pale gold
const HOT = [255, 247, 228];     // warm white heads
const WHITE = [255, 255, 255];

const WEAK = (() => {
  try {
    return (navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 4;
  } catch (e) { return false; }
})();
// quality ladder: start at 0 (1 on weak devices), step down when frames run long, never up
const LEVELS = [
  { dpr: 2, density: 1, half: false },
  { dpr: 1.5, density: 0.8, half: false },
  { dpr: 1.25, density: 0.62, half: false },
  { dpr: 1, density: 0.5, half: false },
  { dpr: 1, density: 0.4, half: true }, // 30 fps
];

/* ---------- tracks: polylines resampled every STEP px, O(1) lookup by arc length ---------- */
const STEP = 4;
function makeTrack(flat) {
  const n0 = flat.length / 2, cum = new Float32Array(n0);
  for (let i = 1; i < n0; i++) cum[i] = cum[i - 1] + Math.hypot(flat[i * 2] - flat[i * 2 - 2], flat[i * 2 + 1] - flat[i * 2 - 1]);
  const len = cum[n0 - 1], n = Math.max(2, Math.ceil(len / STEP) + 1);
  const xs = new Float32Array(n), ys = new Float32Array(n);
  let j = 0;
  for (let i = 0; i < n; i++) {
    const s = Math.min(len, i * STEP);
    while (j < n0 - 2 && cum[j + 1] < s) j++;
    const f = (s - cum[j]) / Math.max(1e-6, cum[j + 1] - cum[j]);
    xs[i] = flat[j * 2] + (flat[j * 2 + 2] - flat[j * 2]) * f;
    ys[i] = flat[j * 2 + 1] + (flat[j * 2 + 3] - flat[j * 2 + 1]) * f;
  }
  return { xs, ys, n, len };
}
function trackAt(t, s, out) {
  const u = clamp(s, 0, t.len) / STEP, i = Math.min(t.n - 2, u | 0), f = u - i;
  out[0] = t.xs[i] + (t.xs[i + 1] - t.xs[i]) * f;
  out[1] = t.ys[i] + (t.ys[i + 1] - t.ys[i]) * f;
  return out;
}
const P = [0, 0];
function trackRange(ctx, t, s0, s1) {
  s0 = Math.max(0, s0); s1 = Math.min(t.len, s1);
  if (s1 <= s0) return;
  trackAt(t, s0, P); ctx.moveTo(P[0], P[1]);
  for (let i = Math.ceil(s0 / STEP), e = Math.floor(s1 / STEP); i <= e; i++) ctx.lineTo(t.xs[i], t.ys[i]);
  trackAt(t, s1, P); ctx.lineTo(P[0], P[1]);
}
// Catmull-Rom through [x, y] points, as a flat dense polyline
function spline(pts, per = 10) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let k = 0; k < per; k++) {
      const t = k / per, t2 = t * t, t3 = t2 * t;
      for (let c = 0; c < 2; c++) {
        out.push(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3));
      }
    }
  }
  const last = pts[pts.length - 1];
  out.push(last[0], last[1]);
  return out;
}

/* ================= the reel: the shield ================= */
// tracer classes: far (thin, dim: depth), amber, gold
const THREAT = [
  { w: 1.25, ramp: ramp(DEEP, 0.6, 5), head: rgba(GOLD, 0.6), hw: 1.25 },
  { w: 1.75, ramp: ramp(AMBER, 1, 8), head: rgba(HOT, 1), hw: 2 },
  { w: 1.75, ramp: ramp([255, 208, 96], 1, 8), head: rgba(WHITE, 1), hw: 2 },
];
const SPARK_RAMP = ramp(GOLD, 0.9, 4, 1.2);
// a small warm halo for impacts, drawn once into a 64 px sprite
let HALO = null;
function haloSprite() {
  if (HALO) return HALO;
  HALO = document.createElement("canvas");
  HALO.width = HALO.height = 64;
  const g = HALO.getContext("2d"), r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  r.addColorStop(0, "rgba(255,236,190,0.9)");
  r.addColorStop(0.18, "rgba(255,196,64,0.35)");
  r.addColorStop(0.5, "rgba(255,170,30,0.08)");
  r.addColorStop(1, "rgba(255,170,30,0)");
  g.fillStyle = r;
  g.fillRect(0, 0, 64, 64);
  return HALO;
}

class Shield {
  constructor(stage) {
    this.st = stage;
    this.r = mulberry32(0x5e1d + (stage.c.dataset.seed | 0));
    this.T = []; this.F = []; this.S = []; this.L = [];
    this.clock = 0; this.nextFar = 0; this.nextLone = 0.1; this.nextWave = 0.35; this.nextScan = 1.2; this.scan = -1;
    this.host = stage.c.parentElement;
    this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.svg.setAttribute("class", "reel__shield");
    this.svg.setAttribute("aria-hidden", "true");
    this.svg.setAttribute("focusable", "false");
    stage.c.before(this.svg);
  }

  resize(w, h, dpr, density) {
    const ow = this.w, oh = this.h;
    this.w = w; this.h = h; this.dpr = dpr; this.density = density;
    const portrait = h > w;
    this.portrait = portrait;
    const A = portrait ? h : w, B = portrait ? w : h;
    this.B = B;
    this.s = clamp(A / 1200, 0.5, 1.4);
    // the shield: an arc of a large circle whose centre sits beyond the far edge; threats come from the near edge
    const R = portrait ? B * 0.98 : Math.max(B * 0.92, A * 0.38);
    const a0 = A * (portrait ? 0.58 : 0.66);
    this.R = R;
    this.cx = portrait ? w / 2 : a0 + R;
    this.cy = portrait ? a0 + R : h / 2;
    this.phc = portrait ? -Math.PI / 2 : Math.PI;
    this.half = Math.asin(Math.min(0.999, (B / 2) / R));
    if (ow !== w || oh !== h) this.drawShield();
    // the live canvas stops just past the arc: nothing moves on the protected side (less to clear and composite)
    const far = Math.min(A, a0 + R * (1 - Math.cos(this.half)) + 34 * this.s);
    return portrait ? { x: 0, y: 0, w, h: Math.ceil(far) } : { x: 0, y: 0, w: Math.ceil(far), h };
  }

  /* the static shield: base and rim light as CSS gradients on the frame, hairlines and ticks as one SVG */
  drawShield() {
    const { w, h, R, cx, cy, phc } = this, s = this.host.style;
    s.setProperty("--shield-x", `${cx.toFixed(1)}px`);
    s.setProperty("--shield-y", `${cy.toFixed(1)}px`);
    s.setProperty("--shield-r", `${R.toFixed(1)}px`);
    s.setProperty("--shield-ax", `${(cx + R * Math.cos(phc)).toFixed(1)}px`);
    s.setProperty("--shield-ay", `${(cy + R * Math.sin(phc)).toFixed(1)}px`);
    // a hairline: one device pixel, never under half a CSS pixel (one device px at 3x would vanish on a phone)
    const dev = Math.max(0.5, 1 / (window.devicePixelRatio || 1));
    const span = this.half + 0.08;
    const a0 = phc - span, a1 = phc + span;
    const pt = (r, a) => `${(cx + r * Math.cos(a)).toFixed(2)} ${(cy + r * Math.sin(a)).toFixed(2)}`;
    const arc = (r) => `M${pt(r, a0)}A${r.toFixed(2)} ${r.toFixed(2)} 0 0 1 ${pt(r, a1)}`;
    const minor = R < 520 ? 2 : 1;
    let ticks = "", major = "";
    const deg = Math.PI / 180, k = this.s;
    for (let d = Math.ceil(-span / deg); d <= span / deg; d++) {
      if (d % minor) continue;
      const a = phc + d * deg;
      if (d % 5 === 0) major += `M${pt(R + 11 * k, a)}L${pt(R + 22 * k, a)}`;
      else ticks += `M${pt(R + 11 * k, a)}L${pt(R + 15 * k, a)}`;
    }
    this.svg.setAttribute("viewBox", `0 0 ${w.toFixed(1)} ${h.toFixed(1)}`);
    this.svg.innerHTML =
      `<path d="${arc(R - 46 * k)}" stroke="#A3AABF" stroke-opacity=".2" stroke-width="${dev}" stroke-dasharray="${(2 * dev).toFixed(3)} ${(6 * k).toFixed(2)}"/>` +
      `<path d="${arc(R - 120 * k)}" stroke="#A3AABF" stroke-opacity=".1" stroke-width="${dev}"/>` +
      `<path d="${arc(R - 240 * k)}" stroke="#A3AABF" stroke-opacity=".07" stroke-width="${dev}"/>` +
      `<path d="${arc(R + 6 * k)}" stroke="#FFE7B0" stroke-opacity=".22" stroke-width="${dev}"/>` +
      `<path d="${ticks}" stroke="#FFE7B0" stroke-opacity=".2" stroke-width="${dev}"/>` +
      `<path d="${major}" stroke="#FFE7B0" stroke-opacity=".42" stroke-width="${dev}"/>` +
      `<path d="${arc(R)}" stroke="#FFE7B0" stroke-opacity=".78" stroke-width="${(1.5 * dev).toFixed(3)}"/>`;
  }

  spawn(c, th, lat, v, len, delay) {
    const phi = this.phc + th;
    const px = this.cx + this.R * Math.cos(phi), py = this.cy + this.R * Math.sin(phi);
    const back = len + 12;
    const sx = this.portrait ? px + lat : -back, sy = this.portrait ? -back : py + lat;
    const dx = px - sx, dy = py - sy, d = Math.hypot(dx, dy);
    this.T.push({ c, x: sx, y: sy, dx: dx / d, dy: dy / d, d, pos: -delay * v, v, len, phi, px, py, hit: false });
  }

  wave() {
    const r = this.r, s = this.s;
    const n = Math.max(4, Math.round((10 + r() * 12) * this.density));
    const thc = (r() * 2 - 1) * this.half * 0.8, spread = 0.02 + r() * 0.045;
    const latc = (r() - 0.5) * this.B * 0.9, latS = this.B * (0.025 + r() * 0.05);
    const v = (1000 + r() * 500) * s, len = (150 + r() * 140) * s;
    let eta = 0;
    for (let i = 0; i < n; i++) {
      const g = (r() + r() + r() - 1.5) * 1.4;
      this.spawn(r() < 0.35 ? 2 : 1, thc + g * spread, latc + (r() + r() - 1) * latS, v * (0.94 + r() * 0.12), len * (0.8 + r() * 0.4), i * 0.035 + r() * 0.16);
      const q = this.T[this.T.length - 1];
      eta = Math.max(eta, (q.d - q.pos) / q.v);
    }
    // the shield sees it coming: a bracket arms over the impact zone before the swarm lands
    this.L.push({ phi: this.phc + thc, half: spread * 2.2 + 0.012, age: 0, eta });
  }

  step(dt) {
    const r = this.r, s = this.s, den = this.density;
    this.clock += dt;
    if (this.clock >= this.nextFar) {
      this.nextFar = this.clock + (0.035 + r() * 0.05) / den;
      this.spawn(0, (r() * 2 - 1) * this.half * 1.05, (r() - 0.5) * this.B * 0.7, (460 + r() * 320) * s, (50 + r() * 90) * s, 0);
    }
    if (this.clock >= this.nextLone) {
      this.nextLone = this.clock + (0.1 + r() * 0.2) / den;
      this.spawn(r() < 0.3 ? 2 : 1, (r() * 2 - 1) * this.half * 1.02, (r() - 0.5) * this.B * 0.6, (850 + r() * 550) * s, (110 + r() * 170) * s, 0);
    }
    if (this.clock >= this.nextWave) {
      this.nextWave = this.clock + 0.8 + r() * 0.9;
      this.wave();
    }
    if (this.clock >= this.nextScan) {
      this.nextScan = this.clock + 4.2 + r() * 2;
      this.scan = 0; this.scanDir = r() < 0.5 ? 1 : -1;
    }
    if (this.scan >= 0) { this.scan += dt / 1.5; if (this.scan > 1) this.scan = -1; }

    const T = this.T;
    for (let i = T.length - 1; i >= 0; i--) {
      const q = T[i];
      q.pos += q.v * dt;
      if (!q.hit && q.pos >= q.d) { q.hit = true; this.impact(q); }
      if (q.pos - q.len >= q.d) { T[i] = T[T.length - 1]; T.pop(); }
    }
    const F = this.F;
    for (let i = F.length - 1; i >= 0; i--) {
      const f = F[i];
      f.age += dt;
      if (f.age >= f.life) { F[i] = F[F.length - 1]; F.pop(); }
    }
    const S = this.S, drag = Math.exp(-5 * dt);
    for (let i = S.length - 1; i >= 0; i--) {
      const p = S[i];
      p.age += dt;
      p.x += p.vx * dt; p.y += p.vy * dt;
      p.vx *= drag; p.vy *= drag;
      if (p.age >= p.life) { S[i] = S[S.length - 1]; S.pop(); }
    }
    const L = this.L;
    for (let i = L.length - 1; i >= 0; i--) {
      const l = L[i];
      l.age += dt;
      if (l.age > l.eta + 0.9) { L[i] = L[L.length - 1]; L.pop(); }
    }
  }

  impact(q) {
    const r = this.r, big = q.c > 0;
    // tangent of the shield at the impact
    const tx = -Math.sin(q.phi), ty = Math.cos(q.phi);
    this.F.push({ x: q.px, y: q.py, phi: q.phi, tx, ty, age: 0, life: big ? 0.6 + r() * 0.25 : 0.3, k: big ? 1 : 0.45, big, ring: big && r() < 0.3 });
    if (!big || this.S.length > 90) return;
    // a couple of sparks thrown back off the shield
    const nx = Math.cos(q.phi), ny = Math.sin(q.phi); // outward normal (towards the threats)
    for (let i = 0, n = 1 + ((r() * 2.5) | 0); i < n; i++) {
      const a = (r() - 0.5) * 2.2, sp = (140 + r() * 220) * this.s;
      const ca = Math.cos(a), sa = Math.sin(a);
      this.S.push({ x: q.px, y: q.py, vx: (nx * ca - ny * sa) * sp, vy: (nx * sa + ny * ca) * sp, age: 0, life: 0.22 + r() * 0.2 });
    }
  }

  draw(ctx) {
    const dpr = this.dpr, T = this.T, R = this.R, cx = this.cx, cy = this.cy, s = this.s;
    ctx.lineCap = "butt";
    ctx.lineJoin = "miter";

    // armed brackets over the zones a swarm is about to hit
    ctx.lineWidth = 1 / dpr;
    ctx.strokeStyle = rgba(AMBER, 1);
    const rl = R + 30 * s;
    for (const l of this.L) {
      const a = Math.min(1, l.age / 0.25) * (l.age > l.eta + 0.2 ? Math.max(0, 1 - (l.age - l.eta - 0.2) / 0.7) : 1);
      if (a <= 0.01) continue;
      ctx.globalAlpha = 0.6 * a;
      ctx.beginPath();
      ctx.arc(cx, cy, rl, l.phi - l.half, l.phi + l.half);
      for (const e of [l.phi - l.half, l.phi + l.half]) {
        ctx.moveTo(cx + (rl - 5 * s) * Math.cos(e), cy + (rl - 5 * s) * Math.sin(e));
        ctx.lineTo(cx + (rl + 5 * s) * Math.cos(e), cy + (rl + 5 * s) * Math.sin(e));
      }
      ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // tracers: each class in k pieces of rising alpha, one stroke per piece for all of them
    for (let c = 0; c < 3; c++) {
      const cls = THREAT[c], K = cls.ramp.length;
      ctx.lineWidth = cls.w / dpr;
      for (let k = 0; k < K; k++) {
        ctx.beginPath();
        let any = false;
        for (let i = 0; i < T.length; i++) {
          const q = T[i];
          if (q.c !== c) continue;
          const head = Math.min(q.pos, q.d), tail = Math.max(0, q.pos - q.len);
          if (head <= tail) continue;
          const s0 = tail + ((head - tail) * k) / K, s1 = tail + ((head - tail) * (k + 1)) / K;
          ctx.moveTo(q.x + q.dx * s0, q.y + q.dy * s0);
          ctx.lineTo(q.x + q.dx * s1, q.y + q.dy * s1);
          any = true;
        }
        if (any) { ctx.strokeStyle = cls.ramp[k]; ctx.stroke(); }
      }
      // heads: a short hot segment on every tracer still in flight
      ctx.lineWidth = cls.hw / dpr;
      ctx.beginPath();
      let any = false;
      const hl = (c ? 9 : 5) * s;
      for (let i = 0; i < T.length; i++) {
        const q = T[i];
        if (q.c !== c || q.hit || q.pos <= 0) continue;
        const h0 = Math.max(0, q.pos - hl);
        ctx.moveTo(q.x + q.dx * h0, q.y + q.dy * h0);
        ctx.lineTo(q.x + q.dx * q.pos, q.y + q.dy * q.pos);
        any = true;
      }
      if (any) { ctx.strokeStyle = cls.head; ctx.stroke(); }
    }

    // impacts: the shield lights up where it is hit, a white glint along it, now and then a ring, a hot point with a
    // small halo (a sprite drawn once, never a per-frame blur). Added with 'lighter' so a swarm landing in one spot
    // builds a hot stretch of the arc (small areas only: 'lighter' is slow to raster without a GPU)
    ctx.globalCompositeOperation = "lighter";
    const halo = haloSprite();
    for (const f of this.F) {
      if (!f.big) continue;
      const p = f.age / f.life, hr = 14 * s * (0.7 + 0.3 * outCubic(Math.min(1, p * 3)));
      ctx.globalAlpha = 0.5 * (1 - p) * (1 - p);
      ctx.drawImage(halo, f.x - hr, f.y - hr, hr * 2, hr * 2);
    }
    for (const f of this.F) {
      const p = f.age / f.life, fade = (1 - p) * (1 - p);
      ctx.strokeStyle = rgba(GOLD, 1);
      ctx.globalAlpha = fade * f.k;
      ctx.lineWidth = 2 / dpr;
      ctx.beginPath();
      const d = (f.big ? 0.03 : 0.014) * (0.5 + 0.5 * outCubic(Math.min(1, p * 4)));
      ctx.arc(cx, cy, R, f.phi - d, f.phi + d);
      ctx.stroke();
      ctx.strokeStyle = "#fff";
      if (f.big) {
        const g = (4 + 16 * outCubic(Math.min(1, p * 3))) * s;
        ctx.globalAlpha = Math.pow(1 - p, 3);
        ctx.lineWidth = 2 / dpr;
        ctx.beginPath();
        ctx.moveTo(f.x - f.tx * g, f.y - f.ty * g);
        ctx.lineTo(f.x + f.tx * g, f.y + f.ty * g);
        ctx.stroke();
      }
      if (f.ring) {
        ctx.globalAlpha = 0.55 * fade;
        ctx.lineWidth = 1 / dpr;
        ctx.beginPath();
        ctx.arc(f.x, f.y, (2 + 10 * outCubic(p)) * s, 0, Math.PI * 2);
        ctx.stroke();
      }
      const dot = (f.big ? 3 : 2) / dpr;
      ctx.globalAlpha = Math.pow(1 - p, 4) * (f.big ? 1 : 0.7);
      ctx.fillStyle = "#fff";
      ctx.fillRect(f.x - dot / 2, f.y - dot / 2, dot, dot);
    }
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = "source-over";

    // sparks thrown back: short streaks along their velocity, bucketed by age
    if (this.S.length) {
      ctx.lineWidth = 1 / dpr;
      for (let k = 0; k < SPARK_RAMP.length; k++) {
        ctx.beginPath();
        let any = false;
        for (const p of this.S) {
          const b = Math.min(SPARK_RAMP.length - 1, ((1 - p.age / p.life) * SPARK_RAMP.length) | 0);
          if (b !== k) continue;
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p.x - p.vx * 0.03, p.y - p.vy * 0.03);
          any = true;
        }
        if (any) { ctx.strokeStyle = SPARK_RAMP[k]; ctx.stroke(); }
      }
    }

    // the shield scans itself: a short bright segment sweeping along the arc
    if (this.scan >= 0) {
      const span = this.half * 1.05, p = this.scan;
      const phi = this.phc + this.scanDir * (-span + 2 * span * p);
      const a = Math.sin(Math.PI * p);
      ctx.lineWidth = 2 / dpr;
      ctx.strokeStyle = "#fff";
      ctx.globalAlpha = 0.8 * a;
      ctx.beginPath();
      ctx.arc(cx, cy, R, Math.min(phi, phi - this.scanDir * 0.012), Math.max(phi, phi - this.scanDir * 0.012));
      ctx.stroke();
      ctx.strokeStyle = rgba(AMBER, 1);
      ctx.globalAlpha = 0.35 * a;
      ctx.beginPath();
      const e = phi - this.scanDir * 0.09;
      ctx.arc(cx, cy, R, Math.min(phi, e), Math.max(phi, e));
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
  }
}

/* ================= hero: a swarm drawn into the image's arc of light, tracers riding it ================= */
// the arc's light ridge in hero.webp (2400 x 1350), measured from the image (brightness-weighted centre line)
const HERO_IMG = [2400, 1350];
const HERO_RIDGE = [[1100, -60], [1133, 40], [1155, 80], [1177, 120], [1199, 160], [1224, 200], [1254, 240], [1287, 280], [1324, 320],
  [1365, 360], [1413, 400], [1467, 440], [1528, 480], [1600, 528], [1700, 574], [1800, 607], [1900, 629], [2000, 643], [2100, 650],
  [2200, 651], [2300, 646], [2400, 641], [2520, 636]];
/* the direction of the image's own spark streaks (structure tensor of hero.webp, 100 px cells, 24 x 14), in degrees,
   signed towards the arc; -1 where the image has no clear streaks. Sparks fly along it into the arc and die there. */
const FLOW_COLS = 24, FLOW_CELL = 100;
const HERO_FLOW = [-1,-1,-1,-1,-1,321,-1,-1,315,292,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,322,319,316,316,301,277,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,327,318,316,314,309,284,258,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,319,314,313,314,306,281,-1,-1,-1,43,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,331,321,319,311,313,316,329,1,32,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,329,328,316,311,313,320,326,340,1,-1,-1,-1,-1,-1,-1,13,-1,165,162,-1,-1,-1,-1,-1,-1,325,319,312,311,318,323,332,339,352,10,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,311,-1,316,325,332,332,331,337,348,356,0,358,-1,-1,-1,347,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,333,331,327,325,331,337,340,338,332,327,329,330,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,326,324,326,332,336,331,319,315,315,322,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,329,-1,326,332,333,331,323,313,314,316,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,331,325,-1,315,314,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,324,326,-1,-1,326,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1];
const FLOW_CELLS = HERO_FLOW.reduce((a, d, i) => (d >= 0 && a.push(i), a), []);
const RIDE = [ramp(GOLD, 0.75, 6, 1.8), ramp(HOT, 0.9, 6, 2)];
const SWARM = [ramp(AMBER, 0.9, 5, 1.1), ramp([255, 214, 110], 0.95, 5, 1.1)];
const GRID = 16; // css px cells of the distance-to-arc grid

class Rider {
  constructor(stage) {
    this.st = stage;
    this.r = mulberry32(0x4e70 + (stage.c.dataset.seed | 0));
    this.R = []; this.S = []; this.acc = 0;
  }

  resize(w, h, dpr, density) {
    const same = this.w === w && this.h === h;
    this.w = w; this.h = h; this.dpr = dpr; this.density = density;
    this.s = clamp(Math.max(w, h) / 1400, 0.45, 1.3);
    this.portrait = h > w;
    if (same && this.tracks) return this.box;
    // cover transform of the image box (object-fit: cover, 50% 50%)
    const k = Math.max(w / HERO_IMG[0], h / HERO_IMG[1]);
    this.k = k; this.ox = (w - HERO_IMG[0] * k) / 2; this.oy = (h - HERO_IMG[1] * k) / 2;
    const dense = spline(HERO_RIDGE.map(([x, y]) => [this.ox + x * k, this.oy + y * k]), 12);
    const n = dense.length / 2;
    // normals pointing to the arc's outer (convex, lower left) side, and the light band's half width along it
    const nx = new Float32Array(n), ny = new Float32Array(n), hw = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      const a = Math.max(0, i - 1), b = Math.min(n - 1, i + 1);
      const tx = dense[b * 2] - dense[a * 2], ty = dense[b * 2 + 1] - dense[a * 2 + 1], l = Math.hypot(tx, ty) || 1;
      nx[i] = -ty / l; ny[i] = tx / l;
      hw[i] = (14 + 34 * (i / (n - 1))) * k;
    }
    // riders keep to the outer fibres, where the band is amber rather than white
    this.tracks = [];
    for (let j = 0; j < 10; j++) {
      const f = 0.55 + (1.4 * j) / 9;
      const flat = new Array(n * 2);
      for (let i = 0; i < n; i++) {
        flat[i * 2] = dense[i * 2] + nx[i] * hw[i] * f;
        flat[i * 2 + 1] = dense[i * 2 + 1] + ny[i] * hw[i] * f;
      }
      this.tracks.push(makeTrack(flat));
    }
    // the live canvas only covers the arc and the swarm's field (less to clear and composite)
    let x0 = w, y0 = h, x1 = 0, y1 = 0;
    for (let i = 0; i < n; i++) {
      const x = dense[i * 2], y = dense[i * 2 + 1];
      if (x < -50 || x > w + 50 || y < -50 || y > h + 50) continue;
      x0 = Math.min(x0, x - hw[i] * 2); x1 = Math.max(x1, x + hw[i] * 2);
      y0 = Math.min(y0, y - hw[i] * 2); y1 = Math.max(y1, y + hw[i] * 2);
    }
    for (const c of FLOW_CELLS) {
      const x = this.ox + ((c % FLOW_COLS) + 0.5) * FLOW_CELL * k, y = this.oy + (Math.floor(c / FLOW_COLS) + 0.5) * FLOW_CELL * k;
      if (x < 0 || x > w || y < 0 || y > h || this.zone(x, y) < 0.3) continue;
      x0 = Math.min(x0, x - FLOW_CELL * k * 0.6); x1 = Math.max(x1, x + FLOW_CELL * k * 0.6);
      y0 = Math.min(y0, y - FLOW_CELL * k * 0.6); y1 = Math.max(y1, y + FLOW_CELL * k * 0.6);
    }
    x0 = Math.max(0, Math.floor(x0)); y0 = Math.max(0, Math.floor(y0));
    x1 = Math.min(w, Math.ceil(x1)); y1 = Math.min(h * (this.portrait ? 0.62 : 0.76), Math.ceil(y1));
    this.box = x1 > x0 && y1 > y0 ? { x: x0, y: y0, w: x1 - x0, h: y1 - y0 } : { x: 0, y: 0, w, h };
    // distance from each 16 px cell of the box to the edge of the light band (once per resize)
    const b = this.box, gw = Math.ceil(b.w / GRID) + 1, gh = Math.ceil(b.h / GRID) + 1, edge = new Float32Array(gw * gh);
    for (let j = 0; j < gh; j++) {
      for (let i = 0; i < gw; i++) {
        const x = b.x + i * GRID, y = b.y + j * GRID;
        let best = 1e9;
        for (let q = 0; q < n; q += 3) {
          const d = Math.hypot(dense[q * 2] - x, dense[q * 2 + 1] - y) - hw[q] * 0.8;
          if (d < best) best = d;
        }
        edge[j * gw + i] = best;
      }
    }
    this.edge = edge; this.gw = gw; this.gh = gh;
    for (const q of this.R) q.t = this.tracks[q.ti];
    this.S.length = 0;
    return this.box;
  }

  edgeAt(x, y) {
    const b = this.box, i = Math.round((x - b.x) / GRID), j = Math.round((y - b.y) / GRID);
    if (i < 0 || j < 0 || i >= this.gw || j >= this.gh) return 1e9;
    return this.edge[j * this.gw + i];
  }

  // keep the headline zone (bottom left on wide frames, bottom on phones) clean
  zone(x, y) {
    const w = this.w, h = this.h;
    const fy = clamp((0.58 * h - y) / (0.12 * h), 0, 1);
    if (this.portrait) return fy;
    return Math.max(fy, clamp((x - 0.44 * w) / (0.14 * w), 0, 1));
  }

  rider() {
    const r = this.r, ti = (r() * this.tracks.length) | 0, t = this.tracks[ti], len = (150 + r() * 220) * this.s;
    return { ti, t, len, pos: -r() * t.len * 0.5, v: (360 + r() * 380) * this.s, c: r() < 0.4 ? 1 : 0 };
  }

  // one spark of the incoming swarm: somewhere the image has streaks, flying along them into the arc
  launch() {
    const r = this.r, k = this.k, b = this.box;
    for (let tries = 0; tries < 4; tries++) {
      const c = FLOW_CELLS[(r() * FLOW_CELLS.length) | 0];
      const x = this.ox + ((c % FLOW_COLS) + r()) * FLOW_CELL * k, y = this.oy + (Math.floor(c / FLOW_COLS) + r()) * FLOW_CELL * k;
      if (x < b.x || y < b.y || x > b.x + b.w || y > b.y + b.h) continue;
      if (this.zone(x, y) < 0.25 || this.edgeAt(x, y) < 24 * this.s) continue;
      const a = ((HERO_FLOW[c] + (r() - 0.5) * 10) * Math.PI) / 180;
      this.S.push({ x, y, dx: Math.cos(a), dy: Math.sin(a), v: (55 + r() * 150) * this.s, age: 0, life: 1.4 + r() * 1.4, hit: -1, c: r() < 0.3 ? 1 : 0 });
      return;
    }
  }

  step(dt) {
    const want = Math.round(7 * this.density);
    while (this.R.length < want) this.R.push(this.rider());
    for (let i = this.R.length - 1; i >= 0; i--) {
      const q = this.R[i];
      q.pos += q.v * dt;
      if (q.pos - q.len > q.t.len) { if (this.R.length > want) this.R.splice(i, 1); else this.R[i] = Object.assign(this.rider(), { pos: -this.r() * 200 * this.s }); }
    }
    // about 80 sparks in the air at full density
    this.acc += dt * 46 * this.density;
    while (this.acc >= 1) { this.acc -= 1; this.launch(); }
    const S = this.S;
    for (let i = S.length - 1; i >= 0; i--) {
      const p = S[i];
      p.age += dt;
      if (p.hit < 0) {
        p.x += p.dx * p.v * dt; p.y += p.dy * p.v * dt;
        if (this.edgeAt(p.x, p.y) <= 0) p.hit = 0; // reached the arc: stopped there
      } else p.hit += dt;
      if (p.hit > 0.3 || (p.hit < 0 && p.age >= p.life)) { S[i] = S[S.length - 1]; S.pop(); }
    }
  }

  draw(ctx) {
    const dpr = this.dpr;
    ctx.lineCap = "butt";
    ctx.lineJoin = "round";
    ctx.lineWidth = 1.5 / dpr;
    for (let c = 0; c < 2; c++) {
      const rp = RIDE[c], K = rp.length;
      for (let k = 0; k < K; k++) {
        ctx.beginPath();
        let any = false;
        for (const q of this.R) {
          if (q.c !== c) continue;
          const tail = q.pos - q.len, s0 = tail + (q.len * k) / K, s1 = tail + (q.len * (k + 1)) / K;
          if (s1 <= 0 || s0 >= q.t.len) continue;
          trackRange(ctx, q.t, s0, s1);
          any = true;
        }
        if (any) { ctx.strokeStyle = rp[k]; ctx.stroke(); }
      }
    }
    // the swarm: crisp short streaks, alpha by age and the headline zone in 5 buckets; a spark that reaches the
    // arc stops, its tail drains into the point and it winks out white
    ctx.lineWidth = 1.25 / dpr;
    for (let c = 0; c < 2; c++) {
      const rp = SWARM[c], K = rp.length;
      for (let k = 0; k < K; k++) {
        ctx.beginPath();
        let any = false;
        for (const p of this.S) {
          if (p.c !== c) continue;
          const left = p.life - p.age;
          const a = Math.min(1, p.age / 0.3) * (p.hit < 0 ? Math.min(1, left / 0.4) : 1) * this.zone(p.x, p.y);
          const bk = Math.min(K - 1, (a * K) | 0);
          if (bk !== k || a < 0.05) continue;
          let l = Math.min(p.age * p.v, p.v * 0.14 + 3 * this.s);
          if (p.hit >= 0) l *= Math.max(0, 1 - p.hit / 0.12);
          if (l < 0.5) continue;
          ctx.moveTo(p.x - p.dx * l, p.y - p.dy * l);
          ctx.lineTo(p.x, p.y);
          any = true;
        }
        if (any) { ctx.strokeStyle = rp[k]; ctx.stroke(); }
      }
    }
    ctx.fillStyle = "#fff";
    const dot = 2.5 / dpr;
    for (const p of this.S) {
      if (p.hit < 0) continue;
      ctx.globalAlpha = Math.pow(Math.max(0, 1 - p.hit / 0.3), 2) * this.zone(p.x, p.y);
      ctx.fillRect(p.x - dot / 2, p.y - dot / 2, dot, dot);
    }
    ctx.globalAlpha = 1;
  }
}

/* ================= 404: tracers converging into the pinch and stopping there ================= */
const PINCH_IMG = [1600, 1600];
const PINCH_AT = [0.527, 0.5]; // the pinch of threat-breach.webp, mirrored like the page shows it

class Pinch {
  constructor(stage) {
    this.st = stage;
    this.r = mulberry32(0x9e11 + (stage.c.dataset.seed | 0));
    this.Q = []; this.F = [];
  }

  resize(w, h, dpr, density) {
    const same = this.w === w && this.h === h;
    this.w = w; this.h = h; this.dpr = dpr; this.density = density;
    this.s = clamp(Math.max(w, h) / 1400, 0.45, 1.3);
    if (same && this.tracks) return null;
    // where the pinch really is: object-fit cover in the image's own box, then that box as transformed by the page
    // CSS (mirrored, and scaled from the top on phones), read from the layout once per resize
    const host = this.st.host, img = host.querySelector(".cover__media img, .media img");
    let bx = 0, by = 0, sx = 1, sy = 1, iw = w, ih = h;
    const hr = host.getBoundingClientRect();
    if (img && img.offsetWidth) {
      const ir = img.getBoundingClientRect();
      iw = img.offsetWidth; ih = img.offsetHeight;
      sx = ir.width / iw; sy = ir.height / ih; bx = ir.left - hr.left; by = ir.top - hr.top;
    }
    const k = Math.max(iw / PINCH_IMG[0], ih / PINCH_IMG[1]);
    const px = bx + ((iw - PINCH_IMG[0] * k) / 2 + PINCH_AT[0] * PINCH_IMG[0] * k) * sx;
    const py = by + ((ih - PINCH_IMG[1] * k) / 2 + PINCH_AT[1] * PINCH_IMG[1] * k) * sy;
    this.px = px; this.py = py;
    // the copy block: tracers fade out over it
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    host.querySelectorAll(".cover__inner > *").forEach((el) => {
      const r = el.getBoundingClientRect();
      if (!r.width) return;
      x0 = Math.min(x0, r.left - hr.left); y0 = Math.min(y0, r.top - hr.top);
      x1 = Math.max(x1, r.right - hr.left); y1 = Math.max(y1, r.bottom - hr.top);
    });
    this.copy = x1 > x0 ? [x0 - 16, y0 - 16, x1 + 16, y1 + 16] : null;
    const r = mulberry32(7);
    this.tracks = [];
    for (let j = 0; j < 22; j++) {
      const side = j % 2 ? 1 : -1;
      const ex = side < 0 ? -40 : w + 40, ey = py + (r() - 0.5) * h * 1.3;
      const c1x = ex + (px - ex) * 0.5, c1y = ey + (py - ey) * 0.1;
      const c2x = px + (ex - px) * 0.28, c2y = py + (ey - py) * 0.04;
      const flat = [];
      for (let i = 0; i <= 48; i++) {
        const t = i / 48, u = 1 - t;
        flat.push(u * u * u * ex + 3 * u * u * t * c1x + 3 * u * t * t * c2x + t * t * t * px,
          u * u * u * ey + 3 * u * u * t * c1y + 3 * u * t * t * c2y + t * t * t * py);
      }
      this.tracks.push(makeTrack(flat));
    }
    for (const q of this.Q) q.t = this.tracks[q.ti];
    return null;
  }

  // nothing crosses the copy: 0 over it, back to 1 within 60 px around it
  zone(x, y) {
    const c = this.copy;
    if (!c) return 1;
    return clamp(Math.max(c[0] - x, x - c[2], c[1] - y, y - c[3]) / 60, 0, 1);
  }

  step(dt) {
    const r = this.r, want = Math.round(9 * this.density);
    while (this.Q.length < want) {
      const ti = (r() * this.tracks.length) | 0, t = this.tracks[ti];
      this.Q.push({ ti, t, pos: -r() * t.len, len: (120 + r() * 160) * this.s, v: (520 + r() * 420) * this.s, c: r() < 0.35 ? 1 : 0, hit: false });
    }
    for (let i = this.Q.length - 1; i >= 0; i--) {
      const q = this.Q[i];
      q.pos += q.v * dt;
      if (!q.hit && q.pos >= q.t.len) { q.hit = true; this.F.push({ age: 0, life: 0.5 }); }
      if (q.pos - q.len >= q.t.len) this.Q.splice(i, 1);
    }
    for (let i = this.F.length - 1; i >= 0; i--) if ((this.F[i].age += dt) >= this.F[i].life) this.F.splice(i, 1);
  }

  draw(ctx) {
    const dpr = this.dpr;
    ctx.lineCap = "butt";
    ctx.lineJoin = "round";
    ctx.lineWidth = 1.5 / dpr;
    // few tracers here: one alpha each (faded where the head crosses the copy), k pieces per tracer
    for (const q of this.Q) {
      const head = Math.min(q.pos, q.t.len), tail = Math.max(0, q.pos - q.len);
      if (head <= tail) continue;
      trackAt(q.t, head, P);
      const a = this.zone(P[0], P[1]);
      if (a < 0.02) continue;
      ctx.globalAlpha = a;
      const rp = RIDE[q.c], K = rp.length;
      for (let k = 0; k < K; k++) {
        ctx.beginPath();
        trackRange(ctx, q.t, tail + ((head - tail) * k) / K, tail + ((head - tail) * (k + 1)) / K);
        ctx.strokeStyle = rp[k];
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1 / dpr;
    for (const f of this.F) {
      const p = f.age / f.life;
      ctx.globalAlpha = 0.6 * (1 - p) * (1 - p) * this.zone(this.px, this.py);
      ctx.beginPath();
      ctx.arc(this.px, this.py, (3 + 18 * outCubic(p)) * this.s, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }
}

const SCENES = { reel: Shield, hero: Rider, accent: Rider, pinch: Pinch };

/* ================= stage: sizing, the loop, pausing, adaptive quality ================= */
class Stage {
  constructor(canvas, reduced) {
    this.c = canvas;
    this.ctx = canvas.getContext("2d");
    if (!this.ctx) throw new Error("no 2d context");
    this.reduced = reduced;
    this.visible = false;
    this.paused = reduced;
    this.raf = 0;
    this.level = WEAK ? 1 : 0;
    this.host = canvas.parentElement;
    this.scope = canvas.closest("[data-streaks-scope]");
    this.toggle = this.scope ? this.scope.querySelector("[data-streaks-toggle]") : null;
    this.scene = new (SCENES[canvas.dataset.streaks] || Shield)(this);
    this.loop = (now) => this.tick(now);
    this.stats = { n: 0, skip: 45, script: 0, busy: 0, iv: [], bad: 0, at: 0 };
    this.half = false;
    // main-thread time of a frame: from the rAF timestamp to a message posted in it (runs after style, layout,
    // paint and the canvas flush)
    if ("MessageChannel" in window) {
      this.mc = new MessageChannel();
      this.mc.port1.onmessage = () => { if (this.frameAt) { this.stats.busy += performance.now() - this.frameAt; this.frameAt = 0; } };
    }
    this.resize();
    // a few seconds already in flight, so the first frame is never empty
    for (let i = 0; i < 75; i++) this.scene.step(1 / 30);
    this.syncUi();

    if ("ResizeObserver" in window) {
      new ResizeObserver(() => { if (this.resize() && !this.raf) this.draw(); }).observe(this.host);
    } else {
      window.addEventListener("resize", () => { if (this.resize() && !this.raf) this.draw(); });
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => {
        this.visible = entries[entries.length - 1].isIntersecting;
        this.update();
      }, { rootMargin: "80px" }).observe(this.host);
    } else {
      this.visible = true;
    }
    document.addEventListener("visibilitychange", () => this.update());
    if (this.toggle) {
      this.toggle.addEventListener("click", () => {
        this.paused = !this.paused;
        this.syncUi();
        this.update();
      });
    }
    this.draw();
    this.update();
  }

  /* the layout box (not getBoundingClientRect: the reel enters with a scale(.95) reveal, and a backing store sized
     while it is scaled would stay 5% soft); returns true when the backing store changed */
  resize() {
    const cw = this.host.clientWidth, ch = this.host.clientHeight;
    if (!cw || !ch) return false;
    const L = LEVELS[this.level];
    const dpr = Math.min(window.devicePixelRatio || 1, WEAK ? Math.min(1.5, L.dpr) : L.dpr);
    this.half = L.half;
    const crop = this.scene.resize(cw, ch, dpr, L.density);
    const box = crop || { x: 0, y: 0, w: cw, h: ch };
    this.box = box;
    const st = this.c.style;
    if (crop) {
      st.left = `${box.x}px`; st.top = `${box.y}px`; st.width = `${box.w}px`; st.height = `${box.h}px`;
      st.right = st.bottom = "auto";
    } else {
      st.left = st.top = st.width = st.height = st.right = st.bottom = "";
    }
    const W = Math.max(1, Math.round(box.w * dpr)), H = Math.max(1, Math.round(box.h * dpr));
    const changed = this.c.width !== W || this.c.height !== H;
    if (changed) { this.c.width = W; this.c.height = H; }
    this.dpr = dpr;
    return true;
  }

  syncUi() {
    if (this.scope) this.scope.classList.toggle("is-paused", this.paused);
    // a toggle button keeps one fixed name ("Pause reel"); aria-pressed carries the state
    if (this.toggle) this.toggle.setAttribute("aria-pressed", String(this.paused));
  }

  update() {
    const run = this.visible && !this.paused && !document.hidden;
    if (run && !this.raf) {
      this.last = 0;
      this.stats.skip = 30;
      this.raf = requestAnimationFrame(this.loop);
    } else if (!run && this.raf) {
      cancelAnimationFrame(this.raf);
      this.raf = 0;
    }
  }

  draw() {
    const ctx = this.ctx, b = this.box, d = this.dpr;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, this.c.width, this.c.height);
    ctx.setTransform(d, 0, 0, d, -b.x * d, -b.y * d);
    this.scene.draw(ctx);
  }

  tick(now) {
    this.raf = requestAnimationFrame(this.loop);
    if (!this.last) { this.last = now; return; }
    const iv = now - this.last;
    if (this.half && (this.odd = !this.odd)) return; // 30 fps: every other frame
    this.last = now;
    const t0 = performance.now();
    this.scene.step(Math.min(0.05, iv / 1000));
    this.draw();
    const ms = performance.now() - t0;
    if (this.mc) { this.frameAt = now; this.mc.port2.postMessage(0); }
    this.adapt(ms, iv);
  }

  /* every 40 frames: mean script time, mean main-thread frame time and the median frame interval. Two bad windows
     in a row step quality down one level (a steady ~33 ms cadence with an idle main thread is a 30 Hz cap, not
     overload, and is left alone). */
  adapt(ms, iv) {
    const S = this.stats;
    if (S.skip > 0) { S.skip--; S.script = 0; S.busy = 0; S.iv.length = 0; S.n = 0; return; }
    S.script += ms; S.iv.push(iv); S.n++;
    if (S.n < 40) return;
    const script = S.script / S.n, busy = S.busy / S.n;
    const sorted = S.iv.slice().sort((a, b) => a - b), med = sorted[sorted.length >> 1];
    const capped = sorted[4] > 30 && sorted[sorted.length - 5] < 37 && busy < 8;
    const bad = script > 6 || busy > 12 || (med > (this.half ? 40 : 24) && !capped);
    S.bad = bad ? S.bad + 1 : 0;
    S.script = 0; S.busy = 0; S.iv.length = 0; S.n = 0;
    if ((S.bad >= 2 || script > 12) && this.level < LEVELS.length - 1) {
      this.level++;
      S.bad = 0; S.skip = 30;
      this.resize();
    }
  }
}

export function initStreaks(nodes, { reduced = false } = {}) {
  const list = [];
  nodes.forEach((canvas) => {
    if (!canvas.getContext) return;
    try { list.push(new Stage(canvas, reduced)); } catch (e) { /* canvas unsupported: the static frame stays */ }
  });
  return list;
}
