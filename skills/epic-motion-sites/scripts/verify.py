"""Walk a motion site in a real headless browser, screenshot every key state
and report the bugs that are invisible in a single screenshot.

Usage:
  python verify.py <url> [--out shots] [--points 0,.2,.44,.7,1]
                   [--steps "go(0)" "go(1)" "go(2)"] [--mobile] [--reduced]

Scroll mode (default): finds the story section (#story, [data-story], or the
tallest section that contains a position:sticky element), scrolls to each
progress point, waits for the smoothed animation to settle, screenshots.

Step mode (--steps): for sliders / clicks. Runs each JS snippet on the page,
waits, screenshots. Use it for patterns B, C, F, G.

Always also shoots the first normal section after the story.

Reports:
  - console errors and failed requests (missing images!)
  - horizontal overflow (page wider than the viewport)
  - images that never loaded
  - text elements that run outside the viewport
Writes <out>/<viewport>-sheet.png, a contact sheet. LOOK AT IT.

Needs: pip install playwright && playwright install chromium
"""
import argparse, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("url")
ap.add_argument("--out", default="shots")
ap.add_argument("--points", default="0,.12,.25,.38,.5,.62,.75,.88,1")
ap.add_argument("--steps", nargs="*")
ap.add_argument("--mobile", action="store_true", help="also run 390x844")
ap.add_argument("--only-mobile", action="store_true")
ap.add_argument("--reduced", action="store_true", help="emulate prefers-reduced-motion")
ap.add_argument("--settle", type=int, default=1100, help="ms to wait per state")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

FIND_STORY = """() => {
  const pick = document.querySelector('#story,[data-story]');
  if (pick) return pick;
  let best=null, h=0;
  document.querySelectorAll('section,div').forEach(el=>{
    if (el.offsetHeight > h && el.offsetHeight > innerHeight*1.5 &&
        [...el.querySelectorAll('*')].some(c=>getComputedStyle(c).position==='sticky')) { best=el; h=el.offsetHeight; }
  });
  return best;
}"""

CHECKS = """() => {
  const out=[];
  const W=document.documentElement.clientWidth;
  if (document.documentElement.scrollWidth > W+1) out.push(`horizontal overflow: page is ${document.documentElement.scrollWidth}px wide, viewport ${W}px`);
  document.querySelectorAll('img').forEach(im=>{ if(im.complete && im.naturalWidth===0) out.push('image failed: '+im.getAttribute('src')); });
  const seen=el=>{ let o=1; for(let e=el;e&&e.nodeType===1;e=e.parentElement){ const s=getComputedStyle(e);
      if(s.display==='none'||s.visibility==='hidden') return 0; o*=+s.opacity; } return o; };
  document.querySelectorAll('h1,h2,h3,p,a,button').forEach(el=>{
    const r=el.getBoundingClientRect();
    if (r.width && r.height && seen(el)>0.5 && r.bottom>0 && r.top<innerHeight &&
        (r.right>W+2 || r.left<-2)) out.push(`text outside viewport: <${el.tagName.toLowerCase()}> "${el.innerText.slice(0,40)}"`);
  });
  return out;
}"""

def run(pw, name, vw, vh):
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=1,
                        reduced_motion="reduce" if a.reduced else "no-preference",
                        is_mobile=vw < 600, has_touch=vw < 600)
    pg = ctx.new_page()
    errors = []
    pg.on("console", lambda m: m.type == "error" and errors.append("console: " + m.text))
    pg.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    pg.on("requestfailed", lambda r: errors.append("request failed: " + r.url))
    pg.on("response", lambda r: r.status >= 400 and errors.append(f"HTTP {r.status}: {r.url}"))
    pg.goto(a.url, wait_until="networkidle")
    pg.add_style_tag(content="html{scroll-behavior:auto!important}")
    pg.wait_for_timeout(800)
    shots, findings = [], set()

    def snap(label):
        pg.wait_for_timeout(a.settle)
        f = os.path.join(a.out, f"{name}-{len(shots):02d}.png")
        pg.screenshot(path=f)
        shots.append((f, label))
        for x in pg.evaluate(CHECKS): findings.add(f"[{label}] {x}")

    if a.steps:
        for s in a.steps:
            pg.evaluate(f"() => {{ {s} }}"); snap(s)
        pg.evaluate("window.scrollTo(0, innerHeight)"); snap("below stage")
    else:
        story = pg.evaluate_handle(FIND_STORY)
        if story.evaluate("e => !!e"):
            top = story.evaluate("e => e.getBoundingClientRect().top + scrollY")
            span = story.evaluate("e => e.offsetHeight - innerHeight")
            for p in [float(x) for x in a.points.split(",")]:
                pg.evaluate(f"window.scrollTo(0, {top + span * p})"); snap(f"p={p:g}")
            pg.evaluate(f"window.scrollTo(0, {top + span + vh * 0.6})"); snap("after story")
        else:
            findings.add("no story section found (#story / [data-story] / sticky) - shooting page height steps")
            H = pg.evaluate("document.body.scrollHeight")
            for i in range(8):
                pg.evaluate(f"window.scrollTo(0,{H*i/8})"); snap(f"y={int(H*i/8)}")
    b.close()

    cols = 3 if vw > 600 else 5
    tw = 480 if vw > 600 else 220
    th = int(tw * vh / vw)
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (f, label) in enumerate(shots):
        im = Image.open(f).convert("RGB").resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(im, (x, y + 22)); d.text((x + 6, y + 5), label, fill="black")
    sp = os.path.join(a.out, f"{name}-sheet.png"); sheet.save(sp)
    print(f"\n== {name} {vw}x{vh}: {len(shots)} states -> {sp}")
    for e in sorted(set(errors)): print("  ERROR", e)
    for x in sorted(findings): print("  WARN ", x)
    if not errors and not findings: print("  OK - no automatic findings. Now read the sheet for overlaps and taste.")
    return len(errors) + len(findings)

with sync_playwright() as pw:
    n = 0
    if not a.only_mobile: n += run(pw, "desktop", 1440, 860)
    if a.mobile or a.only_mobile: n += run(pw, "mobile", 390, 844)
sys.exit(1 if n else 0)
