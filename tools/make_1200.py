#!/usr/bin/env python3
"""Adds a 1200 px wide variant (NAME-1200.webp) next to every image that ships in 800 / 1600 / main widths.

Phones at DPR 3 (390 px x 3 = 1170 px) used to get the 1600 file for full-width images: the 1200 file is about half
its bytes and looks the same there. build.py lists it in srcset when it exists. Same encoder settings as the rest of
the set (WebP q82, method 6; lower when the 1600 file was capped), resized from the largest file. Idempotent: existing -1200 files are kept unless --force.

    ../.venv/bin/python tools/make_1200.py [--force]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DIRS = [ROOT / "assets/img/gen", ROOT / "assets/img/photo"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    made = kept = 0
    for d in DIRS:
        for src in sorted(d.glob("*.webp")):
            stem = src.stem
            if stem.endswith(("-800", "-1200", "-1600", "-320")):
                continue
            if not (d / f"{stem}-1600.webp").exists():
                continue
            out = d / f"{stem}-1200.webp"
            if out.exists() and not a.force:
                kept += 1
                continue
            im = Image.open(src)
            w, h = im.size
            if w <= 1200:
                continue
            im = im.convert("RGB").resize((1200, round(h * 1200 / w)), Image.LANCZOS)
            # some 1600 files were saved under q82 to meet a weight cap: then step the quality down until the 1200
            # file is at most 60% of the 1600 one (its pixel share is 56%), so it is never the heavier choice
            cap = (d / f"{stem}-1600.webp").stat().st_size * 0.6
            for q in (82, 78, 74, 70, 66, 62):
                im.save(out, "WEBP", quality=q, method=6)
                if out.stat().st_size <= cap:
                    break
            made += 1
            print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB "
                  f"(1600: {(d / f'{stem}-1600.webp').stat().st_size // 1024} KB)")
    print(f"made {made}, kept {kept}")


if __name__ == "__main__":
    main()
