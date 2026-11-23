"""Turn a short video into a WebP frame sequence for scroll-scrubbing (pattern H).

Usage:
  python video_to_frames.py <video> <out_dir> [--frames 120] [--width 1600]
                            [--quality 72] [--mobile-width 900] [--start 0 --end 0]

Writes <out_dir>/f0001.webp ... and, with --mobile-width, <out_dir>/m/f0001.webp ...
Prints the frame count, size and the FRAMES config line for the page.

Budget: 100-150 frames at 1600 px, quality ~70, is usually 4-8 MB. That is above the
3 MB budget for other patterns, so lazy-load all but the first frame (see
references/patterns.md, H) and serve the smaller set to phones.
Needs ffmpeg on PATH and Pillow.
"""
import argparse, glob, os, shutil, subprocess, tempfile
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("out")
ap.add_argument("--frames", type=int, default=120)
ap.add_argument("--width", type=int, default=1600)
ap.add_argument("--mobile-width", type=int, default=0)
ap.add_argument("--quality", type=int, default=72)
ap.add_argument("--start", type=float, default=0, help="seconds to skip at the start")
ap.add_argument("--end", type=float, default=0, help="stop at this second (0 = video end)")
a = ap.parse_args()

dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "csv=p=0", a.video]).decode().strip())
end = a.end or dur
span = max(0.1, end - a.start)
tmp = tempfile.mkdtemp()
try:
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", str(a.start), "-t", str(span), "-i", a.video,
                           "-vf", f"fps={a.frames / span},scale={a.width}:-2:flags=lanczos", os.path.join(tmp, "%04d.png")])
    pngs = sorted(glob.glob(os.path.join(tmp, "*.png")))[:a.frames]
    sets = [(a.out, a.width)] + ([(os.path.join(a.out, "m"), a.mobile_width)] if a.mobile_width else [])
    for d, w in sets:
        os.makedirs(d, exist_ok=True)
        total = 0
        for i, p in enumerate(pngs, 1):
            im = Image.open(p).convert("RGB")
            if im.width != w:
                im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            f = os.path.join(d, f"f{i:04d}.webp")
            im.save(f, "WEBP", quality=a.quality, method=6)
            total += os.path.getsize(f)
        print(f"{d}: {len(pngs)} frames {im.width}x{im.height}, {total/1e6:.1f} MB ({total/len(pngs)/1024:.0f} KB/frame)")
    rel = os.path.basename(os.path.normpath(a.out))
    sub = '${innerWidth<860?"m/":""}' if a.mobile_width else ''
    print("\nconst FRAMES={count:%d, path:i=>`%s/%sf${String(i+1).padStart(4,'0')}.webp`};" % (len(pngs), rel, sub))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
