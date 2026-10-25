#!/usr/bin/env python3
"""Screenshot a page the way a reviewer sees it, for side-by-side QA.

Usage
  shoot.py URL OUTDIR --widths 1440,390 --name NAME
           [--selector SEL] [--click SEL] [--hover SEL] [--state LABEL]
           [--slice 900] [--no-scroll] [--keep-scrub] [--mobile]
           [--hide "CSS, SELECTORS"] [--css "extra css"] [--reduced-motion]

  shoot.py --preset vantra|ours OUTDIR [--base URL] [--only home,about] [--jobs 3]
           Captures the standard page set + UI states with matching names
           (see PAGES / STATES below and tools/QA.md).

Per width it writes into OUTDIR:
  NAME-WIDTH-full.png          full page
  NAME-WIDTH-sliceNN.png       900 px tall crops of the full page (01, 02, ...)
  NAME-WIDTH-el.png            --selector element (no state actions)
  NAME-WIDTH-STATE.png         viewport after --click / --hover actions (STATE defaults to "state")
  NAME-WIDTH-STATE-el.png      --selector element after the actions
  NAME-WIDTH-STATE-el-before.png  same element before the actions (--el-before; preset hover states)
  NAME-WIDTH-STATE-frames.png  --frames: strip of the element at ~N ms after the last action (motion check)

How a capture is made (so both sites are shot identically)
  1. Viewport WIDTH x 900 (WIDTH < 768: x 844), deviceScaleFactor 1, scrollbars hidden (headless).
  2. Load, wait for network idle (max 10 s), document.fonts.ready, then --wait-ms.
  3. Inject CSS hiding the Webflow template bar (".ctm-box", ".w-webflow-badge"; change with --hide).
  4. Scroll to the bottom in steps of half a viewport using real mouse-wheel events (drives
     Lenis smooth scroll and fires ScrollTrigger/IntersectionObserver reveals and lazy images).
     If a wheel step does not move the page, falls back to window.scrollTo. Waits at the bottom,
     returns to the top, waits for reveal tweens and images to finish.
  5. Scroll-SCRUBBED animations (GSAP ScrollTrigger with `scrub`, e.g. the statement character
     fill) depend on the current scroll position, so at scroll 0 they would sit at their start
     state. Unless --keep-scrub is set, every ScrollTrigger with vars.scrub is disabled and its
     animation set to progress 1 (finished), via window.ScrollTrigger. Nothing else is altered.
     No CSS is injected to force reveals: if something is still hidden the reveal audit warns.
  6. Full page via Chromium capture-beyond-viewport (fixed header appears once, at the top);
     pages taller than 16000 px are captured in 4000 px clips and stitched.
  7. Reveal audit: prints visible-size text/images whose effective opacity is < 0.1 or that are
     visibility:hidden (ignores fixed/closed menu layers). A clean run prints "audit: ok".
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import pathlib
import subprocess
import sys
import time

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

DEFAULT_HIDE = ".ctm-box, .w-webflow-badge"
MOBILE_MAX = 767

# --------------------------------------------------------------------------------------------
# Standard set. name, Vantra path, YellowForce path. Same NAME on both sides => sidebyside pairs.
VANTRA_BASE = "https://vantra-studio.webflow.io"
OURS_BASE = "http://127.0.0.1:8787"
PAGES = [
    ("home", "/", "/"),
    ("about", "/about-us", "/about/"),
    ("work", "/work", "/services/"),
    ("case", "/work/meridian", "/coverage/network/"),
    ("journal", "/journal", "/insights/"),
    ("note", "/journal/why-we-price-in-outcomes", "/insights/ai-swarms/"),
    ("contact", "/contact-us", "/contact/"),
    ("404", "/404", "/404.html"),
]
# Pages only we have; second item is the reference NAME to compare against.
OURS_EXTRA = [
    ("coverage", "work", "/coverage/"),
]
# UI states. Selector strings may hold alternatives separated by " || " (first that matches wins).
# The YellowForce side looks for data-qa hooks first, then common fallbacks.
STATES = [
    # name, path(vantra, ours), [(kind, vantra selector, ours selector)], element (vantra, ours)
    ("home-menu", ("/", "/"),
     [("click", ".nav_menu-button",
       "[data-qa=menu-toggle] || header button[aria-expanded] || button[aria-controls*=menu]")],
     (None, None)),
    ("home-faq", ("/", "/"),
     [("click", ".faq_row-head >> nth=0",
       "[data-qa=faq-toggle] >> nth=0 || [data-qa=faq] button[aria-expanded] >> nth=0 || details summary >> nth=0")],
     (".section_faq", "[data-qa=faq] || section:has(details) || section:has([aria-expanded][aria-controls*=faq])")),
    ("home-hover", ("/", "/"),
     [("hover", ".section_careers .button >> nth=0",
       "[data-qa=button] >> nth=0 || main a.button >> nth=0 || main .btn >> nth=0")],
     (".section_careers .button >> nth=0",
      "[data-qa=button] >> nth=0 || main a.button >> nth=0 || main .btn >> nth=0")),
]

# --------------------------------------------------------------------------------------------
JS_IMAGES_DONE = """async (ms) => {
  const imgs = [...document.images].filter(i => !i.complete);
  const all = Promise.all(imgs.map(i => new Promise(r => {
    i.addEventListener('load', r, {once: true}); i.addEventListener('error', r, {once: true});
  })));
  await Promise.race([all, new Promise(r => setTimeout(r, ms))]);
  await Promise.race([Promise.all([...document.images].map(i => i.decode ? i.decode().catch(() => 0) : 0)),
                      new Promise(r => setTimeout(r, 3000))]);
  return imgs.length;
}"""

JS_FINISH_SCRUB = """() => {
  const ST = window.ScrollTrigger;
  if (!ST || !ST.getAll) return -1;
  let n = 0;
  ST.getAll().forEach(s => {
    if (s.vars && s.vars.scrub && s.animation) { s.disable(false); s.animation.progress(1); n++; }
  });
  return n;
}"""

JS_AUDIT = """() => {
  const sel = 'h1,h2,h3,h4,h5,p,li,img,video,a,button,blockquote,figure,[class*=card]';
  const bad = [];
  const insideFixed = el => { for (let e = el; e && e !== document.body; e = e.parentElement) {
      const p = getComputedStyle(e).position; if (p === 'fixed') return true; } return false; };
  for (const el of document.querySelectorAll(sel)) {
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    if (el.tagName !== 'IMG' && el.tagName !== 'VIDEO' && !(el.innerText || '').trim()) continue;
    if (insideFixed(el)) continue;
    let op = 1, hidden = false, gone = false;
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none') { gone = true; break; }
      op *= parseFloat(cs.opacity);
      if (e === el && cs.visibility === 'hidden') hidden = true;
    }
    if (gone) continue;
    // clipped away (e.g. closed accordion or overflow:hidden line mask)? skip zero-area intersections
    if (op < 0.1 || hidden) bad.push({tag: el.tagName, cls: (el.className || '').toString().slice(0, 60),
       y: Math.round(r.top + scrollY), op: +op.toFixed(2), hidden,
       txt: (el.innerText || el.alt || '').trim().slice(0, 40)});
  }
  return bad;
}"""


def log(*a):
    print(*a, flush=True)


def viewport_for(width: int, mobile_h: int, desk_h: int) -> dict:
    return {"width": width, "height": mobile_h if width <= MOBILE_MAX else desk_h}


def resolve(page, spec: str | None):
    """Return a Locator for the first alternative in `spec` (" || "-separated) that matches."""
    if not spec:
        return None
    for alt in [s.strip() for s in spec.split("||") if s.strip()]:
        try:
            loc = page.locator(alt)
            if loc.count() > 0:
                return loc.first
        except Exception:
            continue
    return None


def settle_scroll(page, timeout_ms=3000):
    """Wait until scrollY stops changing (Lenis easing)."""
    t0 = time.time()
    last = page.evaluate("scrollY")
    while (time.time() - t0) * 1000 < timeout_ms:
        page.wait_for_timeout(120)
        y = page.evaluate("scrollY")
        if abs(y - last) < 0.5:
            return y
        last = y
    return last


def prescroll(page, vp, step_ratio=0.5, pause_ms=160, bottom_wait=1500, top_wait=1200, max_px=120000):
    w, h = vp["width"], vp["height"]
    page.mouse.move(w // 2, int(h * 0.6))
    step = int(h * step_ratio)
    fallbacks = 0
    stuck = 0
    t0 = time.time()
    while True:
        y, ih, sh = page.evaluate("[scrollY, innerHeight, document.documentElement.scrollHeight]")
        if y + ih >= sh - 2:
            page.wait_for_timeout(700)  # lazy content may extend the page
            y, ih, sh2 = page.evaluate("[scrollY, innerHeight, document.documentElement.scrollHeight]")
            if y + ih >= sh2 - 2:
                break
        if y > max_px or time.time() - t0 > 240:
            log("  ! prescroll limit hit at", y)
            break
        page.mouse.wheel(0, step)
        page.wait_for_timeout(pause_ms)
        y2 = page.evaluate("scrollY")
        if y2 <= y + 1:
            stuck += 1
            if stuck >= 3:
                page.evaluate(f"window.scrollTo(0, {y + step})")
                page.wait_for_timeout(pause_ms)
                fallbacks += 1
                stuck = 0
        else:
            stuck = 0
    settle_scroll(page)
    page.wait_for_timeout(bottom_wait)
    for _ in range(5):
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(250)
        if settle_scroll(page) < 1:
            break
    page.wait_for_timeout(top_wait)
    return fallbacks


def full_capture(page, path: pathlib.Path, chunk=4000, limit=16000):
    sh = page.evaluate("Math.ceil(document.documentElement.scrollHeight)")
    w = page.evaluate("document.documentElement.clientWidth")
    if sh <= limit:
        page.screenshot(path=str(path), full_page=True, animations="allow")
        return Image.open(path).size
    parts = []
    y = 0
    while y < sh:
        hh = min(chunk, sh - y)
        tmp = path.with_suffix(f".part{len(parts):02d}.png")
        page.screenshot(path=str(tmp), full_page=True, clip={"x": 0, "y": y, "width": w, "height": hh})
        parts.append(tmp)
        y += hh
    canvas = Image.new("RGB", (w, sh), "white")
    y = 0
    for p in parts:
        im = Image.open(p).convert("RGB")
        canvas.paste(im, (0, y))
        y += im.height
        p.unlink()
    canvas.save(path, optimize=False)
    return canvas.size


def slice_image(src: pathlib.Path, out_prefix: str, outdir: pathlib.Path, h: int) -> int:
    for old in outdir.glob(f"{out_prefix}-slice[0-9][0-9].png"):
        old.unlink()  # a shorter page must not leave stale slices behind
    im = Image.open(src)
    n = 0
    for i, y in enumerate(range(0, im.height, h), start=1):
        im.crop((0, y, im.width, min(y + h, im.height))).save(outdir / f"{out_prefix}-slice{i:02d}.png")
        n += 1
    return n


def element_capture(page, loc, path: pathlib.Path, pad=24):
    loc.scroll_into_view_if_needed()
    page.wait_for_timeout(400)
    bb = loc.bounding_box()
    vw, vh = page.viewport_size["width"], page.viewport_size["height"]
    if bb and bb["height"] + 2 * pad <= vh:
        x0 = max(0, bb["x"] - pad); y0 = max(0, bb["y"] - pad)
        x1 = min(vw, bb["x"] + bb["width"] + pad); y1 = min(vh, bb["y"] + bb["height"] + pad)
        page.screenshot(path=str(path), clip={"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0})
    else:
        loc.screenshot(path=str(path))


def clip_for(page, loc, pad=24):
    bb = loc.bounding_box()
    vw, vh = page.viewport_size["width"], page.viewport_size["height"]
    if not bb:
        return None
    x0 = max(0, bb["x"] - pad); y0 = max(0, bb["y"] - pad)
    x1 = min(vw, bb["x"] + bb["width"] + pad); y1 = min(vh, bb["y"] + bb["height"] + pad)
    return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}


def capture_frames(page, clip, offsets_ms, path: pathlib.Path):
    """Shoot the clip (or viewport) at roughly the given ms after the action; stitch left to right."""
    import io
    t0 = time.time()
    shots, took = [], []
    for off in offsets_ms:
        wait = off - (time.time() - t0) * 1000
        if wait > 0:
            page.wait_for_timeout(wait)
        took.append(int((time.time() - t0) * 1000))
        png = page.screenshot(clip=clip) if clip else page.screenshot()
        shots.append(Image.open(io.BytesIO(png)).convert("RGB"))
    gap = 8
    W = sum(s.width for s in shots) + gap * (len(shots) - 1)
    H = max(s.height for s in shots)
    strip = Image.new("RGB", (W, H), (255, 0, 255))
    x = 0
    for s in shots:
        strip.paste(s, (x, 0))
        x += s.width + gap
    strip.save(path)
    return took


def shoot_one(browser, url, outdir: pathlib.Path, name, width, a) -> list[str]:
    vp = viewport_for(width, a.mobile_height, a.desktop_height)
    ctx_kw = dict(viewport=vp, device_scale_factor=a.scale,
                  reduced_motion="reduce" if a.reduced_motion else "no-preference")
    if a.mobile and width <= MOBILE_MAX:
        ctx_kw.update(is_mobile=True, has_touch=True)
    ctx = browser.new_context(**ctx_kw)
    page = ctx.new_page()
    written = []
    try:
        resp = page.goto(url, wait_until="load", timeout=90000)
        status = resp.status if resp else "?"
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        page.evaluate("document.fonts.ready.then(() => 1)")
        css = ""
        if a.hide:
            css += f"{a.hide} {{ display: none !important; }}\n"
        if a.css:
            css += a.css + "\n"
        if css:
            page.add_style_tag(content=css)
        page.wait_for_timeout(a.wait_ms)
        fb = 0
        if not a.no_scroll:
            fb = prescroll(page, vp)
        n_img = page.evaluate(JS_IMAGES_DONE, 10000)
        scrub = -2
        if not a.keep_scrub:
            scrub = page.evaluate(JS_FINISH_SCRUB)
            page.wait_for_timeout(200)
        tag = f"{name}-{width}"
        log(f"[{tag}] {url} http={status} vp={vp['width']}x{vp['height']} wheel-fallbacks={fb} "
            f"late-images={n_img} scrub-finished={scrub}")

        actions = a.actions or []
        if not actions:
            p = outdir / f"{tag}-full.png"
            size = full_capture(page, p)
            written.append(str(p))
            if a.slice:
                n = slice_image(p, tag, outdir, a.slice)
                written.append(f"{tag}-slice01..{n:02d}.png")
            log(f"[{tag}] full {size[0]}x{size[1]}")
            if a.selector:
                loc = resolve(page, a.selector)
                if loc:
                    p = outdir / f"{tag}-el.png"
                    element_capture(page, loc, p, a.pad)
                    written.append(str(p))
                else:
                    log(f"[{tag}] ! selector not found: {a.selector}")
        else:
            label = a.state or "state"
            if a.el_before and a.selector:
                loc = resolve(page, a.selector)
                if loc:
                    p = outdir / f"{tag}-{label}-el-before.png"
                    element_capture(page, loc, p, a.pad)
                    written.append(str(p))
            frames = [int(x) for x in a.frames.split(",")] if a.frames else []
            for i, (kind, sel) in enumerate(actions):
                loc = resolve(page, sel)
                if not loc:
                    log(f"[{tag}] ! {kind} target not found: {sel}")
                    continue
                loc.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                last = i == len(actions) - 1
                clip = None
                if last and frames:
                    floc = resolve(page, a.selector) if a.selector else None
                    clip = clip_for(page, floc, a.pad) if floc else None
                if kind == "click":
                    loc.click()
                else:
                    loc.hover()
                if last and frames:
                    p = outdir / f"{tag}-{label}-frames.png"
                    took = capture_frames(page, clip, frames, p)
                    written.append(str(p))
                    log(f"[{tag}] frames at ~{took} ms -> {p.name}")
                page.wait_for_timeout(a.state_wait)
            p = outdir / f"{tag}-{label}.png"
            page.screenshot(path=str(p))
            written.append(str(p))
            if a.selector:
                loc = resolve(page, a.selector)
                if loc:
                    p = outdir / f"{tag}-{label}-el.png"
                    element_capture(page, loc, p, a.pad)
                    written.append(str(p))
                else:
                    log(f"[{tag}] ! selector not found: {a.selector}")
            if a.state_full:
                p = outdir / f"{tag}-{label}-full.png"
                full_capture(page, p)
                written.append(str(p))

        if not a.no_audit and not actions:
            bad = page.evaluate(JS_AUDIT)
            if bad:
                log(f"[{tag}] audit: {len(bad)} element(s) still hidden/transparent:")
                for b in bad[:8]:
                    log(f"    y={b['y']} {b['tag']}.{b['cls']} op={b['op']} hidden={b['hidden']} '{b['txt']}'")
            else:
                log(f"[{tag}] audit: ok")
    finally:
        ctx.close()
    return written


class AppendAction(argparse.Action):
    """--click / --hover keep their command-line order in one list."""
    def __call__(self, parser, ns, values, option_string=None):
        lst = getattr(ns, "actions", None) or []
        lst.append((option_string.lstrip("-"), values))
        ns.actions = lst


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", nargs="?", help="page URL (omit with --preset)")
    ap.add_argument("outdir")
    ap.add_argument("--widths", default="1440,390")
    ap.add_argument("--name", default="page")
    ap.add_argument("--selector", help="element to capture (\" || \" alternatives allowed)")
    ap.add_argument("--click", action=AppendAction, dest="actions_click", help="click before capture (repeatable, ordered)")
    ap.add_argument("--hover", action=AppendAction, dest="actions_hover", help="hover before capture (repeatable, ordered)")
    ap.add_argument("--state", help="label for the state capture file (default: state)")
    ap.add_argument("--state-full", action="store_true", help="also take a full page in the state")
    ap.add_argument("--el-before", action="store_true", help="also capture --selector before the actions (STATE-el-before.png)")
    ap.add_argument("--frames", help="ms offsets after the last action, e.g. 0,120,240,400: stitched strip "
                                     "of the --selector crop (or viewport) -> STATE-frames.png")
    ap.add_argument("--state-wait", type=int, default=900, help="ms after each action (default 900)")
    ap.add_argument("--slice", type=int, default=900, help="slice height, 0 = no slices (default 900)")
    ap.add_argument("--pad", type=int, default=24, help="padding around --selector crops (px)")
    ap.add_argument("--desktop-height", type=int, default=900)
    ap.add_argument("--mobile-height", type=int, default=844)
    ap.add_argument("--scale", type=float, default=1)
    ap.add_argument("--mobile", action="store_true", help="emulate touch phone (is_mobile, has_touch) for widths < 768")
    ap.add_argument("--wait-ms", type=int, default=1000, help="extra wait after load (default 1000)")
    ap.add_argument("--no-scroll", action="store_true", help="skip the scroll-through")
    ap.add_argument("--keep-scrub", action="store_true", help="leave scrubbed ScrollTriggers at their scroll-0 state")
    ap.add_argument("--hide", default=DEFAULT_HIDE, help=f"CSS selectors to display:none (default '{DEFAULT_HIDE}', '' = none)")
    ap.add_argument("--css", default="", help="extra CSS to inject")
    ap.add_argument("--reduced-motion", action="store_true", help="emulate prefers-reduced-motion: reduce")
    ap.add_argument("--no-audit", action="store_true")
    ap.add_argument("--preset", choices=["vantra", "ours"], help="capture the standard page + state set")
    ap.add_argument("--base", help="base URL for --preset (default Vantra live / http://127.0.0.1:8787)")
    ap.add_argument("--only", help="--preset: comma list of names to capture (pages and/or states)")
    ap.add_argument("--jobs", type=int, default=3, help="--preset: parallel captures (default 3)")
    return ap


def run_single(a):
    from playwright.sync_api import sync_playwright
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    widths = [int(x) for x in str(a.widths).split(",") if x.strip()]
    a.actions = getattr(a, "actions", None)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for wdt in widths:
                shoot_one(browser, a.url, outdir, a.name, wdt, a)
        finally:
            browser.close()


def run_preset(a):
    side = a.preset
    base = (a.base or (VANTRA_BASE if side == "vantra" else OURS_BASE)).rstrip("/")
    only = set(x.strip() for x in a.only.split(",")) if a.only else None
    me = pathlib.Path(__file__).resolve()
    common = ["--widths", a.widths, "--slice", str(a.slice)]
    if a.mobile:
        common.append("--mobile")
    if a.reduced_motion:
        common.append("--reduced-motion")
    jobs = []
    for name, vpath, opath in PAGES:
        if only and name not in only:
            continue
        jobs.append([sys.executable, str(me), base + (vpath if side == "vantra" else opath), a.outdir,
                     "--name", name] + common)
    if side == "ours":
        for name, _ref, opath in OURS_EXTRA:
            if only and name not in only:
                continue
            jobs.append([sys.executable, str(me), base + opath, a.outdir, "--name", name] + common)
    for name, (vpath, opath), acts, (vel, oel) in STATES:
        if only and name not in only:
            continue
        page_name, label = name.split("-", 1)
        cmd = [sys.executable, str(me), base + (vpath if side == "vantra" else opath), a.outdir,
               "--name", page_name, "--state", label] + common
        for kind, vsel, osel in acts:
            cmd += [f"--{kind}", vsel if side == "vantra" else osel]
        el = vel if side == "vantra" else oel
        if el:
            cmd += ["--selector", el]
            if any(k == "hover" for k, _v, _o in acts):
                cmd += ["--el-before", "--frames", "0,80,160,240,360,600"]
        jobs.append(cmd)

    def run(cmd):
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr).strip()

    fails = 0
    with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        for rc, out in ex.map(run, jobs):
            print(out, flush=True)
            if rc:
                fails += 1
    if fails:
        log(f"{fails} capture(s) failed")
        sys.exit(1)


def main():
    a = build_parser().parse_args()
    if a.preset:
        run_preset(a)
    else:
        if not a.url:
            sys.exit("URL required (or use --preset)")
        run_single(a)


if __name__ == "__main__":
    main()
