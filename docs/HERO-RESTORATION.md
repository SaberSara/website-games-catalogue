# Hero restoration (15 October 2026)

## Issue and visual source
The user’s approved screenshot `image(7).png` shows full, saturated woodland scenery with an intact fox, owl and wooden signs behind a vivid, colorful wordmark. The old V4 stylesheet switched to screenshot-derived `hero-left-v4.webp` and `hero-right-v4.webp` crops, which baked in UI elements and cut off the fox. It also changed the background to opaque white and reduced artwork opacity to .20 on mobile.

## Fixed
- Use the original transparent-edge `hero-left.webp` and `hero-right.webp` assets, without changing or stretching their subjects unnaturally.
- Restore a continuous pale blue sky and fresh green horizon, avoiding a large pure-white banner.
- Remove mobile opacity dimming; display both illustrated panels at full opacity.
- Make K–12 grade navigation remain interactive, never rasterized into an image.
- At 601–960px, put complete illustrations beneath grade controls; 961–1190px, scale the artwork to end above them; 1191px and wider, restore the reference’s side-by-side scene proportions.
- Repair the 601–700px subject-grid horizontal overflow encountered during visual QA.
- Keep the illustrated navigation images, cards, popups, and parent tools unchanged.

## Validation
- `python tools/build.py`
- `python tools/validate.py`
- `python tools/test_hero.py`: 114 checks passed across 17 widths (320–1920 px)
- `python tools/test_ui.py`: 293 checks passed
- `python tools/test_migration.py`: 15 checks passed
- `python tools/test_coverage.py`: passed

The tests run locally in Chromium against `wonderwood-play.html`. External activity/game destinations are not verified by the hero QA.

## Evidence
- Approved image: `/mnt/data/image(7).png` (user-provided, not checked into repo)
- Rendered desktop: `previews/desktop-1270.png`
- Rendered compact desktop: `previews/desktop-1024.png`
- Rendered tablet: `previews/tablet.png`
- Rendered mobile: `previews/mobile.png`

## Design QA
**Final result: passed** — no P0/P1/P2 issues with hero cropping, colour washout or overlapping grade controls at the tested viewport widths. Remaining P3: the original side illustrations intentionally scale down on mobile; the chosen responsive composition trades decorative size for unobstructed large tap targets.