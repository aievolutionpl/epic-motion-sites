# Ship: performance, accessibility, SEO, deploy

A motion site that stutters, traps the keyboard or shares as a blank link is not finished.
`scripts/verify.py` checks most of this list automatically; the rest is on you.

## 1. Performance budget

| What | Budget | How |
|---|---|---|
| total page weight | ≤ 3 MB (pattern H: ≤ 8 MB desktop, ≤ 2 MB phone) | verify.py reports it |
| hero / assembled image | ≤ 400 KB | `prep_assets.py` flags HEAVY |
| each cutout | ≤ 250 KB, 2× its CSS width | `--width`, `--max-height` |
| font families | 2, from one Google Fonts request | `display=swap`, preconnect |
| layout shift (CLS) | < 0.1 | `width`/`height` on every `<img>` |
| per frame | transform, opacity, filter only | no top/left/width/height |

- **Load the first screen first.** `<link rel="preload" as="image" href="hero.webp" fetchpriority="high">`
  for the one image the hero needs; `loading="lazy"` + `decoding="async"` on everything below the fold.
- **Let the loop sleep.** When the story is off screen and the value has settled, return early from
  `frame()` (both templates do). Pause sliders' autoplay and videos with an IntersectionObserver.
- **Write only what changed.** Compare strings before setting styles or CSS variables.
- **Blur is expensive.** At most 3–4 `filter:blur()` elements on screen at once, none bigger than
  ~400 px; on phones prefer pre-blurred images.
- **Fixed DOM.** Build every node once; never create elements inside `frame()`.
- **Sticky stage height:** `height:100vh;height:100svh` so the mobile address bar does not make the stage jump.
- Never use `background-attachment:fixed` (repaints every frame on mobile).

## 2. Accessibility

**Reduced motion is a contract, not a nicety.** With `prefers-reduced-motion: reduce`:
- snap the smoothed value (`cur=target`), no idle bob, no particles, no autoplay, no intro;
- keep the composition: the reader still sees every scene, just without travel;
- test it: `python scripts/verify.py <url> --reduced`.

**Keyboard and semantics**
- Every control is a real `<button>` or `<a>`; icon-only ones get `aria-label`. verify.py flags unnamed ones.
- Visible focus: `:focus-visible{outline:2px solid currentColor;outline-offset:4px}`.
- Sliders: arrow keys work while the stage is on screen; tabs use `role="tablist"`/`role="tab"`/`aria-selected`;
  the changing description is `aria-live="polite"`.
- A skip link (`<a class="skip" href="#content">`) jumps over a long pinned story.
- Exactly one `<h1>`. If the hero shows no headline (slider), add a visually hidden one (`.sr` class).
- Decorative giant words, canvases, crumbs and particles: `aria-hidden="true"`. The story's
  meaning must also exist as real text (labels, captions, a list).
- Hide panels that are faded out (`visibility:hidden` past their range) so their links can't be tabbed to.
- Wheel hijack only while the stage is on screen, released at the first/last slide.
- No flashing more than 3 times per second.

**Contrast** is checked on the rendered frame, the worst frame of each scene: body ≥ 4.5:1,
large text ≥ 3:1. Over photos or video, put a scrim (gradient band) only where the copy sits.

## 3. SEO and sharing

- `<html lang>`, a `<title>` (brand — what it is), `<meta name="description">` (≤ 155 characters).
- `og:title`, `og:description`, `og:image` (1200×630 is ideal; must be an absolute URL once deployed),
  `twitter:card=summary_large_image`, `theme-color` = the hero field colour.
- A favicon: an inline SVG data URI with the brand initial works and costs zero requests.
- The important copy must be real HTML text, never baked into images.
- For production, move JS-generated content (menu cards, product grids) into the HTML so crawlers
  and no-JS readers get it; keep JS for the motion.

## 4. Deploy

The output is static, so any host works. From the site folder:
```bash
npx vercel --prod                       # Vercel
npx netlify-cli deploy --prod --dir .   # Netlify
```
GitHub Pages: push the folder to a repo, then Settings → Pages → deploy from branch.
After deploying, set `og:image` to the absolute URL and run verify.py once against the live URL.

## 5. Hand-off checklist

- [ ] `verify.py --mobile` clean, and `--reduced` clean (or every remaining WARN explained)
- [ ] both contact sheets looked at: no ghosting, no collisions, readable on every frame
- [ ] taste floor and refuse list (`craft.md` §2–3) pass
- [ ] page weight and asset cost reported (credits used / left)
- [ ] placeholders listed (address, phone, prices, stand-in images from `placeholders.py`)
- [ ] meta description, og tags and favicon present
- [ ] next steps offered: deploy, hero loop video, more sections, real product photos
