# Changelog

## 1.1.0 — 2026-11-23

### Verification (`scripts/verify.py`)
- New checks: text overlapping text (measured on the glyph band, so tight display leading is not a false alarm),
  sampled contrast on the rendered frame, product images under a transparent fixed nav, page weight and
  heavy images, long tasks and CLS, and static basics (`lang`, viewport, title, `alt`, unnamed buttons/links,
  no `prefers-reduced-motion`, meta description, og:image).
- ERROR / WARN / info levels, `--json` report, `--budget-mb`, `--no-contrast`.
- Falls back to `CHROMIUM_PATH` or a preinstalled Chromium when `playwright install` was not run.
- Visually hidden (`.sr-only`) text, `aria-hidden` and `[data-verify-ignore]` are skipped.

### Templates (A: scroll explode, B: giant-word slider) and examples
- Intro choreography on load (word-by-word headline, product drop / bottle lift, ingredient burst).
- Reduced motion fully supported (template A had none); autoplay stops for good on first interaction and pauses off screen.
- Frame-rate independent inertia: the same feel on 60 Hz and 120 Hz screens.
- Fixed: two burgers visible while the layers re-stacked (photo crossfade moved to the closed stack, shorter window).
- Fixed: nav/side-rail colour was a linear mix that passed through ~2:1 contrast mid-scroll; now picked by contrast.
- Fixed: body copy at 95% opacity fell under 4.5:1; white SYK logo on pastel fields (~1.4:1); near ingredient under the cart pill;
  crumbs flying over label text; `nav` transition declared twice; labels not re-sided on resize.
- `100svh` stages, loop sleeps when the story is off screen, styles written only when changed.
- Accessibility: skip link, real `<button>` for the menu icon, focus-visible styles, tablist roles, `aria-live` slider info,
  decorative giant word hidden from screen readers, faded panels removed from the tab order.
- SEO/sharing: meta description, Open Graph/Twitter tags, theme-color, inline SVG favicon, hero image preload.
- Native CSS scroll-driven reveals for the sections below the story (`@supports`-guarded).
- Brand palette lives in CSS variables only (JS reads them); every place to edit is marked `===== EDIT`.

### New
- Pattern **H — Frame Sequence** (Apple-style canvas scrub) with a tested recipe, and `scripts/video_to_frames.py`.
- `references/motion-toolkit.md`: timing/easing table, intros, text reveals, pinned horizontal rail, cursor and magnetic UI,
  colour/ink picking, CSS scroll-driven reveals, View Transitions, video loops.
- `references/ship.md`: performance budget, accessibility contract, SEO/sharing, deploy commands, hand-off checklist.
- `scripts/placeholders.py`: labelled stand-in cutouts (`--preset explode|slider`) so the motion can be reviewed with no image tool.
- `assets/BRIEF.template.md`.

### Improved
- `prep_assets.py`: flags OPAQUE, CUT OFF, HALO, HEAVY, EMPTY; `--key-bg` for flat studio backgrounds; `--json`; JPG input.
- `study_reference.py`: `--scenes` sheet of the key beats; local video files.
- `ai-assets.md`: set consistency (hero first, reference image, fixed seed), video prompts for pattern H and hero loops.
- `gsap.md`: pinned CDN versions, `gsap.matchMedia()` for reduced motion and breakpoints.
- SKILL.md: step → file map, 8 patterns, definition of done, new lessons learned from verifying these builds.

## 1.0.0
- First release: 7 patterns, two templates, verify.py, prep_assets.py, study_reference.py.
