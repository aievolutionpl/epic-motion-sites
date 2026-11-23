# Craft: the story and the taste floor

Motion alone does not make a site premium. A page can move beautifully and still feel like a template. Use this file twice:
- while planning, for the story;
- before hand-off, for the taste floor.

Several ideas here were inspired by [nateherkai/scroll-craft](https://github.com/nateherkai/scroll-craft) (MIT): the feeling curve, the single peak, the signature move and the refuse list. They are rewritten and adapted to this skill's lighter, single-file workflow. See CREDITS.md in the repo root.

---

## 1. The story (decide before code)

Write these into a short `BRIEF.md` next to the site, or into your plan if the user wants speed. Three to five lines each is enough.

**The tell-someone sentence.** "It's the site where ___." Fill the blank with an experience, not a technique. Compare:
- weak: "It's the site with a scroll animation";
- strong: "It's the site where the burger flies apart and every ingredient introduces itself."

If you cannot fill it, the concept is not ready.

**The feeling curve.** Write one line per scene, the emotion first and then what on screen causes it:
```
1 hero      appetite   - the glossy burger bobbing on hot terracotta
2 explode   curiosity  - it bursts apart, every layer named
3 land      calm       - it settles on a plate, the page turns cream
4 menu      decision   - three clear choices with prices
```
If two adjacent scenes have the same feeling, one of them is filler. Cut it or change it.

**One peak.** Pick the single moment a visitor will remember, and give it:
- the best asset;
- the most scroll room;
- a beat of quiet before it.

A page with three peaks has none.

**One signature move.** Invent one interaction that belongs to this brand only, for example:
- the bottle tilts toward the next flavour as the slide changes;
- the gate's fire brightens under the cursor;
- the outfit's hotspots pulse on the garment the visitor last hovered.

A recoloured template effect does not count.

**Vary the devices.** Do not repeat the same motion device in consecutive scenes. Mix them: an explode, then a crossfade, a horizontal rail, a pinned typographic beat, a cursor-reactive layer.

## 2. Taste floor (check the rendered page, not your intention)

**Typography**
- Use at most 2 families. The display face carries the voice and the text face carries the prose.
- Tighten tracking as size grows: display around -0.02 to -0.04em, body at 0.
- Keep body measure at 45–75ch, with line-height about 1.5 for body and 0.85–1.0 for display.
- Use `text-wrap: balance` on headings, and step the hero down on phones: no headline should wrap to 5+ lines at 390px.
- Use emphasis inside a headline in the same family (italic or weight), never a third font.
- Inter is a non-decision. Prefer a face with character: Bricolage Grotesque, DM Serif Display, Archivo, Outfit, Syne, Fraunces, or the brand's own.

**Colour**
- Use one bold field colour per scene, one ink, one cream/neutral and one accent. The accent owns a role (the CTA, the price), not scattered dots.
- Never use pure `#000`; use an off-black with a hue (`#1f1a14`, `#14110c`). Tint secondary text from the ink; never use flat `#888`.
- Contrast on the rendered frame: body ≥ 4.5:1, large text ≥ 3:1. The background changes as you scroll, so check the worst frame.
- When a section inverts (light ↔ dark), restate `color:` on that section as well as the CSS variable. Inherited colour does not update by itself.
- **Avoid these default palettes:**
  - cream + brass + espresso for every craft brand;
  - violet→blue AI gradients.

  Use them only when the brand asks for them.

**Spacing and layout**
- Leave more space above a heading than below it.
- Use fluid section padding (`clamp(64px, 10vw, 140px)`), so phones do not inherit desktop air.
- Give grid children `min-width:0`. Give images that are overridden in CSS both `width` and `height` (or `height:auto`).

**Text over imagery**
- Never put a full-frame dark overlay on the image.
- Put density only where the copy is: a corner gradient, a bottom band, or a column. Better still, mask the image away from the text.

**Fixed chrome**
- A transparent nav over the hero must turn solid (background + ink colour) once the story section has scrolled away. Otherwise it collides with content. Both test builds hit this.
- Over a changing field, pick the chrome's ink per frame by contrast (cream or ink), never a linear mix of the two.

**Motion quality** (see `motion-toolkit.md` for numbers and code)
- The first screen has an entrance (1.2–1.8 s): nothing premium appears all at once.
- One easing family; exits faster than entrances; staggers 40–80 ms.
- Nothing is ever fully still: idle life on the hero object, but calm once the story is moving.
- Two versions of one object (photo ↔ layers) are never visible at once: check the crossfade frames.

## 3. Refuse list (things that make it look AI-generated)

Don't ship any of these unless the user asks for them:
- identical three-card feature grids repeated down the page;
- a "scroll to explore" mouse icon as the only hero idea;
- invented statistics presented as real ("10,000+ happy customers");
- fake testimonials with stock names;
- gradient text everywhere;
- glowing neon buttons;
- emoji bullets;
- the same section rhythm on every build.

Placeholder business data (address, phone, prices) is fine, but say clearly in the hand-off that it is a placeholder.

## 4. Motion etiquette

- Respect `prefers-reduced-motion`. Snap the smoothed value, turn off idle bob and particles and autoplay, but keep the composition.
- Autoplaying sliders stop on the first user interaction and never fight the user's scroll.
- Hijack the wheel only while the stage is on screen, and release it at the first and last slide so the page can scroll on.
- Never animate layout properties (top/left/width/height) per frame. Animate only transform, opacity and filter.
- Keep large images at 2× their displayed size and no more. Use WebP, and cap the height of tall objects (bottles, people). A page's media should usually total under 3 MB.
