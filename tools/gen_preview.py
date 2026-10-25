"""Quick preview renders: gen_preview.py NAME [NAME...] [--w 1200] [--ss 2]
Writes qa/gen-preview/NAME.jpg"""
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from gen_scenes import SCENES, render  # noqa: E402

args = sys.argv[1:]
w = 1200
ss = 2
if "--w" in args:
    i = args.index("--w"); w = int(args[i + 1]); del args[i:i + 2]
if "--ss" in args:
    i = args.index("--ss"); ss = int(args[i + 1]); del args[i:i + 2]
names = args or list(SCENES)
import os
out = Path(os.environ.get("GEN_PREVIEW_DIR", str(Path(__file__).parent.parent / "qa" / "gen-preview")))
out.mkdir(parents=True, exist_ok=True)
for n in names:
    t = time.time()
    dw, dh = SCENES[n]["size"]
    ow = w if dw >= dh else int(w * dw / dh)
    img = render(n, out_w=ow, ss=ss)
    Image.fromarray(img).save(out / f"{n}.jpg", quality=92)
    print(n, img.shape, f"{time.time()-t:.1f}s", flush=True)
