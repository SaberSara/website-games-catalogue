# V4 visual QA and verification

The screenshot supplied by the owner on 15 October 2026 is the approved hero reference: bright forest side panels, fox and left wooden sign, owl and right wooden sign, multicolour logo, white-centred stage, and grade controls. V4 uses this composition and replaces the four header emoji glyphs with custom illustrated PNG files.

**Local testing:** 293 interface checks passed, plus 10 in-memory migration tests. Clean headless Chromium captures at 1270px and 390px had four header icon images, zero JS page errors and zero missing images. Core interaction checks included K–12 grade/subject/topic filters, popup thumbnail and focus behavior, favourites, editor import/export, no horizontal overflow and reduced-motion settings.

**Limitations:** Browser captures used `set_content`; direct file/hosted-site navigation was restricted. Actual third-party games, app installations, persistence on a published domain, Safari, Firefox, assistive technology and physical touch devices still require testing.

**Visual QA result: passed** for V4 banner/navigation changes; publication review remains pending.
