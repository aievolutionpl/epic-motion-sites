---
name: epic-motion-sites
description: Builds award-style, animated "motion sites" in a single HTML file, with photoreal AI-generated product cutouts. Covers scroll-scrubbed product stories, products exploding into layers, giant-word flavour sliders, product fans with configurators, cinematic scenes, cursor-reactive heroes, 3D gallery walks and shop-the-look carousels. Each build is planned as a story, checked against a taste floor and verified automatically in a headless browser. Use this skill whenever someone wants a website, landing page, hero or product page that should feel premium, "wow", animated, scroll-driven, interactive, 3D or Awwwards-like. Also use it when they share a motionsites.ai, Awwwards or Dribbble link and say "make one like this" or "zrób taką stronę", or want a site for a restaurant, drink, food, cosmetics, fashion or other product brand that should move and look expensive. Use it even if they never say "animation".
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

## Workflow

### 1. Pick the pattern
Read `references/patterns.md`. Pick the one that fits the product, and say in one line which one you chose.

| | Pattern | Best for | Starting point |
|---|---|---|---|
| A | Scroll Explode | products made of parts: burger, ramen, sneaker, gadget | `assets/template-scroll-explode.html` |
| B | Giant-Word Slider | flavours or colour variants: drinks, cosmetics | `assets/template-giant-word-slider.html` |
| C | Product Fan + Configurator | many SKUs, "build your pack" | engine + recipe |
| D | Cinematic Story | venues, games, brand stories | engine + recipe |
| E | Living Hero | agencies, portfolios, wellness | engine + recipe |
| F | 3D Gallery Walk | art prints, collections | engine + recipe |
| G | Shop-the-Look | fashion, bundles | engine + recipe |

If the user gave a reference site:
1. Run `python scripts/study_reference.py <page-or-video-url> <outdir>`. It makes an 8-frame contact sheet of the preview video.
2. Look at the sheet and write down the choreography before building. Note what moves, when, and with which colours and type.

On JS-rendered galleries, read `document.querySelector('video').currentSrc` in a browser and pass that URL to the script.

Take patterns and ideas only. Never copy someone's logo, imagery or text. Invent the brand unless the user gives one.

### 2. Plan the story
Read `references/craft.md` §1 and write a short brief:
- **brand:** name, palette (field colour(s) + ink + neutral + one accent) and 2 fonts;
- **the tell-someone sentence:** "It's the site where ___";
- **the feeling curve:** one line per scene (emotion — what causes it);
- **the peak and the signature move.**

Keep the copy per scene tiny: a kicker, a 2–5 word headline, one sentence and one CTA.

Ask the user only what you truly cannot decide. If they said "decide for me", decide, write it down and go.

### 3. Generate the assets
Read `references/ai-assets.md`. In short:
- Generate every movable part as an **isolated cutout on a transparent background**, with the same camera angle and light across the set. Also make one assembled hero shot if the pattern needs it.
- Use whatever image tool is connected: Higgsfield `gpt_image_2_6` with `background:"transparent"`, fal Muse + BiRefNet, or another. Estimate the cost first and report it.
- **Look at every result** on the brand colour. Regenerate any image with a wrong angle, a mismatched style or a baked-in shadow; it costs about 1 credit.
- Run `python scripts/prep_assets.py <src> <out> --width 840 --max-height 1300 --sheet sheet.png --bg "#hex"`. It crops to the alpha bounds, resizes, saves WebP and prints the CSS heights.

If there is no image tool or no credits:
- say so once, with any top-up link;
- offer an alternative;
- build with CSS/SVG placeholders so the motion can be reviewed.

Never switch who pays without the user's OK.

### 4. Build
- **Patterns A and B:** copy the template and adapt the data arrays, palette, copy and assets. Both templates are complete, tested sites.
- **Patterns C–G:** build on `references/scroll-engine.md` and the recipe in `references/patterns.md`.
- **Many independent scroll moments, SplitText/Flip, or a React app:** use GSAP. See `references/gsap.md`.

Premium-feel rules:
- **One smoothed value drives everything:** `cur += (target-cur)*.09` in requestAnimationFrame. Map phases with `ss(a,b,p)` smoothsteps. Never animate straight from scroll events.
- **Overlap the phases.** Colour, position and scale start before the previous move ends.
- Animate only **transform / opacity / filter**. Use a fixed number of DOM nodes and `will-change` on movers.
- **Give it idle life:** a slow bob or rotation so a still frame never looks frozen.
- **Use depth layers:** near (big, blurred, fast), mid, far (small, slightly blurred, slow).
- **Fade the background colour** between scenes. The nav follows, and **turns solid once the story has scrolled away**.
- **Art-direct mobile separately (<860px):**
  - stack the text above the object;
  - put the labels on one side;
  - make the gaps larger;
  - hide secondary text and counters;
  - add `white-space:nowrap` on pills and controls.
- **Support `prefers-reduced-motion`:** snap the value, with no idle motion and no autoplay.

### 5. Verify (required)
1. Serve over HTTP, e.g. `python -m http.server 5500 --directory <site>`. A `file://` page breaks fetches and previews.
2. Run the automatic walk:
   ```
   python scripts/verify.py http://localhost:5500/ --out shots --mobile
   python scripts/verify.py http://localhost:5500/ --out shots --mobile --steps "go(0)" "go(1)" "go(2)"   # sliders
   ```
   It screenshots every key state on desktop (1440×860) and mobile (390×844). It reports console errors, missing images, horizontal overflow and visible text running off-screen.
3. **Open `desktop-sheet.png` and `mobile-sheet.png` and look at them.** Check for:
   - overlapping labels or headlines;
   - objects hitting the nav;
   - ghosting during crossfades;
   - unreadable text on the colour field;
   - elements from the neighbouring slide leaking in.
4. Then run the taste floor in `references/craft.md` §2–3.
5. Fix the issues and run it again until it is clean.

To drive the page by hand in a browser tool, see the testing snippet in `references/scroll-engine.md`. It sets smooth scrolling to auto and snaps `cur=target`.

### 6. Hand-off
Tell the user:
- where the files are;
- what happens at each scroll point or slide;
- what the assets cost;
- what is a placeholder (address, phone, prices).

Offer the next steps: deploy (GitHub Pages / Vercel / Netlify), a looping hero video (image-to-video), more sections, or swapping in real product photos.

## Lessons learned from real builds
- `html{scroll-behavior:smooth}` breaks scripted scrolling. verify.py overrides it.
- Higgsfield runs at most 4 concurrent jobs. Submit in groups of 4 and resubmit only the items rejected by the rate limit.
- Flat foods come out too top-down. Say "viewed from the side at a low angle, camera 15° above, appears as a thin wide oval".
- Separate layers never re-stack exactly into the hero photo. Show the photo while the product is assembled, and crossfade to the layers just as they start separating.
- Drop parts that can't stand alone (sauce, crumbs). They live in the hero photo.
- Size exploded stacks from their exploded height `TOTAL+(N-1)*GAP`, or the top layer hits the headline.
- In sliders, neighbouring slides must reach opacity 0 at distance 1, or their ingredients leak into the current slide.
- Keep blurred near-depth objects away from text blocks.
- Tall objects (bottles, people) need a height cap in prep_assets, or one bottle weighs 250 KB.
- A transparent fixed nav collides with content below the story. Toggle a solid state.
- At 390px, a pill CTA + counter + 2 round buttons overflow. Hide the counter on phones.
