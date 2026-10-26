/* YellowForce site behaviour. Plain ES module, no build step.
   Globals from /assets/js/vendor: gsap, ScrollTrigger, SplitText, Lenis (all optional: the site works without them).
   The canvas engine (streaks.js) is imported on demand, only on pages that have a canvas (Home, 404). */

const EMAIL = "info@yellow-force.com";
const root = document.documentElement;
const reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
const { gsap, ScrollTrigger, SplitText, Lenis } = window;
const hasGsap = Boolean(gsap && ScrollTrigger);
const EASE = "power2.inOut";
// reveals: decelerating, so content is mostly there within the first 150 ms of its entrance
const EASE_IN = "power3.out";
// weak machine (same test as the canvas engine): native scrolling, no smoothing on top
const WEAK = (() => {
  try { return (navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 4; } catch (e) { return false; }
})();
let lenis = null;

const motionOn = () => !reduceMQ.matches && root.classList.contains("motion") && hasGsap;
const emOf = (el) => parseFloat(getComputedStyle(el).fontSize) || 16;

/* ---------- copy email + toast ---------- */
const URGENT_NOTE = "Put URGENT in the subject. We answer 24/7.";
let toastTimer = 0;
function toast(title, value, note = "", ms = 2400) {
  const el = document.querySelector("[data-toast]");
  if (!el) return;
  const t = el.querySelector("[data-toast-title]");
  const v = el.querySelector("[data-toast-value]");
  const n = el.querySelector("[data-toast-note]");
  // clear first so the polite live region announces repeat copies too
  [t, v, n].forEach((x) => { if (x) x.textContent = ""; });
  requestAnimationFrame(() => {
    if (t) t.textContent = title;
    if (v) v.textContent = value;
    if (n) { n.textContent = note; n.hidden = !note; }
    el.classList.add("is-visible");
  });
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("is-visible"), ms);
}

async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch (e) { /* fall through */ }
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;pointer-events:none;";
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand("copy");
    ta.remove();
    return ok;
  } catch (e) {
    return false;
  }
}

function selectNode(node) {
  if (!node) return;
  const range = document.createRange();
  range.selectNodeContents(node);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
}

function initCopyEmail() {
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-copy-email]");
    if (!btn) return;
    e.preventDefault();
    const urgent = btn.getAttribute("data-copy-email") === "urgent";
    const addr = btn.getAttribute("data-email") || EMAIL; // legal pages point at privacy@ / security@
    const ok = await copyText(addr);
    if (ok) {
      toast("Email copied", addr, urgent ? URGENT_NOTE : "");
      btn.classList.add("is-copied");
      setTimeout(() => btn.classList.remove("is-copied"), 2400);
    } else {
      // Clipboard blocked: show and select the address so the user can copy it.
      toast("Press Cmd+C or Ctrl+C to copy", addr, urgent ? URGENT_NOTE : "", 9000);
      const own = btn.querySelector("[data-email-text]");
      setTimeout(() => selectNode(own || document.querySelector("[data-toast-value]")), 40);
    }
  });
}

/* ---------- broken image slots: keep the gradient fallback ---------- */
function initMediaFallback() {
  document.querySelectorAll(".media img").forEach((img) => {
    const miss = () => img.classList.add("is-missing");
    if (img.complete && img.naturalWidth === 0 && img.getAttribute("src")) miss();
    img.addEventListener("error", miss, { once: true });
  });
}

/* ---------- nav bar + menu card (src/partials/nav.html) ---------- */
function initNav() {
  const shell = document.querySelector("[data-nav-shell]");
  if (!shell) return;
  const toggle = shell.querySelector("[data-nav-toggle]");
  const drawer = document.getElementById(toggle.getAttribute("aria-controls"));
  const scrim = document.querySelector("[data-nav-scrim]");
  let open = false;

  const focusables = () =>
    [...shell.querySelectorAll("a[href], button:not([disabled])")].filter((el) => el.offsetParent !== null && !el.closest("[hidden]"));

  function onKey(e) {
    if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false, true);
    } else if (e.key === "Tab") {
      // move focus ourselves on every Tab: Safari's default Tab skips links, so a wrap-only trap leaks
      const f = focusables();
      if (!f.length) return;
      e.preventDefault();
      const i = f.indexOf(document.activeElement);
      let n;
      if (i === -1) n = e.shiftKey ? f.length - 1 : 0;
      else n = (i + (e.shiftKey ? -1 : 1) + f.length) % f.length;
      f[n].focus();
    }
  }

  function setOpen(next, returnFocus) {
    if (next === open) return;
    open = next;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    shell.classList.toggle("is-open", open);
    root.classList.toggle("nav-open", open);
    const rows = drawer.querySelectorAll("[data-nav-anim]");
    if (open) {
      drawer.hidden = false;
      if (scrim) scrim.hidden = false;
      if (lenis) lenis.stop();
      document.addEventListener("keydown", onKey);
      // focus the first visible row before the rows fade in (rows tween opacity only, so they stay focusable)
      const first = focusables().find((el) => drawer.contains(el));
      if (first) first.focus({ preventScroll: true });
      if (motionOn()) {
        gsap.killTweensOf([drawer, scrim, ...rows]);
        gsap.fromTo(drawer, { height: 0 }, { height: "auto", duration: 0.45, ease: EASE_IN });
        // rows the bar already shows are display:none in the card from 768px up: no stagger slot for them
        const shown = [...rows].filter((el) => el.offsetParent !== null);
        gsap.fromTo(shown, { opacity: 0, y: emOf(drawer), scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.45, ease: EASE_IN, stagger: 0.05 });
        if (scrim) gsap.fromTo(scrim, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.35, ease: EASE_IN });
      }
    } else {
      if (lenis) lenis.start();
      document.removeEventListener("keydown", onKey);
      const done = () => {
        if (open) return;
        drawer.hidden = true;
        if (scrim) scrim.hidden = true;
        drawer.style.height = "";
      };
      if (motionOn()) {
        gsap.killTweensOf([drawer, scrim, ...rows]);
        gsap.to(drawer, { height: 0, duration: 0.4, ease: EASE_IN, onComplete: done });
        if (scrim) gsap.to(scrim, { autoAlpha: 0, duration: 0.35, ease: EASE_IN });
      } else {
        done();
      }
      if (returnFocus) toggle.focus({ preventScroll: true });
    }
  }

  toggle.addEventListener("click", () => setOpen(!open, false));
  if (scrim) scrim.addEventListener("click", () => setOpen(false, false));
  document.addEventListener("click", (e) => {
    if (open && !shell.contains(e.target) && !e.target.closest("[data-toast]")) setOpen(false, false);
  });
  drawer.addEventListener("click", (e) => {
    const a = e.target.closest("a[href]");
    if (a) setOpen(false, false);
  });

  drawer.querySelectorAll("[data-nav-sub]").forEach((btn) => {
    const panel = document.getElementById(btn.getAttribute("aria-controls"));
    if (!panel) return;
    btn.addEventListener("click", () => {
      const exp = btn.getAttribute("aria-expanded") !== "true";
      btn.setAttribute("aria-expanded", String(exp));
      const links = panel.querySelectorAll("li");
      if (exp) {
        panel.hidden = false;
        if (motionOn()) {
          gsap.fromTo(panel, { height: 0 }, { height: "auto", duration: 0.45, ease: EASE_IN });
          gsap.fromTo(links, { opacity: 0, y: emOf(panel) * 0.5 }, { opacity: 1, y: 0, duration: 0.45, ease: EASE_IN, stagger: 0.04 });
        }
      } else if (motionOn()) {
        gsap.to(panel, { height: 0, duration: 0.4, ease: EASE_IN, onComplete: () => { panel.hidden = true; panel.style.height = ""; } });
      } else {
        panel.hidden = true;
      }
    });
  });
}

/* ---------- FAQ accordion ---------- */
function initFaq() {
  document.querySelectorAll("[data-faq]").forEach((list) => {
    list.querySelectorAll(".faq__item").forEach((item) => {
      const btn = item.querySelector(".faq__q");
      const panel = item.querySelector(".faq__a");
      if (!btn || !panel) return;
      const inner = panel.firstElementChild;
      const startOpen = item.classList.contains("is-open");
      btn.setAttribute("aria-expanded", String(startOpen));
      panel.hidden = !startOpen;
      btn.addEventListener("click", () => {
        const open = btn.getAttribute("aria-expanded") !== "true";
        btn.setAttribute("aria-expanded", String(open));
        item.classList.toggle("is-open", open);
        if (motionOn()) {
          gsap.killTweensOf([panel, inner]);
          if (open) {
            panel.hidden = false;
            gsap.fromTo(panel, { height: 0 }, { height: "auto", duration: 0.45, ease: EASE_IN, onComplete: refreshSoon });
            gsap.fromTo(inner, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: EASE_IN });
          } else {
            gsap.to(inner, { opacity: 0, duration: 0.25, ease: EASE_IN });
            gsap.to(panel, { height: 0, duration: 0.4, ease: EASE_IN, onComplete: () => { panel.hidden = true; panel.style.height = ""; refreshSoon(); } });
          }
        } else {
          panel.hidden = !open;
        }
      });
    });
  });
}

let refreshTimer = 0;
function refreshSoon() {
  if (!hasGsap) return;
  clearTimeout(refreshTimer);
  refreshTimer = setTimeout(() => ScrollTrigger.refresh(), 120);
}

/* ---------- carousels ---------- */
class Carousel {
  constructor(el) {
    this.el = el;
    this.viewport = el.querySelector("[data-carousel-viewport]");
    this.track = el.querySelector("[data-carousel-track]");
    this.slides = [...this.track.children];
    this.prev = el.querySelector("[data-carousel-prev]");
    this.next = el.querySelector("[data-carousel-next]");
    this.index = 0;
    this.offset = 0;
    this.measure();
    this.el.classList.add("is-start");
    // keyboard focus on a slide brings that slide into view (the clipped section never scrolls natively);
    // a mouse press that focuses a card link is not keyboard focus and must not move the row mid-drag
    this.track.addEventListener("focusin", (e) => {
      let kb = true;
      try { kb = e.target.matches(":focus-visible"); } catch (err) { /* old engines: treat as keyboard */ }
      if (!kb) return;
      const i = this.slides.findIndex((s) => s.contains(e.target));
      if (i > -1) this.go(Math.min(i, this.maxIndex));
    });
    if (this.prev) this.prev.addEventListener("click", () => this.go(this.index - 1));
    if (this.next) this.next.addEventListener("click", () => this.go(this.index + 1));
    el.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") { e.preventDefault(); this.go(this.index - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); this.go(this.index + 1); }
    });
    this.bindDrag();
    let raf = 0;
    window.addEventListener("resize", () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => { this.measure(); this.go(Math.min(this.index, this.maxIndex), true); });
    });
  }

  measure() {
    const a = this.slides[0], b = this.slides[1];
    this.step = a && b ? b.offsetLeft - a.offsetLeft : (a ? a.offsetWidth : 0);
    const visible = this.el.clientWidth;
    this.maxOffset = Math.max(0, this.track.scrollWidth - visible);
    this.maxIndex = this.step ? Math.ceil(this.maxOffset / this.step - 0.02) : 0;
  }

  apply(px, instant) {
    if (instant) this.track.style.transition = "none";
    this.track.style.transform = `translate3d(${-px}px,0,0)`;
    if (instant) { void this.track.offsetWidth; this.track.style.transition = ""; }
  }

  go(i, instant = false) {
    if (i > this.maxIndex) i = 0;
    if (i < 0) i = this.maxIndex;
    this.index = i;
    this.offset = Math.min(i * this.step, this.maxOffset);
    this.apply(this.offset, instant);
    this.el.classList.toggle("is-start", this.offset <= 0);
    this.el.classList.toggle("is-end", this.offset >= this.maxOffset);
  }

  bindDrag() {
    const vp = this.viewport;
    let startX = 0, startY = 0, dx = 0, dragging = false, decided = false, horizontal = false, pid = null, moved = false;
    vp.addEventListener("pointerdown", (e) => {
      if (e.button !== 0 && e.pointerType === "mouse") return;
      startX = e.clientX; startY = e.clientY; dx = 0;
      dragging = true; decided = false; horizontal = false; moved = false; pid = e.pointerId;
    });
    vp.addEventListener("pointermove", (e) => {
      if (!dragging || e.pointerId !== pid) return;
      const mx = e.clientX - startX, my = e.clientY - startY;
      if (!decided) {
        if (Math.abs(mx) < 6 && Math.abs(my) < 6) return;
        decided = true;
        horizontal = Math.abs(mx) > Math.abs(my);
        if (!horizontal) { dragging = false; return; }
        try { vp.setPointerCapture(pid); } catch (err) { /* ignore */ }
        this.el.classList.add("is-dragging");
      }
      dx = mx;
      moved = true;
      let px = this.offset - dx;
      if (px < 0) px = px * 0.35;
      if (px > this.maxOffset) px = this.maxOffset + (px - this.maxOffset) * 0.35;
      this.apply(px, false);
    });
    const end = (e) => {
      if (!dragging || (e && e.pointerId !== pid)) return;
      dragging = false;
      this.el.classList.remove("is-dragging");
      if (!horizontal) return;
      const threshold = Math.min(80, this.step * 0.18);
      const n = Math.max(1, Math.round(Math.abs(dx) / (this.step || 1)));
      if (dx < -threshold) this.go(Math.min(this.index + n, this.maxIndex));
      else if (dx > threshold) this.go(Math.max(this.index - n, 0));
      else this.go(this.index);
    };
    vp.addEventListener("pointerup", end);
    vp.addEventListener("pointercancel", end);
    vp.addEventListener("click", (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    vp.addEventListener("dragstart", (e) => e.preventDefault());
  }
}

function initCarousels() {
  document.querySelectorAll("[data-carousel]").forEach((el) => {
    if (el.querySelector("[data-carousel-track]")) new Carousel(el);
  });
}

/* ---------- live clock (San Francisco) ---------- */
function initClock() {
  const nodes = document.querySelectorAll("[data-clock]");
  if (!nodes.length) return;
  // the time-zone formatter is costly to build (about 2 ms, 11 ms at 6x CPU): made when a clock first shows
  let fmt = null;
  const tick = () => {
    if (fmt === null) {
      try {
        fmt = new Intl.DateTimeFormat("en-US", { timeZone: "America/Los_Angeles", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23" });
      } catch (e) {
        fmt = false;
      }
    }
    if (!fmt) return;
    const s = `SF ${fmt.format(new Date())}`;
    nodes.forEach((n) => { n.textContent = s; });
  };
  // tick only while a clock is on screen (it lives in the reel, far down Home); it reads "Live" until then
  let timer = 0;
  const run = (on) => {
    if (on && !timer) { tick(); timer = setInterval(tick, 1000); }
    else if (!on && timer) { clearInterval(timer); timer = 0; }
  };
  if ("IntersectionObserver" in window) {
    const seen = new Set();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) seen.add(e.target); else seen.delete(e.target); });
      run(seen.size > 0);
    }, { rootMargin: "50% 0px" });
    nodes.forEach((n) => io.observe(n));
  } else {
    run(true);
  }
}

/* ---------- canvas engine: loaded and started only when needed ---------- */
function initCanvases() {
  const all = [...document.querySelectorAll("canvas[data-streaks]")];
  if (!all.length) return;
  let engine = null;
  const load = () => engine || (engine = import("./streaks.js"));
  const start = (canvas) => {
    if (canvas.dataset.streaksOn) return;
    canvas.dataset.streaksOn = "1";
    load().then(({ initStreaks }) => {
      initStreaks([canvas], { reduced: reduceMQ.matches });
      // shown only once the engine has sized it (the canvas is hidden until then: no layout shift from its crop)
      canvas.classList.add("is-on");
    }).catch(() => { /* engine failed: the static image stays */ });
  };
  const vh = window.innerHeight;
  const near = [], far = [];
  all.forEach((c) => {
    const r = (c.parentElement || c).getBoundingClientRect();
    (r.top < vh * 1.5 ? near : far).push(c);
  });
  // first screen: start after the first frame is on screen, so setting up the canvas never delays first paint
  if (near.length) requestAnimationFrame(() => setTimeout(() => near.forEach(start), 0));
  if (!far.length) return;
  if (!("IntersectionObserver" in window)) { far.forEach(start); return; }
  // further down (the reel): fetch the engine early, set the canvas up in idle time about two screens before it
  // scrolls in (its set-up is one block of script: never in the middle of a scroll frame if it can be helped)
  const idle = window.requestIdleCallback ? (fn) => window.requestIdleCallback(fn, { timeout: 400 }) : (fn) => setTimeout(fn, 1);
  setTimeout(load, 1500);
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      far.filter((c) => (c.parentElement || c) === e.target).forEach((c) => idle(() => start(c)));
    });
  }, { rootMargin: "200% 0px" });
  far.forEach((c) => io.observe(c.parentElement || c));
}

/* ---------- prefetch internal pages on hover, focus or touch, so the next page opens at once ---------- */
function initPrefetch() {
  const conn = navigator.connection;
  if (conn && (conn.saveData || /(^|-)2g$/.test(conn.effectiveType || ""))) return;
  const done = new Set([location.pathname]);
  const pageOf = (target) => {
    const a = target && target.closest ? target.closest("a[href]") : null;
    if (!a || a.target === "_blank" || a.hasAttribute("download")) return null;
    let u;
    try { u = new URL(a.href, location.href); } catch (e) { return null; }
    if (u.origin !== location.origin || !/(\/|\.html)$/.test(u.pathname)) return null;
    return done.has(u.pathname) ? null : u.pathname;
  };
  const add = (path) => {
    if (!path || done.has(path)) return;
    done.add(path);
    const l = document.createElement("link");
    l.rel = "prefetch";
    l.href = path;
    document.head.appendChild(l);
  };
  // a mouse resting on a link or keyboard focus staying on one for 65 ms (not every link the pointer or Tab passes);
  // a press or a touch at once
  let timer = 0;
  const soon = (e) => {
    const path = pageOf(e.target);
    clearTimeout(timer);
    if (path) timer = setTimeout(() => add(path), 65);
  };
  const cancel = () => clearTimeout(timer);
  document.addEventListener("pointerover", (e) => { if (e.pointerType === "mouse") soon(e); }, { passive: true });
  document.addEventListener("pointerout", cancel, { passive: true });
  document.addEventListener("focusin", soon);
  document.addEventListener("focusout", cancel);
  document.addEventListener("pointerdown", (e) => add(pageOf(e.target)), { passive: true });
  document.addEventListener("touchstart", (e) => add(pageOf(e.target)), { passive: true });
}

/* ---------- smooth scroll ---------- */
/* Lenis only where it helps: a mouse or trackpad on a capable machine. Touch screens (Lenis leaves touch native
   anyway) and weak machines keep the browser's own scrolling, which runs off the main thread and never stutters.
   lerp .15 (Lenis default .1): a wheel tick lands in about 0.25 s instead of 0.4 s, still smooth.
   If smooth-scroll frames run long anyway (median over 25 ms twice in a row), it hands back to native scrolling. */
function initLenis() {
  if (!Lenis) return;
  let touchOnly = false;
  try { touchOnly = window.matchMedia("(hover: none) and (pointer: coarse)").matches; } catch (e) { /* keep false */ }
  if (touchOnly || WEAK) return;
  lenis = new Lenis({
    autoRaf: false,
    lerp: 0.15,
    anchors: true,
    prevent: (node) => Boolean(node && node.closest && node.closest("[data-lenis-prevent]")),
  });
  lenis.on("scroll", ScrollTrigger.update);
  const win = [];
  let slow = 0;
  const tick = (time, delta) => {
    if (!lenis) return;
    lenis.raf(time * 1000);
    if (lenis.isScrolling !== "smooth" || document.hidden) return;
    win.push(delta);
    if (win.length < 30) return;
    win.sort((a, b) => a - b);
    slow = win[15] > 25 ? slow + 1 : 0;
    win.length = 0;
    if (slow >= 2) {
      gsap.ticker.remove(tick);
      lenis.destroy();
      lenis = null;
    }
  };
  gsap.ticker.add(tick);
  gsap.ticker.lagSmoothing(0);
}

/* ---------- reveals ---------- */
/* accessible name of a two-line heading: a <br> counts as a space ("What<br>we stop." -> "What we stop.") */
function spokenText(el) {
  const c = el.cloneNode(true);
  c.querySelectorAll("br").forEach((br) => br.replaceWith(" "));
  return c.textContent.replace(/\s+/g, " ").trim();
}

/* Reveals start the moment an element's top enters the viewport (was 92% / 95% down: a block peeking at the bottom
   edge stayed blank) and are short: .05 s delay (was .15), .5 s decelerating (was .45 s power2.inOut, whose slow
   start made content feel late), list items .08 s apart (was .15). The first screen is not here: it plays from CSS
   (base.css [data-intro]). */
const IN = { delay: 0.05, duration: 0.5, ease: EASE_IN, start: "top bottom" };
// a trigger on an element that is itself moved down by its from-state is measured there: start that much earlier,
// so it fires the moment its real top edge enters (a block peeking in at the bottom never stays blank)
const startAt = (px) => `top bottom+=${Math.ceil(px)}`;

function revealLines(el) {
  gsap.set(el, { opacity: 1 });
  if (!SplitText) {
    gsap.from(el, { opacity: 0, y: emOf(el) * 0.25, duration: IN.duration, ease: IN.ease, delay: IN.delay, scrollTrigger: { trigger: el, start: startAt(emOf(el) * 0.25), once: true } });
    return;
  }
  const label = spokenText(el);
  SplitText.create(el, {
    type: "lines",
    linesClass: "split-line",
    autoSplit: true,
    onSplit(self) {
      if (label) el.setAttribute("aria-label", label);
      return gsap.from(self.lines, {
        opacity: 0,
        y: emOf(el) * 0.25,
        duration: IN.duration,
        ease: IN.ease,
        delay: IN.delay,
        stagger: 0.02,
        scrollTrigger: { trigger: el, start: IN.start, once: true },
      });
    },
  });
}

function revealStatement(el) {
  if (!SplitText) return;
  // the text is read from a screen-reader-only copy next to it; the split copy is aria-hidden in the markup
  SplitText.create(el, {
    type: "words,chars",
    tag: "span",
    aria: "none",
    autoSplit: true,
    onSplit(self) {
      return gsap.fromTo(self.chars, { opacity: 0.15 }, {
        opacity: 1,
        ease: "none",
        stagger: 0.1,
        scrollTrigger: { trigger: el, start: "top bottom", end: "bottom 30%", scrub: 0.4 },
      });
    },
  });
}

function initReveals() {
  const sel = (kind) => `[data-reveal="${kind}"]:not([data-intro])`;
  // data-delay is a choreography offset inside a group; it is halved like the CSS first screen's
  const delayOf = (el, base) => (el.dataset.delay ? parseFloat(el.dataset.delay) / 2 : base);
  const jobs = [];
  const add = (selector, fn) => document.querySelectorAll(selector).forEach((el) => jobs.push([el, () => fn(el)]));

  add(sel("lines"), revealLines);
  add('[data-reveal="statement"]', revealStatement);

  add(`${sel("fade")}, ${sel("status")}`, (el) => {
    const delay = delayOf(el, el.dataset.reveal === "status" ? 0.27 : IN.delay);
    const em = emOf(el);
    gsap.fromTo(el, { opacity: 0, y: em * 0.5 }, { opacity: 1, y: 0, duration: IN.duration, ease: IN.ease, delay, scrollTrigger: { trigger: el, start: startAt(em * 0.5), once: true } });
  });

  add(sel("frame"), (el) => {
    const shift = emOf(el) * 2 + el.offsetHeight * 0.025;
    gsap.fromTo(el, { opacity: 0, scale: 0.95, y: emOf(el) * 2 }, { opacity: 1, scale: 1, y: 0, duration: 0.6, ease: IN.ease, delay: IN.delay, scrollTrigger: { trigger: el, start: startAt(shift), once: true } });
  });

  // opacity only (never visibility): hidden-until-scrolled content must stay reachable by Tab and screen readers
  add(sel("stagger"), (list) => {
    const items = [...list.children];
    gsap.set(list, { opacity: 1 });
    gsap.fromTo(items, { opacity: 0, y: emOf(list) * 0.5 }, {
      opacity: 1, y: 0, duration: IN.duration, ease: IN.ease, delay: delayOf(list, IN.delay), stagger: parseFloat(list.dataset.stagger || 0.08),
      scrollTrigger: { trigger: list, start: IN.start, once: true },
    });
  });

  // gauges fill one row after the other over their navy-11 track, then each gets a slow light pass (CSS .is-live)
  add("[data-bars]", (wrap) => {
    const bars = [...wrap.querySelectorAll(".ledger__fill")];
    bars.forEach((b, i) => b.style.setProperty("--i", i));
    gsap.fromTo(bars, { scaleX: 0 }, {
      scaleX: 1, duration: 1.2, ease: "power2.inOut", stagger: 0.16, delay: 0.15,
      scrollTrigger: { trigger: wrap, start: "top 90%", once: true },
      onComplete: () => bars.forEach((b) => b.classList.add("is-live")),
    });
  });

  /* Set up lazily: what is on screen or within 3/4 of a screen below it now (or already scrolled past), the rest when
     it comes within 3/4 of a screen. Splitting every heading and building every trigger at once was the biggest
     block of script at load (about 15 ms on a fast laptop, 80 to 95 ms at 6x CPU). The hidden state is CSS until a
     reveal is set up, so nothing flashes. Reads first (all boxes), then writes. */
  const vh = window.innerHeight;
  const now = [], later = [];
  jobs.forEach((job) => (job[0].getBoundingClientRect().top < vh * 1.75 ? now : later).push(job));
  now.forEach(([, fn]) => fn());
  if (!later.length) return;
  if (!("IntersectionObserver" in window)) { later.forEach(([, fn]) => fn()); return; }
  // one element can carry two reveals (a ledger is a stagger list with bars)
  const pending = new Map();
  later.forEach(([el, fn]) => { if (!pending.has(el)) pending.set(el, []); pending.get(el).push(fn); });
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting || !pending.has(e.target)) return;
      io.unobserve(e.target);
      const fns = pending.get(e.target);
      pending.delete(e.target);
      fns.forEach((fn) => fn());
    });
  }, { rootMargin: "0px 0px 75% 0px" });
  pending.forEach((fns, el) => io.observe(el));
}

function showAll() {
  root.classList.remove("motion");
}

/* ---------- boot ---------- */
function init() {
  root.classList.add("js");
  initMediaFallback();
  initCopyEmail();
  initNav();
  initFaq();
  initCarousels();
  initClock();
  initCanvases();
  initPrefetch();

  if (motionOn()) {
    try {
      gsap.registerPlugin(ScrollTrigger);
      if (SplitText) gsap.registerPlugin(SplitText);
      initLenis();
      const run = () => { initReveals(); root.classList.add("ready"); ScrollTrigger.refresh(); };
      // headings split by line once the fonts are in (SplitText re-splits by itself if they land later); the first
      // screen does not wait for this (CSS), so the cap is short
      if (document.fonts && document.fonts.ready) {
        Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 500))]).then(run);
      } else {
        run();
      }
    } catch (err) {
      showAll();
      root.classList.add("ready");
    }
  } else {
    showAll();
    root.classList.add("ready");
  }
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();
