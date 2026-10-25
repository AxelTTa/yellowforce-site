"""Brand asset generator for the YellowForce site (Axel's logo kit in brand/).

Run with the project venv (needs Pillow, fontTools, brotli):
  ../.venv/bin/python tools/make_icons.py

Reads   assets/logo/mark.svg        the kit mark (two slanted parallelograms, paths yf-back + yf-front),
                                    tight viewBox; the site inlines this same file (src/partials/logo-mark.html)
        brand/favicon.ico, brand/app_icon.png   kit raster icons
        assets/fonts/inter-latin-var.woff2, instrument-sans-latin-var.woff2

Writes  assets/logo/symbol-on-light.svg       amber front over navy back
        assets/logo/symbol-on-dark.svg        amber front over white back
        assets/logo/wordmark.svg              "Yellow" Inter 750 navy + "Force" Inter 400 slate, outlined
        assets/logo/wordmark-on-dark.svg      same, white + slate-light
        assets/logo/logo-horizontal.svg       mark + wordmark, kit proportions, outlined (no font needed)
        assets/logo/logo-horizontal-on-dark.svg
        static/favicon.svg (kit favicon + dark-tab style), static/favicon.ico (kit), static/favicon-32.png,
        static/apple-touch-icon.png (180, full bleed), static/icon-192.png, static/icon-512.png (kit app icon),
        static/icon-maskable-512.png, static/site.webmanifest
        assets/img/og.png (1200x630)

The live site does not use the wordmark SVGs: it sets the wordmark as HTML text in our Inter
(src/partials/logo.html). The outlined SVGs are for places that cannot load the font.
"""
from __future__ import annotations

import json
import math
import random
import re
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

SITE = Path(__file__).resolve().parent.parent
BRAND = SITE / "brand"
LOGO = SITE / "assets" / "logo"
STATIC = SITE / "static"
FONTS = SITE / "assets" / "fonts"
IMG = SITE / "assets" / "img"
INTER = FONTS / "inter-latin-var.woff2"
INSTRUMENT = FONTS / "instrument-sans-latin-var.woff2"

# brand palette (tokens.css)
NAVY = (7, 27, 62)          # #071B3E
NAVY_DEEP = (4, 16, 41)     # #041029
NAVY_ABYSS = (3, 11, 28)    # #030B1C
AMBER = (255, 191, 0)       # #FFBF00
AMBER_WARM = (255, 162, 26)
WARM_WHITE = (255, 245, 226)
PAPER = (244, 245, 247)     # #F4F5F7
SLATE = (119, 127, 152)     # #777F98
SLATE_LIGHT = (163, 170, 191)  # #A3AABF
WHITE = (255, 255, 255)

TRACKING = -0.027           # wordmark letter-spacing, em (kit: -2 at 74px)
# kit horizontal lockup, in units of the wordmark font size F
LOCK_MARK_H = 130 / 74      # mark height
LOCK_GAP = 43.4 / 74        # mark right edge to text origin
LOCK_BASE = 85.3 / 74       # mark top to text baseline


def hexc(rgb):
    return "#%02X%02X%02X" % rgb


# ---------------------------------------------------------------- mark geometry (from mark.svg)
def read_mark():
    svg = (LOGO / "mark.svg").read_text()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    paths = {}
    for m in re.finditer(r'<path\b([^>]*)/?>', svg):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
        paths[attrs.get("class", f"p{len(paths)}")] = attrs["d"]
    if "yf-back" not in paths or "yf-front" not in paths:
        raise SystemExit("assets/logo/mark.svg needs two paths with class yf-back and yf-front")
    return vb, paths["yf-back"], paths["yf-front"]


def flatten(d: str, steps: int = 16):
    """Absolute M/H/V/L/Q/Z path -> list of polygons (list of (x, y))."""
    toks = re.findall(r"[MHVLQZmhvlqz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    polys, cur, i, cmd = [], [], 0, None
    x = y = 0.0
    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t.upper()
            i += 1
            if cmd == "Z":
                if cur:
                    polys.append(cur)
                cur = []
            continue
        nums = lambda n: [float(v) for v in toks[i:i + n]]
        if cmd == "M":
            x, y = nums(2); i += 2; cur = [(x, y)]; cmd = "L"
        elif cmd == "L":
            x, y = nums(2); i += 2; cur.append((x, y))
        elif cmd == "H":
            x = nums(1)[0]; i += 1; cur.append((x, y))
        elif cmd == "V":
            y = nums(1)[0]; i += 1; cur.append((x, y))
        elif cmd == "Q":
            cx, cy, ex, ey = nums(4); i += 4
            for k in range(1, steps + 1):
                u = k / steps
                cur.append(((1 - u) ** 2 * x + 2 * u * (1 - u) * cx + u * u * ex,
                            (1 - u) ** 2 * y + 2 * u * (1 - u) * cy + u * u * ey))
            x, y = ex, ey
        else:
            raise SystemExit(f"unsupported path command {cmd} in mark.svg")
    if cur:
        polys.append(cur)
    return polys


def draw_mark(img: Image.Image, x0: float, y0: float, height: float, back, front, ss: int = 4):
    """Composite the mark onto img with its viewBox top-left at (x0, y0), scaled to `height` px."""
    vb, d_back, d_front = read_mark()
    s = height / vb[3]
    W, H = img.size
    layer = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    for d, col in ((d_back, back), (d_front, front)):
        for poly in flatten(d):
            pts = [((x0 + (px - vb[0]) * s) * ss, (y0 + (py - vb[1]) * s) * ss) for px, py in poly]
            dr.polygon(pts, fill=tuple(col) + (255,))
    img.alpha_composite(layer.resize((W, H), Image.LANCZOS))
    return vb[2] * s  # drawn width


def mark_width(height: float) -> float:
    vb, _, _ = read_mark()
    return vb[2] * height / vb[3]


# ---------------------------------------------------------------- fonts: kerning + outlines
_TT = {}


def ttfont(path: Path, wght: float):
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    key = (str(path), wght)
    if key not in _TT:
        _TT[key] = instantiateVariableFont(TTFont(path), {"wght": wght})
    return _TT[key]


def kern(font, a: str, b: str) -> float:
    """GPOS pair kerning (font units) between glyph names a and b."""
    if "GPOS" not in font:
        return 0
    t = font["GPOS"].table
    idx = set()
    for fr in t.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            idx.update(fr.Feature.LookupListIndex)
    for li in sorted(idx):
        lk = t.LookupList.Lookup[li]
        for st in lk.SubTable:
            if lk.LookupType == 9:
                st = st.ExtSubTable
            if getattr(st, "LookupType", 2) != 2 or a not in st.Coverage.glyphs:
                continue
            if st.Format == 1:
                ps = st.PairSet[st.Coverage.glyphs.index(a)]
                for r in ps.PairValueRecord:
                    if r.SecondGlyph == b and r.Value1 is not None:
                        return getattr(r.Value1, "XAdvance", 0) or 0
            elif st.Format == 2:
                c1 = st.ClassDef1.classDefs.get(a, 0)
                c2 = st.ClassDef2.classDefs.get(b, 0)
                v = st.Class1Record[c1].Class2Record[c2].Value1
                if v is not None and getattr(v, "XAdvance", 0):
                    return v.XAdvance
    return 0


def run_layout(path: Path, wght: float, text: str, tracking: float):
    """Glyph names and pen x positions (font units) for text with kerning + tracking (em)."""
    font = ttfont(path, wght)
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    names = [cmap[ord(ch)] for ch in text]
    xs, x = [], 0.0
    for i, n in enumerate(names):
        xs.append(x)
        x += hmtx[n][0] + tracking * upm
        if i + 1 < len(names):
            x += kern(font, n, names[i + 1])
    return font, names, xs, x  # x = advance incl. trailing tracking


def wordmark_runs():
    """[(path, wght, text, role)] for the two-tone wordmark."""
    return [(INTER, 750, "Yellow", "yellow"), (INTER, 400, "Force", "force")]


def wordmark_svg_paths(size: float, ox: float, baseline: float):
    """SVG <path> d strings per role for the wordmark at font size `size`, origin ox, baseline y."""
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    out, x = {}, ox
    xmin = ymin = math.inf
    xmax = ymax = -math.inf
    for path, wght, text, role in wordmark_runs():
        font, names, xs, adv = run_layout(path, wght, text, TRACKING)
        upm = font["head"].unitsPerEm
        k = size / upm
        gs = font.getGlyphSet()
        pen = SVGPathPen(gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        bp = BoundsPen(gs)
        for n, gx in zip(names, xs):
            tf = (k, 0, 0, -k, x + gx * k, baseline)
            gs[n].draw(TransformPen(pen, tf))
            gs[n].draw(TransformPen(bp, tf))
        if bp.bounds:
            xmin, ymin = min(xmin, bp.bounds[0]), min(ymin, bp.bounds[1])
            xmax, ymax = max(xmax, bp.bounds[2]), max(ymax, bp.bounds[3])
        out[role] = pen.getCommands()
        x += adv * k
    return out, (xmin, ymin, xmax, ymax)


def svg_doc(view, body, label="YellowForce"):
    x, y, w, h = view
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{label}"><title>{label}</title>{body}</svg>\n')


def write_logo_svgs():
    vb, d_back, d_front = read_mark()

    def mark_body(back, tf=""):
        g = f'<g transform="{tf}">' if tf else ""
        return (f'{g}<path class="yf-back" fill="{hexc(back)}" d="{d_back}"/>'
                f'<path class="yf-front" fill="{hexc(AMBER)}" d="{d_front}"/>{"</g>" if tf else ""}')

    for name, back in (("symbol-on-light", NAVY), ("symbol-on-dark", WHITE)):
        (LOGO / f"{name}.svg").write_text(svg_doc(vb, mark_body(back)))

    # wordmark alone (font size 100, origin 0, baseline 100)
    F = 100.0
    paths, (x0, y0, x1, y1) = wordmark_svg_paths(F, 0, F)
    pad = 2
    view = (x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad)
    for name, cy, cf in (("wordmark", NAVY, SLATE), ("wordmark-on-dark", WHITE, SLATE_LIGHT)):
        body = (f'<path class="yf-yellow" fill="{hexc(cy)}" d="{paths["yellow"]}"/>'
                f'<path class="yf-force" fill="{hexc(cf)}" d="{paths["force"]}"/>')
        (LOGO / f"{name}.svg").write_text(svg_doc(view, body))

    # horizontal lockup, kit proportions: mark height 1.757F, gap .587F, baseline 1.153F below mark top
    mh = LOCK_MARK_H * F
    s = mh / vb[3]
    mw = vb[2] * s
    tx = mw + LOCK_GAP * F
    paths, (_, wy0, wx1, wy1) = wordmark_svg_paths(F, tx, LOCK_BASE * F)
    top, bottom = min(0, wy0), max(mh, wy1)
    pad = 0.12 * F
    view = (-pad, top - pad, wx1 + 2 * pad, bottom - top + 2 * pad)
    tf = f"scale({s:.5f}) translate({-vb[0]:.2f} {-vb[1]:.2f})"
    for name, back, cy, cf in (("logo-horizontal", NAVY, NAVY, SLATE),
                               ("logo-horizontal-on-dark", WHITE, WHITE, SLATE_LIGHT)):
        body = (mark_body(back, tf) +
                f'<path class="yf-yellow" fill="{hexc(cy)}" d="{paths["yellow"]}"/>'
                f'<path class="yf-force" fill="{hexc(cf)}" d="{paths["force"]}"/>')
        (LOGO / f"{name}.svg").write_text(svg_doc(view, body))


# ---------------------------------------------------------------- icons
def favicon_svg():
    """Kit favicon framing (256 box, translate(25 59) scale(.99) of the kit path space) + dark tab style."""
    vb, d_back, d_front = read_mark()
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">'
            '<style>.b{fill:#071B3E}.f{fill:#FFBF00}@media (prefers-color-scheme:dark){.b{fill:#FFFFFF}}</style>'
            f'<g transform="translate(25 59) scale(.99)"><path class="b" d="{d_back}"/><path class="f" d="{d_front}"/></g>'
            '</svg>\n')


def favicon_png(size: int):
    """Kit favicon framing rendered to PNG (navy back, amber front, transparent)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    vb, _, _ = read_mark()
    k = size / 256
    # kit: path space origin at (25, 59), scale .99 -> viewBox top-left (x=0, y=12) lands at (25, 59 + 12*.99)
    draw_mark(img, 25 * k + vb[0] * 0.99 * k, (59 + vb[1] * 0.99) * k, vb[3] * 0.99 * k, NAVY, AMBER, ss=8)
    return img


def maskable_icon(size: int):
    """Full-bleed navy square, on-dark mark inside the maskable safe zone (60% wide)."""
    img = Image.new("RGBA", (size, size), NAVY + (255,))
    w = size * 0.6
    h = w / mark_width(1.0)
    draw_mark(img, (size - w) / 2, (size - h) / 2, h, WHITE, AMBER)
    return img


# ---------------------------------------------------------------- OG image
def pil_font(path: Path, size: float, wght: float):
    f = ImageFont.truetype(str(path), int(round(size)))
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def draw_run(d: ImageDraw.ImageDraw, x: float, baseline: float, text: str, path: Path, wght: float,
             size: float, tracking: float, fill):
    """Draw text glyph by glyph with GPOS kerning + tracking (Pillow's basic layout has neither)."""
    font, names, xs, adv = run_layout(path, wght, text, tracking)
    k = size / font["head"].unitsPerEm
    f = pil_font(path, size, wght)
    for ch, gx in zip(text, xs):
        d.text((x + gx * k, baseline), ch, font=f, fill=fill, anchor="ls")
    return adv * k


def run_width(text, path, wght, size, tracking):
    font, names, xs, adv = run_layout(path, wght, text, tracking)
    return (adv - tracking * font["head"].unitsPerEm) * size / font["head"].unitsPerEm


def streak_layer(size, seed=11):
    """Long-exposure light (amber + warm white) like the live reel: faint lanes, bright comets with hot
    heads. Returned as an RGB light layer (black = no light) for screen blending, faded toward the type."""
    W, H = size
    rnd = random.Random(seed)
    sc = W / 1200
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    core = Image.new("RGB", (W, H), (0, 0, 0))
    heads = Image.new("RGB", (W, H), (0, 0, 0))
    dg, dc, dh = ImageDraw.Draw(glow), ImageDraw.Draw(core), ImageDraw.Draw(heads)
    palette = [AMBER, AMBER_WARM, (255, 218, 128), WARM_WHITE]

    def col(h, a):
        x = max(0.0, min(0.999, h)) * (len(palette) - 1)
        i, f = int(x), x - int(x)
        p, q = palette[i], palette[i + 1]
        return tuple(int((p[c] + (q[c] - p[c]) * f) * a) for c in range(3))

    lanes = []
    n = 40
    for i in range(n):
        k = i / (n - 1) * 2 - 1
        lanes.append(dict(off=k * (0.36 + rnd.random() * 0.1), amp=0.01 + rnd.random() * 0.04,
                          freq=0.5 + rnd.random() * 1.2, ph=rnd.random() * math.tau, hue=rnd.random() * 0.7,
                          a=0.12 + rnd.random() * 0.24, w=1 if rnd.random() < 0.7 else 2))

    def pt(l, u):
        dd = (u - 0.72) / 0.3
        spread = 1 - 0.62 * math.exp(-dd * dd)
        y = H * (0.46 + l["off"] * spread * 0.62) + math.sin(u * l["freq"] * math.tau + l["ph"]) * l["amp"] * H * (0.35 + 0.65 * spread) + math.sin(u * math.pi * 1.15) * H * 0.04
        return ((u * 1.12 - 0.06) * W, y)

    for l in lanes:
        seg = [pt(l, j / 160) for j in range(161)]
        dc.line(seg, fill=col(l["hue"], l["a"]), width=max(1, int(l["w"] * sc)))
        dg.line(seg, fill=col(l["hue"] * 0.6, l["a"] * 0.45), width=int(7 * sc))
    for _ in range(16):
        l = lanes[rnd.randrange(n)]
        head = 0.45 + rnd.random() * 0.62
        ln = 0.12 + rnd.random() * 0.28
        hue = rnd.random() * 0.75
        bright = 0.55 + rnd.random() * 0.45
        steps = 40
        for j in range(steps):
            u0 = head - ln + ln * j / steps
            u1 = head - ln + ln * (j + 1) / steps
            t = (j + 1) / steps
            dc.line([pt(l, u0), pt(l, u1)], fill=col(hue + 0.35 * t ** 3, bright * t ** 1.5), width=max(2, int(2.4 * sc)))
            dg.line([pt(l, u0), pt(l, u1)], fill=col(hue * 0.4, 0.5 * bright * t ** 1.3), width=int(12 * sc))
        hx, hy = pt(l, head)
        r = 3.2 * sc
        dh.ellipse([hx - r, hy - r, hx + r, hy + r], fill=col(1.0, bright))
        r2 = 9 * sc
        dg.ellipse([hx - r2, hy - r2, hx + r2, hy + r2], fill=col(0.1, 0.55 * bright))
    glow = glow.filter(ImageFilter.GaussianBlur(8 * sc))
    heads = heads.filter(ImageFilter.GaussianBlur(1.6 * sc))
    out = ImageChops.add(ImageChops.add(glow, core), heads)
    mask = Image.linear_gradient("L").rotate(90).resize((W, H))
    mask = mask.point(lambda v: int(max(0, min(255, v * 2.0 - 175))))
    return Image.composite(out, Image.new("RGB", (W, H), (0, 0, 0)), mask)


def og_image():
    S = 2  # render at 2x, downsample
    W, H = 1200 * S, 630 * S
    # navy field: brand navy top-left to deep navy bottom-right
    grad = Image.linear_gradient("L").resize((W, H))
    diag = Image.linear_gradient("L").rotate(90).resize((W, H))
    t = ImageChops.add(grad.point(lambda v: v // 2), diag.point(lambda v: v // 2))
    img = Image.composite(Image.new("RGB", (W, H), NAVY_DEEP), Image.new("RGB", (W, H), NAVY), t)
    # soft brand-navy lift behind the light on the right (stays blue, no grey wash)
    lift = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(lift).ellipse([int(W * .5), int(H * .05), int(W * 1.15), int(H * .9)], fill=(5, 13, 30))
    img = ImageChops.add(img, lift.filter(ImageFilter.GaussianBlur(140 * S)))
    img = ImageChops.screen(img, streak_layer((W, H)))
    rgba = img.convert("RGBA")
    d = ImageDraw.Draw(rgba)
    M = 72 * S

    # lockup top-left: kit proportions, on-dark colors
    F = 30 * S
    mh = LOCK_MARK_H * F
    top = 64 * S
    mw = draw_mark(rgba, M, top, mh, WHITE, AMBER)
    x = M + mw + LOCK_GAP * F
    base = top + LOCK_BASE * F
    x += draw_run(d, x, base, "Yellow", INTER, 750, F, TRACKING, WHITE)
    draw_run(d, x, base, "Force", INTER, 400, F, TRACKING, SLATE_LIGHT)

    # live tag top-right
    tag = "24/7"
    tf = 22 * S
    tw = run_width(tag, INSTRUMENT, 500, tf, 0)
    ty = top + mh / 2 + tf * 0.36
    draw_run(d, W - M - tw, ty, tag, INSTRUMENT, 500, tf, 0, PAPER)
    r = 6 * S
    cx, cy = W - M - tw - 16 * S, top + mh / 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)

    # headline + subline bottom-left, domain bottom-right
    hs = 128 * S
    sub_base = H - 66 * S
    l2 = sub_base - 62 * S
    l1 = l2 - hs * 0.94
    for line, yb in (("Fight AI.", l1), ("With AI.", l2)):
        draw_run(d, M - hs * 0.01, yb, line, INTER, 700, hs, -0.045, PAPER)
    ss = 30 * S
    draw_run(d, M, sub_base, "Fully managed cybersecurity. 24/7.", INTER, 450, ss, -0.015, SLATE_LIGHT)
    dom = "yellow-force.com"
    ds = 24 * S
    draw_run(d, W - M - run_width(dom, INSTRUMENT, 500, ds, 0), sub_base, dom, INSTRUMENT, 500, ds, 0, PAPER)

    IMG.mkdir(parents=True, exist_ok=True)
    rgba.convert("RGB").resize((1200, 630), Image.LANCZOS).save(IMG / "og.png", optimize=True)


# ---------------------------------------------------------------- main
def main():
    STATIC.mkdir(parents=True, exist_ok=True)
    write_logo_svgs()
    (STATIC / "favicon.svg").write_text(favicon_svg())
    shutil.copyfile(BRAND / "favicon.ico", STATIC / "favicon.ico")
    favicon_png(32).save(STATIC / "favicon-32.png", optimize=True)

    app = Image.open(BRAND / "app_icon.png").convert("RGBA")
    # apple-touch: full bleed (iOS rounds it): kit app icon flattened on navy
    flat = Image.new("RGBA", app.size, NAVY + (255,))
    flat.alpha_composite(app)
    flat.convert("RGB").resize((180, 180), Image.LANCZOS).save(STATIC / "apple-touch-icon.png", optimize=True)
    for n in (192, 512):
        app.resize((n, n), Image.LANCZOS).save(STATIC / f"icon-{n}.png", optimize=True)
    maskable_icon(512).convert("RGB").save(STATIC / "icon-maskable-512.png", optimize=True)

    manifest = {
        "name": "YellowForce",
        "short_name": "YellowForce",
        "description": "Fully managed cybersecurity. We fight AI with AI, plus our cyber experts, 24/7.",
        "start_url": "/",
        "display": "browser",
        "background_color": "#071B3E",
        "theme_color": "#071B3E",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (STATIC / "site.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n")
    og_image()
    print("logo svgs, icons, manifest and og.png written")


if __name__ == "__main__":
    main()
