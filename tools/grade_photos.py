#!/usr/bin/env python3
"""Grade YellowForce photos to the brand look and export responsive WebP files.

Brand look (Axel's logo kit: navy #071B3E, amber #FFBF00, slate #777F98):
blacks sit on deep navy (#030B1C floor, deep shadows around #071B3E, never
neutral black), shadows navy-tinted, midtones desaturated with a slight
slate-blue cast (#777F98), highlights and small light sources pushed to amber
#FFBF00 and warm white like light streaks, gentle S-curve, soft amber
halation on bright light, navy-tinted film grain, subtle vignette. Built to
sit next to the generated light-streak family in assets/img/gen/.

Usage (from site/):
    ../.venv/bin/python tools/grade_photos.py              # all photos + both QA sheets
    ../.venv/bin/python tools/grade_photos.py insight-1    # only some
    ../.venv/bin/python tools/grade_photos.py --sheet      # also rebuild the QA sheets
    ../.venv/bin/python tools/grade_photos.py --sheet-only # only the QA sheets

QA sheets: qa/photo-contact-sheet.jpg (all 14 at 800 px) and
qa/photo-brand-check.jpg (a few photos next to flat #071B3E / #FFBF00 swatches).

Sources live outside the site in ../photo-src/ (originals, free Unsplash
License, see CREDITS.md). Outputs go to assets/img/photo/:
NAME.webp (max 2400 wide), NAME-1600.webp, NAME-800.webp.
"""
from __future__ import annotations

import argparse
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

SITE = Path(__file__).resolve().parent.parent
SRC = SITE.parent / "photo-src" / "orig"
OUT = SITE / "assets" / "img" / "photo"
QA = SITE / "qa"

# Brand colours (sRGB 0..255).
NAVY_FLOOR = (3, 11, 28)     # #030B1C, the darkest any pixel goes
NAVY = (7, 27, 62)           # #071B3E, brand navy
SLATE = (119, 127, 152)      # #777F98, brand slate
AMBER = (255, 191, 0)        # #FFBF00, brand amber
WARM_WHITE = (255, 243, 222)

# Three ramps, luminance -> sRGB.
# MONO: the photo itself. Navy floor, navy shadows, slate-blue desaturated
# mids (#777F98 at 0.64), then a neutral-warm climb to warm white (cool-to-warm
# through neutral, so a blend with the amber ramps never passes through olive).
MONO = [
    (0.00, NAVY_FLOOR),
    (0.09, (5, 17, 43)),
    (0.20, (10, 28, 62)),
    (0.34, (36, 46, 72)),
    (0.50, (84, 90, 112)),
    (0.64, SLATE),
    (0.80, (180, 178, 184)),
    (0.92, (228, 220, 208)),
    (1.00, (248, 241, 228)),
]
# LIGHT: what light sources turn into. Deep amber -> brand amber #FFBF00 -> warm-white core.
# Below the amber it runs through burnt orange, not olive: dim amber light must read warm.
LIGHT = [
    (0.00, NAVY_FLOOR),
    (0.35, (66, 42, 22)),
    (0.55, (156, 98, 12)),
    (0.70, (230, 152, 0)),
    (0.82, AMBER),
    (0.92, (255, 216, 112)),
    (1.00, WARM_WHITE),
]
# WASH: broad lit surfaces (a floor, a sky, a wall). Slate-grey into a soft
# amber-caramel and warm white, never khaki and never a flat amber field.
WASH = [
    (0.00, NAVY_FLOOR),
    (0.40, (62, 58, 66)),
    (0.60, (154, 114, 74)),
    (0.76, (218, 156, 74)),
    (0.88, (246, 194, 108)),
    (1.00, (253, 234, 198)),
]
GLOW = np.array([1.0, 0.70, 0.10])  # halation tint (amber, a touch warmer than #FFBF00 so it never reads olive on navy)
# Grain tint: in the shadows grain follows the navy hue so blacks never turn grey;
# in the mids and highlights it is close to neutral-warm.
GRAIN_SHADOW = np.array([0.45, 0.75, 1.35], dtype=np.float32)
GRAIN_LIGHT = np.array([1.0, 0.97, 0.92], dtype=np.float32)

# Each photo: source file, output name, aspect (w, h), focus point (0..1),
# zoom (>=1 crops tighter), exposure (gamma-like, >1 darker), max width,
# glow strength, flip. Filled in after selection; see MANIFEST.md.
PHOTOS: list[dict] = [
    # Insights (4:3 cards)
    dict(name="insight-1", src="JyRTi3LoQnc.jpg", aspect=(4, 3), max=2000, focus=(0.5, 0.5)),
    dict(name="insight-2", src="IGiut6NQmxc.jpg", aspect=(4, 3), max=2000, focus=(0.55, 0.5)),
    dict(name="insight-3", src="PSpf_XgOM5w.jpg", aspect=(4, 3), max=2000, focus=(0.5, 0.5)),
    # About
    dict(name="about-team", src="UYsx3SfIopg.jpg", aspect=(16, 9), max=2400, focus=(0.62, 0.45), zoom=1.3, spread=0.7),
    dict(name="about-strip-1", src="Vr0uBwEBWIg.jpg", aspect=(4, 3), max=2000, focus=(0.5, 0.5)),
    dict(name="about-strip-2", src="Ye19Jm4tA8g.jpg", aspect=(4, 3), max=2000, focus=(0.5, 0.45), exposure=0.85),
    dict(name="about-strip-3", src="VHmBX7FnXw0.jpg", aspect=(4, 3), max=2000, focus=(0.55, 0.5)),
    # Contact (4:5)
    dict(name="contact-photo", src="h54xsHoAj8k.jpg", aspect=(4, 5), max=1800, focus=(0.5, 0.5)),
    # Page heroes (16:9)
    dict(name="services-hero", src="s0XabTAKvak.jpg", aspect=(16, 9), max=2400, focus=(0.5, 0.5), exposure=1.15),
    dict(name="coverage-hero", src="AwkDru_0tQw.jpg", aspect=(16, 9), max=2400, focus=(0.6, 0.5)),
    # Spares
    dict(name="photo-spare-1", src="kbtIiCzK4lQ.jpg", aspect=(4, 3), max=2000, focus=(0.363, 0.576), zoom=1.69),
    dict(name="photo-spare-2", src="KN66Tjx8Zzs.jpg", aspect=(16, 9), max=2400, focus=(0.5, 0.5)),
    dict(name="photo-spare-3", src="i2M4JeyBIV8.jpg", aspect=(16, 9), max=2400, focus=(0.5, 0.5)),
    dict(name="photo-spare-4", src="ztijhVkK7ZI.jpg", aspect=(4, 5), max=1800, focus=(0.45, 0.5), spread=0.3, exposure=1.2),
]


def _lut(ramp) -> np.ndarray:
    xs = np.array([p for p, _ in ramp])
    cols = np.array([c for _, c in ramp], dtype=np.float64) / 255.0
    grid = np.linspace(0, 1, 1024)
    return np.stack([np.interp(grid, xs, cols[:, i]) for i in range(3)], axis=-1).astype(np.float32)


LUT_MONO = _lut(MONO)
LUT_LIGHT = _lut(LIGHT)
LUT_WASH = _lut(WASH)
FLOOR = np.array(NAVY_FLOOR, dtype=np.float32) / 255.0


def crop_to_aspect(im: Image.Image, aspect: tuple[int, int], focus=(0.5, 0.5), zoom=1.0) -> Image.Image:
    w, h = im.size
    target = aspect[0] / aspect[1]
    if w / h > target:
        ch = h / zoom
        cw = ch * target
    else:
        cw = w / zoom
        ch = cw / target
    cx = min(max(focus[0] * w, cw / 2), w - cw / 2)
    cy = min(max(focus[1] * h, ch / 2), h - ch / 2)
    box = (round(cx - cw / 2), round(cy - ch / 2), round(cx + cw / 2), round(cy + ch / 2))
    return im.crop(box)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def grade(rgb: np.ndarray, exposure=1.0, glow=0.22, keep_chroma=0.04, lift=0.0, warm=1.0, spread=0.8,
          vignette=0.26) -> np.ndarray:
    """rgb float32 0..1 (sRGB) -> graded float32 0..1, without grain.

    warm:     how strongly light sources go amber (0 = pure navy/slate mono).
    spread:   how much broad bright areas (walls, floors, sky) are held back to a
              soft caramel wash so only light itself turns amber (0 = everything bright goes amber).
    vignette: darkening at the corners, in tone space so corners fall to navy, not black.
    """
    h, w, _ = rgb.shape
    # Luminance with a red-leaning mix so tail lights and warm lamps read as light.
    lum = rgb[..., 0] * 0.36 + rgb[..., 1] * 0.52 + rgb[..., 2] * 0.12
    # Auto levels on robust percentiles, then exposure.
    lo, hi = np.percentile(lum, [0.4, 99.85])
    hi = max(hi, lo + 0.05)
    L = np.clip((lum - lo) / (hi - lo), 0, 1)
    L = np.clip(L + lift, 0, 1) ** exposure
    # Subtle elliptical vignette (applied in tone space so blacks stay at the floor).
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx / w - 0.5) * 2, (yy / h - 0.5) * 2
    r = np.sqrt(nx * nx * 0.85 + ny * ny * 1.0)
    L = L * (1 - vignette * smoothstep(0.55, 1.45, r))
    # Gentle S-curve around 0.42.
    L = np.clip(L, 0, 1)
    s = 1 / (1 + np.exp(-(L - 0.42) * 6.0))
    s0, s1 = 1 / (1 + np.exp(0.42 * 6.0)), 1 / (1 + np.exp(-(0.58) * 6.0))
    L = (0.55 * L + 0.45 * (s - s0) / (s1 - s0)).astype(np.float32)
    idx = np.clip((L * 1023).astype(np.int32), 0, 1023)
    mono = LUT_MONO[idx]
    light = LUT_LIGHT[idx]
    wash = LUT_WASH[idx]
    # Where is "light" (thin, bright) versus a broad bright surface?
    bright = smoothstep(0.45, 0.8, L).astype(np.float32)
    area = ndimage.gaussian_filter(bright, max(w, h) * 0.035)
    area = np.clip(area / 0.55, 0, 1)
    ramp = smoothstep(0.45, 0.82, L) * warm
    t_light = ramp * (1 - spread * area)          # thin light: full amber
    t_wash = ramp * spread * area * 0.6           # broad surfaces: soft amber wash
    out = (mono * (1 - t_light - t_wash)[..., None]
           + light * t_light[..., None] + wash * t_wash[..., None])
    # Keep a trace of the original chroma for life (near-monochrome, not flat).
    chroma = rgb - lum[..., None]
    # Only in the upper tones: original skin red over navy mids would read violet.
    out = out + keep_chroma * chroma * smoothstep(0.3, 0.85, L)[..., None]
    # Halation: thin bright light bleeds amber into the dark around it.
    hl = smoothstep(0.75, 1.0, L).astype(np.float32) * (1 - 0.7 * area)
    sig = max(w, h) * 0.010
    halo = ndimage.gaussian_filter(hl, sig) * 0.6 + ndimage.gaussian_filter(hl, sig * 4) * 0.4
    out = out + glow * warm * halo[..., None] * GLOW[None, None, :]
    # Hue-preserving shoulder: a per-channel clip would cap red first and turn
    # hot amber lemon-yellow. Scale back into range, then burn towards white.
    peak = np.maximum(out.max(axis=-1, keepdims=True), 1.0)
    out = out / peak
    out = out + (1 - out) * np.clip((peak - 1) * 0.8, 0, 0.5)
    return np.clip(out, FLOOR[None, None, :], 1)


def add_grain(img: np.ndarray, amount=0.022, seed=7) -> np.ndarray:
    h, w, _ = img.shape
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((h, w)).astype(np.float32)
    n = ndimage.gaussian_filter(n, 0.65)
    n /= n.std() + 1e-6
    lum = img[..., 0] * 0.2126 + img[..., 1] * 0.7152 + img[..., 2] * 0.0722
    # Film grain is strongest in the mids, lighter in deep shadows and hot highlights.
    weight = 0.30 + 1.25 * lum * (1 - lum) * 2
    # Navy-tinted in the shadows (so the floor never goes grey), neutral-warm above.
    sh = (1 - smoothstep(0.0, 0.30, lum)).astype(np.float32)[..., None]
    tint = sh * GRAIN_SHADOW + (1 - sh) * GRAIN_LIGHT
    out = img + (n * amount * weight)[..., None] * tint
    return np.clip(out, FLOOR[None, None, :] * 0.85, 1)


def to_img(a: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def process(spec: dict, quality=82) -> list[Path]:
    src = SRC / spec["src"]
    im = Image.open(src).convert("RGB")
    if spec.get("flip"):
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = crop_to_aspect(im, spec["aspect"], spec.get("focus", (0.5, 0.5)), spec.get("zoom", 1.0))
    maxw = min(spec.get("max", 2400), im.width)
    big = im.resize((maxw, round(maxw * spec["aspect"][1] / spec["aspect"][0])), Image.LANCZOS)
    base = grade(
        np.asarray(big, dtype=np.float32) / 255.0,
        exposure=spec.get("exposure", 1.0),
        glow=spec.get("glow", 0.22),
        keep_chroma=spec.get("chroma", 0.04),
        lift=spec.get("lift", 0.0),
        warm=spec.get("warm", 1.0),
        spread=spec.get("spread", 0.8),
        vignette=spec.get("vignette", 0.26),
    )
    base_img = to_img(base)
    written = []
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, width in (("", maxw), ("-1600", 1600), ("-800", 800)):
        width = min(width, maxw)
        hgt = round(width * spec["aspect"][1] / spec["aspect"][0])
        sized = base_img if width == maxw else base_img.resize((width, hgt), Image.LANCZOS)
        arr = np.asarray(sized, dtype=np.float32) / 255.0
        # Grain sized for each output so it reads the same at every width.
        arr = add_grain(arr, amount=spec.get("grain", 0.022) * (0.85 if width <= 800 else 1.0), seed=zlib.crc32(spec["name"].encode()))
        p = OUT / f"{spec['name']}{suffix}.webp"
        to_img(arr).save(p, "WEBP", quality=quality, method=6)
        written.append(p)
    return written


def _font(size: int):
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            pass
    return ImageFont.load_default()


def contact_sheet(names: list[str]) -> Path:
    """All photos at 800 px on brand navy, amber labels."""
    QA.mkdir(parents=True, exist_ok=True)
    tiles = []
    for n in names:
        p = OUT / f"{n}-800.webp"
        if p.exists():
            tiles.append((n, Image.open(p).convert("RGB")))
    cols, cw, chh, pad, lab = 4, 480, 360, 16, 26
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cw + pad) + pad, rows * (chh + lab + pad) + pad), NAVY)
    d = ImageDraw.Draw(sheet)
    font = _font(16)
    for i, (n, im) in enumerate(tiles):
        x = pad + (i % cols) * (cw + pad)
        y = pad + (i // cols) * (chh + lab + pad)
        t = im.copy()
        t.thumbnail((cw, chh), Image.LANCZOS)
        sheet.paste(t, (x + (cw - t.width) // 2, y + (chh - t.height) // 2))
        d.text((x, y + chh + 5), f"{n}  {im.width}x{im.height}", fill=AMBER, font=font)
    out = QA / "photo-contact-sheet.jpg"
    sheet.save(out, quality=88)
    return out


BRAND_CHECK = ["coverage-hero", "insight-2", "about-strip-3", "photo-spare-3", "about-team", "contact-photo"]


def brand_check(names=BRAND_CHECK) -> Path:
    """A few graded photos beside flat brand swatches, on paper, so the
    navy blacks and amber highlights can be judged against the real colours."""
    QA.mkdir(parents=True, exist_ok=True)
    paper = (244, 245, 247)
    pad, th, sw = 24, 300, 150
    font, small = _font(18), _font(14)
    swatches = [("#071B3E navy", NAVY, (255, 255, 255)), ("#030B1C floor", NAVY_FLOOR, (255, 255, 255)),
                ("#777F98 slate", SLATE, (255, 255, 255)), ("#FFBF00 amber", AMBER, NAVY)]
    ims = []
    for n in names:
        p = OUT / f"{n}-800.webp"
        if p.exists():
            im = Image.open(p).convert("RGB")
            im = im.resize((round(im.width * th / im.height), th), Image.LANCZOS)
            ims.append((n, im))
    # Two rows of photos; each row starts with a navy and an amber swatch.
    rows = [ims[: (len(ims) + 1) // 2], ims[(len(ims) + 1) // 2:]]
    row_w = [2 * (sw + pad) + sum(im.width + pad for _, im in r) for r in rows]
    W = max(row_w) + pad
    top = 56
    H = top + len(rows) * (th + 34 + pad) + sw // 2 + 34 + pad
    sheet = Image.new("RGB", (W, H), paper)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 18), "Photo grade vs brand colours (photos at 800 px, scaled to 300 px tall)", fill=NAVY, font=font)
    y = top
    for r in rows:
        x = pad
        for label, col, ink in (swatches[0], swatches[3]):
            d.rectangle([x, y, x + sw - 1, y + th - 1], fill=col)
            d.text((x + 10, y + th - 26), label, fill=ink, font=small)
            x += sw + pad
        for n, im in r:
            sheet.paste(im, (x, y))
            d.text((x, y + th + 8), n, fill=NAVY, font=small)
            x += im.width + pad
        y += th + 34 + pad
    # Strip of the brand swatches, then what the photos actually use (sampled
    # from the files above): their floor (darkest 10%) and their light (amber pixels).
    allpx = np.concatenate([np.asarray(im).reshape(-1, 3).astype(np.float32) for _, im in ims])
    Y = allpx @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    floor = np.median(allpx[Y <= np.percentile(Y, 10)], axis=0)
    hot = allpx[(allpx[:, 0] > 200) & (allpx[:, 0] - allpx[:, 2] > 120)]
    light = np.median(hot, axis=0) if len(hot) else np.array(AMBER, dtype=np.float32)
    hexc = lambda c: "#%02X%02X%02X" % tuple(int(round(v)) for v in c)
    sampled = [(f"photos: floor {hexc(floor)}", tuple(int(v) for v in floor), (255, 255, 255)),
               (f"photos: light {hexc(light)}", tuple(int(v) for v in light), NAVY)]
    x = pad
    sw2 = (W - pad - 6 * pad) // 6
    for label, col, ink in swatches + sampled:
        d.rectangle([x, y, x + sw2 - 1, y + sw // 2 - 1], fill=col)
        d.text((x + 10, y + sw // 2 - 24), label, fill=ink, font=small)
        x += sw2 + pad
    out = QA / "photo-brand-check.jpg"
    sheet.save(out, quality=90)
    return out


def floor_report(names: list[str]) -> None:
    """Print the darkest colours each 800 px file actually uses (should be navy, never neutral)."""
    for n in names:
        p = OUT / f"{n}-800.webp"
        if not p.exists():
            continue
        a = np.asarray(Image.open(p).convert("RGB")).reshape(-1, 3).astype(np.float32)
        Y = a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        dark = a[Y <= np.percentile(Y, 10)]
        med = np.median(dark, axis=0).round().astype(int)
        neutral = float(np.mean((a.max(1) - a.min(1) < 8) & (Y < 60))) * 100
        print(f"  {n:15s} darkest-10% median #{med[0]:02X}{med[1]:02X}{med[2]:02X}  neutral-dark px {neutral:.1f}%")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="only these output names")
    ap.add_argument("--sheet", action="store_true", help="rebuild qa/photo-contact-sheet.jpg and qa/photo-brand-check.jpg")
    ap.add_argument("--sheet-only", action="store_true", help="only rebuild the QA sheets")
    a = ap.parse_args(argv)
    todo = [] if a.sheet_only else [p for p in PHOTOS if not a.names or p["name"] in a.names]
    for spec in todo:
        files = process(spec)
        sizes = ", ".join(f"{f.name} {f.stat().st_size // 1024}KB" for f in files)
        print(f"{spec['name']}: {sizes}")
    floor_report([p["name"] for p in todo])
    if a.sheet or a.sheet_only or not a.names:
        print(contact_sheet([p["name"] for p in PHOTOS]))
        print(brand_check())
    return 0


if __name__ == "__main__":
    sys.exit(main())
