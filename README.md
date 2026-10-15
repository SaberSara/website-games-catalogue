# Wonderwood — Learning Games Catalogue V4

A friendly, colourful, California-standards-informed educational game catalogue for **Kindergarten to Grade 12**.

Open `index.html` to try the fully self-contained version. The source is in `src/`, `data/` and `assets/`. The HTML/CSS/JS is responsive, and its child-facing pages have no ads, trackers or accounts built in. Third-party games follow their own policies.

## What is included
- The approved bright, **white-centred forest banner** with the fox, owl, wooden signs and multicolour Wonderwood wordmark.
- Locally illustrated Home, Subjects, Favorites and Parent/Teacher top-navigation icons (no top-nav emojis).
- K–12 grade groups, eight subjects, topic filters, search, full-card click, favorites and clear browser/mobile-app badges.
- Compact thumbnail-first game popup with collapsible grown-up notes.
- Parent/Teacher curriculum view and local editing/import/export.

## Edit and rebuild
Edit `data/curriculum.json`, `data/games.json`, `src/template.html`, `src/styles.css`, `src/app.js` and `assets/`.
Run:
```sh
python3 tools/validate.py
python3 tools/build.py
python3 -m http.server 8000
```
Then open `http://localhost:8000`. Rebuilding creates a normal static index.html that uses local source files and assets. The initial committed index.html is portable and embeds everything; this is why it can run without a web server. A local editor save does **not** commit to GitHub—export games.json, review, update data, rebuild and commit.

## Content status
433 editorial topic shelves, including starter Grades 2–12 suggestions rather than a verified full standards audit. 28 starter resource records; 14 have scoped publisher no-ad statements; 14 remain pending review. External games have **not** been independently play-tested. No-ad claims do not guarantee absence of analytics, purchases, third-party links or accessibility barriers.

## Release status
Source uploaded to this GitHub repository; **no public GitHub Pages site or deployment is configured** by this commit. Test external destinations, grade fit, accessibility and real-device browser behavior before publishing. See `docs/` for scope and verification notes.
