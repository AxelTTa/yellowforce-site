/* Live long-exposure light streaks on a <canvas>.
   <canvas data-streaks="reel"> (full, on deep navy) or data-streaks="accent" (transparent, softer, for hero overlays).
   Brand: amber #FFBF00 and warm white light on navy #071B3E / #041029 shadows (never neutral black).
   Optional controls: a [data-streaks-scope] ancestor with a [data-streaks-toggle] button; the scope gets .is-paused.
   DPR-aware (capped at 2), pauses offscreen / hidden tab / on toggle, static frame under reduced motion. */

const PALETTE = [
  [255, 191, 0],   // brand amber #FFBF00
  [255, 162, 26],  // warm amber (glow)
  [255, 218, 128], // pale gold
  [255, 245, 226], // warm white
];

const VARIANTS = {
  reel: { lanes: 42, comets: 30, fast: 8, bg: "#041029", lift: 0.5, spread: 1.35, pinch: 0.62, focus: 0.56, center: 0.52, swell: 1, laneAlpha: 1, cometAlpha: 1, grain: 0.07, haze: 0.085, speed: 1 },
  accent: { lanes: 22, comets: 14, fast: 4, bg: null, lift: 0, spread: 1.1, pinch: 0.45, focus: 0.62, center: 0.42, swell: 0.8, laneAlpha: 0.75, cometAlpha: 0.8, grain: 0, haze: 0.05, speed: 0.8 },
};

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
function color(h, alpha) {
  const x = Math.max(0, Math.min(0.999, h)) * (PALETTE.length - 1);
  const i = Math.floor(x), f = x - i;
  const p = PALETTE[i], q = PALETTE[i + 1];
  return `rgba(${mix(p[0], q[0], f) | 0},${mix(p[1], q[1], f) | 0},${mix(p[2], q[2], f) | 0},${alpha.toFixed(3)})`;
}

class Streaks {
  constructor(canvas, reduced) {
    this.c = canvas;
    this.v = VARIANTS[canvas.dataset.streaks] || VARIANTS.reel;
    this.ctx = canvas.getContext("2d", { alpha: !this.v.bg });
    this.reduced = reduced;
    this.visible = false;
    this.paused = reduced;
    this.raf = 0;
    this.t = 7.3;
    this.last = 0;
    this.drawnOnce = false;
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
    const r = this.rnd, v = this.v;
    this.lanes = Array.from({ length: v.lanes }, (_, i) => {
      const k = (i / (v.lanes - 1)) * 2 - 1;
      return {
        off: k * (0.36 + r() * 0.1) + (r() - 0.5) * 0.06,
        amp: 0.01 + r() * 0.045,
        freq: 0.5 + r() * 1.3,
        phase: r() * Math.PI * 2,
        drift: (r() - 0.5) * 0.35,
        width: 0.45 + r() * 1.0,
        hue: r() * 0.85,
        alpha: (0.04 + r() * 0.1) * v.laneAlpha,
      };
    });
    this.comets = [];
    for (let i = 0; i < v.comets; i++) this.comets.push(this.spawn(true, false));
    for (let i = 0; i < v.fast; i++) this.comets.push(this.spawn(true, true));
  }

  spawn(initial, fast) {
    const r = this.rnd;
    return {
      lane: Math.floor(r() * this.lanes.length),
      u: initial ? r() * 1.3 - 0.15 : -0.1 - r() * 0.5,
      speed: (fast ? 0.7 + r() * 0.7 : 0.07 + r() * 0.22) * this.v.speed,
      len: fast ? 0.28 + r() * 0.3 : 0.1 + r() * 0.3,
      width: fast ? 0.8 + r() * 0.8 : 1 + r() * 1.8,
      hue: fast ? 0.7 + r() * 0.3 : r(),
      bright: (0.45 + r() * 0.55) * this.v.cometAlpha,
      fast,
    };
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
    if (this.v.grain && !this.noise) this.makeNoise();
  }

  makeNoise() {
    const n = document.createElement("canvas");
    n.width = n.height = 160;
    const g = n.getContext("2d");
    const img = g.createImageData(160, 160);
    const r = mulberry32(99);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = (r() * 255) | 0;
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
    const base = H * (v.center + l.off * spread * v.spread * 0.5);
    const wave = Math.sin(u * l.freq * Math.PI * 2 + l.phase + t * l.drift) * l.amp * H;
    const swell = Math.sin(u * Math.PI * 1.15 + t * 0.11) * H * 0.05 * v.swell;
    return base + wave * (0.35 + 0.65 * spread) + swell;
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

  draw() {
    const ctx = this.ctx, w = this.w, h = this.h, v = this.v, t = this.t, s = this.scale;
    ctx.globalCompositeOperation = "source-over";
    ctx.globalAlpha = 1;
    const fx = this.x(v.focus), fy = h * v.center;
    if (v.bg) {
      ctx.fillStyle = v.bg;
      ctx.fillRect(0, 0, w, h);
      // brand navy lift behind the light, so the frame reads navy, not black
      if (v.lift) {
        const lift = ctx.createRadialGradient(fx, fy, 0, fx, fy, Math.max(w, h) * 0.75);
        lift.addColorStop(0, `rgba(18,48,95,${v.lift})`);
        lift.addColorStop(0.5, `rgba(7,27,62,${v.lift * 0.9})`);
        lift.addColorStop(1, "rgba(7,27,62,0)");
        ctx.fillStyle = lift;
        ctx.fillRect(0, 0, w, h);
      }
    } else {
      ctx.clearRect(0, 0, w, h);
    }

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

    // exposure lanes (faint persistent trails)
    const N = 56;
    for (const l of this.lanes) {
      ctx.beginPath();
      for (let i = 0; i <= N; i++) {
        const u = i / N;
        const X = this.x(u), Y = this.y(l, u, t);
        if (i === 0) ctx.moveTo(X, Y); else ctx.lineTo(X, Y);
      }
      ctx.strokeStyle = color(l.hue, l.alpha);
      ctx.lineWidth = l.width * s;
      ctx.stroke();
    }

    // comets: glow pass + core pass + hot head
    const M = 18;
    for (const c of this.comets) {
      const l = this.lanes[c.lane];
      const u1 = c.u, u0 = c.u - c.len;
      if (u1 < -0.08 || u0 > 1.08) continue;
      const pts = [];
      for (let i = 0; i <= M; i++) {
        const u = u0 + (c.len * i) / M;
        pts.push(this.x(u), this.y(l, u, t));
      }
      const x0 = pts[0], y0 = pts[1], x1 = pts[pts.length - 2], y1 = pts[pts.length - 1];
      const path = new Path2D();
      path.moveTo(x0, y0);
      for (let i = 2; i < pts.length; i += 2) path.lineTo(pts[i], pts[i + 1]);

      const glow = ctx.createLinearGradient(x0, y0, x1, y1);
      glow.addColorStop(0, color(c.hue * 0.6, 0));
      glow.addColorStop(1, color(c.hue * 0.6, 0.16 * c.bright));
      ctx.strokeStyle = glow;
      ctx.lineWidth = c.width * 7 * s;
      ctx.stroke(path);

      const core = ctx.createLinearGradient(x0, y0, x1, y1);
      core.addColorStop(0, color(c.hue, 0));
      core.addColorStop(0.7, color(c.hue, 0.55 * c.bright));
      core.addColorStop(1, color(Math.min(1, c.hue + 0.3), 0.95 * c.bright));
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

    // navy vignette + grain (reel only)
    if (v.bg) {
      const vig = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.25, w / 2, h / 2, Math.max(w, h) * 0.75);
      vig.addColorStop(0, "rgba(3,11,28,0)");
      vig.addColorStop(1, "rgba(3,11,28,0.6)");
      ctx.fillStyle = vig;
      ctx.fillRect(0, 0, w, h);
    }
    if (v.grain && this.noise) {
      ctx.save();
      ctx.globalAlpha = v.grain;
      ctx.globalCompositeOperation = "overlay";
      const ox = (Math.random() * 160) | 0, oy = (Math.random() * 160) | 0;
      ctx.translate(-ox, -oy);
      ctx.fillStyle = this.noise;
      ctx.fillRect(0, 0, w + 160, h + 160);
      ctx.restore();
    }
    this.drawnOnce = true;
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
