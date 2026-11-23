# Motion toolkit

The moves that separate "it animates" from "it feels expensive". Everything here is vanilla
and plugs into the engine in `scroll-engine.md`. Pick what the story needs, not all of it.

## 1. Timing and easing

| Kind of motion | Duration | Easing | Distance |
|---|---|---|---|
| hover / press | 150–250 ms | `cubic-bezier(.2,.8,.2,1)` | 2–8 px, scale ≤1.04 |
| element entrance | 500–900 ms | `outExpo` / `outCubic` | 24–60 px + opacity (+ blur 8→0) |
| element exit | 60–70% of its entrance | `inCubic` | shorter than the entrance |
| move between two states | as long as the scroll gives it | smoothstep `ss()` / `inOutCubic` | any |
| hero intro, whole sequence | 1.2–1.8 s | staggered `outExpo` | — |
| playful drop / pop (max once per page) | 800–1100 ms | `outBack` | — |
| idle bob / drift | 3–8 s periods | `Math.sin` | 4–12 px, 1–3° |

```js
const outCubic=t=>1-Math.pow(1-t,3);
const outExpo =t=>t>=1?1:1-Math.pow(2,-10*t);
const inCubic =t=>t*t*t;
const inOutCubic=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const outBack =t=>{const c=1.4;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2)};
// frame-rate independent smoothing: f = the per-frame factor you would use at 60 fps (.09 = the engine's feel).
// Plain `cur+=(target-cur)*.09` runs twice as fast on 120 Hz screens (iPhone Pro, MacBook).
const damp=(cur,target,f,dt)=>cur+(target-cur)*(1-Math.pow(1-f,Math.min(dt,64)/16.67));
```
- **Stagger** 40–80 ms per item and cap the whole cascade at about 600 ms; longer feels slow.
- **Never animate from scale 0** or opacity alone. Start at 0.9–0.97 scale with a short travel.
- **Exits are quicker than entrances.** The eye cares about what arrives.
- One easing family per site. Mixing bouncy and silky reads as unfinished.

## 2. Intro choreography (on load, before any scroll)

A premium page never appears all at once. Give the first screen a 1.2–1.8 s entrance:
kicker → headline words → body → CTA, with the product arriving on its own curve.
Both templates do it inside `frame(t)`:
```js
let t0=null; const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
// in frame(t):
if(t0===null) t0=t;
const it=reduce?9:(t-t0)/1000;                         // seconds since first frame
const e=(delay,dur=.8)=>outExpo(clamp((it-delay)/dur));
el.style.opacity=e(.3); el.style.transform=`translateY(${(1-e(.3))*40}px)`;
// when it > total: clear the inline styles once and stop touching them
```
Gate on `document.fonts.ready` if a late font swap would make the headline jump.
verify.py waits about 2 s before the first shot, so keep the intro under 1.8 s.

## 3. Text reveals (no SplitText needed)

**Word rise** (used in template A): split once, animate each word.
```js
h1.innerHTML=h1.textContent.trim().split(/\s+/).map((w,i)=>`<span class="w" data-i="${i}">${w}</span>`).join(' ');
// .w{display:inline-block} then per word: opacity, translateY(40px→0), blur(8px→0), delay i*.08 s
```
**Line mask** (text slides up from under an invisible edge): wrap each line in a mask.
Use `clip-path:inset(-.3em -.1em 0 -.1em)` on the mask instead of `overflow:hidden`, or accents
(Ś, Ć, Ż, É) and ascenders get clipped at tight display leading.

**Counter roll-up**: only for real numbers. `el.textContent=Math.round(lerp(0,value,e)).toLocaleString(lang)`.

Screen readers read the split spans fine as long as the words stay in order and in the DOM.

## 4. Pinned horizontal rail

The vertical scroll drives a horizontal track. Great as a "chapter 2" device after an explode.
```html
<section id="rail" style="height:300vh"><div class="stage"><div class="track" id="track">…cards…</div></div></section>
```
```js
// progress q of #rail measured like the story; track is wider than the viewport
const max=track.scrollWidth-innerWidth;
track.style.transform=`translateX(${-ss(.05,.95,q)*max}px)`;
cards.forEach((c,i)=>c.style.transform=`translateY(${Math.sin(q*6+i)*10}px) rotate(${(q-.5)*-4}deg)`);
```
On phones (<860 px), drop the pin: `overflow-x:auto; scroll-snap-type:x mandatory` and a normal-height section.

## 5. Cursor-driven details (desktop only)

Skip all of these when `matchMedia('(pointer:coarse)').matches` or reduced motion is on.
- **Follower / spotlight**: lerp a point toward the mouse (`mx+=(rx-mx)*.12`) and use it for a
  `radial-gradient` mask, a glow, or a parallax offset (`translate(cx*-12px, cy*-8px)`).
- **Magnetic CTA**: within 80 px, pull the button 25% of the way toward the cursor; spring back on leave.
  ```js
  btn.addEventListener('pointermove',e=>{const r=btn.getBoundingClientRect();
    btn.style.transform=`translate(${(e.clientX-r.left-r.width/2)*.25}px,${(e.clientY-r.top-r.height/2)*.25}px)`;});
  btn.addEventListener('pointerleave',()=>btn.style.transform='');      // + transition:transform .4s
  ```
- **Tilt card**: `rotateX/rotateY` up to 8° from the cursor position, `perspective:900px` on the parent.
- A custom cursor is a refuse-list item unless it carries meaning (e.g. it shows "drag").

## 6. Colour across scenes

- Fade the field with `mix(c1,c2,t)` (two stops) or `mixN(colours,f)` (one stop per slide).
- **Pick the ink, never mix it.** A linear mix of cream→ink over terra→cream passes through
  mid-grey on mid-terra and is unreadable for a moment. Choose per frame:
  ```js
  const fg=contrast(CREAM,bg)>=contrast(INK,bg)?CREAM:INK;   // + CSS transition: color .35s
  ```
  `lum`/`contrast` helpers are in template A.
- Only write a style when its value changed (`if(bg!==lastBg)`): setting a CSS variable on `<html>`
  every frame forces a style recalc of the whole page.

## 7. Below the story: native scroll-driven CSS

The normal sections (menu, product grid, facts) still deserve a small entrance. Use the
browser's own scroll timeline; it costs no JS and leaves content visible where unsupported:
```css
@supports (animation-timeline: view()){
  @media (prefers-reduced-motion: no-preference){
    .reveal{animation:rise linear both;animation-timeline:view();animation-range:entry 0% entry 70%}
    @keyframes rise{from{opacity:0;transform:translateY(60px) scale(.97)}}
  }
}
```
Keep the JS engine for the main story: scroll timelines cannot do inertia, cross-scene logic or canvas.

## 8. State swaps: View Transitions

For clicks that change a whole view (grid → product detail, tab → tab), let the browser morph it:
```js
const swap=()=>{ /* update the DOM */ };
document.startViewTransition ? document.startViewTransition(swap) : swap();
```
Give the shared element the same `view-transition-name` in both states (e.g. the product image).
For multi-page sites, `@view-transition{navigation:auto}` in both pages' CSS cross-fades navigations.

## 9. Video loops

Hero loops (image-to-video from your hero still) need:
`<video autoplay muted loop playsinline preload="metadata" poster="hero.webp">`.
- 4–8 s, a seamless loop (first and last frame alike), 1–3 MB, H.264 MP4, plus WebM if you can.
- Pause with an IntersectionObserver when off screen; with reduced motion, show the poster instead.
- Sound is off by default. A sound toggle is fine, autoplaying audio never is.
