/* Live long-exposure light streaks on a <canvas>.
   <canvas data-streaks="reel"> (full frame, filmic, on deep navy) or data-streaks="accent" (transparent, softer,
   for hero overlays). Brand: amber #FFBF00 and warm white light on navy shadows #030B1C / #071B3E (never neutral
   black, never royal blue). Optional controls: a [data-streaks-scope] ancestor with a [data-streaks-toggle]
   button; the scope gets .is-paused. DPR-aware (capped at 2), pauses offscreen / hidden tab / on toggle, one static
   frame under reduced motion. */

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
   most #0B2350 behind the light, a river of amber trails pinched through the middle, drawn on a half resolution
   layer so every trail is soft (no vector lines, no comet heads), two blurred glow passes, a warm amber bloom
   with a white core, a navy vignette and film grain. Mean luma about 58 at 1440.
   accent: transparent overlay for the hero. */
const VARIANTS = {
  reel: { film: true, lanes: 72, comets: 44, fast: 10, ribbons: 6, spread: 1.4, pinch: 0.48, tilt: 0.3, focus: 0.5, center: 0.5, swell: 0.8, laneAlpha: 1, cometAlpha: 1, centerBias: 2, exposure: 1.05, shade: 0.85, lightGain: 1, bloom: 1.25, glow: 1.8, vignette: 0.5, grain: 0.1, speed: 0.85 },
  accent: { lanes: 22, comets: 14, fast: 4, spread: 1.1, pinch: 0.45, focus: 0.62, center: 0.42, swell: 0.8, laneAlpha: 0.75, cometAlpha: 0.8, centerBias: 0, haze: 0.05, speed: 0.8 },
};

const EDGE = [3, 11, 28];    // #030B1C navy-deep
const CORE = [11, 35, 80];   // #0B2350, the brightest the base gets

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
    const k = film && (this.c.getBoundingClientRect().width || 1200) < 640 ? 0.75 : 1;
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
    const rect = this.c.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.w = Math.max(1, rect.width);
    this.h = Math.max(1, rect.height);
    this.dpr = dpr;
    const W = Math.round(this.w * dpr), H = Math.round(this.h * dpr);
    if (this.c.width !== W || this.c.height !== H) {
      this.c.width = W;
      this.c.height = H;
    }
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.scale = Math.min(1.6, Math.max(0.6, this.w / 1200));
    if (this.film) {
      // soft: half CSS resolution (about 2px of trail blur); glow chain 1/8, 1/24, 1/64 (wide halation);
      // light: the 1/8 frame where base, glow, bloom and vignette are combined on the CPU
      this.soft = layer(this.w * 0.5, this.h * 0.5);
      this.glow = layer(this.w / 8, this.h / 8);
      this.haze = layer(this.w / 24, this.h / 24);
      this.mist = layer(this.w / 64, this.h / 64);
      this.light = layer(this.w / 8, this.h / 8);
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
    // bloom: amber falling off from a white core, a wide flat ellipse
    const sy1 = portrait ? 0.55 : Math.max(0.26, Math.min(0.5, (h / w) * 0.6));
    const R1 = portrait ? Math.max(w * 0.72, h * 0.4) : w * 0.44;
    const k = v.bloom;
    const stops = [
      [0, 255, 248, 236, 0.75 * k], [0.06, 255, 234, 198, 0.42 * k], [0.16, 255, 186, 64, 0.22 * k],
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
    if (this.toggle) {
      this.toggle.setAttribute("aria-pressed", String(this.paused));
      this.toggle.setAttribute("aria-label", this.paused ? (this.toggle.dataset.labelPlay || "Play animation") : (this.toggle.dataset.labelPause || "Pause animation"));
    }
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

  /* ---------- reel: filmic long exposure ---------- */
  drawFilm() {
    const ctx = this.ctx, w = this.w, h = this.h, v = this.v, t = this.t, s = this.scale;
    const portrait = h > w;

    // 1. soft trail layer at half resolution: lanes and comets, varied width and opacity, no heads
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

    // 2. glow chain: the soft layer averaged down to 1/8, 1/24 and 1/64 (scaled back up = wide halation)
    const G = this.glow, gx = G.getContext("2d");
    gx.globalCompositeOperation = "copy";
    gx.imageSmoothingQuality = "high";
    gx.drawImage(S, 0, 0, G.width, G.height);
    const Hz = this.haze, hx = Hz.getContext("2d");
    hx.globalCompositeOperation = "copy";
    hx.imageSmoothingQuality = "high";
    hx.drawImage(G, 0, 0, Hz.width, Hz.height);
    const M = this.mist, mx = M.getContext("2d");
    mx.globalCompositeOperation = "copy";
    mx.imageSmoothingQuality = "high";
    mx.drawImage(Hz, 0, 0, M.width, M.height);

    // 3. the 1/8 frame: glow summed at half gain (no clipping), then on the CPU (about 15k pixels):
    //    a filmic shoulder on luma with the hue kept, the brightest light rolling off to warm white (not
    //    lemon); the navy base pulled down under the light so amber stays amber (no khaki); the warm bloom
    //    (screen) and the navy vignette. Everything smooth lives here, so the full-size frame takes only
    //    three more passes: this frame scaled up, the soft trails and the grain.
    const T = this.light, tx = T.getContext("2d", { willReadFrequently: true });
    tx.imageSmoothingQuality = "high";
    tx.globalCompositeOperation = "source-over";
    tx.globalAlpha = 1;
    tx.fillStyle = "#000";
    tx.fillRect(0, 0, T.width, T.height);
    tx.globalCompositeOperation = "lighter";
    tx.globalAlpha = 0.5;
    tx.drawImage(M, 0, 0, T.width, T.height);
    tx.drawImage(M, 0, 0, T.width, T.height);
    tx.drawImage(M, 0, 0, T.width, T.height);
    tx.drawImage(Hz, 0, 0, T.width, T.height);
    tx.globalAlpha = 0.5 * 0.55;
    tx.drawImage(G, 0, 0, T.width, T.height);
    tx.globalAlpha = 1;
    const img = tx.getImageData(0, 0, T.width, T.height), d = img.data;
    const fb = this.fBase, fl = this.fBloom, fv = this.fVig;
    const E = 2 * v.glow, sh = v.shade, eR = EDGE[0] / 255, eG = EDGE[1] / 255, eB = EDGE[2] / 255;
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
          r += (Lt * 1.08 - r) * u; g += (Lt - g) * u; b += (Lt * 0.86 - b) * u;
        }
        o = 1 - Math.min(1, Lt * 1.6) * sh;
      }
      const q3 = q * 3;
      r = Math.min(1, fb[q3] * o + r); g = Math.min(1, fb[q3 + 1] * o + g); b = Math.min(1, fb[q3 + 2] * o + b);
      r += fl[q3] * (1 - r); g += fl[q3 + 1] * (1 - g); b += fl[q3 + 2] * (1 - b);
      const a = fv[q];
      d[i] = (r + (eR - r) * a) * 255; d[i + 1] = (g + (eG - g) * a) * 255; d[i + 2] = (b + (eB - b) * a) * 255;
      d[i + 3] = 255;
    }
    tx.putImageData(img, 0, 0);

    ctx.globalAlpha = 1;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "medium";
    ctx.globalCompositeOperation = "copy";
    ctx.drawImage(T, 0, 0, w, h);
    ctx.globalCompositeOperation = "lighter";
    ctx.drawImage(S, 0, 0, w, h);

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
