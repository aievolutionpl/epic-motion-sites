# Motion site patterns

These seven patterns were distilled from studio.motionsites.ai/explore (Nov 2026). Each entry covers:
- what it looks like,
- which assets it needs,
- the choreography,
- the implementation notes.

Build on the engine in `scroll-engine.md` (helpers `ss`, `lerp`, `mix`, `clamp`, rAF loop).

---

## A. Scroll Explode — "the ingredient ballet"
Reference: Noodle Twirl. Our tested build: `assets/template-scroll-explode.html` (STAK burger).

**Look:**
- Hero on a strong terracotta/brand field: a huge serif headline on the left and the product photo on the right, tilted about -9° and gently bobbing.
- On scroll the background fades to cream, the product moves to the centre and **explodes vertically into its layers**.
- Each layer gets a hairline label: number, name and a one-line note, alternating left and right.
- A headline at the top says something like "A little bit of everything".
- Then the layers re-stack and the product lands on a plate under "Your table is waiting." with a CTA.
- Crumbs or particles orbit during the explode.

**Assets:**
- 1 assembled hero shot (1:1);
- N layer cutouts (16:9 / 21:9), same angle, transparent.

**Choreography** (`p` = 0..1 over a 520vh section):
- `toCream=ss(.14,.3)`
- `toCenter=ss(.1,.32)`
- `ex=ss(.22,.46)-ss(.64,.8)`
- photo → layers crossfade `ss(.19,.26)`, and back `ss(.7,.8)`
- labels `ss(.3,.42)-ss(.56,.64)`
- land `ss(.7,.92)`
- plate `ss(.62,.82)`
- final panel `ss(.8,.9)`

**Notes:**
- Layer offset is `(i-(N-1)/2)*GAP*ex` plus a small alternating rotate and translateX.
- Counter-scale labels with `scale(1/s)` so the text stays readable.

Fits: burgers, ramen, sandwiches, cakes, sneakers (sole/midsole/upper/laces), headphones, skincare routines, cocktails.

---

## B. Giant-Word Slider — flavour carousel
Reference: Smoothie Slider ("Blendy"). Our tested build: `assets/template-giant-word-slider.html` (SYK lemonade).

**Look:**
- Each slide is a pastel field colour with the flavour name in a **giant white word behind** the centred product bottle.
- Ingredient cutouts float around it at different depths: near ones big and blurred (`filter:blur(6px)`), far ones small and sharp, all slowly drifting.
- Nav tabs list the flavours, with a "SHOP NOW" button and arrows at the bottom.

**Transition:**
- The whole slide group slides horizontally.
- The word, product and ingredients move at **different speeds** (parallax: word 1.4×, product 1×, near ingredients 1.8×).
- The background colour cross-fades.
- Drive it with wheel/arrows/tabs into a target index, then `cur+=(target-cur)*.08`.

**Assets:**
- 1 product per flavour (consistent packshot, transparent);
- 3–4 ingredient cutouts per flavour.

---

## C. Product Fan + Configurator
Reference: Protein Bars ("Stride").

**Look:**
- Hero has 6–7 products fanned in a gentle arc (rotations -20°…+20°, staggered y); the centre one is bigger.
- Hover or arrow keys **promote** a product to the centre. The big flavour name below updates, with an outlined index number ("02").
- Flavour ingredients float behind, and soft radial rings pulse from the centre.

**Further scenes:**
1. "Inside": one product rotates and tilts to show its back (nutrition), with ingredients bursting around it.
2. "Grab a bag": cards in flavour colours.
3. "Build your 3-pack & save": dark section with selectable thumbnails. Picked items fly into slots arranged in a triangle, and an "Add to cart" pill shows a live price.

**Assets:** front packshot per SKU (transparent), optional back shot, ingredient cutouts.

---

## D. Cinematic Story
Reference: Forge Gate ("Embers").

**Look:**
- A full-bleed dark AI scene (still or a muted loop video) with dramatic light.
- On scroll a **giant word rises from the bottom**, masked behind a foreground element such as a rock ridge or sand dune PNG, so the letters look planted in the scene.
- Small 01–04 feature captions sit along the bottom.
- Next scene: a left text column ("Unveiling deep halls of the forge.") plus 3 thumbnail cards that fan out and say "Exploring".
- A thin vertical icon rail sits on the left.

**Implementation:**
- Layers: background image (slow scale 1→1.08), giant word, foreground PNG, then text.
- The word's `translateY` is driven by `ss()`.
- Cards use stagger `ss(.4+i*.04, .55+i*.04)`.

**Assets:**
- 1 wide scene (21:9 or 16:9) with an empty middle;
- 1 foreground cutout (ridge/fog/leaves) on transparent;
- 3 detail images;
- optional 5–8 s loop video from the scene (image-to-video).

---

## E. Living Hero — cursor-reactive scene
Reference: Flower Valley ("Fernhollow").

**Look:**
- A lush, blurred-depth AI scene fills the screen, with a big condensed headline and one tagline centred.
- Moving the cursor **lights up** the area under it with a radial glow and spawns drifting light particles (fireflies) that fade out.
- The scene gently parallaxes toward the cursor.
- A "Scroll to wander" hint and a sound toggle sit in the corner.

**Implementation:**
- Use a `<canvas>` overlay for particles: an array pool of about 120, additive blend `globalCompositeOperation='lighter'`.
- Use a CSS `radial-gradient` mask or `mix-blend-mode:screen` for the glow, following a lerped cursor position.
- Parallax: `translate(cx*-12px, cy*-8px) scale(1.05)`.
- On touch devices, run an automatic wandering cursor.

**Assets:** 1 rich scene (or loop video), optionally a sharper "lit" version to reveal through the mask.

---

## F. 3D Gallery Walk
Reference: Print Gallery ("Zestwell — Citrus Season").

**Look:**
- A warm cream corridor in CSS 3D (`perspective:1200px`) with framed prints hung on the left and right walls, receding into the distance.
- Scroll or drag walks forward (`translateZ`).
- A huge condensed title sits fixed at the bottom-left, with a "Gallery / List" toggle.
- Clicking a print flies it to the screen centre; then a product panel slides in (title, artist, price, paper/size/frame options, Add to bag).

**Implementation:**
- Each frame is placed with `rotateY(±80deg) translateZ(...)` along the z axis.
- The camera is a wrapper with `translateZ(progress*depth)`.
- Use the FLIP technique for click-to-centre.
- Mobile: fall back to a horizontal snap carousel.

**Assets:** 8–12 artworks (AI illustrations in one consistent style) and a frame drawn with CSS borders.

---

## G. Shop-the-Look
Reference: Outfit Carousel.

**Look:**
- A white editorial page. A row of full-body model cutouts stands on a soft floor shadow; the centre model is sharp and the neighbours are faded and blurred.
- Arrows or a progress bar switch looks.
- A right-hand sidebar "In this look" lists the items (thumbnail, name, price, +).
- Clicking the model zooms in and shows **hotspots** on each garment, with a tooltip.
- Bottom: "Complete the look" bundle price and a dark CTA.

**Implementation:**
- Carousel transforms: `translateX`, `scale(.8)` and `opacity:.35` with `blur(4px)` for non-active items.
- Hotspots are absolutely positioned in % of the model image.

**Assets:**
- 5–6 model cutouts in the same pose style and lighting (same camera, full body, white backdrop → transparent);
- product thumbnails.
- Use invented brands only.

---

## Shared chrome (all patterns)
- **Nav:** logo left; 3–5 uppercase links centre with a small underline on the active one; a pill CTA and a hamburger on the right. The nav colour follows the scene.
- **Scene indicator:** a vertical "01 / SECTION 01" rail on the left and dots on the right.
- **Type:** display at `clamp(54px,7.6vw,118px)` with line-height ~.86; kicker 13–15px, letter-spacing .2em, weight 600.
- **CTA pill:** cream on colour, or ink on cream; arrow →; hover lift.
- **After the story section,** use normal sections (menu/products grid, footer with address and hours) so the page is also useful.
