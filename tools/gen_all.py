"""Render every YellowForce generated visual at final size and export WebP.

    .venv/bin/python tools/gen_all.py              # all scenes
    .venv/bin/python tools/gen_all.py hero cta     # some scenes
    options: --ss 2 (supersampling), --jobs 5, --sheet-only

Outputs assets/img/gen/NAME.webp (main), NAME-1600.webp, NAME-800.webp,
qa/gen-contact-sheet.jpg and assets/img/gen/MANIFEST.md.
Everything is seeded: the same code gives the same pictures.
"""
import os
import shutil
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SITE = HERE.parent
OUT = SITE / "assets" / "img" / "gen"
QA = SITE / "qa"
Q = 82
MAX_KB = 300


def aspect_label(w, h):
    from math import gcd
    g = gcd(w, h)
    return f"{w // g}:{h // g}"


def render_one(name, ss=2):
    from gen_scenes import SCENES, render
    t = time.time()
    img = Image.fromarray(render(name, ss=ss))
    OUT.mkdir(parents=True, exist_ok=True)
    w, h = img.size
    opts = dict(quality=Q, method=6)
    img.save(OUT / f"{name}.webp", **opts)
    # keep page weight in line with the rest of the set: very detailed frames
    # (dense fields of fine trails) step the quality down until the main file fits
    q = Q
    while (OUT / f"{name}.webp").stat().st_size > MAX_KB * 1024 and q > 58:
        q -= 3
        opts = dict(quality=q, method=6)
        img.save(OUT / f"{name}.webp", **opts)
    for tw in (1600, 800):
        p = OUT / f"{name}-{tw}.webp"
        if tw >= w:
            shutil.copyfile(OUT / f"{name}.webp", p)
        else:
            img.resize((tw, round(h * tw / w)), Image.LANCZOS).save(p, **opts)
    return name, (w, h), time.time() - t


def sheet(names):
    tw, pad, lab = 420, 14, 22
    cells = []
    for n in names:
        im = Image.open(OUT / f"{n}-800.webp").convert("RGB")
        im = im.resize((tw, round(im.height * tw / im.width)), Image.LANCZOS)
        cells.append((n, im))
    cols = 5
    rows = (len(cells) + cols - 1) // cols
    rh = [max(im.height for _, im in cells[r * cols:(r + 1) * cols]) + lab + pad for r in range(rows)]
    S = Image.new("RGB", (cols * (tw + pad) + pad, sum(rh) + pad), (24, 24, 24))
    d = ImageDraw.Draw(S)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    except Exception:
        font = ImageFont.load_default()
    y = pad
    for r in range(rows):
        for c, (n, im) in enumerate(cells[r * cols:(r + 1) * cols]):
            x = pad + c * (tw + pad)
            S.paste(im, (x, y))
            d.text((x, y + im.height + 4), n, fill=(225, 225, 225), font=font)
        y += rh[r]
    QA.mkdir(parents=True, exist_ok=True)
    S.save(QA / "gen-contact-sheet.jpg", quality=88)


SWATCH_NAMES = ["hero", "threat-breach", "domain-cloud", "about-1", "service-6", "cta"]


def _font(size):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception:
        return ImageFont.load_default()


def swatch_check(names=SWATCH_NAMES):
    """qa/brand-swatch-check.jpg: images between flat brand swatches (#071B3E
    left, #FFBF00 right) with the colours measured in each image: open field
    (median of the darker half), lit amber (bright, saturated pixels) and the
    hottest core."""
    import numpy as np
    NAVY, AMBER = (7, 27, 62), (255, 191, 0)
    ref = [("#030B1C", (3, 11, 28)), ("#071B3E", NAVY), ("#777F98", (119, 127, 152)),
           ("#FFBF00", AMBER), ("#FFF3D1", (255, 243, 209))]
    iw, sw, pad, chip = 720, 150, 24, 54
    f13, f15, f20 = _font(13), _font(15), _font(20)
    rows = []
    for n in names:
        im = Image.open(OUT / f"{n}-800.webp").convert("RGB")
        im = im.resize((iw, round(im.height * iw / im.width)), Image.LANCZOS)
        a = np.asarray(Image.open(OUT / f"{n}.webp").convert("RGB")).reshape(-1, 3).astype(float)
        L = a @ [0.2126, 0.7152, 0.0722]
        mx, mn = a.max(1), a.min(1)
        sat = (mx - mn) / np.maximum(mx, 1)
        field = np.median(a[L <= np.percentile(L, 50)], 0)
        lit_m = (L > np.percentile(L, 97)) & (sat > 0.45)
        lit = np.median(a[lit_m], 0) if lit_m.any() else field
        core = np.median(a[L >= np.percentile(L, 99.95)], 0)
        rows.append((n, im, [("field", field), ("lit", lit), ("core", core)]))
    W = pad + sw + iw + sw + pad + 3 * (chip + 70) + pad
    H = pad + 70 + sum(im.height + 34 for _, im, _ in rows) + pad
    S = Image.new("RGB", (W, H), (244, 245, 247))
    d = ImageDraw.Draw(S)
    d.text((pad, pad), "Generated visuals vs brand swatches: #071B3E navy (left), #FFBF00 amber (right). "
                       "Chips: colours measured in each image.", fill=(7, 27, 62), font=f20)
    x = pad
    for lab, c in ref:
        d.rectangle([x, pad + 34, x + 28, pad + 58], fill=c, outline=(200, 200, 200))
        d.text((x + 34, pad + 39), lab, fill=(60, 66, 84), font=f15)
        x += 130
    y = pad + 70
    for n, im, chips in rows:
        h = im.height
        d.rectangle([pad, y, pad + sw - 1, y + h - 1], fill=NAVY)
        S.paste(im, (pad + sw, y))
        d.rectangle([pad + sw + iw, y, pad + sw + iw + sw - 1, y + h - 1], fill=AMBER)
        d.text((pad, y + h + 6), f"{n}", fill=(7, 27, 62), font=f15)
        cx = pad + sw + iw + sw + pad
        for lab, c in chips:
            c = tuple(int(round(v)) for v in c)
            d.rectangle([cx, y, cx + chip, y + chip], fill=c, outline=(200, 200, 200))
            d.text((cx, y + chip + 4), lab, fill=(60, 66, 84), font=f13)
            d.text((cx, y + chip + 20), "#%02X%02X%02X" % c, fill=(60, 66, 84), font=f13)
            cx += chip + 70
        y += h + 34
    S.save(QA / "brand-swatch-check.jpg", quality=90)


def manifest(names):
    from gen_scenes import SCENES
    lines = [
        "# Generated visuals (YellowForce)",
        "",
        "Made by `tools/gen_all.py` (engine `tools/gen_core.py`, compositions `tools/gen_scenes.py`).",
        "Our own work, rendered from code: no third-party images, no licence limits. Seeded, so a re-run gives the same files.",
        "",
        "Look (brand kit, 2026-10-26, round 1): long-exposure light trails in amber #FFBF00 with warm-white hot cores (#FFF3D1)",
        "on deep, moody navy: open dark fields about #051026 (averaging #040C1E), corners down to #020712, lifted back towards",
        "brand navy #071B3E where light scatters into the air; never neutral black. Photographic compositions (roads, tunnels,",
        "beams in haze, fields in every focus plane) rather than diagrams; lit haze gives the dark soft midtones.",
        "Very faint slate-blue (#777F98) out-of-focus particles add depth. HDR accumulation, hue-keeping filmic tone map,",
        "bloom (the wide part lifts the navy instead of tinting it), amber halation, film grain, vignette.",
        "Check: `qa/brand-swatch-check.jpg` (images between flat #071B3E and #FFBF00 swatches, measured colours).",
        "",
        "Round 2 (2026-10-26): the card grids alternate bright and dark like the reference. One card per row is high-key",
        "(light fills most of the frame, a warm-white core, like `cta`): Services 2, 3, 6 and Coverage endpoint, cloud,",
        "applications, data, governance, in a checkerboard. The others stay dark but were lifted (service-4, identity,",
        "ot-iot, network). Domain images keep the domain hero readable: the white title zone keeps at least 3:1 and the",
        "paragraph zone at least 4.5:1 against the brightest 5% of pixels once the hero scrim is applied.",
        "Home tiles 03 and 04 are full scenes now: `threat-phishing` (deepfakes, a stream and its copy) and",
        "`threat-ransomware` (a torrent piling into a bright wall). No icons.",
        "",
        "Round 3 (2026-10-26): `domain-ai-agents` is a murmuration of light now (was a faint dust smear, mean 23): a folded",
        "3D sheet of tiny agents arcing over the upper half and down the right third, dense warm-white folds where the",
        "sheet turns edge-on, stragglers and two small rogue clusters flying against the flow (mean 44). The centred hero",
        "title keeps navy behind it (white text at 10:1 or more) and the coverage card's top-left label band stays dark.",
        "`service-1` gained depth (two soft, out-of-focus deltas behind the sharp one, lit haze; was 91% near-black) and",
        "`service-5` more light in its stream and air. The photo family was regraded to sit nearer this set (see",
        "`assets/img/photo/MANIFEST.md`).",
        "",
        "Round 4 (2026-10-26): the darkest images were lifted without changing their shapes (additions use their own seeds,",
        "drawn after the original elements). `threat-swarm` (was mean 24, 73% near-black) gains an outer, out-of-focus shell of",
        "the same swarm through the top and bottom of the frame and a warm haze over the disc (mean about 39, 45% near-black).",
        "`threat-breach` (was 29, 72%) gains a deeper, soft layer of the funnelling field and a wider spray, with no extra light",
        "in the gap so the pinch stays tight (about 40, 51%). The four dark domain heroes now carry structure into the lower",
        "third under the centred title and sit at mean 35+: `domain-email` (soft near lanes rising from below into the same",
        "vanishing point), `domain-network` (a lower ring of softer nodes linked up into the graph), `domain-ot-iot` (rings turn",
        "all the way round under the axis), `domain-identity` (outer ridges fall off less, haze lit under the print). Hero text",
        "contrast stays well above 3:1 (title) and 4.5:1 (paragraph) with the hero scrim. The photo family was regraded to",
        "this set's near-black navy floor with muted slate mids (`assets/img/photo/MANIFEST.md`).",
        "",
        "Phone versions (2026-10-27, `tools/gen_mobile.py`; Axel: \"first image is a little blurry\"): phones fill tall frames",
        "with these 16:9 pictures by their height, and `sizes=\"100vw\"` gave an iPhone 15 the 1200 px hero stretched 3.7x.",
        "`NAME-m.webp` 2048x2560 (+ `-m-1536`, `-m-1024`) is the same scene rendered at phone resolution, cut 4:5 at the page's",
        "object-position (hero 50%, cta 28%, domain-* 50%), so a frame up to 4:5 shows the same pixels as before, sharp (the hero",
        "canvas still rides its streaks). The hero's phone render drops about 20 trails that zigzag where its field flips",
        "(a speck at 2400 px, a staircase at phone size). `NAME-sq.webp` 1200 (+ `-sq-800`) is the centre square a tile shows",
        "(domain-*, service-*). Served with `<picture>`: portrait under `(max-width: 1023px) and (max-aspect-ratio: 4/5)`",
        "(cta: 767px), squares under 1024px. Desktop files are untouched.",
        "",
        "Every image ships in three widths: `NAME.webp` (main), `NAME-1600.webp`, `NAME-800.webp`, WebP q82.",
        "For square and 4:5 images the main file is 1600 wide, so `NAME.webp` and `NAME-1600.webp` are the same picture.",
        "Suggested `srcset`: `NAME-800.webp 800w, NAME-1600.webp 1600w, NAME.webp <main width>w`.",
        "Most compositions keep the left and bottom-left calm for overlaid text; the hero keeps its bottom-left (headline) and bottom-right (status card) clean.",
        "",
        "| File (base name) | Aspect | Main size | Main KB | Slot | Description |",
        "|---|---|---|---|---|---|",
    ]
    for n in names:
        sc = SCENES[n]
        p = OUT / f"{n}.webp"
        w, h = Image.open(p).size
        kb = p.stat().st_size // 1024
        lines.append(f"| `{n}` | {aspect_label(w, h)} | {w}x{h} | {kb} | {sc['slot']} | {sc['desc']} |")
    lines += ["", "Regenerate: `/path/to/.venv/bin/python tools/gen_all.py [names] [--ss 2]` (numpy, scipy, opencv, pillow).", "",
              "- `about-2-320.webp`, `threat-swarm-320.webp`, `status-320.webp` (2026-10-26): 320 px downsizes of the full frames "
              "(PIL Lanczos, WebP q84) for the 32 px reason chips on Home, which scale the image up to about 2.6x. Same crop "
              "(object-position and scale stay in CSS).", ""]
    (OUT / "MANIFEST.md").write_text("\n".join(lines))


def run_parallel(names, ss, jobs):
    """One subprocess per image (keeps memory bounded, works where process pools cannot)."""
    import subprocess
    pending = list(names)
    running = []
    while pending or running:
        while pending and len(running) < jobs:
            n = pending.pop(0)
            running.append(subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--one", n, "--ss", str(ss)],
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
        for p in list(running):
            if p.poll() is not None:
                out = p.stdout.read()
                print("\n".join(l for l in out.splitlines() if "Warning" not in l and not l.startswith("  ")), flush=True)
                running.remove(p)
        time.sleep(0.2)


if __name__ == "__main__":
    from gen_scenes import ORDER
    args = sys.argv[1:]
    ss = 2
    jobs = 5
    if "--ss" in args:
        i = args.index("--ss"); ss = int(args[i + 1]); del args[i:i + 2]
    if "--jobs" in args:
        i = args.index("--jobs"); jobs = int(args[i + 1]); del args[i:i + 2]
    if "--one" in args:
        i = args.index("--one")
        name, size, dt = render_one(args[i + 1], ss)
        print(f"{name:22s} {size[0]}x{size[1]}  {dt:5.1f}s  {(OUT / (name + '.webp')).stat().st_size // 1024} KB")
        sys.exit(0)
    sheet_only = "--sheet-only" in args
    args = [a for a in args if a != "--sheet-only"]
    names = args or ORDER
    if not sheet_only:
        if jobs <= 1:
            for n in names:
                name, size, dt = render_one(n, ss)
                print(f"{name:22s} {size[0]}x{size[1]}  {dt:5.1f}s  {(OUT / (name + '.webp')).stat().st_size // 1024} KB",
                      flush=True)
        else:
            run_parallel(names, ss, jobs)
    done = [n for n in ORDER if (OUT / f"{n}.webp").exists()]
    sheet(done)
    manifest(done)
    if all((OUT / f"{n}.webp").exists() for n in SWATCH_NAMES):
        swatch_check()
    print("sheet + manifest:", len(done), "images")
