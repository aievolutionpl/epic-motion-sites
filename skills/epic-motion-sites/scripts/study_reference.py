"""Turn a reference site's preview video into contact sheets you can look at.

Usage:
  python study_reference.py <url-or-file> <out_dir> [--frames 8] [--scenes]

<url> can be a direct .mp4/.webm, a local video file, or a page URL. For a page, the
script fetches the HTML and takes the first .mp4/.webm it finds; on motionsites.ai the
design pages are JS-rendered, so if nothing is found, open the page in the browser and
read `document.querySelector('video').currentSrc`, then pass that.

Writes:
  <name>-sheet.jpg    evenly spaced frames (the overall flow), read left-to-right
  <name>-scenes.jpg   with --scenes: one frame per hard cut / big change (the key beats)

Then write the choreography down before building: what moves, in which order,
how far, how fast, with which colours and type. Take patterns only, never assets.
Needs ffmpeg/ffprobe on PATH.
"""
import argparse, os, re, subprocess, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("url"); ap.add_argument("out")
ap.add_argument("--frames", type=int, default=8)
ap.add_argument("--scenes", action="store_true", help="also sheet the frames where the picture changes most")
ap.add_argument("--threshold", type=float, default=0.18, help="scene-change sensitivity for --scenes (lower = more)")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}

url = a.url
if os.path.exists(url):
    vid = url
    name = re.sub(r"[^a-z0-9-]", "", os.path.splitext(os.path.basename(url))[0].lower()) or "ref"
else:
    if not re.search(r"\.(mp4|webm)(\?|$)", url):
        html = urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read().decode("utf8", "ignore")
        m = re.search(r"https?://[^\"' ]+\.(?:mp4|webm)", html)
        if not m:
            raise SystemExit("No video found in page HTML - grab <video>.currentSrc in the browser and pass it directly.")
        url = m.group(0)
    name = re.sub(r"[^a-z0-9-]", "", os.path.basename(url.split("?")[0]).rsplit(".", 1)[0].lower()) or "ref"
    vid = os.path.join(a.out, name + os.path.splitext(url.split("?")[0])[1])
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r, open(vid, "wb") as f:
        f.write(r.read())

dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vid]).decode().strip())
cols = 4; rows = (a.frames + cols - 1) // cols
sheet = os.path.join(a.out, name + "-sheet.jpg")
subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", vid, "-vf",
                       f"fps={a.frames/dur},scale=480:-1,tile={cols}x{rows}", "-frames:v", "1", sheet])
print("video  ->", vid)
print("sheet  ->", sheet, f"({a.frames} frames over {dur:.1f}s, read left-to-right)")

if a.scenes:
    sc = os.path.join(a.out, name + "-scenes.jpg")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", vid, "-vf",
                           f"select='eq(n,0)+gt(scene,{a.threshold})',scale=480:-1,tile=4x3",
                           "-fps_mode", "vfr", "-frames:v", "1", sc])
    print("scenes ->", sc, "(first frame + each big change, up to 12; raise --threshold for fewer)")
