"""Walk a motion site in a real headless browser, screenshot every key state
and report the bugs that are invisible in a single screenshot.

Usage:
  python verify.py <url> [--out shots] [--points 0,.2,.44,.7,1]
                   [--steps "go(0)" "go(1)" "go(2)"] [--mobile] [--only-mobile]
                   [--reduced] [--settle 1100] [--json report.json]

Scroll mode (default): finds the story section (#story, [data-story], or the
tallest section that contains a position:sticky element), scrolls to each
progress point, waits for the smoothed animation to settle, screenshots.

Step mode (--steps): for sliders / clicks. Runs each JS snippet on the page,
waits, screenshots. Use it for patterns B, C, F, G.

Always also shoots the first normal section after the story.

ERROR (must fix):
  - console errors, page errors, failed requests, HTTP 4xx/5xx (missing images!)
WARN (fix, or justify in the hand-off):
  - horizontal overflow (page wider than the viewport)
  - images that never loaded
  - visible text that runs outside the viewport
  - visible text overlapping other visible text   (skip with aria-hidden / data-verify-ignore)
  - low contrast of visible text on the rendered frame (approximate, sampled)
  - product images colliding with a transparent fixed nav
  - page weight over budget, single images over 500 KB
  - missing basics: <html lang>, viewport meta, <title>, img alt, unnamed buttons/links,
    no prefers-reduced-motion handling anywhere in the page
INFO (read, no action required):
  - long tasks, layout shift (CLS), meta description / og:image presence

Writes <out>/<viewport>-sheet.png, a contact sheet. LOOK AT IT: no script can
judge ghosting, rhythm or taste.

Needs: pip install playwright pillow && playwright install chromium
If Chromium is installed elsewhere, set CHROMIUM_PATH=/path/to/chrome.
"""
import argparse, glob, json, os, statistics, sys
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
ap.add_argument("--budget-mb", type=float, default=3.0, help="total page weight budget")
ap.add_argument("--no-contrast", action="store_true", help="skip the sampled contrast check")
ap.add_argument("--json", help="also write a machine-readable report here")
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

# Runs at every state. Returns {warn:[...], text:[...boxes for contrast...]}
CHECKS = """() => {
  const warn=[], W=document.documentElement.clientWidth, H=innerHeight;
  if (document.documentElement.scrollWidth > W+1) warn.push(`horizontal overflow: page is ${document.documentElement.scrollWidth}px wide, viewport ${W}px`);
  document.querySelectorAll('img').forEach(im=>{ if(im.complete && im.naturalWidth===0) warn.push('image failed: '+im.getAttribute('src')); });
  const seen=el=>{ let o=1; for(let e=el;e&&e.nodeType===1;e=e.parentElement){ const s=getComputedStyle(e);
      if(s.display==='none'||s.visibility==='hidden') return 0; o*=+s.opacity; } return o; };
  const ignored=el=>{ if(el.closest('[aria-hidden="true"],[data-verify-ignore],script,style,noscript,svg')) return true;
    for(let x=el;x&&x!==document.body;x=x.parentElement){ const r=x.getBoundingClientRect();   /* .sr-only text */
      if((r.width<=2||r.height<=2)&&getComputedStyle(x).overflow!=='visible') return true; }
    return false; };

  /* text boxes: one entry per element that owns text nodes, with its tight line rects */
  const groups=new Map();
  const tw=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  for(let n; (n=tw.nextNode());){ if(n.textContent.trim().length<2) continue;
    const el=n.parentElement; if(!el||ignored(el)) continue;
    if(!groups.has(el)) groups.set(el,[]); groups.get(el).push(n); }
  const boxes=[], rg=document.createRange();
  groups.forEach((nodes,el)=>{
    const op=seen(el); if(op<.5) return;
    const rects=[];
    nodes.forEach(n=>{ rg.selectNodeContents(n); for(const q of rg.getClientRects()) if(q.width>1&&q.height>1) rects.push({l:q.left,t:q.top,r:q.right,b:q.bottom}); });
    if(!rects.length) return;
    const onScreen=rects.filter(q=>q.b>0&&q.t<H);
    if(!onScreen.length) return;
    const txt=(el.innerText||el.textContent).trim().replace(/\\s+/g,' ').slice(0,40);
    if(onScreen.some(q=>q.r>W+2||q.l<-2)) warn.push(`text outside viewport: <${el.tagName.toLowerCase()}> "${txt}"`);
    const cs=getComputedStyle(el);
    boxes.push({el,rects:onScreen,txt,op,color:cs.color,size:parseFloat(cs.fontSize),weight:+cs.fontWeight||400});
  });

  /* text on text. Content-area rects include ascender/descender room, so tight display
     leading would always "overlap"; compare only the glyph band (middle 50% of each line). */
  const area=q=>Math.max(0,q.r-q.l)*Math.max(0,q.b-q.t);
  const inter=(p,q)=>area({l:Math.max(p.l,q.l),t:Math.max(p.t,q.t),r:Math.min(p.r,q.r),b:Math.min(p.b,q.b)});
  const core=q=>{const h=q.b-q.t; return {l:q.l+2,r:q.r-2,t:q.t+h*.25,b:q.b-h*.25};};
  for(let i=0;i<boxes.length;i++) for(let j=i+1;j<boxes.length;j++){
    const A=boxes[i],B=boxes[j];
    if(A.el.contains(B.el)||B.el.contains(A.el)) continue;
    let hit=false;
    for(const p0 of A.rects){ const p=core(p0); for(const q0 of B.rects){ const q=core(q0), x=inter(p,q);
      if(x>0.25*Math.min(area(p),area(q))&&x>40){hit=true;break;} } if(hit)break; }
    if(hit) warn.push(`text overlaps text: "${A.txt}" x "${B.txt}"`);
  }

  /* product images under a transparent fixed nav */
  const nav=[...document.querySelectorAll('nav,header')].find(e=>['fixed','sticky'].includes(getComputedStyle(e).position));
  if(nav){
    const bg=getComputedStyle(nav).backgroundColor, m=bg.match(/[\\d.]+/g)||[0,0,0,0];
    const alpha=bg.startsWith('rgba')?+m[3]:(bg==='transparent'?0:1);
    const nr=nav.getBoundingClientRect();
    if(alpha<.3) document.querySelectorAll('img').forEach(im=>{
      if(nav.contains(im)||ignored(im)||seen(im)<.5) return;
      const r=im.getBoundingClientRect(); if(r.width<60) return;
      const pad=0.12*Math.min(r.width,r.height);             /* cutouts have soft margins */
      const ov=Math.min(r.bottom-pad,nr.bottom)-Math.max(r.top+pad,nr.top);
      const ovx=Math.min(r.right,nr.right)-Math.max(r.left,nr.left);
      if(ov>8&&ovx>40) warn.push(`image under transparent nav: ${im.getAttribute('src')}`);
    });
  }
  return {warn, text: boxes.map(b=>({rects:b.rects,txt:b.txt,op:b.op,color:b.color,size:b.size,weight:b.weight}))};
}"""

STATIC = """() => {
  const warn=[], info=[];
  if(!document.documentElement.lang) warn.push('missing <html lang="..">');
  if(!document.querySelector('meta[name=viewport]')) warn.push('missing viewport meta');
  if(!document.title.trim()) warn.push('missing <title>');
  if(!document.querySelector('meta[name=description]')) info.push('no meta description (add one before deploy)');
  if(!document.querySelector('meta[property="og:image"]')) info.push('no og:image (link previews will be blank)');
  document.querySelectorAll('img:not([alt])').forEach(im=>warn.push('img without alt: '+im.getAttribute('src')));
  document.querySelectorAll('a,button').forEach(el=>{
    const name=(el.innerText||'').trim()||el.getAttribute('aria-label')||el.getAttribute('title')||
               [...el.querySelectorAll('img[alt]')].map(i=>i.alt).join('');
    if(!name && getComputedStyle(el).display!=='none') warn.push(`unnamed <${el.tagName.toLowerCase()}> (add text or aria-label): ${el.outerHTML.slice(0,60)}`);
  });
  let src=[...document.scripts].map(s=>s.textContent).join('\\n');
  for(const sh of document.styleSheets){ try{ for(const r of sh.cssRules) src+=r.cssText; }catch(e){} }
  if(!/prefers-reduced-motion/.test(src)) warn.push('no prefers-reduced-motion handling found (snap the smoothed value, stop idle motion/autoplay)');
  return {warn, info};
}"""

PERF = """() => {
  const res=performance.getEntriesByType('resource').map(e=>({u:e.name,b:e.encodedBodySize||e.transferSize||0,t:e.initiatorType}));
  const nav=performance.getEntriesByType('navigation')[0];
  const total=res.reduce((s,r)=>s+r.b,0)+(nav?nav.encodedBodySize||0:0);
  return {total, heavy:res.sort((x,y)=>y.b-x.b).slice(0,5), lt:window.__lt||[], cls:window.__cls||0};
}"""

INIT = """
window.__lt=[]; window.__cls=0;
try{ new PerformanceObserver(l=>l.getEntries().forEach(e=>__lt.push(Math.round(e.duration)))).observe({type:'longtask',buffered:true}); }catch(e){}
try{ new PerformanceObserver(l=>l.getEntries().forEach(e=>{ if(!e.hadRecentInput) __cls+=e.value; })).observe({type:'layout-shift',buffered:true}); }catch(e){}
"""


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def contrast(c1, c2):
    l1, l2 = sorted((lum(c1), lum(c2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def parse_rgb(s):
    v = [float(x) for x in s[s.index("(") + 1:s.index(")")].replace("/", ",").replace(" ", ",").split(",") if x]
    return v[:3], (v[3] if len(v) > 3 else 1.0)


def check_contrast(png, boxes, label, sink):
    im = Image.open(png).convert("RGB")
    W, H = im.size
    px = im.load()
    for b in boxes:
        if b["op"] < 0.9:                       # mid-fade: judge the settled state instead
            continue
        off = max(4, int(b["size"] * 0.3))
        ring = []
        for q in b["rects"]:
            l, t, r, bt = int(q["l"]) - off, int(q["t"]) - off, int(q["r"]) + off, int(q["b"]) + off
            stepx, stepy = max(2, (r - l) // 40), max(2, (bt - t) // 12)
            for x in range(l, r, stepx):
                for y in (t, bt):
                    if 0 <= x < W and 0 <= y < H: ring.append(px[x, y])
            for y in range(t, bt, stepy):
                for x in (l, r):
                    if 0 <= x < W and 0 <= y < H: ring.append(px[x, y])
        if len(ring) < 8:
            continue
        bg = [statistics.median(p[i] for p in ring) for i in range(3)]
        fg, alpha = parse_rgb(b["color"])
        alpha *= b["op"]
        fg = [f * alpha + g * (1 - alpha) for f, g in zip(fg, bg)]
        cr = contrast(fg, bg)
        large = b["size"] >= 24 or (b["size"] >= 18.6 and b["weight"] >= 700)
        need = 3.0 if large else 4.5
        if cr < need:
            key = b["txt"]
            if key not in sink or sink[key][0] > cr:
                sink[key] = (cr, need, label)


def launch(pw):
    try:
        return pw.chromium.launch()
    except Exception as e:
        cands = [os.environ.get("CHROMIUM_PATH")] + sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
        for c in cands:
            if c and os.path.exists(c):
                return pw.chromium.launch(executable_path=c)
        raise SystemExit(f"Could not start Chromium ({e}).\nRun: playwright install chromium   or set CHROMIUM_PATH.")


REPORT = {}


def run(pw, name, vw, vh):
    b = launch(pw)
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=1,
                        reduced_motion="reduce" if a.reduced else "no-preference",
                        is_mobile=vw < 600, has_touch=vw < 600)
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    errors = []
    pg.on("console", lambda m: m.type == "error" and errors.append("console: " + m.text))
    pg.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    pg.on("requestfailed", lambda r: errors.append("request failed: " + r.url))
    pg.on("response", lambda r: r.status >= 400 and errors.append(f"HTTP {r.status}: {r.url}"))
    pg.goto(a.url, wait_until="networkidle")
    pg.add_style_tag(content="html{scroll-behavior:auto!important}")
    pg.wait_for_timeout(800)
    shots, findings, info, low = [], set(), [], {}

    st = pg.evaluate(STATIC)
    findings.update(st["warn"]); info += st["info"]

    def snap(label):
        pg.wait_for_timeout(a.settle)
        f = os.path.join(a.out, f"{name}-{len(shots):02d}.png")
        pg.screenshot(path=f)
        shots.append((f, label))
        r = pg.evaluate(CHECKS)
        for x in r["warn"]: findings.add(f"[{label}] {x}")
        if not a.no_contrast: check_contrast(f, r["text"], label, low)

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

    # walk to the bottom so lazy images count toward the weight
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(600)
    perf = pg.evaluate(PERF)
    b.close()

    for txt, (cr, need, label) in sorted(low.items(), key=lambda kv: kv[1][0]):
        findings.add(f"[{label}] low contrast ~{cr:.1f}:1 (needs {need:g}): \"{txt}\"")
    mb = perf["total"] / 1e6
    if mb > a.budget_mb:
        findings.add(f"page weight {mb:.1f} MB > budget {a.budget_mb:g} MB")
    for r in perf["heavy"]:
        if r["t"] == "img" and r["b"] > 500_000:
            findings.add(f"heavy image {r['b']//1024} KB: {r['u'].split('/')[-1]} (resize / WebP / cap height)")
    info.append(f"page weight {mb:.2f} MB; heaviest: " + ", ".join(f"{r['u'].split('/')[-1][:28]} {r['b']//1024}KB" for r in perf["heavy"][:3]))
    if perf["lt"]: info.append(f"long tasks: {len(perf['lt'])} (max {max(perf['lt'])} ms)")
    info.append(f"CLS {perf['cls']:.3f}" + ("  <- layout shifts; set width/height on images, reserve space for fonts" if perf["cls"] > 0.1 else ""))

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
    print(f"\n== {name} {vw}x{vh}{' reduced-motion' if a.reduced else ''}: {len(shots)} states -> {sp}")
    for e in sorted(set(errors)): print("  ERROR", e)
    for x in sorted(findings): print("  WARN ", x)
    for x in info: print("  info ", x)
    if not errors and not findings: print("  OK - no automatic findings. Now read the sheet for ghosting, rhythm and taste.")
    REPORT[name] = {"sheet": sp, "errors": sorted(set(errors)), "warnings": sorted(findings), "info": info,
                    "shots": [{"file": f, "state": l} for f, l in shots]}
    return len(errors) + len(findings)


with sync_playwright() as pw:
    n = 0
    if not a.only_mobile: n += run(pw, "desktop", 1440, 860)
    if a.mobile or a.only_mobile: n += run(pw, "mobile", 390, 844)
if a.json:
    with open(a.json, "w", encoding="utf8") as f: json.dump(REPORT, f, indent=2, ensure_ascii=False)
    print("report ->", a.json)
sys.exit(1 if n else 0)
