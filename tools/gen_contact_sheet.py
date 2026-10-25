"""Build qa/all-images-contact-sheet.jpg: every generated and photo image on one sheet,
800 px variants scaled to one cell size, with the number of pages that use each image
(counted in src/). Run from site/:  ../.venv/bin/python tools/gen_contact_sheet.py
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SITE = Path(__file__).resolve().parent.parent
IMG = SITE / "assets" / "img"
OUT = SITE / "qa" / "all-images-contact-sheet.jpg"


def usage():
    uses = {}
    for f in (SITE / "src").rglob("*.html"):
        for m in set(re.findall(r"img/((?:gen|photo)/[a-z0-9-]+?)(?:-800|-1600)?\.webp", f.read_text())):
            uses.setdefault(m, set()).add(f)
    # the CTA partial is included on every page that ends with the band
    if "gen/cta" in uses:
        pages = [f for f in (SITE / "src" / "pages").rglob("*.html") if "<!-- include:cta -->" in f.read_text()]
        uses["gen/cta"] |= set(pages)
    return {k: len(v) for k, v in uses.items()}


def main():
    names = []
    for fam in ("gen", "photo"):
        for p in sorted((IMG / fam).glob("*-800.webp")):
            names.append(f"{fam}/{p.name[:-9]}")
    u = usage()
    cw, ch, pad, lab = 360, 240, 10, 22
    cols = 6
    rows = (len(names) + cols - 1) // cols
    S = Image.new("RGB", (cols * (cw + pad) + pad, rows * (ch + lab + pad) + pad), (244, 245, 247))
    d = ImageDraw.Draw(S)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    except Exception:
        font = ImageFont.load_default()
    for i, n in enumerate(names):
        im = Image.open(IMG / f"{n}-800.webp").convert("RGB")
        full = Image.open(IMG / f"{n}.webp")
        # cover-crop to the cell like the cards on the site
        r = max(cw / im.width, ch / im.height)
        t = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
        x0, y0 = (t.width - cw) // 2, (t.height - ch) // 2
        t = t.crop((x0, y0, x0 + cw, y0 + ch))
        x = pad + (i % cols) * (cw + pad)
        y = pad + (i // cols) * (ch + lab + pad)
        S.paste(t, (x, y))
        d.text((x, y + ch + 4), f"{n}  ({full.width}x{full.height})  used on {u.get(n, 0)}", fill=(7, 27, 62), font=font)
    S.save(OUT, quality=86)
    print(OUT, len(names), "images")


if __name__ == "__main__":
    main()
