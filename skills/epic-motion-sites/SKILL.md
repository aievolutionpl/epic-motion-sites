---
name: epic-motion-sites
description: Builds award-style, animated "motion sites" in a single HTML file, with photoreal AI-generated product cutouts. Covers scroll-scrubbed product stories, products exploding into layers, giant-word flavour sliders, product fans with configurators, cinematic scenes, cursor-reactive heroes, 3D gallery walks, shop-the-look carousels and Apple-style frame-sequence scrubs. Each build is planned as a story, checked against a taste floor and verified automatically in a headless browser. Use this skill whenever someone wants a website, landing page, hero or product page that should feel premium, "wow", animated, scroll-driven, interactive, 3D or Awwwards-like. Also use it when they share a motionsites.ai, Awwwards, Dribbble or Apple product page link and say "make one like this" or "zrób taką stronę", or want a site for a restaurant, drink, food, cosmetics, fashion, gadget or other product brand that should move and look expensive. Use it even if they never say "animation".
license: MIT
---

# Epic Motion Sites

by **AI Evolution Polska**

This skill builds a site whose wow factor comes from three things working together:
1. **Choreographed motion.** One smoothed value (scroll progress, slide index or cursor position) drives every element.
2. **Photoreal AI cutouts on transparent backgrounds.** Product parts can fly, stack and orbit.
3. **Confident art direction.** Huge type, bold colour fields, one memorable peak.

The output is one `index.html` (HTML + CSS + vanilla JS, no build step) plus an `img/` folder. It runs from any static host.

Write the site copy in the user's language. Paths below are relative to this skill's folder.

| Step | Read | Run |
|---|---|---|
| 1 pick | `references/patterns.md` | `scripts/study_reference.py` (if there is a reference) |
| 2 plan | `references/craft.md` §1, `assets/BRIEF.template.md` | — |
| 3 assets | `references/ai-assets.md` | `scripts/prep_assets.py`, `scripts/placeholders.py`, `scripts/video_to_frames.py` |
| 4 build | `assets/template-*.html`, `references/scroll-engine.md`, `references/motion-toolkit.md` (`gsap.md` if needed) | — |
| 5 verify | `references/craft.md` §2–3 | `scripts/verify.py` |
| 6 ship | `references/ship.md` | — |

## Workflow

### 1. Pick the pattern
Pick the one that fits the product, and say in one line which one you chose and why.

| | Pattern | Best for | Starting point |
|---|---|---|---|
| A | Scroll Explode | products made of parts: burger, ramen, sneaker, gadget | `assets/template-scroll-explode.html` |
| B | Giant-Word Slider | flavours or colour variants: drinks, cosmetics | `assets/template-giant-word-slider.html` |
| C | Product Fan + Configurator | many SKUs, "build your pack" | engine + recipe |
| D | Cinematic Story | venues, games, brand stories | engine + recipe |
| E | Living Hero | agencies, portfolios, wellness | engine + recipe |
| F | 3D Gallery Walk | art prints, collections | engine + recipe |
| G | Shop-the-Look | fashion, bundles | engine + recipe |
| H | Frame Sequence (Apple scrub) | gadgets, cars, watches, anything that turns or opens | engine + tested recipe |

A page can chain two devices (e.g. A, then a horizontal rail from `motion-toolkit.md` §4), but it keeps **one peak**.

If the user gave a reference site:
1. Run `python scripts/study_reference.py <page-or-video-url> <outdir> --scenes`. It writes an 8-frame sheet of the flow and a sheet of the key beats.
2. Look at both and write down the choreography before building: what moves, in which order, how far, with which colours and type.

On JS-rendered galleries, read `document.querySelector('video').currentSrc` in a browser and pass that URL to the script.

Take patterns and ideas only. Never copy someone's logo, imagery or text. Invent the brand unless the user gives one.

### 2. Plan the story
Copy `assets/BRIEF.template.md` next to the site and fill it in (or put it in your plan if the user wants speed):
- **brand:** name, palette (field colour(s) + ink + neutral + one accent) and 2 fonts;
- **the tell-someone sentence:** "It's the site where ___";
- **the feeling curve:** one line per scene (emotion — what causes it);
- **the peak and the signature move.**

Keep the copy per scene tiny: a kicker, a 2–5 word headline, one sentence and one CTA.

Ask the user only what you truly cannot decide. If they said "decide for me", decide, write it down and go.

### 3. Generate the assets
Read `references/ai-assets.md`. In short:
- Generate the **assembled hero first**, then every movable part as an **isolated cutout on a transparent background**, with the same camera angle and light (pass the hero as a reference image when the tool allows).
- Use whatever image tool is connected: Higgsfield `gpt_image_2_6` with `background:"transparent"`, fal Muse + BiRefNet, or another. Estimate the cost first and report it.
- Run `python scripts/prep_assets.py <src> <out> --width 840 --max-height 1300 --sheet sheet.png --bg "#hex"`. It crops, resizes, saves WebP, prints the CSS heights and **flags** `OPAQUE`, `CUT OFF`, `HALO` and `HEAVY` files.
- **Look at the sheet** on the brand colour. Regenerate flagged images and any with a wrong angle, a mismatched style or a baked-in shadow; a retake costs about 1 credit.
- Pattern H: image-to-video from the hero, then `python scripts/video_to_frames.py clip.mp4 <site>/frames --mobile-width 900`.

If there is no image tool or no credits:
- say so once, with any top-up link;
- run `python scripts/placeholders.py <site>/img --preset explode|slider` so the motion can be reviewed now;
- swap in real cutouts later under the same file names.

Never switch who pays without the user's OK.

### 4. Build
- **Patterns A and B:** copy the template and edit the blocks marked `===== EDIT`: meta, palette (CSS variables, read by JS), copy, data arrays. Both templates are complete, tested sites with intro, reduced motion and a11y built in.
- **Patterns C–H:** build on `references/scroll-engine.md` and the recipe in `references/patterns.md`.
- **Many independent scroll moments, SplitText/Flip, or a React app:** use GSAP. See `references/gsap.md`.

Premium-feel rules (details and code in `references/motion-toolkit.md`):
- **One smoothed value drives everything**, frame-rate independent: `cur+=(target-cur)*(1-Math.pow(1-.09,dt/16.67))`. Map phases with `ss(a,b,p)`. Never animate straight from scroll events.
- **An entrance on load** (1.2–1.8 s, staggered `outExpo`). Nothing premium appears all at once.
- **Overlap the phases.** Colour, position and scale start before the previous move ends.
- Animate only **transform / opacity / filter**. Fixed DOM, `will-change` on movers, write a style only when it changed, and let the loop sleep when the story is off screen.
- **Idle life:** a slow bob or rotation, so a still frame never looks frozen; calm once the story moves.
- **Depth layers:** near (big, blurred, fast), mid, far (small, slightly blurred, slow). Max 3–4 blurred elements.
- **Fade the field colour** between scenes. Chrome on top **picks** ink or cream by contrast (never a mix), and the nav **turns solid once the story has scrolled away**.
- **Art-direct mobile separately (<860px):** text above the object, labels on one side, larger gaps, hide secondary text and counters, `white-space:nowrap` on pills and controls, `100svh` stages.
- **Reduced motion:** snap the value, no idle motion, intro, particles or autoplay; keep the composition.

### 5. Verify (required)
1. Serve over HTTP, e.g. `python -m http.server 5500 --directory <site>`. A `file://` page breaks fetches and previews.
2. Run the automatic walk:
   ```
   python scripts/verify.py http://localhost:5500/ --out shots --mobile
   python scripts/verify.py http://localhost:5500/ --out shots --mobile --steps "go(0)" "go(1)" "go(2)"   # sliders
   python scripts/verify.py http://localhost:5500/ --out shots-rm --reduced                              # reduced motion
   ```
   It screenshots every key state on desktop (1440×860) and mobile (390×844), and reports:
   - **ERROR:** console errors, failed requests, missing images;
   - **WARN:** horizontal overflow, text off-screen, **text overlapping text**, **low contrast on the rendered frame**, images under a transparent nav, page weight, missing `lang`/viewport/title/alt, unnamed buttons, no reduced-motion handling;
   - **info:** long tasks, CLS, meta description and og:image.

   Add `--points .7,.75,.8,.85` to zoom in on a transition, and `--json report.json` for a machine-readable report. Decorative text can opt out with `aria-hidden="true"` or `data-verify-ignore`.
3. **Open `desktop-sheet.png` and `mobile-sheet.png` and look at them.** No script sees these:
   - ghosting (two versions of the product visible during a crossfade);
   - objects hitting the nav or headline;
   - elements from the neighbouring slide leaking in;
   - rhythm: does each scene earn its scroll length?
4. Then run the taste floor in `references/craft.md` §2–3.
5. Fix the issues and run it again until it is clean.

To drive the page by hand in a browser tool, see the testing snippet in `references/scroll-engine.md`. It sets smooth scrolling to auto and snaps `cur=target`.

### 6. Hand-off
Go through the checklist in `references/ship.md` §5, then tell the user:
- where the files are;
- what happens at each scroll point or slide;
- what the assets cost, and the page weight;
- what is a placeholder (address, phone, prices, stand-in images).

Offer the next steps: deploy (Vercel / Netlify / GitHub Pages, commands in `ship.md`), a looping hero video (image-to-video), more sections, or swapping in real product photos.

## Definition of done
- `verify.py --mobile` and `--reduced` report no ERROR, and every remaining WARN is fixed or explained.
- Both contact sheets were looked at; nothing ghosts, collides or leaks.
- The tell-someone sentence is true of the rendered page, and it has one clear peak.
- Meta description, og tags and favicon are in; assets and weight are within budget.

## Lessons learned from real builds
- `html{scroll-behavior:smooth}` breaks scripted scrolling. verify.py overrides it.
- Higgsfield runs at most 4 concurrent jobs. Submit in groups of 4 and resubmit only the items rejected by the rate limit.
- Flat foods come out too top-down. Say "viewed from the side at a low angle, camera 15° above, appears as a thin wide oval".
- Separate layers never re-stack exactly into the hero photo. Crossfade to the layers just as they start separating, and back only once the stack is fully closed, in a short window. Swapping mid-move showed two burgers at once.
- Drop parts that can't stand alone (sauce, crumbs). They live in the hero photo.
- Orbiting crumbs above the product covered label text. Keep particles behind the product (lower z-index).
- Size exploded stacks from their exploded height `TOTAL+(N-1)*GAP`, or the top layer hits the headline.
- In sliders, neighbouring slides must reach opacity 0 at distance 1, or their ingredients leak into the current slide.
- Keep blurred near-depth objects away from text blocks and the nav. A near ingredient at the top right sat under the cart pill.
- Tall objects (bottles, people) need a height cap in prep_assets, or one bottle weighs 250 KB.
- A transparent fixed nav collides with content below the story. Toggle a solid state.
- Mixing the nav colour linearly from cream to ink while the field goes terra → cream makes it unreadable mid-scroll (about 2:1). Pick whichever has more contrast.
- Body copy at `opacity:.95` dropped cream-on-terra from 4.8:1 to 4.4:1. Tint secondary text with a colour, not opacity.
- A white logo on pastel fields is about 1.4:1. Use the ink.
- Captions over video or busy scenes need a scrim; white text over a test clip measured 1.1–1.4:1.
- At 390px, a pill CTA + counter + 2 round buttons overflow. Hide the counter on phones.
