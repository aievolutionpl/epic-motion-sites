# When to use GSAP (and how it maps to the built-in engine)

The built-in vanilla engine (`scroll-engine.md`) is the default:
- it has zero dependencies;
- it works in a single `index.html`;
- it is easy for an agent to reason about, because everything is a function of one progress value `p`.

Reach for **GSAP + ScrollTrigger** when the site needs:
- many independently triggered sections (10+ scroll moments);
- pinning several different sections one after another;
- SplitText line/word/char reveals;
- Flip transitions (grid → detail);
- MorphSVG or MotionPath;
- a React/Vue/Next.js project where cleanup matters.

GSAP is 100% free, including all former Club plugins (SplitText, MorphSVG and others), for commercial use too. That changed after Webflow acquired GSAP.

For deep, correct GSAP usage, install the official skills, [greensock/gsap-skills](https://github.com/greensock/gsap-skills) (MIT):
```
npx skills add https://github.com/greensock/gsap-skills
# or in Claude Code
/plugin marketplace add greensock/gsap-skills
```
Let those skills own the API details. This file only covers how to use GSAP inside an epic-motion-site.

## CDN setup (single-file sites)
Pin exact versions (a floating `@3` can change under a finished site). GSAP 3.15 and Lenis 1.3 are
current stable lines as of Nov 2026; GSAP 4 is in beta, so stay on 3.x.
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/ScrollTrigger.min.js"></script>
<script>gsap.registerPlugin(ScrollTrigger); ScrollTrigger.config({ignoreMobileResize:true});</script>
```
Optional smooth scrolling with Lenis (MIT):
```html
<script src="https://cdn.jsdelivr.net/npm/lenis@1.3.27/dist/lenis.min.js"></script>
<script>
  const lenis = new Lenis({ lerp: .09 });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add(t => lenis.raf(t * 1000)); gsap.ticker.lagSmoothing(0);
</script>
```
Only add Lenis when the page has no wheel-hijacking slider. Two systems fighting over the wheel feel broken.

## Translating the engine to ScrollTrigger
| Built-in engine | GSAP |
|---|---|
| `#story` 520vh + sticky stage | `ScrollTrigger.create({trigger:'#story', pin:'#stage', start:'top top', end:'+=420%'})` |
| `cur += (target-cur)*.09` | `scrub: 0.8` (seconds of catch-up) |
| `ss(.22,.46,p)` phase | timeline labels and positions: `tl.to(obj,{…}, 0.22)` with timeline duration 1 |
| `ex = ss(a,b,p) - ss(c,d,p)` | two tweens on the same property: out at `a`, back at `c` |
| stagger `ss(s+i*d, …)` | `stagger: 0.03` |
| `mix(c1,c2,t)` background | `tl.to('#stage', {backgroundColor:'#fbf3e0'}, .14)` |

Example skeleton:
```js
const tl = gsap.timeline({ defaults:{ ease:'power2.inOut' },
  scrollTrigger:{ trigger:'#story', pin:'#stage', start:'top top', end:'+=420%', scrub:.8 } });
tl.to('#stage', { backgroundColor:'#fbf3e0', duration:.16 }, .14)
  .to('#burger', { x:0, rotate:0, duration:.22 }, .10)
  .to('.layer', { y:i=>(i-(N-1)/2)*GAP, duration:.24, stagger:.01 }, .22)
  .to('.layer', { y:0, duration:.16 }, .64);
```

## Reduced motion and breakpoints
Wrap every timeline in `gsap.matchMedia()`, so reduced motion and phones get their own version
and everything is reverted cleanly when the condition changes:
```js
const mm=gsap.matchMedia();
mm.add({desk:'(min-width:860px)', phone:'(max-width:859px)', calm:'(prefers-reduced-motion: reduce)'}, ctx=>{
  const {phone,calm}=ctx.conditions;
  if(calm){ gsap.set('.layer',{y:0}); return; }          // static composition, no scrub
  const GAP=phone?130:78;
  /* build the timeline here, using GAP */
});
```
In React use `useGSAP()` from `@gsap/react`, which scopes and cleans up for you.

## Verification is the same
`scripts/verify.py` works for GSAP sites too, because it only scrolls and screenshots. Give ScrollTrigger time to catch up with `--settle 1400` when `scrub` is above 1.
