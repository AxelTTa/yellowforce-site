#!/usr/bin/env python3
"""Grade YellowForce photos to the brand look and export responsive WebP files.

Brand look (Axel's logo kit: navy #071B3E, amber #FFBF00, slate #777F98):
blacks sit on deep navy (#030B1C floor, deep shadows around #071B3E, never
neutral black), shadows navy-tinted, midtones a muted, near-neutral dark
slate (round 4: blue chroma cut so they sit with the generated family), highlights and small light sources pushed to amber
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
# Round 3 (2026-10-26): the photo family was far darker than the generated family and the reference's
# mid-key galleries (mean luma 16 to 30, up to 89% near-black). Shadows now sit on a navy floor
# (open dark about #0B1E45, brand-navy hue), midtones are lifted about +0.5 EV, amber light is kept.
# Only the vignetted corners fall to deep navy (#050E22), never neutral black.
NAVY_FLOOR = (5, 14, 34)     # #050E22, the darkest any pixel goes (corners only)
NAVY_OPEN = (11, 30, 69)     # #0B1E45, open shadows: navy, not black
NAVY = (7, 27, 62)           # #071B3E, brand navy
SLATE = (119, 127, 152)      # #777F98, brand slate
AMBER = (255, 191, 0)        # #FFBF00, brand amber
WARM_WHITE = (255, 244, 226)

# Three ramps, luminance -> sRGB.
# MONO: the photo itself. Deep navy floor in the corners, open shadows on navy,
# muted slate mids, then a neutral-warm climb to warm white
# (cool-to-warm through neutral, so a blend with the amber ramps never passes through olive).
# Round 4 (2026-10-26, QA C1): next to the generated family (near-black navy floor, warm-neutral mids) the round 3
# ramp read as a royal-blue duotone (median tone about 15/28/59). The darkest tones now sit back near #050E22
# and the blue chroma of the shadow and mid steps is cut by about 40 to 50% at the same luminance, so the mids
# trend to a neutral dark slate instead of saturated blue. Amber light is unchanged.
MONO = [
    (0.00, NAVY_FLOOR),
    (0.07, (7, 16, 35)),
    (0.16, (19, 28, 47)),
    (0.30, (41, 48, 68)),
    (0.46, (88, 91, 108)),
    (0.62, (131, 132, 142)),
    (0.78, (184, 180, 184)),
    (0.90, (228, 220, 208)),
    (1.00, (248, 241, 228)),
]
# LIGHT: what light sources turn into. Deep amber -> brand amber #FFBF00 -> warm-white core.
# Below the amber it runs through burnt orange, not olive: dim amber light must read warm.
# Above the amber it rolls into warm white early, so hot light glows instead of sitting flat.
LIGHT = [
    (0.00, NAVY_FLOOR),
    (0.35, (66, 44, 30)),
    (0.55, (150, 94, 12)),
    (0.70, (228, 150, 0)),
    (0.80, AMBER),
    (0.88, (255, 214, 120)),
    (0.94, (255, 234, 190)),
    (1.00, WARM_WHITE),
]
# WASH: broad lit surfaces (a floor, a sky, a wall). Slate-grey into a soft,
# low-chroma caramel and then cream: lit, warm, never a flat amber field.
WASH = [
    (0.00, NAVY_FLOOR),
    (0.40, (60, 62, 80)),
    (0.60, (128, 106, 86)),
    (0.76, (192, 160, 120)),
    (0.88, (234, 214, 180)),
    (1.00, (252, 244, 230)),
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
    # Round 3 (2026-10-26): every photo is graded on the lifted navy floor (open shadows #0B1E45,
    # +0.5 EV mids, see MONO). Targets on the 800 px files: mean luma 40+, under 60% of pixels below 25.
    # Round 4 (2026-10-26): same lift on the darker, less blue MONO ramp (darkest 10% about #060F22,
    # median tone about 19/25/42); photo-spare-2 and about-team open a little more to stay at mean 40+.
    # `shadow` lifts the deepest tones of the darkest sources; `exposure` < 1 opens the mids further.
    # Insights (4:3 cards)
    # insight-1: tighter on the fibre bundle so the light swarm fills the card instead of a black field.
    dict(name="insight-1", src="JyRTi3LoQnc.jpg", aspect=(4, 3), max=2000, focus=(0.42, 0.5), zoom=1.35, exposure=0.85, shadow=0.12),
    dict(name="insight-2", src="IGiut6NQmxc.jpg", aspect=(4, 3), max=2000, focus=(0.55, 0.5)),
    dict(name="insight-3", src="PSpf_XgOM5w.jpg", aspect=(4, 3), max=2000, focus=(0.5, 0.42), zoom=1.15, exposure=0.7, shadow=0.12),
    # About
    # round 3: the careers panel ("Join the fight.") was a murky blur with an unreadable figure. Now a
    # zoom-burst long exposure from a moving train: light rushing forward, no people. In the panel's
    # square crop at 30% the streaks run in from the left and meet at its right edge, next to the title.
    # A light pre-blur calms the stepped edges of the zoom. Same name, aspect and size.
    dict(name="about-team", src="YU5C3R3Evqc.jpg", aspect=(16, 9), max=2308, focus=(0.5, 0.5), exposure=0.85, shadow=0.08, soften=1.2),
    # round 2: a brighter, cleaner hand on a backlit keyboard (round 1 source Vr0uBwEBWIg was murky at
    # thumbnail size and had plastic bokeh blobs). Also the hero "Under attack?" card thumbnail.
    dict(name="about-strip-1", src="A6QgqHWq2eQ.jpg", aspect=(4, 3), max=2000, focus=(0.52, 0.46), exposure=0.85, lift=0.02),
    dict(name="about-strip-2", src="Ye19Jm4tA8g.jpg", aspect=(4, 3), max=2000, focus=(0.5, 0.45), exposure=0.85),
    dict(name="about-strip-3", src="VHmBX7FnXw0.jpg", aspect=(4, 3), max=2000, focus=(0.55, 0.5)),
    # Contact (4:5)
    # round 3: tighter, so the lit hand fills the frame (the top third was empty).
    dict(name="contact-photo", src="7oAnFA7NXgM.jpg", aspect=(4, 5), max=1800, focus=(0.46, 0.58), zoom=1.1, spread=0.5, soften=1.6, exposure=0.92),
    # Page heroes (16:9)
    dict(name="services-hero", src="s0XabTAKvak.jpg", aspect=(16, 9), max=2400, focus=(0.5, 0.5), exposure=1.1, bottom=0.3, shadow=0.05),
    dict(name="coverage-hero", src="AwkDru_0tQw.jpg", aspect=(16, 9), max=2400, focus=(0.6, 0.5), exposure=0.9, shadow=0.06),
    # Spares
    # round 2: no person at all. A long aisle of locked boxes under strip lights (round 1 source
    # kbtIiCzK4lQ was the last figure in profile). Same name, aspect and size.
    dict(name="photo-spare-1", src="a66u8vmMcMc.jpg", aspect=(4, 3), max=1578, focus=(0.5, 0.47), zoom=1.25, exposure=1.15, bottom=0.45),
    # photo-spare-2 is the About cover: lifted the most (it was mean 20, 85% near-black).
    dict(name="photo-spare-2", src="KN66Tjx8Zzs.jpg", aspect=(16, 9), max=2342, focus=(0.5, 0.5), exposure=0.70, shadow=0.10),
    dict(name="photo-spare-3", src="i2M4JeyBIV8.jpg", aspect=(16, 9), max=2400, focus=(0.5, 0.5)),
    dict(name="photo-spare-4", src="jcRi2yH6OhE.jpg", aspect=(4, 5), max=1600, focus=(0.6, 0.62), zoom=1.25, spread=0.6),
]


def _lut(ramp) -> np.ndarray:
    xs = np.array([p for p, _ in ramp])
    cols = np.array([c for _, c in ramp], dtype=np.float64) / 255.0
    grid = np.linspace(0, 1, 1024)
    return np.stack([np.interp(grid, xs, cols[:, i]) for i in range(3)], axis=-1).astype(np.float32)


LUT_MONO = _lut(MONO)
# S-curve (tone space): pivot, slope and how much of it is mixed in.
S_PIVOT, S_SLOPE, S_MIX = 0.40, 6.5, 0.50
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
          vignette=0.30, bloom=0.35, bottom=0.0, gain=1.0, mid=0.5, shadow=0.0, halo_area=0.4) -> np.ndarray:
    """rgb float32 0..1 (sRGB) -> graded float32 0..1, without grain.

    warm:     how strongly light sources go amber (0 = pure navy/slate mono).
    spread:   how much broad bright areas (walls, floors, sky) are held back to a
              soft caramel wash so only light itself turns amber (0 = everything bright goes amber).
    vignette: darkening at the corners, in tone space so corners fall to navy, not black.
    bloom:    soft highlight glow in linear light (shared look with assets/img/gen/).
    gain:     scales the tone range before the curve (below 1 pulls a blown wall or sky back from white).
    bottom:   light falloff towards the bottom edge (a lit floor fades into the dark instead of sitting flat).
    mid:      midtone lift in EV (round 3 default +0.5): a linear-light gain with a soft shoulder, so the
              mids open up while the light keeps its highlight roll-off.
    shadow:   extra lift of the deepest tones towards the navy floor (0..0.2), for very dark sources.
    """
    h, w, _ = rgb.shape
    # Luminance with a red-leaning mix so tail lights and warm lamps read as light.
    lum = rgb[..., 0] * 0.36 + rgb[..., 1] * 0.52 + rgb[..., 2] * 0.12
    # Auto levels on robust percentiles, then exposure.
    lo, hi = np.percentile(lum, [0.4, 99.85])
    hi = max(hi, lo + 0.05)
    L = np.clip((lum - lo) / (hi - lo), 0, 1)
    L = np.clip(L + lift, 0, 1) ** exposure * gain
    if mid:
        # +mid EV in linear light, Reinhard-style shoulder pinned at 1 so highlights do not clip.
        g = 2.0 ** mid
        lin = np.clip(L, 0, 1) ** 2.2
        lin = lin * g / (1 + lin * (g - 1))
        L = lin ** (1 / 2.2)
    if shadow:
        L = L + shadow * (1 - L) ** 4 * smoothstep(0.0, 0.25, L) + shadow * 0.35 * (1 - L) ** 8
    # Subtle elliptical vignette (applied in tone space so blacks stay at the floor).
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx / w - 0.5) * 2, (yy / h - 0.5) * 2
    r = np.sqrt(nx * nx * 0.85 + ny * ny * 1.0)
    L = L * (1 - vignette * smoothstep(0.55, 1.45, r))
    if bottom:
        L = L * (1 - bottom * smoothstep(0.55, 1.0, yy / h))
    # Gentle S-curve (round 4: a touch more contrast, so the darker floor reads as depth, not as a flat filter).
    L = np.clip(L, 0, 1)
    s = 1 / (1 + np.exp(-(L - S_PIVOT) * S_SLOPE))
    s0, s1 = 1 / (1 + np.exp(S_PIVOT * S_SLOPE)), 1 / (1 + np.exp(-(1 - S_PIVOT) * S_SLOPE))
    L = ((1 - S_MIX) * L + S_MIX * (s - s0) / (s1 - s0)).astype(np.float32)
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
    # Round 3: broad light glows too (less suppression), and a wide, faint third radius lets amber
    # fall off into the navy through gold and bronze like the generated family, not as a hard duotone edge.
    hl = smoothstep(0.72, 1.0, L).astype(np.float32) * (1 - halo_area * area)
    sig = max(w, h) * 0.010
    halo = (ndimage.gaussian_filter(hl, sig) * 0.5 + ndimage.gaussian_filter(hl, sig * 4) * 0.32
            + ndimage.gaussian_filter(hl, sig * 12) * 0.18)
    # the halo is light in the air: it shows over the dark and fades out over what is already bright
    halo = halo * (1 - smoothstep(0.55, 0.95, L)) ** 0.5
    out = out + glow * warm * halo[..., None] * GLOW[None, None, :]
    # Bloom, in linear light like the generated family: highlights spread a
    # soft multi-scale glow (lens + mist filter), so photos share the same
    # luminous, slightly dreamy light instead of hard duotone edges.
    out = add_bloom(np.clip(out, 0, None), bloom, warm)
    # Hue-preserving shoulder: a per-channel clip would cap red first and turn
    # hot amber lemon-yellow. Scale back into range, then burn towards warm white.
    peak = np.maximum(out.max(axis=-1, keepdims=True), 1.0)
    out = out / peak
    out = out + (np.asarray(WARM_WHITE, np.float32) / 255.0 - out) * np.clip((peak - 1) * 0.9, 0, 0.6)
    return np.clip(out, FLOOR[None, None, :], 1)


# Bloom tint: the glow keeps the colour of the light that makes it, pulled a
# little towards warm white (amber light glows golden, white light glows cream).
BLOOM_WARM = np.array([1.0, 0.86, 0.62], dtype=np.float32)


def add_bloom(img: np.ndarray, strength=0.35, warm=1.0) -> np.ndarray:
    """img: graded sRGB-ish 0..1 floats. Returns sRGB-ish with highlight bloom
    (values may exceed 1; the caller applies the shoulder)."""
    if strength <= 0:
        return img
    import cv2
    h, w, _ = img.shape
    lin = np.power(img, 2.2).astype(np.float32)
    Y = lin @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    # soft-knee highlight extraction
    k = np.clip((Y - 0.18) / 0.82, 0, 1) ** 1.6
    src = lin * (k / np.maximum(Y, 1e-4))[..., None] * Y[..., None] ** 0.5
    q = 4
    small = cv2.resize(src, (max(8, w // q), max(8, h // q)), interpolation=cv2.INTER_AREA)
    m = max(w, h) / q
    b = np.zeros_like(small)
    for frac, wt in ((0.004, 0.35), (0.014, 0.35), (0.045, 0.30)):
        b += wt * cv2.GaussianBlur(small, (0, 0), max(0.8, frac * m))
    b = cv2.resize(b, (w, h), interpolation=cv2.INTER_LINEAR)
    bl = (b @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    tint = 0.5 * b + 0.5 * bl * (BLOOM_WARM * warm + (1 - warm))
    lin = lin + strength * tint
    return np.power(np.maximum(lin, 0), 1 / 2.2)


def add_grain(img: np.ndarray, amount=1.15, seed=7) -> np.ndarray:
    """Film grain matched to the generated family (tools/gen_core.py develop):
    luminance-shaped (strongest in the mids), slightly clumped, mostly
    monochrome, navy-tinted in the shadows so the floor never turns grey."""
    h, w, _ = img.shape
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((h, w)).astype(np.float32)
    n = ndimage.gaussian_filter(n, 0.65)
    n /= n.std() + 1e-6
    lum = np.clip(img[..., 0] * 0.2126 + img[..., 1] * 0.7152 + img[..., 2] * 0.0722, 0, 1)
    amp = (0.9 + 4.5 * np.sqrt(lum) * (1 - lum) ** 1.2) / 255.0 * amount
    sh = (1 - smoothstep(0.0, 0.30, lum)).astype(np.float32)[..., None]
    tint = sh * GRAIN_SHADOW + (1 - sh) * GRAIN_LIGHT
    out = img + (n * amp)[..., None] * tint
    out = out + rng.standard_normal((h, w, 3)).astype(np.float32) * (0.35 / 255.0) * amount
    return np.clip(out, FLOOR[None, None, :] * 0.85, 1)


def to_img(a: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


# Weight budgets per output (KB) for a 16:9 frame of that width; scaled by pixel count for other aspects.
WEIGHT_KB = {"main": 165, "-1600": 105, "-800": 34}
REF_PX = {"main": 2400 * 1350, "-1600": 1600 * 900, "-800": 800 * 450}


def process(spec: dict, quality=82) -> list[Path]:
    src = SRC / spec["src"]
    im = Image.open(src).convert("RGB")
    if spec.get("flip"):
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = crop_to_aspect(im, spec["aspect"], spec.get("focus", (0.5, 0.5)), spec.get("zoom", 1.0))
    maxw = spec.get("max", 2400)
    if im.width < maxw * 0.95:
        maxw = im.width          # never upscale a real shortfall; a zoomed crop within 5% keeps its size
    big = im.resize((maxw, round(maxw * spec["aspect"][1] / spec["aspect"][0])), Image.LANCZOS)
    if spec.get("soften"):
        # noisy night sources: calm the sensor noise before the tone map amplifies it
        from PIL import ImageFilter
        big = big.filter(ImageFilter.GaussianBlur(spec["soften"]))
    base = grade(
        np.asarray(big, dtype=np.float32) / 255.0,
        exposure=spec.get("exposure", 1.0),
        glow=spec.get("glow", 0.30),
        keep_chroma=spec.get("chroma", 0.04),
        lift=spec.get("lift", 0.0),
        warm=spec.get("warm", 1.0),
        spread=spec.get("spread", 0.8),
        vignette=spec.get("vignette", 0.30),
        bloom=spec.get("bloom", 0.50),
        bottom=spec.get("bottom", 0.0),
        gain=spec.get("gain", 1.0),
        mid=spec.get("mid", 0.5),
        shadow=spec.get("shadow", 0.0),
        halo_area=spec.get("halo_area", 0.4),
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
        arr = add_grain(arr, amount=spec.get("grain", 1.0) * (0.85 if width <= 800 else 1.0), seed=zlib.crc32(spec["name"].encode()))
        p = OUT / f"{spec['name']}{suffix}.webp"
        out_img = to_img(arr)
        # Page weight: the lifted shadows carry more visible grain and detail than the old near-black
        # ones, so step the quality down until each file fits its budget (same weights as round 2).
        q = quality
        out_img.save(p, "WEBP", quality=q, method=6)
        budget = WEIGHT_KB[suffix or "main"] * min(1.25, max(0.6, (width * hgt) / REF_PX[suffix or "main"]))
        while p.stat().st_size > budget * 1024 and q > 62:
            q -= 4
            out_img.save(p, "WEBP", quality=q, method=6)
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
    swatches = [("#071B3E navy", NAVY, (255, 255, 255)), ("#%02X%02X%02X floor" % NAVY_FLOOR, NAVY_FLOOR, (255, 255, 255)),
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
