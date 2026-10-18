# Wonderwood V4 — K–12 learning catalogue

## GitHub Pages website

**Publishing is configured but not yet activated.** Open [Settings → Pages](https://github.com/SaberSara/website-games-catalogue/settings/pages), choose **GitHub Actions** under **Build and deployment → Source**, then run or rerun [Deploy Wonderwood to GitHub Pages](https://github.com/SaberSara/website-games-catalogue/actions/workflows/deploy-pages.yml) on `main`. Once the deployment is successful, use the actual website URL shown in Pages settings (normally `https://sabersara.github.io/website-games-catalogue/`).

The workflow validates and rebuilds the source, then uploads only the generated web page, runtime CSS/JavaScript and local images; it automatically republishes after pushes to `main`. See [GitHub Pages setup and eligibility](docs/GITHUB-PAGES.md). The site is publicly accessible even if the code repository remains private. GitHub Pages with private repositories requires an eligible paid plan.

Updated **15 October 2026**. This is an editable static website build. GitHub code integration is separate from publishing a live site. Updated using the approved bright hero-banner screenshot and matching illustrated top navigation. Repository integration is tracked separately.

## Teacher-curated Learning Hub import — 18 October 2026

A ZIP supplied by the project owner provided **71 activity cards**: **70 unique links**, including two videos that open their credited YouTube sources. The one repeated Solar System Explorer link was deduplicated. All **70 original thumbnails** are stored locally as optimised WebP files. The Academy promotional destination was excluded. Resources retain source order and original lesson tags, with grade/subject placements identified as editorial where the source did not give an exact grade.

Teacher verification is **user-attested**, not an independent advertisement, gameplay or availability audit. The new popup labels teacher verification separately from unchecked advertising status.

The resulting catalogue has **222 entries**, with **188 shown** in child browsing (118 publisher no-ad claims + 70 teacher-verified selections) and 34 hidden candidates. See [the curation explanation](docs/LEARNING-HUB-IMPORT.md) and [the extracted source mapping](docs/HUB-IMPORT-MANIFEST.json). Updates pushed to main will rebuild GitHub Pages when Pages is enabled.

## Open the website

Open **`wonderwood-play.html`** in a modern browser. This portable file includes the interface, artwork, curriculum and starter links. It needs no server to browse; external games need internet access. A file previewer may show HTML source instead of running it—open the downloaded file in a browser.

The catalogue has no advertisements, child accounts or backend. **Visitor analytics are optional**: once a Cloudflare Web Analytics site token is configured for GitHub Pages, a cookie-free traffic beacon reports aggregate website visits and loading performance. Local/portable previews remain untracked. No child actions, grade choices, search terms or individual game clicks are sent to analytics. See [analytics setup and privacy](docs/ANALYTICS.md). This does **not** describe the policies of third-party games.

## What changed from V3

- Restored the approved **white-centred bright hero banner** with the exact illustrated left and right signage cropped from the supplied visual reference.
- Replaced only the four top navigation emoji glyphs with **locally stored glossy illustrated images**: home, book, star, people. Emojis remain in other playful areas.
- Kept the original multicolour Wonderwood logo, K–12 selector, filterable cards, platform badges, compact thumbnail-first game popup, favorites, parent editor, and motion/accessibility rules.
- The mobile hero uses softened illustration panels so text and grade controls stay readable.

## What changed from V2

- Keep the approved colorful woodland layout, image-led subject tiles, selected playful emojis and practical UI icons. Not every emoji was replaced.
- Compact game popup: repeated thumbnail, one-line introduction, device/cost/grade tiles, concise publisher-evidence status, collapsed grown-up notes and one clear launch action.
- Short labels such as “Subjects”, “All games”, “Explore”, “Open” and “App page”. Detailed curriculum and evidence remain available to adults.
- All **13 California grade levels, K–12**, grouped into K–2, 3–5, 6–8 and 9–12. These are catalogue navigation groups, not universal subject-standard bands.
- All grades work in search, subjects, topic filters, quick-topic panels, resource editing and JSON validation. Older-grade subject labels use English, History, Wellbeing, PE & Fitness and Computing.
- A grade-by-grade set of PhET maths/science simulations, Code.org coding activities, Khan Academy practices, and Starfall elementary games added with scoped documentary evidence. These are suggested editorial mappings, not a standards assessment.
- Retain full-card activation, independent favorites, clear app/browser indicators, hover/press animations, keyboard operation and reduced-motion support.

## Content scope — important

**433 topic shelves** = the previous 98 Kindergarten/Grade 1 clusters + 335 new starter shelves for Grades 2–12. The new shelves are expressly marked **exact-code review pending**. They are not a full California standards audit, complete course, prescribed pacing sequence or state endorsement. High-school mathematics/science shelves use shared course topics rather than inventing a compulsory grade sequence.

**222 resource records** = 118 records with publisher no-ad claims and 34 candidates withheld from child browsing pending adult review. Resources span all 13 grades and cover 263 of the 433 topic shelves with at least one visible item. A topic association is editorial, not a guarantee of California-standards mastery. Some grade/subject/topic combinations remain empty—especially health, movement, and younger history. Records include collections, app variants, simulations and creative projects, not 152 distinct scored games.

The publisher claim for Khan Academy concerns **third-party advertising**; Khan Academy may show labeled sponsor/supporter messages. This distinction is shown in the adult evidence notes. Code.org courses may require teacher setup or accounts; PhET simulations are explorations rather than quizzes. Starfall offers some member-only activities. Read `docs/RESOURCE-COVERAGE.md`.

**No external games were hands-on play-tested for this build.** Documentary evidence is not a safety guarantee. The visible activity popup says when runtime testing has not occurred. No-ads does not mean no analytics, no purchases, no external links or complete accessibility. PhET's privacy policy discloses limited usage analytics. Thematic artwork is not an official screenshot or endorsement.

Read `docs/CURRICULUM.md` and `docs/CURATION.md` before adding or publishing content.

## Edit and rebuild

The build and data validation use Python's standard library:

```sh
python tools/validate.py
python tools/build.py
python -m http.server 8000
```

Use `python3` where appropriate. The optional final command serves the source folder at `http://localhost:8000`; Ctrl+C stops it. No Node packages, API keys or paid service are needed to run the website. The generated files are `index.html` (separate local assets and source files) and `wonderwood-play.html` (portable all-in-one file). Edit `src/` and `data/`, then rebuild rather than independently editing both generated HTML copies.

| Location | Purpose |
| --- | --- |
| `src/template.html` | Page structure and accessible controls |
| `src/styles.css` | Woodland design, compact popup, responsive layouts and motion |
| `src/app.js` | Navigation, filtering, popup, favorites, local editor and validation |
| `data/curriculum.json` | Grades, subjects, topics, scope notes and source register |
| `data/games.json` | Destinations, access, cost, suggested topics and review evidence |
| `assets/` | Local decorative WebP assets reused from the approved V2 build |
| `previews/` | Browser-rendered V3 screenshots and comparisons |
| `docs/reference/` | V2 reference captures for the design comparison |

## Manage links

Open **Parent / Teacher → Manage links**. Add or edit a title, official HTTPS destination, device/access type, price, grades, subjects and topics. New or edited links return to **Review queue**. A curator can record an explicit publisher no-ad statement and attest to a hands-on check; the UI does not independently verify that attestation.

Edits and favorites are **local browser drafts only**. Export `games.json` for backup. To publish a local edit, replace `data/games.json` with that export, run validation/build, and deliberately deploy the generated static files. Importing or saving in this editor does not write to GitHub or update anybody else's browser.

The expanded build retains the V3 draft key `wonderwood-catalogue-v3`; favorites retain the V2 key. **Seed revision 2** merges the 124 newly introduced links into valid legacy drafts while preserving existing titles/notes and intentionally removed V2/V3 records. After migration, the local draft is stamped, so intentionally removing a new game stays removed on subsequent loads. A different filename/origin may not share local storage; JSON export/import is still the reliable handover. Migration tests use an in-memory stub, **not actual browser-origin persistence**.

## Verification

**293 interface checks passed**, plus **15 mocked-storage migration checks**. They cover grade/subject paths, compact popup behavior, full-card/keyboard interactions, favorites, imports, edit/review states, reduced motion and responsive overflow. Check counts include repeated grade/subject/viewport cases; they are not 303 independent feature audits.

The browser tests rendered the actual standalone HTML in headless Chromium through `set_content`. Real local/hosted navigation is blocked by this environment's browser policy. Thus external handoffs, hosted/file-origin persistence, actual app installs, user downloads, Safari/Firefox, real touchscreens and assistive-technology use remain untested.

Optional test tooling (not website runtime dependencies):

```sh
python -m pip install playwright
# Install/provide Chromium for your own environment, then set CHROMIUM_PATH if needed.
python tools/test_ui.py
python tools/test_migration.py
python tools/capture.py
```

The capture script defaults to `/usr/bin/chromium`; edit it or use the environment variable supported by the other test scripts when necessary. The reports and precise limitations are in `docs/VERIFICATION.md`, `docs/ui-test-report.json`, `docs/migration-test-report.json` and `design-qa.md`.

## Before public launch

Verify each exact third-party destination on supported devices, complete educator review of the curriculum and grade fit, test real-origin persistence and external handoffs, perform a proper accessibility review, and decide who can publish catalogue changes. Do not treat the local editor as authenticated administration or the popup as a parental-control/security gate.

GitHub integration status and manual deployment details: `docs/INTEGRATION.md`.

## Visitors and analytics

Open **Parent / Teacher → 📊 Analytics** for a privacy-focused traffic overview and a link to your Cloudflare dashboard. The public Cloudflare site token is configured in the GitHub Pages deployment workflow (an optional Actions variable `CF_WEB_ANALYTICS_TOKEN` can override it). The beacon reports aggregate visits and performance **only on the deployed Wonderwood site**, not offline previews. Visitor totals remain private to Cloudflare; no placeholder numbers are shown. See [analytics instructions and opt-out](docs/ANALYTICS.md).
