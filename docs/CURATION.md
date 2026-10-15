# Resource curation and advertising evidence — K–12 expansion

Updated 15 October 2026. **152 records total: 118 publisher-claim-backed visible entries and 34 pending review entries hidden from children.** Includes 124 new research records compared with V4, spanning PhET, Code.org, Khan Academy, Starfall, Chrome Music Lab, iCivics and Mission US.

## Evidence rule

The visible state `publisher_claim_reviewed` means documentary evidence of an explicit, scoped publisher no-ad statement. It does not mean that an external game was independently tested or certified. For the supplied seed data, **`runtimeTested` is false for every record**. The compact popup still displays “Not play-tested”. The local curator attestation form can change an individual local draft only after a curator explicitly confirms the required checks.

“No ads” is separate from cost, purchase prompts, analytics, third-party links, login requirements and curriculum fit. Evidence for one app does not automatically apply to another platform version. Exact official destinations and scope notes are retained in `data/games.json`.

The 23 inherited V2 records and their nine publisher-claim decisions are documented in `CURATION-V2-ARCHIVE.md`. Those research records are retained, not silently re-audited. Fourteen inherited candidates remain in the review queue, plus twenty new pending links.

## Publishers with explicit advertising-policy evidence

| Provider | Visible resources | Evidence scope / cautions |
|---|---:|---|
| PhET (University of Colorado Boulder) | 69 including five inherited records | `https://phet.colorado.edu/en/privacy-policy` states no advertisements or ad tracking on the official PhET site and simulations. Interactive explorations, not necessarily independent games. Some analytics disclosed. |
| Code.org | 13 | `https://studio.code.org/terms-and-privacy` prohibits advertising on Code.org services. Some curriculum routes require classroom use or teacher setup. Under-13 users cannot use App Lab, Game Lab, or Web Lab outside a classroom. Courses A–F and Sprite Lab are differentiated. |
| Khan Academy | 22 plus existing Khan Academy Kids variant | `https://www.khanacademy.org/about/privacy-policy` prohibits third-party advertisements; **labeled sponsorships or supporter messages may appear**. Its website contains practice exercises and videos, not just mini-games. |
| Starfall | 12 | `https://teach.starfall.com/privacy` states no advertising. Some collections mix public and member-only material. |
| Teach Your Monster | 2 approved iOS variants | Publisher app-store no-ad claims cover particular apps, not automatically their browser equivalents. Trial/purchase requirements are retained. |

The figures above count **records**, not unique learning platforms or standalone games. The original ad-evidence decisions remain unchanged. Every new entry has `runtimeTested: false` and the topic associations are editorial suggestions.

## Review queue — withheld from children's views

Chrome Music Lab (6), iCivics (9), Mission US (5), and 14 inherited links remain marked `needs_review`. Some of these are likely excellent experiences, but no sufficiently scoped and current no-ad claim was confirmed for their exact launch experience. Mission US experiences can feature slavery, imprisonment, discrimination and other sensitive historical topics; the publisher recommends a grown-up preview. The current Mission US entries land on the official mission selection page rather than individual playable URLs and should be deep-linked during review.

## Link-specific details

Each record in `data/games.json` preserves an exact HTTPS destination, grades, subject and topic IDs, the price qualifier, device, source evidence or pending-review reason, a parent follow-up prompt, and whether it has actually been play-tested. Link validation verifies shape and curriculum mapping only; no claim is made that every third-party site will remain live or load on every device. For grade and subject counts see `docs/RESOURCE-COVERAGE.md`.

## Before public launch

An adult curator should open and play each exact destination on supported devices, check advertising/sponsors/promotions, payments, accounts, external links, instructions, reading load, keyboard/touch controls and accessibility, then review grade/topic fit with an educator. Record the actual play-test date and review notes. Return changed, broken or unsuitable links to the hidden queue. Revisit publisher evidence periodically.

The grown-up popup is informational. It is not parental authentication, consent capture or a security boundary. The catalogue's local editor is not a multi-user administration system.
