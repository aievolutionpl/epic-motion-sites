# Scroll engine (vanilla, no libraries)

Every pattern shares this core. It is about 40 lines and has no GSAP or Lenis, so there is no dependency or licence question. It runs at 60fps when you animate only `transform`, `opacity`, `filter` and background colour.

## Markup
```html
<section id="story" style="height:520vh">          <!-- scroll length = how long the story lasts -->
  <div class="stage" id="stage">                     <!-- position:sticky; top:0; height:100vh; overflow:hidden -->
    <div class="panel" id="pHero">…</div>            <!-- text panels, position:absolute -->
    <div class="obj" id="obj">…</div>                <!-- the moving product -->
  </div>
</section>
<section id="menu">…normal content…</section>
```
Rules of thumb:
- Use about 130vh of scroll per scene, so a 4-scene story is roughly 520vh.
- Don't put `scroll-behavior:smooth` on `html` while testing; only add it at the end for anchor links.

## Core JS
```js
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const ss=(a,b,v)=>{const t=clamp((v-a)/(b-a));return t*t*(3-2*t)};      // smoothstep phase
const lerp=(a,b,t)=>a+(b-a)*t;
const mix=(c1,c2,t)=>{const h=c=>[1,3,5].map(i=>parseInt(c.slice(i,i+2),16));
  const A=h(c1),B=h(c2);return `rgb(${A.map((v,i)=>Math.round(lerp(v,B[i],t))).join(',')})`};

const story=document.getElementById('story');
let target=0,cur=0;
function measure(){const r=story.getBoundingClientRect();target=clamp(-r.top/(r.height-innerHeight));}
addEventListener('scroll',measure,{passive:true}); addEventListener('resize',measure); measure();

function frame(t){
  cur+=(target-cur)*.09;                 // inertia: .06 = floaty, .12 = snappy
  const p=cur, W=innerWidth, H=innerHeight, mobile=W<860;
  // phases
  const a=ss(.10,.30,p), b=ss(.22,.46,p)-ss(.64,.80,p);
  stage.style.background=mix('#b8461a','#fbf3e0',a);
  obj.style.transform=`translate(-50%,-50%) translate(${lerp(W*.2,0,a)}px,${Math.sin(t/900)*8*(1-a)}px) scale(${lerp(1,.8,b)})`;
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```

## Recipes
- **Text panel in/out:** `opacity = ss(in0,in1,p) - ss(out0,out1,p)`, plus `translateY((1-ss(in0,in1,p))*30px)`.
- **Stagger N items:** item i uses `ss(s+i*d, e+i*d, p)`, with d around .03.
- **Counter-scale labels inside a scaled parent:** `scale(1/s)`.
- **Idle life:** `Math.sin(t/900+i)` bob, and `Math.sin(t/1400)` slight rotation, both multiplied by `(1-phase)` so they calm down once the story starts.
- **Particles orbiting:** `angle=k.a+t/6000*k.sp`, `r=k.r*(.35+ex*1.1)`.
- **Slider (non-scroll patterns):** keep `targetIndex` from wheel (throttled), arrows, tabs or swipe; `curIndex+=(targetIndex-curIndex)*.08`; parallax layers use `(i-curIndex)*W*speed`.
- **Cursor patterns:** `mx+=(rawX-mx)*.1`, then normalise to -1..1 for parallax.
- **Reduced motion:** if `matchMedia('(prefers-reduced-motion: reduce)').matches`, set `cur=target` each frame and turn off idle bob and particles.

## Testing snippet (run with the browser pane's javascript tool)
```js
document.documentElement.style.scrollBehavior='auto';
const s=document.getElementById('story');
window.scrollTo({top:(s.offsetHeight-innerHeight)*0.44,behavior:'instant'});   // progress 0.44
measure(); cur=target; await new Promise(r=>setTimeout(r,500)); cur=target; 'ok'
```
Screenshot at these points:
- p = 0;
- just before and just after each crossfade;
- the middle of each scene;
- the final state;
- the first normal section.

Check both 1440×860 and mobile (375×812). `cur=target` is needed because the pane throttles rAF, so the lerp otherwise lags far behind.

## Common layout bugs
- Grid cards overflowing: add `min-width:0` to the grid children and `overflow:hidden` to the media boxes.
- An object colliding with the headline in the exploded state: compute scale from the exploded height `TOTAL+(N-1)*GAP` and about 64% of H, and shift it down a little.
- Labels clipped on mobile: put all labels on one side, shift the object the other way (`-W*.2*ex`), use a larger GAP and hide the small text.
- The preview pane shows a frozen page: you opened `file://`. Serve it with `python -m http.server`.
