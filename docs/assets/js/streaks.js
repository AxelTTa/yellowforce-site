/* Live long-exposure light streaks on a <canvas>.
   <canvas data-streaks="reel"> (full frame, filmic, on deep navy) or data-streaks="accent" (transparent, softer,
   for hero overlays). Brand: amber #FFBF00 and warm white light on navy shadows #030B1C / #071B3E (never neutral
   black, never royal blue). Optional controls: a [data-streaks-scope] ancestor with a [data-streaks-toggle]
   button; the scope gets .is-paused. Both variants run continuously while on screen. DPR-aware (capped at 2, sized
   from the layout box so a reveal transform never shrinks the backing store), pauses offscreen / hidden tab / on
   toggle, one static frame under reduced motion. */

const PALETTE = [
  [255, 191, 0],   // brand amber #FFBF00
  [255, 162, 26],  // warm amber (glow)
  [255, 218, 128], // pale gold
  [255, 245, 226], // warm white
];
const FILM_PALETTE = [
  [240, 142, 18],  // deep amber (outer trails)
  [255, 162, 26],  // warm amber
  [255, 191, 0],   // brand amber #FFBF00
  [255, 218, 128], // pale gold
  [255, 245, 226], // warm white
];

/* reel: a filmic long exposure, graded like the generated image family. Deep navy edges (#030B1C) rising to at
   most #0B2350 behind the light, a river of amber trails pinched through the middle, drawn at device resolution
   so every trail is crisp (Axel, 2026-10-26: the half resolution trails read as blurry), with the softness kept
   in the light around them: a smooth two-radius halation, a warm amber bloom with a warm white core (#FFE9C2), a
   navy vignette and film grain. The light and the trails are summed with a tone map (core: how close the core
   gets to #FFE9C2; trailPeak: a trail's peak over its local mean; trailWhite: how much of the light a trail
   cannot add as amber comes back as warm white). Mean luma about 58 at 1440.
   accent: transparent overlay for the hero, runs continuously like the reel (Axel, 2026-10-26). */
const VARIANTS = {
  reel: { film: true, lanes: 72, comets: 44, fast: 10, ribbons: 6, spread: 1.4, pinch: 0.48, tilt: 0.3, focus: 0.5, center: 0.5, swell: 0.8, laneAlpha: 1, cometAlpha: 1, centerBias: 2, exposure: 1.05, shade: 0.85, lightGain: 1, bloom: 1.25, glow: 1.8, vignette: 0.5, grain: 0.1, speed: 0.85, core: 1, lift: 0.35, trailPeak: 2.75, trailWhite: 1.4 },
  accent: { lanes: 22, comets: 14, fast: 4, spread: 1.1, pinch: 0.45, focus: 0.62, center: 0.42, swell: 0.8, laneAlpha: 0.75, cometAlpha: 0.8, centerBias: 0, haze: 0.05, speed: 0.8 },
};

const EDGE = [3, 11, 28];    // #030B1C navy-deep
const CORE = [11, 35, 80];   // #0B2350, the brightest the base gets
const WARM = [1, 233 / 255, 194 / 255]; // #FFE9C2, the warm white the hottest light rolls into (never lemon)
const LW = 0.299 * WARM[0] + 0.587 * WARM[1] + 0.114 * WARM[2];

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function mix(a, b, t) { return a + (b - a) * t; }
function color(h, alpha, pal = PALETTE) {
  const x = Math.max(0, Math.min(0.999, h)) * (pal.length - 1);
  const i = Math.floor(x), f = x - i;
  const p = pal[i], q = pal[i + 1];
  return `rgba(${mix(p[0], q[0], f) | 0},${mix(p[1], q[1], f) | 0},${mix(p[2], q[2], f) | 0},${Math.max(0, alpha).toFixed(3)})`;
}
/* blur of an RGB float image (w x h x 3): three separable box passes of radius r, edges clamped (about a
   Gaussian of sigma 1.2 r). dst gets the result; tmp is scratch; src is left as is. */
function boxPass(src, dst, w, h, r, horizontal) {
  const k = 1 / (2 * r + 1);
  const len = horizontal ? w : h, lines = horizontal ? h : w;
  const step = horizontal ? 3 : w * 3;
  for (let l = 0; l < lines; l++) {
    const base = horizontal ? l * w * 3 : l * 3;
    for (let c = 0; c < 3; c++) {
      const o = base + c;
      let acc = 0;
      for (let i = -r; i <= r; i++) acc += src[o + Math.min(len - 1, Math.max(0, i)) * step];
      for (let i = 0; i < len; i++) {
        dst[o + i * step] = acc * k;
        acc += src[o + Math.min(len - 1, i + r + 1) * step] - src[o + Math.max(0, i - r) * step];
      }
    }
  }
}
function blur3(src, dst, tmp, w, h, r) {
  boxPass(src, tmp, w, h, r, true); boxPass(tmp, dst, w, h, r, false);
  boxPass(dst, tmp, w, h, r, true); boxPass(tmp, dst, w, h, r, false);
  boxPass(dst, tmp, w, h, r, true); boxPass(tmp, dst, w, h, r, false);
}

function layer(w, h) {
  const c = document.createElement("canvas");
  c.width = Math.max(1, Math.round(w));
  c.height = Math.max(1, Math.round(h));
  return c;
}

class Streaks {
  constructor(canvas, reduced) {
    this.c = canvas;
    this.v = VARIANTS[canvas.dataset.streaks] || VARIANTS.reel;
    this.film = !!this.v.film;
    this.ctx = canvas.getContext("2d", { alpha: !this.film });
    this.reduced = reduced;
    this.visible = false;
    this.paused = reduced;
    this.raf = 0;
    this.t = 7.3;
    this.last = 0;
    this.frame = 0;
    this.rnd = mulberry32(0x59f0 + (canvas.dataset.seed | 0));
    this.scope = canvas.closest("[data-streaks-scope]");
    this.toggle = this.scope ? this.scope.querySelector("[data-streaks-toggle]") : null;
    this.build();
    this.resize();
    this.syncUi();

    if ("ResizeObserver" in window) {
      new ResizeObserver(() => { this.resize(); if (!this.raf) this.draw(); }).observe(canvas);
    } else {
      window.addEventListener("resize", () => { this.resize(); if (!this.raf) this.draw(); });
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => {
        this.visible = entries[entries.length - 1].isIntersecting;
        this.update();
      }, { rootMargin: "80px" }).observe(canvas);
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

  build() {
    const r = this.rnd, v = this.v, film = this.film;
    // phones draw fewer lanes and comets (same look, less work)
    const k = film && (this.c.clientWidth || this.c.getBoundingClientRect().width || 1200) < 640 ? 0.75 : 1;
    this.nLanes = Math.max(12, Math.round(v.lanes * k));
    this.nComets = Math.round(v.comets * k);
    this.nFast = Math.round(v.fast * k);
    this.lanes = Array.from({ length: this.nLanes }, (_, i) => {
      const kk = (i / (this.nLanes - 1)) * 2 - 1;
      const l = {
        off: kk * (0.36 + r() * 0.1) + (r() - 0.5) * 0.06,
        amp: 0.01 + r() * 0.045,
        freq: 0.5 + r() * 1.3,
        phase: r() * Math.PI * 2,
        drift: (r() - 0.5) * 0.35,
      };
      if (film) {
        // mostly fine trails, a few thick soft ones; varied width and opacity, brighter toward the middle
        const q = r();
        const c = 1 - Math.abs(kk);
        l.width = 0.7 + q * q * 4.2;
        l.hue = Math.min(0.95, 0.02 + r() * 0.5 + c * 0.25);
        l.alpha = (0.05 + r() * 0.16) * (0.6 + c * 0.35) * (1.1 - q * 0.5) * v.exposure;
      } else {
        l.width = 0.45 + r() * 1.0;
        l.hue = r() * 0.85;
        l.alpha = (0.04 + r() * 0.1) * v.laneAlpha;
      }
      return l;
    });
    this.comets = [];
    for (let i = 0; i < this.nComets; i++) this.comets.push(this.spawn(true, false));
    for (let i = 0; i < this.nFast; i++) this.comets.push(this.spawn(true, true));
    // ribbons: wide soft bands of light that ride the center lanes (the river of the long exposure)
    const mid = (this.nLanes - 1) / 2;
    this.ribbons = Array.from({ length: v.ribbons || 0 }, (_, i) => ({
      lane: Math.round(mid + (i - ((v.ribbons || 1) - 1) / 2) * (this.nLanes / 16) + (r() - 0.5) * 2),
      width: 24 + r() * 70,
      alpha: 0.035 + r() * 0.05,
      hue: 0.12 + r() * 0.4,
    }));
  }

  pickLane() {
    const r = this.rnd, n = this.lanes.length, b = this.v.centerBias;
    if (!b) return Math.floor(r() * n);
    // average of several uniforms: most comets travel the middle lanes, a few the outer ones
    let a = 0;
    for (let i = 0; i <= b; i++) a += r();
    return Math.min(n - 1, Math.floor((a / (b + 1)) * n));
  }

  spawn(initial, fast) {
    const r = this.rnd;
    const c = {
      lane: this.pickLane(),
      u: initial ? r() * 1.3 - 0.15 : -0.1 - r() * 0.5,
      speed: (fast ? 0.7 + r() * 0.7 : 0.07 + r() * 0.22) * this.v.speed,
      len: fast ? 0.28 + r() * 0.3 : 0.1 + r() * 0.3,
      width: fast ? 0.8 + r() * 0.8 : 1 + r() * 1.8,
      hue: fast ? 0.7 + r() * 0.3 : r(),
      bright: (0.45 + r() * 0.55) * this.v.cometAlpha,
      fast,
    };
    if (this.film) {
      // film: longer, softer trails with a wider spread of widths (a few thick, most fine)
      const q = r();
      c.len += fast ? 0 : 0.04;
      c.width = fast ? 0.8 + q * 1.4 : 0.9 + q * q * 3.2;
      c.hue = 0.2 + c.hue * 0.8;
      c.bright *= this.v.exposure;
    }
    return c;
  }

  resize() {
    // the layout box, not getBoundingClientRect(): the reel enters with a scale(.95) reveal, and a backing store
    // sized while it is scaled stays 5% too small (upscaled, soft) once the transform is gone
    let cw = this.c.clientWidth, ch = this.c.clientHeight;
    if (!cw || !ch) {
      const rect = this.c.getBoundingClientRect();
      cw = rect.width; ch = rect.height;
    }
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.w = Math.max(1, cw);
    this.h = Math.max(1, ch);
    this.dpr = dpr;
    const W = Math.round(this.w * dpr), H = Math.round(this.h * dpr);
    if (this.c.width !== W || this.c.height !== H) {
      this.c.width = W;
      this.c.height = H;
    }
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.scale = Math.min(1.6, Math.max(0.6, this.w / 1200));
    if (this.film) {
      // soft: the trail layer, at device resolution so the trails stay crisp; half: a half CSS resolution copy (two
      // even steps down to the glow, so fine trails never shimmer in it); glow: the trails' 1/8 mean; light: the
      // 1/8 frame where the halation (blurred on the CPU), base, bloom and vignette are combined
      this.soft = layer(this.w * dpr, this.h * dpr);
      this.half = layer(this.w * 0.5, this.h * 0.5);
      this.glow = layer(this.w / 8, this.h / 8);
      this.light = layer(this.w / 8, this.h / 8);
      const n3 = this.light.width * this.light.height * 3;
      this.gSrc = new Float32Array(n3);
      this.gWide = new Float32Array(n3);
      this.gMid = new Float32Array(n3);
      this.gTmp = new Float32Array(n3);
      this.gHas = false; // new, empty glow layer: the next frame reads its own
      // trail compositing: the trails scaled by how much room the light under them has left (amber part and
      // warm white part), at the soft layer's (device) resolution
      this.trail = layer(this.soft.width, this.soft.height);
      this.trailW = layer(this.soft.width, this.soft.height);
      this.roomA = layer(this.light.width, this.light.height);
      this.roomW = layer(this.light.width, this.light.height);
      this.field();
      if (!this.noise) this.makeNoise();
    }
  }

  /* static per-pixel field at 1/8 resolution (recomputed on resize only): the navy base, the warm bloom
     (as a screen colour and amount) and the vignette amount */
  field() {
    const v = this.v, w = this.w, h = this.h, T = this.light, tw = T.width, th = T.height;
    const portrait = h > w;
    const fx = this.x(v.focus), fy = h * v.center;
    const n = tw * th;
    const base = new Float32Array(n * 3), bloom = new Float32Array(n * 3), vig = new Float32Array(n);
    // base: elliptical radial gradient, #0B2350 (CORE) at the centre to #030B1C (EDGE)
    const R0 = portrait ? h * 0.62 : w * 0.62, sy0 = portrait ? 0.9 : 0.6;
    const MID = [mix(EDGE[0], CORE[0], 0.55), mix(EDGE[1], CORE[1], 0.55), mix(EDGE[2], CORE[2], 0.55)];
    // bloom: amber falling off from a warm white core (#FFE9C2), a wide flat ellipse
    const sy1 = portrait ? 0.55 : Math.max(0.26, Math.min(0.5, (h / w) * 0.6));
    const R1 = portrait ? Math.max(w * 0.72, h * 0.4) : w * 0.44;
    const k = v.bloom;
    const stops = [
      [0, 255, 233, 194, 0.75 * k], [0.06, 255, 222, 168, 0.42 * k], [0.16, 255, 186, 64, 0.22 * k],
      [0.36, 255, 156, 30, 0.15 * k], [0.62, 236, 130, 14, 0.07 * k], [1, 236, 130, 14, 0],
    ];
    // vignette: clear inside 0.32 of the short side, navy-deep at v.vignette in the corners
    const r0 = Math.min(w, h) * 0.32, r1 = Math.hypot(w, h) * 0.55;
    for (let j = 0; j < th; j++) {
      const y = ((j + 0.5) / th) * h;
      for (let i = 0; i < tw; i++) {
        const x = ((i + 0.5) / tw) * w, q = j * tw + i;
        let d = Math.min(1, Math.hypot(x - fx, (y - fy) / sy0) / R0);
        const c = d < 0.4 ? [CORE, MID, d / 0.4] : [MID, EDGE, (d - 0.4) / 0.6];
        for (let ch = 0; ch < 3; ch++) base[q * 3 + ch] = mix(c[0][ch], c[1][ch], c[2]) / 255;
        d = Math.min(1, Math.hypot(x - fx, (y - fy) / sy1) / R1);
        let si = 0;
        while (si < stops.length - 2 && d > stops[si + 1][0]) si++;
        const A = stops[si], B = stops[si + 1], f = Math.min(1, (d - A[0]) / (B[0] - A[0]));
        const a = mix(A[4], B[4], f);
        for (let ch = 0; ch < 3; ch++) bloom[q * 3 + ch] = (mix(A[ch + 1], B[ch + 1], f) / 255) * a;
        const rv = Math.hypot(x - w / 2, y - h / 2);
        vig[q] = Math.max(0, Math.min(1, (rv - r0) / (r1 - r0))) * v.vignette;
      }
    }
    this.fBase = base; this.fBloom = bloom; this.fVig = vig;
  }

  makeNoise() {
    const n = document.createElement("canvas");
    n.width = n.height = 192;
    const g = n.getContext("2d");
    const img = g.createImageData(192, 192);
    const r = mulberry32(99);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = ((r() + r() + r()) / 3 * 255) | 0; // soft (triangular-ish) distribution around mid grey
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    this.noise = this.ctx.createPattern(n, "repeat");
  }

  x(u) { return (u * 1.12 - 0.06) * this.w; }

  y(l, u, t) {
    const v = this.v, H = this.h;
    const d = (u - v.focus) / 0.3;
    const spread = 1 - v.pinch * Math.exp(-d * d);
    // tall (phone) frames: the river spreads further and crosses more steeply, so the light fills the frame
    const tall = this.film && H > this.w;
    const base = H * (v.center + l.off * spread * v.spread * (tall ? 0.62 : 0.5));
    // amplitudes follow the frame's short side, so tall (phone) frames do not turn wavy
    const A = Math.min(H, this.w * 0.62);
    const wave = Math.sin(u * l.freq * Math.PI * 2 + l.phase + t * l.drift) * l.amp * A;
    const swell = Math.sin(u * Math.PI * 1.15 + t * 0.11) * A * 0.05 * v.swell;
    const tilt = v.tilt ? (v.focus - u) * v.tilt * (tall ? H * 1.1 : A) : 0;
    return base + wave * (0.35 + 0.65 * spread) + swell + tilt;
  }

  syncUi() {
    if (this.scope) this.scope.classList.toggle("is-paused", this.paused);
    // a toggle button keeps one fixed name ("Pause reel"); aria-pressed carries the state
    if (this.toggle) this.toggle.setAttribute("aria-pressed", String(this.paused));
  }

  update() {
    const run = this.visible && !this.paused && !document.hidden;
    if (run && !this.raf) {
      this.last = performance.now();
      this.raf = requestAnimationFrame((n) => this.tick(n));
    } else if (!run && this.raf) {
      cancelAnimationFrame(this.raf);
      this.raf = 0;
    }
  }

  tick(now) {
    const dt = Math.min(0.05, (now - this.last) / 1000);
    this.last = now;
    this.t += dt;
    for (let i = 0; i < this.comets.length; i++) {
      const c = this.comets[i];
      c.u += c.speed * dt;
      if (c.u - c.len > 1.08) this.comets[i] = this.spawn(false, c.fast);
    }
    this.draw();
    this.raf = requestAnimationFrame((n) => this.tick(n));
  }

  lanePath(l, t, u0 = 0, u1 = 1, n = 56) {
    const p = new Path2D();
    for (let i = 0; i <= n; i++) {
      const u = u0 + ((u1 - u0) * i) / n;
      if (i === 0) p.moveTo(this.x(u), this.y(l, u, t)); else p.lineTo(this.x(u), this.y(l, u, t));
    }
    return p;
  }

  draw() {
    if (this.film) this.drawFilm(); else this.drawAccent();
  }

  /* the trails' 1/8 mean (G over black), read back to the CPU */
  readGlow() {
    const T = this.light, tx = T.getContext("2d", { willReadFrequently: true });
    tx.globalCompositeOperation = "source-over";
    tx.globalAlpha = 1;
    tx.fillStyle = "#000";
    tx.fillRect(0, 0, T.width, T.height);
    tx.drawImage(this.glow, 0, 0, T.width, T.height);
    return tx.getImageData(0, 0, T.width, T.height).data;
  }

  /* ---------- reel: filmic long exposure ---------- */
  drawFilm() {
    const ctx = this.ctx, w = this.w, h = this.h, v = this.v, t = this.t, s = this.scale;
    const portrait = h > w;
    // while it runs, the light is built from the previous frame's mean (read before this frame's trails are
    // queued, so the read never waits on the GPU drawing them; one frame late is invisible in a glow). A static
    // frame (first draw, resize, reduced motion) reads its own.
    let gm = this.raf && this.gHas ? this.readGlow() : null;

    // 1. trail layer at device resolution: lanes and comets, varied width and opacity, no heads
    const S = this.soft, sx = S.getContext("2d");
    sx.setTransform(S.width / w, 0, 0, S.height / h, 0, 0);
    sx.globalCompositeOperation = "source-over";
    sx.clearRect(0, 0, w, h);
    sx.globalCompositeOperation = "lighter";
    sx.lineCap = "round";
    sx.lineJoin = "round";
    // ribbons: wide bands along the center lanes, faded at both ends
    for (const rb of this.ribbons) {
      const l = this.lanes[Math.max(0, Math.min(this.lanes.length - 1, rb.lane))];
      const g = sx.createLinearGradient(0, 0, w, 0);
      g.addColorStop(0, color(rb.hue, 0, FILM_PALETTE));
      g.addColorStop(0.2, color(rb.hue, rb.alpha * 0.25, FILM_PALETTE));
      g.addColorStop(0.5, color(rb.hue, rb.alpha, FILM_PALETTE));
      g.addColorStop(0.8, color(rb.hue, rb.alpha * 0.25, FILM_PALETTE));
      g.addColorStop(1, color(rb.hue, 0, FILM_PALETTE));
      sx.strokeStyle = g;
      sx.lineWidth = rb.width * s * (portrait ? 0.7 : 1);
      sx.stroke(this.lanePath(l, t));
    }
    // exposure lanes: persistent trails, brighter toward the middle of the frame
    for (const l of this.lanes) {
      const g = sx.createLinearGradient(0, 0, w, 0);
      g.addColorStop(0, color(l.hue * 0.7, l.alpha * 0.35, FILM_PALETTE));
      g.addColorStop(0.5, color(l.hue, l.alpha, FILM_PALETTE));
      g.addColorStop(1, color(l.hue * 0.7, l.alpha * 0.35, FILM_PALETTE));
      sx.strokeStyle = g;
      sx.lineWidth = l.width * s;
      sx.stroke(this.lanePath(l, t));
    }
    // moving light: a wide dim pass and a core pass, fading in from the tail and easing off at the front
    for (const c of this.comets) {
      const l = this.lanes[c.lane];
      const u1 = c.u, u0 = c.u - c.len;
      if (u1 < -0.08 || u0 > 1.08) continue;
      const path = this.lanePath(l, t, u0, u1, 18);
      const g = sx.createLinearGradient(this.x(u0), this.y(l, u0, t), this.x(u1), this.y(l, u1, t));
      g.addColorStop(0, color(c.hue, 0, FILM_PALETTE));
      g.addColorStop(0.75, color(c.hue, 0.5 * c.bright, FILM_PALETTE));
      g.addColorStop(0.93, color(Math.min(1, c.hue + 0.15), 0.75 * c.bright, FILM_PALETTE));
      g.addColorStop(1, color(c.hue, 0.2 * c.bright, FILM_PALETTE));
      sx.strokeStyle = g;
      sx.lineWidth = c.width * 3.2 * s;
      sx.globalAlpha = 0.3;
      sx.stroke(path);
      sx.globalAlpha = 1;
      sx.lineWidth = c.width * s;
      sx.stroke(path);
    }

    // 2. the trails averaged down to 1/2, then 1/8 (G): their local mean, the source of the halation
    const Hf = this.half, fx2 = Hf.getContext("2d");
    fx2.globalCompositeOperation = "copy";
    fx2.imageSmoothingQuality = "high";
    fx2.drawImage(S, 0, 0, Hf.width, Hf.height);
    const G = this.glow, gx = G.getContext("2d");
    gx.globalCompositeOperation = "copy";
    gx.imageSmoothingQuality = "high";
    gx.drawImage(Hf, 0, 0, G.width, G.height);

    // 3. the 1/8 frame, on the CPU (about 15k pixels). First the trail layer's local mean (G), which says how
    //    bright the trails over each pixel get. The halation is G blurred twice on the CPU, wide (sigma about
    //    5 px of this frame) and medium (about 1.4 px), three box passes each: a smooth falloff where the old
    //    1/24 and 1/64 layers scaled back up drew blotchy blocks. Then the glow summed at half gain and per pixel:
    //    a filmic shoulder on luma with the hue kept; the navy base pulled down under the light so amber stays
    //    amber (no khaki); the warm bloom (screen); the navy vignette; the highlights graded toward warm white
    //    #FFE9C2 (never lemon). Last, the additive sum with the sharp trails is tone mapped: added as is, amber
    //    on amber clips red first and then green, and the hottest light turns lemon. So each pixel keeps two
    //    room masks: how much of a trail can stay amber before the sum reaches the warm white ceiling (roomA,
    //    from the trails' local peak), and what is left of the ceiling for the rest of its light, added as warm
    //    white (roomW). A trail crossing the core lifts it toward #FFE9C2, never past it. Everything smooth
    //    lives here, so the full-size frame takes only a few more passes: this frame scaled up, the trails
    //    through the two masks (at device resolution, 1:1 with the canvas) and the grain.
    const T = this.light, tx = T.getContext("2d", { willReadFrequently: true }), tw = T.width, th = T.height;
    if (!gm) gm = this.readGlow();
    this.gHas = true;
    const gs = this.gSrc, gw = this.gWide, gd = this.gMid, gt = this.gTmp;
    for (let i = 0, q = 0; i < gm.length; i += 4, q += 3) { gs[q] = gm[i]; gs[q + 1] = gm[i + 1]; gs[q + 2] = gm[i + 2]; }
    blur3(gs, gw, gt, tw, th, 4);
    blur3(gs, gd, gt, tw, th, 1);
    if (!this.roomImg || this.roomImg[0].width !== tw || this.roomImg[0].height !== th) {
      this.roomImg = [tx.createImageData(tw, th), tx.createImageData(tw, th), tx.createImageData(tw, th)];
    }
    const img = this.roomImg[2], d = img.data;
    // the glow at half gain, as the old additive passes summed it (3 x wide + medium + .55 x the mean, clipped)
    for (let i = 0, q = 0; i < d.length; i += 4, q += 3) {
      d[i] = Math.min(255, 0.5 * (3 * gw[q] + gd[q] + 0.55 * gs[q]));
      d[i + 1] = Math.min(255, 0.5 * (3 * gw[q + 1] + gd[q + 1] + 0.55 * gs[q + 1]));
      d[i + 2] = Math.min(255, 0.5 * (3 * gw[q + 2] + gd[q + 2] + 0.55 * gs[q + 2]));
    }
    const ra = this.roomImg[0].data, rw = this.roomImg[1].data;
    const fb = this.fBase, fl = this.fBloom, fv = this.fVig;
    const E = 2 * v.glow, sh = v.shade, eR = EDGE[0] / 255, eG = EDGE[1] / 255, eB = EDGE[2] / 255;
    const wR = WARM[0], wG = WARM[1], wB = WARM[2], top = v.core, kP = v.trailPeak / 255, kW = v.trailWhite;
    // the ceiling the trails lift the light to: #FFE9C2 lifted toward white by v.lift (a trail still reads over the core)
    const cR = wR + (1 - wR) * v.lift, cG = wG + (1 - wG) * v.lift, cB = wB + (1 - wB) * v.lift;
    for (let i = 0, q = 0; i < d.length; i += 4, q++) {
      let r = (d[i] / 255) * E, g = (d[i + 1] / 255) * E, b = (d[i + 2] / 255) * E;
      const L = 0.299 * r + 0.587 * g + 0.114 * b;
      let o = 1;
      if (L > 0.002) {
        const Lt = 1 - Math.exp(-L * 1.15);
        const k = Lt / L;
        r *= k; g *= k; b *= k;
        let u = (Lt - 0.42) / 0.5;
        if (u > 0) {
          u = Math.min(1, u); u *= u;
          const c = Lt / LW;
          r += (wR * c - r) * u; g += (wG * c - g) * u; b += (wB * c - b) * u;
        }
        o = 1 - Math.min(1, Lt * 1.6) * sh;
      }
      const q3 = q * 3;
      r = Math.min(1, fb[q3] * o + r); g = Math.min(1, fb[q3 + 1] * o + g); b = Math.min(1, fb[q3 + 2] * o + b);
      r += fl[q3] * (1 - r); g += fl[q3 + 1] * (1 - g); b += fl[q3 + 2] * (1 - b);
      const a = fv[q];
      r += (eR - r) * a; g += (eG - g) * a; b += (eB - b) * a;
      // highlights graded toward warm white: the core settles just under #FFE9C2 (v.core), mids stay amber
      let s = (0.299 * r + 0.587 * g + 0.114 * b - 0.5) * 2;
      if (s > 0) {
        s = Math.min(1, s); s *= s * (3 - 2 * s);
        r *= 1 + (wR * top - 1) * s; g *= 1 + (wG * top - 1) * s; b *= 1 + (wB * top - 1) * s;
      }
      d[i] = r * 255; d[i + 1] = g * 255; d[i + 2] = b * 255;
      d[i + 3] = 255;
      // room for the trails: their local peak is about trailPeak x their local mean
      const pr = Math.min(1, gm[i] * kP), pg = Math.min(1, gm[i + 1] * kP), pb = Math.min(1, gm[i + 2] * kP);
      const hr = cR - r, hg = cG - g, hb = cB - b;
      let m = 1;
      if (pr > 0.004) m = Math.min(m, hr / pr);
      if (pg > 0.004) m = Math.min(m, hg / pg);
      if (pb > 0.004) m = Math.min(m, hb / pb);
      if (m < 0) m = 0;
      const n = (1 - m) * kW * 255;
      ra[i] = ra[i + 1] = ra[i + 2] = m * 255;
      rw[i] = Math.max(0, hr - m * pr) * n; rw[i + 1] = Math.max(0, hg - m * pg) * n; rw[i + 2] = Math.max(0, hb - m * pb) * n;
      ra[i + 3] = rw[i + 3] = 255;
    }
    tx.putImageData(img, 0, 0);
    this.roomA.getContext("2d").putImageData(this.roomImg[0], 0, 0);
    this.roomW.getContext("2d").putImageData(this.roomImg[1], 0, 0);

    ctx.globalAlpha = 1;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "medium";
    ctx.globalCompositeOperation = "copy";
    ctx.drawImage(T, 0, 0, w, h);
    // the trails through the room masks, at device resolution: the amber part (trails x roomA) plus the warm
    // white part (the trails' luminance x roomW), then added to the frame in one 1:1 pass (no upscale, so crisp)
    const Q = this.trail, qx = Q.getContext("2d"), P = this.trailW, px = P.getContext("2d"), qw = Q.width, qh = Q.height;
    qx.imageSmoothingEnabled = px.imageSmoothingEnabled = true;
    qx.imageSmoothingQuality = px.imageSmoothingQuality = "high";
    qx.globalCompositeOperation = "source-over";
    qx.fillStyle = "#000";
    qx.fillRect(0, 0, qw, qh);
    qx.drawImage(S, 0, 0, qw, qh);
    px.globalCompositeOperation = "copy";
    px.drawImage(Q, 0, 0);
    px.globalCompositeOperation = "saturation";
    px.fillStyle = "#808080";
    px.fillRect(0, 0, qw, qh);
    px.globalCompositeOperation = "multiply";
    px.drawImage(this.roomW, 0, 0, qw, qh);
    qx.globalCompositeOperation = "multiply";
    qx.drawImage(this.roomA, 0, 0, qw, qh);
    qx.globalCompositeOperation = "lighter";
    qx.drawImage(P, 0, 0);
    ctx.globalCompositeOperation = "lighter";
    ctx.drawImage(Q, 0, 0, w, h);

    // 4. grain: overlay for the mids, a faint veil for the shadows; it moves every other frame (a 24-30 fps
    //    feel) and stays put on the static frame
    if (v.grain && this.noise) {
      if (this.frame++ % 2 === 0 || !this.grainAt) this.grainAt = [(Math.random() * 192) | 0, (Math.random() * 192) | 0];
      const [ox, oy] = this.grainAt;
      ctx.save();
      ctx.translate(-ox, -oy);
      ctx.fillStyle = this.noise;
      ctx.globalCompositeOperation = "overlay";
      ctx.globalAlpha = v.grain;
      ctx.fillRect(0, 0, w + 192, h + 192);
      ctx.globalCompositeOperation = "source-over";
      ctx.globalAlpha = v.grain * 0.22;
      ctx.fillRect(0, 0, w + 192, h + 192);
      ctx.restore();
    }
    ctx.globalCompositeOperation = "source-over";
    ctx.globalAlpha = 1;
  }

  /* ---------- accent: transparent streaks over the hero image ---------- */
  drawAccent() {
    const ctx = this.ctx, w = this.w, h = this.h, v = this.v, t = this.t, s = this.scale;
    ctx.globalCompositeOperation = "source-over";
    ctx.globalAlpha = 1;
    ctx.clearRect(0, 0, w, h);
    const fx = this.x(v.focus), fy = h * v.center;

    // warm amber haze around the focus point
    const haze = ctx.createRadialGradient(fx, fy, 0, fx, fy, Math.max(w, h) * 0.55);
    haze.addColorStop(0, `rgba(255,176,20,${v.haze})`);
    haze.addColorStop(0.45, `rgba(255,150,10,${v.haze * 0.35})`);
    haze.addColorStop(1, "rgba(255,150,10,0)");
    ctx.fillStyle = haze;
    ctx.fillRect(0, 0, w, h);

    ctx.globalCompositeOperation = "lighter";
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    for (const l of this.lanes) {
      ctx.strokeStyle = color(l.hue, l.alpha);
      ctx.lineWidth = l.width * s;
      ctx.stroke(this.lanePath(l, t));
    }

    for (const c of this.comets) {
      const l = this.lanes[c.lane];
      const u1 = c.u, u0 = c.u - c.len;
      if (u1 < -0.08 || u0 > 1.08) continue;
      const path = this.lanePath(l, t, u0, u1, 18);
      const x0 = this.x(u0), y0 = this.y(l, u0, t), x1 = this.x(u1), y1 = this.y(l, u1, t);

      const glow = ctx.createLinearGradient(x0, y0, x1, y1);
      glow.addColorStop(0, color(c.hue * 0.6, 0));
      glow.addColorStop(1, color(c.hue * 0.6, 0.2 * c.bright));
      ctx.strokeStyle = glow;
      ctx.lineWidth = c.width * 8 * s;
      ctx.stroke(path);

      const core = ctx.createLinearGradient(x0, y0, x1, y1);
      core.addColorStop(0, color(c.hue, 0));
      core.addColorStop(0.7, color(c.hue, Math.min(1, 0.62 * c.bright)));
      core.addColorStop(1, color(Math.min(1, c.hue + 0.3), Math.min(1, 1 * c.bright)));
      ctx.strokeStyle = core;
      ctx.lineWidth = c.width * s;
      ctx.stroke(path);

      const r = (c.fast ? 5 : 8) * c.width * s;
      const head = ctx.createRadialGradient(x1, y1, 0, x1, y1, r);
      head.addColorStop(0, `rgba(255,247,230,${0.85 * c.bright})`);
      head.addColorStop(0.35, `rgba(255,191,0,${0.22 * c.bright})`);
      head.addColorStop(1, "rgba(255,162,26,0)");
      ctx.fillStyle = head;
      ctx.fillRect(x1 - r, y1 - r, r * 2, r * 2);
    }
    ctx.globalCompositeOperation = "source-over";
  }
}

export function initStreaks(nodes, { reduced = false } = {}) {
  const list = [];
  nodes.forEach((canvas) => {
    if (!canvas.getContext) return;
    try { list.push(new Streaks(canvas, reduced)); } catch (e) { /* canvas unsupported: fallback gradient stays */ }
  });
  return list;
}
