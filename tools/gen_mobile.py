#!/usr/bin/env python3
"""Phone versions of the generated visuals (Axel, 2026-10-27: "first image is a little blurry" on mobile).

Why: phones show the 16:9 pictures in tall frames that the picture fills by its height (object-fit: cover). With
sizes="100vw" an iPhone 15 (DPR 3) loaded the 1200 px file for the home hero and stretched it over 2508 device px of
height: 3.7x upscaled. A bigger 16:9 file would be mostly thrown away (a phone shows about a quarter of its width),
so this renders the same scene (gen_scenes.render: same seeds, same design coordinates, same grade) at a higher
output width and keeps only what the frame shows.

  portrait  NAME-m.webp 2048x2560 (4:5), NAME-m-1536.webp, NAME-m-1024.webp
            Full height of the 16:9 frame, placed like the page's object-position X on it: x0 = X * (W - 0.8 H).
            Shown with the same object-position, any frame up to 4:5 wide shows exactly the pixels it showed with
            the 16:9 file, only sharper. That keeps the home hero canvas (streaks.js maps HERO_FLOW / HERO_RIDGE with
            cover + 50% 50% on the 2400x1350 frame) riding the image's own streaks.
            Served by <picture><source media="(max-width: 1023px) and (max-aspect-ratio: 4/5)" sizes="80vh">
            (the CTA band: max-width 767px, it is framed at 28% on phones only).
            Tablet crop (round 2): cta also ships cta-t.webp (4:5 at 50%, the band's tablet framing), served to
            768-1023px portrait screens; the 404 ships threat-breach-m.webp 2408x3440 (+ -m-2016, -m-1536, -m-1120), 7:10
            at 50%: the page grows it 1.28x from the top (legal.css) and streaks.js reads that transform for the
            pinch, so the crop keeps the square's geometry (full height, centred: any frame up to 7:10 shows the
            same pixels) and is taller to stay at 1 px per device px or more after the zoom (1.06 on an iPhone 15).
  square    NAME-sq.webp 1200x1200, NAME-sq-800.webp: the centre square of a 16:9 or 4:3 picture, which is all a
            tile (1:1 at every width) shows. Rendered at the main file's size and cropped, so it is the same pixels
            as the desktop file. Served to tiles under 768px.

    ../.venv/bin/python tools/gen_mobile.py                 # every job below
    ../.venv/bin/python tools/gen_mobile.py hero cta        # some scenes (every kind listed for them)
  ops       NAME-t.webp (+ NAME-t-<w>.webp): tablet crop of a domain page's "What we do." band, see OPS_T (round 3).

    options: --kind portrait|tablet|tall|square|ops, --ss 2, --jobs 2 (a portrait or 404 render peaks near 10 GB at ss 2;
             the endpoint ops render, 4523x3392, near 13 GB: run ops with --jobs 1)
"""
from __future__ import annotations

import math
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE.parent / "assets" / "img" / "gen"

ASPECT = 0.8                 # portrait crop, width / height (4:5)
P_H = 2560                   # portrait main height: 852 px tall iPhone 15 frame (836 css) x DPR 3 = 2508
P_SIZES = (2560, 1920, 1280)  # heights: -m (2048 wide), -m-1536, -m-1024
SQ_SIZES = (1200, 800)       # 372 css tile x DPR 3 = 1116
Q = 82
MAX_KB = {"m": 350, "sq": 160}

DOMAINS = ["domain-network", "domain-endpoint", "domain-cloud", "domain-identity", "domain-email",
           "domain-applications", "domain-data", "domain-ai-agents", "domain-ot-iot", "domain-governance"]
SERVICES = [f"service-{i}" for i in range(1, 7)]

# name -> {kind: horizontal object-position the page uses on phones}
JOBS = {"hero": {"portrait": 0.5}, "cta": {"portrait": 0.28, "tablet": 0.5}, "threat-breach": {"tall": 0.5}}
for _n in DOMAINS:
    JOBS[_n] = {"portrait": 0.5, "square": 0.5}
for _n in SERVICES:
    JOBS[_n] = {"square": 0.5}

# scene flags for the phone render only (portrait kind; desktop and square files keep the scene as it is).
# domain-applications: the flaring line of code sat right under the centred phone title (critic round 2); row 34 puts
# it at about 75 to 80% of the frame height, below the copy on every phone (see gen_scenes.domain_applications).
PORTRAIT_FLAGS = {"domain-applications": {"flaw_row": 34}}

# 404 (tall): 7:10, served under (max-aspect-ratio: 7/10), so the frame is never wider than the crop. The page scales
# it 1.28x from the top (legal.css): 841 css x 1.28 x 3 = 3230 device px tall on an iPhone 15. Round 2 critic: the
# 2880 file was still 0.89 there, so the main file is 3440 tall (2408 wide, exactly 7:10): 1.06 on an iPhone 15,
# 1.13 on a Pixel 7. The 2880 one stays as -m-2016 for screens that need less.
TALL_ASPECT = 0.7
TALL_SIZES = (3440, 2880, 2194, 1600)  # heights: -m (2408 wide), -m-2016, -m-1536, -m-1120

MAX_KB["tall"] = 560

# Tablet crops of the domain pages' "What we do." band (critic round 3). At 768-1023 the band is a portrait frame
# (750x901 css at 768x1024, 88svh tall) that the picture fills by its height, then grows by the page's --ops-zoom
# (endpoint 1.6): the desktop files were 0.62 to 0.89 px per device px there (0.54 to 0.77 on an iPad Air).
# NAME-t.webp is the same scene rendered taller and cut to 9:10, full height, at the page's desktop --ops-pos X
# (x0 = X * (W - 0.9 H)): any frame up to 9:10 wide (every 768-1023 screen up to 4:5; the widest is 0.89 at 4:5)
# shows exactly the pixels it showed with the desktop file, after the same object-position and zoom, only sharper.
# Square and 4:5 pictures keep their whole frame (the crop is capped at the picture's own width): threat-breach-t is
# also the 404's tablet file (any tablet aspect: a square covers landscape frames too).
# Main height = 1060 css (88svh on an 834x1194 iPad Pro 11) x zoom x DPR 2; the second size covers 768x1024 (901 css).
OPS_ASPECT = 0.9
OPS_T = {  # name: (--ops-pos X on its page, heights (main, smaller), crop aspect)
    "service-3": (0.0, (3392, 2880), OPS_ASPECT),    # endpoint, zoom 1.6
    "service-1": (0.6, (2440, 2080), OPS_ASPECT),    # network, zoom 1.15
    "about-1": (0.8, (2440, 2080), OPS_ASPECT),      # cloud, zoom 1.15
    "service-5": (0.0, (2440, 2080), OPS_ASPECT),    # data, zoom 1.15
    "hero": (0.5, (2120, 1808), OPS_ASPECT),         # applications
    "reel-poster": (0.5, (2120, 1808), OPS_ASPECT),  # ot-iot
    "about-3": (0.5, (2120, 1808), OPS_ASPECT),      # governance
    "threat-swarm": (0.5, (2160, 1800), 1.0),        # ai-agents (square, whole)
    "threat-breach": (0.5, (2560, 2048), 1.0),       # identity + 404 (square, whole; 404 frame is 100svh tall)
    "contact": (0.0, (2700, 2440), 1.0),             # email, zoom 1.3 (4:5, whole)
}
for _n in OPS_T:
    JOBS.setdefault(_n, {})["ops"] = OPS_T[_n][0]
MAX_KB["t"] = 900


def _save(img: Image.Image, path: Path, cap_kb: int, q0: int = Q) -> int:
    """WebP, method 6; steps the quality down (to 70) until the file fits its cap. Returns the quality used."""
    q = q0
    img.save(path, "WEBP", quality=q, method=6)
    while path.stat().st_size > cap_kb * 1024 and q > 70:
        q -= 3
        img.save(path, "WEBP", quality=q, method=6)
    return q


def portrait(name: str, pos: float, ss: int = 2, suffix: str = "-m", sizes=P_SIZES, cap: str = "m",
             aspect: float = ASPECT) -> list[str]:
    from gen_scenes import SCENES, render
    dw, dh = SCENES[name]["size"]
    out_h = sizes[0]
    out_w = int(math.ceil(out_h * dw / dh))
    flags = PORTRAIT_FLAGS.get(name, {}) if suffix == "-m" else {}
    big = Image.fromarray(render(name, out_w=out_w, ss=ss, smooth_trails=True, **flags))
    W, H = big.size
    aspect = min(aspect, W / H)   # a crop never wider than the picture (ops: square and 4:5 pictures stay whole)
    cw = round(aspect * H)
    x0 = round(pos * (W - cw))
    crop = big.crop((x0, 0, x0 + cw, H))
    del big
    if crop.size != (round(aspect * out_h), out_h):
        crop = crop.resize((round(aspect * out_h), out_h), Image.LANCZOS)
    done = []
    q = _save(crop, OUT / f"{name}{suffix}.webp", MAX_KB[cap])
    done.append(f"{name}{suffix}.webp {crop.size[0]}x{crop.size[1]} q{q} {(OUT / f'{name}{suffix}.webp').stat().st_size // 1024}KB")
    for h in sizes[1:]:
        w = round(aspect * h)
        p = OUT / f"{name}{suffix}-{w}.webp"
        crop.resize((w, h), Image.LANCZOS).save(p, "WEBP", quality=q, method=6)
        done.append(f"{p.name} {p.stat().st_size // 1024}KB")
    return done


def square(name: str, pos: float, ss: int = 2) -> list[str]:
    from gen_scenes import render
    big = Image.fromarray(render(name, ss=ss))   # the main file's own size: same pixels as the desktop picture
    W, H = big.size
    side = min(W, H)
    x0 = round(pos * (W - side))
    y0 = (H - side) // 2
    sq = big.crop((x0, y0, x0 + side, y0 + side))
    done = []
    main = sq.resize((SQ_SIZES[0],) * 2, Image.LANCZOS)
    q = _save(main, OUT / f"{name}-sq.webp", MAX_KB["sq"])
    done.append(f"{name}-sq.webp {SQ_SIZES[0]} q{q} {(OUT / f'{name}-sq.webp').stat().st_size // 1024}KB")
    for s in SQ_SIZES[1:]:
        p = OUT / f"{name}-sq-{s}.webp"
        sq.resize((s, s), Image.LANCZOS).save(p, "WEBP", quality=q, method=6)
        done.append(f"{p.name} {p.stat().st_size // 1024}KB")
    return done


def run_one(name: str, kind: str, ss: int) -> None:
    t = time.time()
    if kind == "portrait":
        out = portrait(name, JOBS[name][kind], ss)
    elif kind == "tablet":
        out = portrait(name, JOBS[name][kind], ss, suffix="-t")
    elif kind == "tall":
        out = portrait(name, JOBS[name][kind], ss, sizes=TALL_SIZES, cap="tall", aspect=TALL_ASPECT)
    elif kind == "ops":
        pos, heights, aspect = OPS_T[name]
        out = portrait(name, pos, ss, suffix="-t", sizes=heights, cap="t", aspect=aspect)
    else:
        out = square(name, JOBS[name][kind], ss)
    print(f"{name:20s} {kind:8s} {time.time() - t:5.1f}s  " + " | ".join(out), flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    ss, jobs, kinds = 2, 2, ("portrait", "tablet", "tall", "square", "ops")
    if "--ss" in args:
        i = args.index("--ss"); ss = int(args[i + 1]); del args[i:i + 2]
    if "--jobs" in args:
        i = args.index("--jobs"); jobs = int(args[i + 1]); del args[i:i + 2]
    if "--kind" in args:
        i = args.index("--kind"); kinds = (args[i + 1],); del args[i:i + 2]
    if "--one" in args:
        i = args.index("--one")
        run_one(args[i + 1], args[i + 2], ss)
        sys.exit(0)
    names = args or list(JOBS)
    todo = [(n, k) for n in names for k in kinds if k in JOBS.get(n, {})]
    # one subprocess per image keeps memory bounded (a portrait render peaks near 9 GB at ss 2)
    running: list[subprocess.Popen] = []
    while todo or running:
        while todo and len(running) < jobs:
            n, k = todo.pop(0)
            running.append(subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--one", n, k, "--ss", str(ss)],
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
        for p in list(running):
            if p.poll() is not None:
                print("\n".join(l for l in p.stdout.read().splitlines() if "Warning" not in l), flush=True)
                running.remove(p)
        time.sleep(0.2)
