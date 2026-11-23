"""Make stand-in cutouts (transparent WebP) so a motion site runs before the real
photos exist: when there is no image tool, no credits, or you want to review the
choreography first. Swap in real cutouts later under the same file names.

Usage:
  python placeholders.py <out_dir> --preset explode                 # STAK template names
  python placeholders.py <out_dir> --preset slider --flavours cytryna:#f4d65a,malina:#f3a0b6
  python placeholders.py <out_dir> topbun:840x440:dome:#d9a35b  patty:840x360:slab:#5a3220  ...

Spec = name:WxH:shape:#colour   shapes: dome, bowl, slab, disc, blob, bottle, box, person
Each file is shaded (so depth reads) and labelled with its name, so nobody mistakes
it for a final asset. Sizes are 2x the CSS size, like prep_assets.py output.
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("specs", nargs="*")
ap.add_argument("--preset", choices=["explode", "slider"])
ap.add_argument("--flavours", default="cytryna:#f4d65a,malina:#f3a0b6,marakuja:#f6a45a")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

EXPLODE = [  # name, w, h, shape, colour  (matches LAYERS in template-scroll-explode.html)
    ("topbun", 840, 440, "dome", "#d99a4e"), ("lettuce", 880, 266, "slab", "#7fbf4d"),
    ("tomato", 840, 140, "slab", "#d8432f"), ("onion", 840, 200, "slab", "#a04a8c"),
    ("pickles", 840, 158, "slab", "#6f8f3a"), ("cheese", 840, 360, "slab", "#f2b632"),
    ("patty", 840, 360, "slab", "#5a3220"), ("bottombun", 840, 358, "bowl", "#d9a35b"),
]


def hexrgb(c):
    c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def font(px):
    try:
        return ImageFont.load_default(size=px)
    except TypeError:          # Pillow < 10.1
        return ImageFont.load_default()


def shape(w, h, kind, col, label):
    S = 2                                      # supersample for smooth edges
    W, H = w * S, h * S
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    m = int(min(W, H) * .04)
    if kind == "dome":
        d.pieslice([m, m, W - m, (H - m) * 2 - m], 180, 360, fill=255)
    elif kind == "bowl":
        d.rounded_rectangle([m, m, W - m, H * .45], radius=int(H * .2), fill=255)
        d.pieslice([m, -H + m * 2, W - m, H - m], 0, 180, fill=255)
    elif kind == "slab":
        d.rounded_rectangle([m, m, W - m, H - m], radius=int(min(W, H) * .45), fill=255)
    elif kind in ("disc", "blob"):
        d.ellipse([m, m, W - m, H - m], fill=255)
    elif kind == "bottle":
        nw = W * .32
        d.rounded_rectangle([(W - nw) / 2, m, (W + nw) / 2, H * .3], radius=int(nw * .2), fill=255)
        d.rounded_rectangle([m, H * .22, W - m, H - m], radius=int(W * .28), fill=255)
    elif kind == "person":
        hw = W * .3
        d.ellipse([(W - hw) / 2, m, (W + hw) / 2, m + hw * 1.2], fill=255)
        d.rounded_rectangle([W * .12, m + hw * 1.3, W * .88, H - m], radius=int(W * .3), fill=255)
    else:  # box
        d.rounded_rectangle([m, m, W - m, H - m], radius=int(min(W, H) * .08), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(S * .6))

    base = hexrgb(col)
    shade = Image.new("RGB", (W, H))
    sd = ImageDraw.Draw(shade)
    for y in range(H):                         # top light, bottom shadow
        k = 1.18 - 0.42 * (y / H)
        sd.line([(0, y), (W, y)], fill=tuple(min(255, int(v * k)) for v in base))
    hl = Image.new("L", (W, H), 0)             # soft specular highlight
    ImageDraw.Draw(hl).ellipse([W * .18, H * .08, W * .55, H * .4], fill=70)
    shade = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), shade, hl.filter(ImageFilter.GaussianBlur(W * .05)))
    out = shade.convert("RGBA"); out.putalpha(mask)
    out = out.resize((w, h), Image.LANCZOS)

    td = ImageDraw.Draw(out)
    f = font(max(14, min(w, h) // 7))
    tb = td.textbbox((0, 0), label, font=f)
    tx, ty = (w - (tb[2] - tb[0])) / 2, (h - (tb[3] - tb[1])) / 2
    ink = (255, 255, 255, 230) if sum(base) < 420 else (40, 28, 18, 220)
    td.text((tx, ty), label, font=f, fill=ink)
    return out


def save(name, im):
    p = os.path.join(a.out, name + ".webp")
    im.save(p, "WEBP", quality=86, method=6)
    print(f"{name:14s} {im.width}x{im.height}  css_h@{im.width//2}={im.height//2}  -> {p}")


jobs = []
if a.preset == "explode":
    jobs += EXPLODE
elif a.preset == "slider":
    for fl in a.flavours.split(","):
        n, _, c = fl.partition(":"); c = c or "#f4d65a"
        dark = "#" + "".join(f"{int(v * .72):02x}" for v in hexrgb(c))   # product must stand off its own field
        jobs += [(f"b-{n}", 344, 1300, "bottle", dark), (f"{n[:3]}-a", 560, 550, "blob", c), (f"{n[:3]}-b", 560, 536, "disc", dark)]
for s in a.specs:
    n, wh, kind, col = (s.split(":") + ["box", "#c8b8a0"])[:4]
    w, h = (int(v) for v in wh.lower().split("x"))
    jobs.append((n, w, h, kind, col))
if not jobs:
    raise SystemExit("Nothing to make. Use --preset explode|slider or name:WxH:shape:#colour specs.")

made = {}
for n, w, h, kind, col in jobs:
    im = shape(w, h, kind, col, n.upper())
    save(n, im); made[n] = im

if a.preset == "explode":                           # assembled hero = the layers stacked (like the template)
    tops = [150, 34, 24, 22, 22, 44, 100, 0]
    H = sum(tops) * 2 + made["bottombun"].height
    hero = Image.new("RGBA", (880, H), (0, 0, 0, 0))
    y, layers = 0, []
    for (n, *_), t in zip(EXPLODE, tops):
        layers.append((made[n], y)); y += t * 2
    for im, yy in reversed(layers):
        hero.alpha_composite(im, ((880 - im.width) // 2, yy))
    hero = hero.resize((1008, round(H * 1008 / 880)), Image.LANCZOS)
    save("burger", hero)
print("Placeholders only: say so in the hand-off and swap in real cutouts under the same names.")
