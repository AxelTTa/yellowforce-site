/* YellowForce site behaviour. Plain ES module, no build step.
   Globals from /assets/js/vendor: gsap, ScrollTrigger, SplitText, Lenis (all optional: the site works without them). */
import { initStreaks } from "./streaks.js";

const EMAIL = "info@yellow-force.com";
const root = document.documentElement;
const reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
const { gsap, ScrollTrigger, SplitText, Lenis } = window;
const hasGsap = Boolean(gsap && ScrollTrigger);
const EASE = "power2.inOut";
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
    const ok = await copyText(EMAIL);
    if (ok) {
      toast("Email copied", EMAIL, urgent ? URGENT_NOTE : "");
      btn.classList.add("is-copied");
      setTimeout(() => btn.classList.remove("is-copied"), 2400);
    } else {
      // Clipboard blocked: show and select the address so the user can copy it.
      toast("Press Cmd+C or Ctrl+C to copy", EMAIL, urgent ? URGENT_NOTE : "", 9000);
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

/* ---------- nav pill ---------- */
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
      const f = focusables();
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
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
      if (motionOn()) {
        gsap.killTweensOf([drawer, scrim, ...rows]);
        gsap.fromTo(drawer, { height: 0 }, { height: "auto", duration: 0.45, ease: EASE });
        gsap.fromTo(rows, { autoAlpha: 0, y: emOf(drawer), scale: 0.98 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.45, ease: EASE, stagger: 0.06 });
        if (scrim) gsap.fromTo(scrim, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.45, ease: EASE });
      }
      document.addEventListener("keydown", onKey);
      const first = drawer.querySelector("a[href], button");
      if (first) first.focus({ preventScroll: true });
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
        gsap.to(drawer, { height: 0, duration: 0.45, ease: EASE, onComplete: done });
        if (scrim) gsap.to(scrim, { autoAlpha: 0, duration: 0.45, ease: EASE });
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
          gsap.fromTo(panel, { height: 0 }, { height: "auto", duration: 0.45, ease: EASE });
          gsap.fromTo(links, { autoAlpha: 0, y: emOf(panel) * 0.5 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: EASE, stagger: 0.04 });
        }
      } else if (motionOn()) {
        gsap.to(panel, { height: 0, duration: 0.45, ease: EASE, onComplete: () => { panel.hidden = true; panel.style.height = ""; } });
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
            gsap.fromTo(panel, { height: 0 }, { height: "auto", duration: 0.45, ease: EASE, onComplete: refreshSoon });
            gsap.fromTo(inner, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: EASE });
          } else {
            gsap.to(inner, { opacity: 0, duration: 0.3, ease: EASE });
            gsap.to(panel, { height: 0, duration: 0.45, ease: EASE, onComplete: () => { panel.hidden = true; panel.style.height = ""; refreshSoon(); } });
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
    this.slides.forEach((s, i) => {
      s.setAttribute("role", "group");
      s.setAttribute("aria-roledescription", "slide");
      s.setAttribute("aria-label", `${i + 1} of ${this.slides.length}`);
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
  let fmt;
  try {
    fmt = new Intl.DateTimeFormat("en-US", { timeZone: "America/Los_Angeles", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23" });
  } catch (e) {
    return;
  }
  const tick = () => {
    const s = `SF ${fmt.format(new Date())}`;
    nodes.forEach((n) => { n.textContent = s; });
  };
  tick();
  setInterval(tick, 1000);
}

/* ---------- smooth scroll ---------- */
function initLenis() {
  if (!Lenis) return;
  lenis = new Lenis({
    autoRaf: false,
    lerp: 0.1,
    anchors: true,
    prevent: (node) => Boolean(node && node.closest && node.closest("[data-lenis-prevent]")),
  });
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
}

/* ---------- reveals ---------- */
function revealLines(el) {
  gsap.set(el, { autoAlpha: 1 });
  if (!SplitText) {
    gsap.from(el, { autoAlpha: 0, y: emOf(el) * 0.25, duration: 0.45, ease: EASE, delay: 0.15, scrollTrigger: { trigger: el, start: "top 92%", once: true } });
    return;
  }
  SplitText.create(el, {
    type: "lines",
    linesClass: "split-line",
    autoSplit: true,
    onSplit(self) {
      return gsap.from(self.lines, {
        opacity: 0,
        y: emOf(el) * 0.25,
        duration: 0.45,
        ease: EASE,
        delay: 0.15,
        stagger: 0.02,
        scrollTrigger: { trigger: el, start: "top 92%", once: true },
      });
    },
  });
}

function revealStatement(el) {
  if (!SplitText) return;
  SplitText.create(el, {
    type: "words,chars",
    autoSplit: true,
    onSplit(self) {
      return gsap.fromTo(self.chars, { opacity: 0.15 }, {
        opacity: 1,
        ease: "none",
        stagger: 0.1,
        scrollTrigger: { trigger: el, start: "top bottom", end: "bottom 30%", scrub: 0.8 },
      });
    },
  });
}

function initReveals() {
  document.querySelectorAll('[data-reveal="lines"]').forEach(revealLines);
  document.querySelectorAll('[data-reveal="statement"]').forEach(revealStatement);

  document.querySelectorAll('[data-reveal="fade"], [data-reveal="status"]').forEach((el) => {
    const delay = parseFloat(el.dataset.delay || (el.dataset.reveal === "status" ? 0.54 : 0.15));
    gsap.fromTo(el, { autoAlpha: 0, y: emOf(el) * 0.5 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: EASE, delay, scrollTrigger: { trigger: el, start: "top 95%", once: true } });
  });

  document.querySelectorAll('[data-reveal="frame"]').forEach((el) => {
    gsap.fromTo(el, { autoAlpha: 0, scale: 0.95, y: emOf(el) * 2 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.6, ease: EASE, delay: 0.15, scrollTrigger: { trigger: el, start: "top 92%", once: true } });
  });

  document.querySelectorAll('[data-reveal="stagger"]').forEach((list) => {
    const items = [...list.children];
    gsap.set(list, { autoAlpha: 1 });
    gsap.fromTo(items, { autoAlpha: 0, y: emOf(list) * 0.5 }, {
      autoAlpha: 1, y: 0, duration: 0.45, ease: EASE, delay: parseFloat(list.dataset.delay || 0.15), stagger: parseFloat(list.dataset.stagger || 0.15),
      scrollTrigger: { trigger: list, start: "top 92%", once: true },
    });
  });

  document.querySelectorAll("[data-bars]").forEach((wrap) => {
    const bars = wrap.querySelectorAll(".ledger__fill");
    gsap.fromTo(bars, { scaleX: 0 }, { scaleX: 1, duration: 1.1, ease: "power2.out", stagger: 0.08, delay: 0.3, scrollTrigger: { trigger: wrap, start: "top 85%", once: true } });
  });
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
  initStreaks(document.querySelectorAll("canvas[data-streaks]"), { reduced: reduceMQ.matches });

  if (motionOn()) {
    try {
      gsap.registerPlugin(ScrollTrigger);
      if (SplitText) gsap.registerPlugin(SplitText);
      initLenis();
      const run = () => { initReveals(); root.classList.add("ready"); ScrollTrigger.refresh(); };
      if (document.fonts && document.fonts.ready) {
        Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 1200))]).then(run);
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
