# Scroll engine (vanilla, no libraries)

Every pattern shares this core. It is about 50 lines, with no GSAP or Lenis, so there are no
dependency or licence questions. It runs at 60–120 fps when you animate only `transform`,
`opacity`, `filter` and background colour.

## Markup
```html
<section id="story" style="height:520vh">          <!-- scroll length = how long the story lasts -->
  <div class="stage" id="stage">                     <!-- position:sticky; top:0; height:100vh; height:100svh; overflow:hidden -->
    <div class="panel" id="pHero">…</div>            <!-- text panels, position:absolute -->
    <div class="obj" id="obj">…</div>                <!-- the moving product -->
  </div>
</section>
<section id="menu">…normal content…</section>
```
Rules of thumb:
- Use about 130vh of scroll per scene, so a 4-scene story is roughly 520vh. Give the peak more.
- `100svh` (with a `100vh` fallback first) keeps the stage steady while the mobile address bar moves.
- Don't put `scroll-behavior:smooth` on `html` while testing; verify.py overrides it anyway.

## Core JS
```js
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const ss=(a,b,v)=>{const t=clamp((v-a)/(b-a));return t*t*(3-2*t)};      // smoothstep phase
const lerp=(a,b,t)=>a+(b-a)*t;
const hex=c=>[1,3,5].map(i=>parseInt(c.slice(i,i+2),16));
const mix=(c1,c2,t)=>{const A=hex(c1),B=hex(c2);return `rgb(${A.map((v,i)=>Math.round(lerp(v,B[i],t))).join(',')})`};
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;

const story=document.getElementById('story');
let target=0,cur=0,on=true,last=0;
function measure(){const r=story.getBoundingClientRect();
  target=clamp(-r.top/(r.height-innerHeight)); on=r.bottom>0&&r.top<innerHeight;}
addEventListener('scroll',measure,{passive:true}); addEventListener('resize',measure); measure();

function frame(t){
  const dt=Math.min(t-(last||t),64); last=t;
  // inertia: .06 = floaty, .09 = default, .12 = snappy. Corrected for 120 Hz screens.
  cur = reduce ? target : cur+(target-cur)*(1-Math.pow(1-.09,dt/16.67));
  if(!on && Math.abs(target-cur)<1e-4){ requestAnimationFrame(frame); return; }   // sleep off screen
  const p=cur, W=innerWidth, H=innerHeight, mobile=W<860, idle=reduce?0:1;
  // phases
  const a=ss(.10,.30,p), b=ss(.22,.46,p)-ss(.64,.80,p);
  stage.style.background=mix('#b8461a','#fbf3e0',a);
  obj.style.transform=`translate(-50%,-50%) translate(${lerp(W*.2,0,a)}px,${Math.sin(t/900)*8*(1-a)*idle}px) scale(${lerp(1,.8,b)})`;
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```
Template A adds the production details: brand colours read from CSS variables, an intro,
ink picked by contrast, and writes skipped when a value has not changed.

## Recipes
- **Text panel in/out:** `opacity = ss(in0,in1,p) - ss(out0,out1,p)`, plus `translateY((1-ss(in0,in1,p))*30px)`.
  Set `visibility:hidden` once it is fully out, so its links leave the tab order.
- **Stagger N items:** item i uses `ss(s+i*d, e+i*d, p)`, with d around .03.
- **Counter-scale labels inside a scaled parent:** `scale(1/s)`.
- **Idle life:** `Math.sin(t/900+i)` bob, and `Math.sin(t/1400)` slight rotation, both multiplied by `(1-phase)*idle`
  so they calm down once the story starts and vanish with reduced motion.
- **Particles orbiting:** `angle=k.a+t/6000*k.sp`, `r=k.r*(.35+ex*1.1)`.
- **Crossfading two versions of one object** (photo ↔ layers): swap only while they overlap exactly
  (stack closed), and keep the swap short (≤ .04 of p). Mid-move swaps show two objects.
- **Slider (non-scroll patterns):** keep `targetIndex` from wheel (throttled), arrows, tabs or swipe;
  smooth `curIndex` toward it the same way; parallax layers use `(i-curIndex)*W*speed`.
- **Cursor patterns:** `mx+=(rawX-mx)*.1`, then normalise to -1..1 for parallax. Off on touch.
- **Colour of chrome over a changing field:** pick ink or cream by contrast each frame; never mix them.
  See `motion-toolkit.md` §6.
- **Reduced motion:** `cur=target`, `idle=0`, no particles, intro and autoplay; keep the composition.
- More moves (easings, intros, text reveals, horizontal rail, magnetic UI, view transitions):
  `motion-toolkit.md`.

## Testing snippet (run with the browser pane's javascript tool)
```js
document.documentElement.style.scrollBehavior='auto';
const s=document.getElementById('story');
window.scrollTo({top:(s.offsetHeight-innerHeight)*0.44,behavior:'instant'});   // progress 0.44
measure(); cur=target; await new Promise(r=>setTimeout(r,500)); cur=target; 'ok'
```
Screenshot at these points:
- p = 0 (after the intro has finished, about 2 s);
- just before and just after each crossfade;
- the middle of each scene;
- the final state;
- the first normal section.

Check both 1440×860 and mobile (390×844). `cur=target` is needed because the pane throttles rAF,
so the lerp otherwise lags far behind. verify.py does all of this for you with `--points`.

## Common layout bugs
- Grid cards overflowing: add `min-width:0` to the grid children and `overflow:hidden` to the media boxes.
- An object colliding with the headline in the exploded state: compute scale from the exploded height
  `TOTAL+(N-1)*GAP` and about 64% of H, and shift it down a little.
- Labels clipped on mobile: put all labels on one side, shift the object the other way (`-W*.2*ex`),
  use a larger GAP and hide the small text. Re-assign label sides on resize, not only at build time.
- The stage jumps on phones while scrolling: you used `100vh` only. Add `100svh`.
- The preview pane shows a frozen page: you opened `file://`. Serve it with `python -m http.server`.
