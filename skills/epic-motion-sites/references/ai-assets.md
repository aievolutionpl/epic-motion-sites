# AI assets for motion sites

The look depends on **consistent, isolated, transparent cutouts**. Plan them as a set: the same camera angle, light and style. That way the parts can recombine into one object.

## Which service
1. **Higgsfield** (connector `generate_image_batch`, `jobs_wait`, `balance`). Use model `gpt_image_2_6` with these params:
   ```json
   {"model":"gpt_image_2_6","quality":"medium","background":"transparent","aspect_ratio":"21:9","prompt":"…"}
   ```
   - About 1 credit per image (medium + transparent); low quality is 0.75.
   - Check `balance` first and estimate with `estimate_image_cost`.
   - **Max 4 concurrent jobs.** Submit 4, wait with `jobs_wait`, then submit the next ones. Items rejected for rate limit created no job and cost nothing, so resubmit only those.
   - The results are already true RGBA PNGs, so there is no background-removal step.
2. **fal.ai** (MCP connector or API):
   - `meta/muse-image/text-to-image` ($0.01) on a pure white background, then `fal-ai/birefnet/v2` for the cutout.
   - If it says "out of credits", tell the user once with the top-up link, offer Higgsfield and wait for their choice.
3. **Any other generator** that can produce transparent PNGs, or a white background followed by a background remover.
4. If none is available, run `python scripts/placeholders.py <site>/img --preset explode` (or `--preset slider`,
   or `name:WxH:shape:#colour` specs). It writes shaded, labelled stand-in cutouts under the template's
   file names, so the whole choreography can be reviewed now and real photos dropped in later.

Respect the user's cost preferences. Default to cheap, good models, and use premium ones only when the user asks.

## Keep the set consistent
- Generate the **assembled hero first**, approve it, then generate the parts in the same words.
- If the tool accepts a reference image (Higgsfield, fal edit models), pass the approved hero as the
  reference for every part: "the [part] from this burger, isolated…". Same light, same style.
- Keep a fixed seed per set when the tool exposes one, and change only the subject words.
- One camera description for the whole set, copied verbatim into every prompt.

## Prompt recipe (cutout layer)
```
Professional food photography, [ONE item, quantity, state — e.g. "two thick slices of ripe red tomato lying flat side by side"],
viewed from the side at a low angle (camera 15 degrees above), [shape hint — "appear as thin wide ovals"],
isolated, floating, filling the frame width, photoreal. Transparent background, no shadow, no plate, no text.
```
- Swap the first two words for the domain: "Studio product photography", "Fashion catalogue photography" and so on.
- Flat items such as slices, cheese and leaves default to a top-down view. **Always state the low camera angle.**
- For melting or draping items, say "draped as if over an invisible round patty, corners drooping, glossy drips".
- Aspect ratios:
  - **21:9** for flat layers;
  - **16:9** for domes (buns, caps);
  - **1:1** for the assembled hero;
  - **3:4 or 9:16** for bottles and people.

## Prompt recipe (assembled hero)
```
Professional food photography of a single [product], isolated, centered, front side view at eye level slightly from above:
[list every layer top→bottom in the same words used for the layer prompts]. Warm studio lighting, sharp detail, appetizing.
Transparent background, no plate, no shadow, no text.
```

## Scenes (patterns D/E)
- Use 16:9 or 21:9 with the background **opaque**, and leave an empty, darker middle area for the giant headline.
- Describe the light ("rim-lit by fire, reflections on wet stone").
- Generate a separate foreground cutout (ridge, fog, leaves) on transparent, to mask the giant word.

## Video (pattern H, hero loops)
- **Frame sequences** (pattern H): image-to-video from the approved hero still. Ask for a locked-off,
  slow, continuous move: "slow 360° turntable rotation, camera locked, seamless studio background #hex,
  no cuts, no zoom". Models with first + last frame input can animate between two stills
  (e.g. exploded → assembled). 4–6 s is plenty. Then `scripts/video_to_frames.py`.
- **Hero loops** (patterns D/E): "subtle ambient motion only: drifting fog, flickering firelight,
  camera static". Ask for a loop or pick a clip whose first and last frames match.
- Video costs much more than stills. Estimate, say the number, and get an OK before generating.

## Review before use
- Make a contact sheet: paste each cutout onto the brand colour (`scripts/prep_assets.py --sheet`) and look at it.
- Regenerate anything with:
  - a wrong angle;
  - a mismatched style;
  - a half-finished shape;
  - a baked-in shadow;
  - text artefacts.

  It costs about 1 credit, much cheaper than a weak page.

## Prepare for the web
Run `python scripts/prep_assets.py <src_dir> <out_dir> [--width 840] [--sheet sheet.png --bg "#b8461a"] [--json sizes.json]`. It:
- crops each image to its alpha bounding box (threshold 12), so layout math uses the visible object;
- resizes it to the given width (2× the CSS width, for retina);
- saves it as WebP (q84, with alpha); a typical layer is 50–150 KB;
- prints `name  WxH  css_height@420`, which you use as the layer `h`;
- **flags** what will look wrong: `OPAQUE` (no transparency), `CUT OFF` (object touches the frame),
  `HALO` (fringe from background removal), `HEAVY` (too many KB). Regenerate flagged images;
- with `--key-bg`, removes a flat light studio background from opaque images (a fallback, not a
  replacement for a real background remover).

Keep the PNG originals in `img/src/`. Tell the user what the assets cost (credits used / remaining).
