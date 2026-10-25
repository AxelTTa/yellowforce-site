#!/usr/bin/env python3
"""Put two screenshots side by side (same width, labeled, top-aligned) for visual QA.

Usage
  sidebyside.py LEFT.png RIGHT.png OUT.png --labels Vantra,YellowForce [--slice 900] [--diff]
      OUT.png               full composite (left | right [| diff])
      OUT-sliceNN.png       with --slice N: matching N px bands, pairwise, one file per band
  sidebyside.py --pairs qa/ref qa/ours qa/compare [--slice 900] [--diff] [--only home,about]
      Batch: every qa/ours/NAME-WIDTH-*.png that has a qa/ref twin (same file name, or the
      reference name from PAIR_MAP, e.g. coverage -> work) gets a composite in qa/compare/,
      full pages also get slices. Prints a mean-difference score per pair (0 = identical,
      higher = more different; only meaningful when layouts line up).

Options
  --width W     scale both to W px wide (default: the smaller of the two widths)
  --diff        add a third panel: per-pixel |left - right|, brightened (white = different)
  --no-full     with --slice, skip the full composite (long pages make big files)
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None

PAIR_MAP = {"coverage": "work"}  # our page name -> reference page name
HEADER_H = 44
GAP = 12
BG = (17, 17, 17)
FG = (245, 245, 240)
MUTED = (150, 150, 145)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def hatch(w, h):
    """Fill for 'no content here' (one page shorter than the other)."""
    im = Image.new("RGB", (w, h), (222, 222, 222))
    d = ImageDraw.Draw(im)
    for x in range(-h, w, 18):
        d.line([(x, 0), (x + h, h)], fill=(200, 200, 200), width=4)
    return im


def scale_to(im: Image.Image, width: int) -> Image.Image:
    im = im.convert("RGB")
    if im.width == width:
        return im
    h = round(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


def pad_to(im: Image.Image, h: int) -> Image.Image:
    if im.height >= h:
        return im
    out = hatch(im.width, h)
    out.paste(im, (0, 0))
    return out


def diff_panel(a: Image.Image, b: Image.Image) -> tuple[Image.Image, float]:
    h = max(a.height, b.height)
    A = np.asarray(pad_to(a, h), dtype=np.int16)
    B = np.asarray(pad_to(b, h), dtype=np.int16)
    d = np.abs(A - B).max(axis=2).astype(np.float32)
    score = float(d.mean())
    vis = np.clip(d * 3, 0, 255).astype(np.uint8)
    return Image.fromarray(vis, "L").convert("RGB"), score


def compose(panels: list[Image.Image], labels: list[str], subtitle: str = "") -> Image.Image:
    h = max(p.height for p in panels)
    W = sum(p.width for p in panels) + GAP * (len(panels) - 1)
    out = Image.new("RGB", (W, h + HEADER_H), BG)
    d = ImageDraw.Draw(out)
    f_big, f_small = font(20), font(14)
    x = 0
    for p, lab in zip(panels, labels):
        d.text((x + 14, 11), lab, fill=FG, font=f_big)
        if subtitle:
            tw = d.textlength(subtitle, font=f_small)
            d.text((x + p.width - tw - 14, 15), subtitle, fill=MUTED, font=f_small)
        out.paste(pad_to(p, h), (x, HEADER_H))
        x += p.width + GAP
    return out


def side_by_side(left: pathlib.Path, right: pathlib.Path, out: pathlib.Path, labels, slice_h=0,
                 width=None, diff=False, no_full=False) -> list[tuple[str, float | None]]:
    L, R = Image.open(left), Image.open(right)
    w = width or min(L.width, R.width)
    L, R = scale_to(L, w), scale_to(R, w)
    labels = list(labels)
    results = []
    out.parent.mkdir(parents=True, exist_ok=True)
    if not (slice_h and no_full):
        panels = [L, R]
        score = None
        if diff:
            dp, score = diff_panel(L, R)
            panels.append(dp)
        lab = labels + (["diff"] if diff else [])
        compose(panels, lab, f"{L.width}x{L.height} | {R.width}x{R.height}").save(out)
        results.append((str(out), score))
    if slice_h:
        stem = out.with_suffix("")
        for old in out.parent.glob(f"{stem.name}-slice[0-9][0-9].png"):
            old.unlink()
        H = max(L.height, R.height)
        for i, y in enumerate(range(0, H, slice_h), start=1):
            bands = []
            for im in (L, R):
                if y < im.height:
                    bands.append(pad_to(im.crop((0, y, w, min(y + slice_h, im.height))), min(slice_h, H - y)))
                else:
                    bands.append(hatch(w, min(slice_h, H - y)))
            score = None
            panels = list(bands)
            if diff:
                dp, score = diff_panel(bands[0], bands[1])
                panels.append(dp)
            lab = labels + (["diff"] if diff else [])
            p = pathlib.Path(f"{stem}-slice{i:02d}.png")
            compose(panels, lab, f"slice {i:02d}  y {y}-{min(y + slice_h, H)}").save(p)
            results.append((str(p), score))
    return results


NAME_RE = re.compile(r"^(?P<name>.+?)-(?P<width>\d{3,4})-(?P<kind>.+)\.png$")


def run_pairs(refdir: pathlib.Path, oursdir: pathlib.Path, outdir: pathlib.Path, a):
    only = set(x.strip() for x in a.only.split(",")) if a.only else None
    n = 0
    for f in sorted(oursdir.glob("*.png")):
        m = NAME_RE.match(f.name)
        if not m or "-slice" in m["kind"]:
            continue
        name, width, kind = m["name"], m["width"], m["kind"]
        if only and name not in only:
            continue
        ref_name = PAIR_MAP.get(name, name)
        ref = refdir / f"{ref_name}-{width}-{kind}.png"
        if not ref.exists():
            print(f"skip {f.name}: no reference {ref.name}")
            continue
        out = outdir / f"{name}-{width}-{kind}.png"
        sl = a.slice if kind == "full" else 0
        res = side_by_side(ref, f, out, a.labels.split(","), sl, a.width, a.diff, a.no_full and kind == "full")
        n += 1
        if a.diff:
            scores = [s for _p, s in res if s is not None]
            print(f"{out.name}: {len(res)} file(s), mean diff {sum(scores) / len(scores):.1f}" if scores else out.name)
        else:
            print(f"{out.name}: {len(res)} file(s)")
    if not n:
        sys.exit("no pairs found")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("left", nargs="?")
    ap.add_argument("right", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--labels", default="Vantra,YellowForce")
    ap.add_argument("--slice", type=int, default=0, help="also write N px tall pairwise slices (OUT-sliceNN.png)")
    ap.add_argument("--width", type=int, help="common width (default: smaller of the two)")
    ap.add_argument("--diff", action="store_true", help="add a difference panel and print scores")
    ap.add_argument("--no-full", action="store_true", help="with --slice: skip the full composite")
    ap.add_argument("--pairs", nargs=3, metavar=("REFDIR", "OURSDIR", "OUTDIR"))
    ap.add_argument("--only", help="--pairs: comma list of page names")
    a = ap.parse_args()
    if a.pairs:
        run_pairs(*(pathlib.Path(x) for x in a.pairs), a)
        return
    if not (a.left and a.right and a.out):
        ap.error("LEFT RIGHT OUT required (or --pairs)")
    res = side_by_side(pathlib.Path(a.left), pathlib.Path(a.right), pathlib.Path(a.out),
                       a.labels.split(","), a.slice, a.width, a.diff, a.no_full)
    for p, s in res:
        print(p if s is None else f"{p}  mean diff {s:.1f}")


if __name__ == "__main__":
    main()
