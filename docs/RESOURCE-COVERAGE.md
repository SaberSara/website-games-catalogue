# K–12 activity-link coverage — 15 October 2026

This is the current link catalogue, not a claim that every California standard or topic has a matching game. Only records with scoped publisher-policy evidence are displayed to children; further candidates remain grown-up-only.

- **152 catalogue records:** 118 visible publisher-policy-backed entries, 34 pending adult review.
- **13 grade levels** have visible activities from Kindergarten through Grade 12.
- **225 of 433 editorial topics** have at least one visible record tagged to that topic. This is **editorial matching**, not an educator-approved standards audit.
- **0 third-party destinations were hands-on tested** for advertising, login redirects, payments, device controls, safety or accessibility.
- Publisher statements are not universal guarantees. Khan Academy's website prohibits third-party ads but permits labeled sponsor messages; Starfall has member-only items; some Code.org projects require a class/account.

## Visible resources by grade

Counts are **distinct catalogue cards for that grade**; one card can cover multiple topics and subjects. Grade 9–12 math/science suggestions reflect pathways and electives, not required grade-specific classes.

| Grade | Visible cards | Reading/ELA | Math | Science | History | Art/Music | Health | PE | Coding |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Kindergarten | 14 | 6 | 6 | 0 | 0 | 0 | 2 | 0 | 2 |
| Grade 1 | 15 | 6 | 6 | 2 | 0 | 0 | 1 | 0 | 2 |
| Grade 2 | 18 | 2 | 11 | 2 | 0 | 2 | 1 | 0 | 4 |
| Grade 3 | 27 | 1 | 17 | 4 | 0 | 3 | 0 | 0 | 5 |
| Grade 4 | 31 | 1 | 15 | 10 | 0 | 3 | 0 | 0 | 5 |
| Grade 5 | 29 | 1 | 15 | 8 | 0 | 3 | 0 | 0 | 5 |
| Grade 6 | 31 | 1 | 18 | 6 | 1 | 4 | 0 | 0 | 4 |
| Grade 7 | 33 | 1 | 18 | 8 | 1 | 4 | 0 | 0 | 4 |
| Grade 8 | 38 | 1 | 13 | 18 | 1 | 4 | 0 | 0 | 4 |
| Grade 9 | 53 | 2 | 14 | 32 | 0 | 3 | 0 | 0 | 4 |
| Grade 10 | 49 | 2 | 12 | 29 | 1 | 3 | 0 | 0 | 4 |
| Grade 11 | 43 | 1 | 11 | 26 | 1 | 3 | 0 | 0 | 3 |
| Grade 12 | 43 | 1 | 11 | 26 | 1 | 3 | 0 | 0 | 3 |

## What these numbers do **not** mean

- A blank PE or health shelf **must not** be filled with unrelated on-screen quizzes. Suitable teacher-led movement, nutrition and wellbeing games are still being reviewed.
- An empty history shelf does not mean history is missing from the curriculum. iCivics and Mission US options exist in the queue but require publisher-policy and age-content checks. Mission US links currently reach the official selection page, not individual missions.
- PhET simulation links are for guided exploration, not automatically an independent game or mastery test.
- A link's publisher no-ad statement is different from a documented adult play-test of that specific game on that specific device. Every record still says `runtimeTested: false`.
- `thumbnailAsset` selects original Wonderwood **themed illustrations**, never a purported screenshot from the external game.

## Where to edit

Edit `data/games.json`, not generated HTML. Each record has `grades`, `subjects`, `topicIds`, `priceLabel`, `platform`, `devices`, review evidence and an exact official URL. Rebuild with `python tools/build.py`, then run `python tools/validate.py`, `python tools/test_coverage.py`, `python tools/test_migration.py` and optionally `python tools/test_ui.py`.

For provider policy and restrictions see `docs/CURATION.md`. For full machine-readable coverage see `docs/coverage-test-report.json`.
