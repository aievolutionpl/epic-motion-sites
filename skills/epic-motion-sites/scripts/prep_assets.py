"""Crop transparent AI cutouts to their visible pixels, resize, save as WebP and
flag the cutouts that will look wrong on the page.

Usage:
  python prep_assets.py <src_dir> <out_dir> [--width 840] [--css 420] [--max-height 1400]
                        [--sheet sheet.png] [--bg "#b8461a"] [--key-bg] [--json sizes.json]

Prints: name  WxH  css_height  size   (css_height = height when shown at --css px wide;
use it as the layer `h` in the scroll-explode template).
Files whose name contains "hero" or "assembled" get width*1.2.

Flags (regenerate or fix these before building):
  OPAQUE    no transparency at all - the generator ignored "transparent background".
            Re-run with a background remover, or --key-bg for flat studio backgrounds.
  CUT OFF   the object touches the frame edge - part of it is missing.
  HALO      a light or dark fringe left by background removal.
  HEAVY     over 250 KB (400 KB for hero/assembled) - lower --width or --max-height.
  EMPTY     nothing left after --key-bg (the object was as light as the background).

--key-bg removes a flat, light studio background by flood-filling from the corners.
It is a fallback for when no real background remover is available, not a replacement.
"""
import argparse, glob, json, os
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--width", type=int, default=840)
ap.add_argument("--css", type=int, default=420)
ap.add_argument("--max-height", type=int, default=1400, help="cap height for tall objects")
ap.add_argument("--quality", type=int, default=84)
ap.add_argument("--sheet"); ap.add_argument("--bg", default="#b8461a")
ap.add_argument("--key-bg", action="store_true", help="flood-fill a flat light background to transparent")
ap.add_argument("--json", help="write {name:{w,h,css_h,kb}} here")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)


def key_background(im, tol=26):
    rgb = im.convert("RGB")
    W, H = rgb.size
    marker = (255, 0, 254)
    for xy in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0), (W // 2, H - 1)]:
        if rgb.getpixel(xy) != marker:
            ImageDraw.floodfill(rgb, xy, marker, thresh=tol)
    r, g, b = rgb.split()
    m = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v == 255 else 0),
                                                g.point(lambda v: 255 if v == 0 else 0)),
                            b.point(lambda v: 255 if v == 254 else 0))
    alpha = ImageChops.invert(m).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA"); out.putalpha(alpha)
    return out


def checks(im):
    flags = []
    A = im.getchannel("A")
    lo, hi = A.getextrema()
    if lo > 250:
        return ["OPAQUE"]
    if hi < 12:
        return ["EMPTY"]
    W, H = im.size
    bb = A.point(lambda v: 255 if v > 12 else 0).getbbox()
    pre_cropped = bb == (0, 0, W, H)    # bbox already = frame: cannot judge cut-offs
    edge = []
    for side, box in (("top", (0, 0, W, 2)), ("bottom", (0, H - 2, W, H)), ("left", (0, 0, 2, H)), ("right", (W - 2, 0, W, H))):
        strip = A.crop(box)
        solid = sum(strip.histogram()[201:])
        if solid > 0.04 * strip.width * strip.height:
            edge.append(side)
    if edge and not pre_cropped:
        flags.append("CUT OFF " + "/".join(edge))
    # fringe: semi-transparent edge pixels much lighter/darker than the opaque interior
    rgb = im.convert("RGB")
    ring = [rgb.getpixel((x, y)) for (x, y) in
            ((x, y) for y in range(0, H, max(1, H // 160)) for x in range(0, W, max(1, W // 160)))
            if 40 < A.getpixel((x, y)) < 200]
    core = [rgb.getpixel((x, y)) for (x, y) in
            ((x, y) for y in range(0, H, max(1, H // 60)) for x in range(0, W, max(1, W // 60)))
            if A.getpixel((x, y)) > 250]
    if len(ring) > 30 and core:
        lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
        d = sum(map(lum, ring)) / len(ring) - sum(map(lum, core)) / len(core)
        if abs(d) > 70:
            flags.append("HALO " + ("light" if d > 0 else "dark"))
    return flags


done, report, warned = [], {}, 0
files = sorted(sum((glob.glob(os.path.join(a.src, e)) for e in ("*.png", "*.webp", "*.jpg", "*.jpeg")), []))
for f in files:
    name = os.path.splitext(os.path.basename(f))[0]
    im = Image.open(f)
    if a.key_bg and im.convert("RGBA").getchannel("A").getextrema()[0] > 250:   # only opaque inputs
        im = key_background(im)
    im = im.convert("RGBA")
    flags = checks(im)
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if bb: im = im.crop(bb)
    w = int(a.width * (1.2 if ("hero" in name or "assembled" in name) else 1))
    h = round(im.height * w / im.width)
    if h > a.max_height:               # tall objects (bottles, people): cap by height instead
        h = a.max_height; w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    out = os.path.join(a.out, name + ".webp")
    im.save(out, "WEBP", quality=a.quality, method=6)
    kb = os.path.getsize(out) // 1024
    if kb > (400 if ("hero" in name or "assembled" in name) else 250): flags.append("HEAVY")
    done.append((name, im))
    css_h = round(a.css * im.height / im.width)
    report[name] = {"w": im.width, "h": im.height, "css_h": css_h, "kb": kb, "flags": flags}
    warned += bool(flags)
    print(f"{name:14s} {im.width}x{im.height}  css_h@{a.css}={css_h}  {kb}KB" + (f"   !! {', '.join(flags)}" if flags else ""))

if a.json:
    with open(a.json, "w") as fh: json.dump(report, fh, indent=2)
    print("sizes ->", a.json)

if a.sheet and done:
    cols, cw, ch = 3, 600, 340
    rows = (len(done) + cols - 1) // cols
    bg = tuple(int(a.bg.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    sheet = Image.new("RGB", (cols * cw, rows * ch), bg)
    d = ImageDraw.Draw(sheet)
    ink = (255, 255, 255) if sum(bg) < 380 else (30, 24, 18)
    for i, (n, im) in enumerate(done):
        t = im.copy(); t.thumbnail((cw - 20, ch - 40))
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(t, (x + (cw - t.width) // 2, y + 10), t)
        d.text((x + 10, y + ch - 22), n + ("  !! " + ", ".join(report[n]["flags"]) if report[n]["flags"] else ""), fill=ink)
    sheet.save(a.sheet)
    print("sheet ->", a.sheet, "(look at it on the brand colour)")
if warned:
    print(f"\n{warned} file(s) flagged. Regenerate or fix them before building.")
