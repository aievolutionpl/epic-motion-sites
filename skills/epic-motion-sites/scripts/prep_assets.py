"""Crop transparent AI cutouts to their visible pixels, resize, and save as WebP.

Usage:
  python prep_assets.py <src_dir> <out_dir> [--width 840] [--css 420]
                        [--sheet sheet.png] [--bg "#b8461a"]

Prints: name  WxH  css_height  (height when shown at --css px wide).
Files whose name contains "hero" or "assembled" get width*1.2.
"""
import argparse, glob, os
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--width", type=int, default=840)
ap.add_argument("--css", type=int, default=420)
ap.add_argument("--max-height", type=int, default=1400, help="cap height for tall objects")
ap.add_argument("--quality", type=int, default=84)
ap.add_argument("--sheet"); ap.add_argument("--bg", default="#b8461a")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

done = []
for f in sorted(glob.glob(os.path.join(a.src, "*.png")) + glob.glob(os.path.join(a.src, "*.webp"))):
    name = os.path.splitext(os.path.basename(f))[0]
    im = Image.open(f).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if bb: im = im.crop(bb)
    w = int(a.width * (1.2 if ("hero" in name or "assembled" in name) else 1))
    h = round(im.height * w / im.width)
    if h > a.max_height:               # tall objects (bottles, people): cap by height instead
        h = a.max_height; w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    out = os.path.join(a.out, name + ".webp")
    im.save(out, "WEBP", quality=a.quality, method=6)
    done.append((name, im))
    print(f"{name:14s} {im.width}x{im.height}  css_h@{a.css}={round(a.css*im.height/im.width)}  {os.path.getsize(out)//1024}KB")

if a.sheet and done:
    cols, cw, ch = 3, 600, 320
    rows = (len(done) + cols - 1) // cols
    bg = tuple(int(a.bg.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    sheet = Image.new("RGB", (cols * cw, rows * ch), bg)
    for i, (_, im) in enumerate(done):
        t = im.copy(); t.thumbnail((cw - 20, ch - 20))
        sheet.paste(t, ((i % cols) * cw + 10, (i // cols) * ch + 10), t)
    sheet.save(a.sheet)
    print("sheet ->", a.sheet)
