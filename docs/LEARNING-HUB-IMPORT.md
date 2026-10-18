# Learning Hub import — 18 October 2026

## What was imported

The project owner supplied `aropl-kids-learning-hub-main.zip` and confirmed that its links were **teacher verified**. We extracted **71 activity cards** from `index.html`, omitted the separate Academy promotion, and deduplicated the one repeated **Solar System Explorer** card (source positions 39 and 56). The result is **70 new unique catalogue records** and **70 resized local WebP thumbnails**, appended to the existing 152 entries. Import order is stored as `hubOrder` and `sourcePositions`, including original subject grouping via `hubSection`. The exact source-card trail is in `HUB-IMPORT-MANIFEST.json`.

The resulting source catalogue contains **222 entries**, of which **118** retain publisher no-ad evidence, **70** have user-attested teacher verification, and **34** remain hidden for future review. That is **188 visible** resources; some are articles, PDFs, research references, videos or simulations rather than games.

## Scope of verification

"Teacher verified" reflects the **project owner's attestation** about the source Hub's links. It does **not** establish that this assistant inspected each external page, that it is advertisement-free, that its prices are free, that it has been hands-on tested, or that it aligns to a particular California standard. This import does not synthesize third-party advertising clearance. Teacher-curated records carry `review.status="teacher_verified"` and `review.advertisingStatus="not_independently_checked"`. Child-facing popups show these as separate statements; publisher no-ad records keep their distinct review status.

A successful local static-data test is **not** confirmation that linked third-party pages or videos are currently reachable. The supplied static source may refer to sites that change or require login.

## Original lessons and school grades

The Hub has four source sections: **Assessments, Math, English, Science**. Its “English” section contains cross-disciplinary informational reading, biology, environment and health links. Resources were therefore assigned editorial Wonderwood subjects **by actual topic**, not by section label alone; the original section and lesson tag remain in the data. The Grade 9 assessments and Grade 9 DNA replication activity retain their explicit Grade 9 label; the electromagnet video has a source title explicitly stating *Science 5*, recorded as Grade 5. Other age/grade placements are **editorial suggestions**, flagged in `gradeEvidence`—not teacher-supplied exact grade claims. Curriculum topic IDs are existing editorial clusters, not newly invented standard codes.

## Artwork and video hosting

- Every imported record uses its own **original source thumbnail** from the supplied ZIP. The images are downscaled and converted to `.webp` for quick loading, then stored in Wonderwood `assets/`, so card artwork does not depend on a remote Hub image server. The same image is shown in the popup.
- **Math Smash 3D** and **Solar System Explorer** link to their existing `/games/.../index.html` locations on the original Hub's Vercel host. Their executable game code is **not copied** to Wonderwood.
- The two `.mp4` videos are **not uploaded**. Their cards open the linked original creator YouTube videos using the `creditLink` values recorded in the Hub's HTML: Joshua Alejo (electromagnets) and yourgenome (DNA replication).
- No Academy destination, branding asset or promotional card is imported.
- A biology study site mentions an access code in the original source; this import does not publicly repeat that code. Users should check access with their teacher.

## Maintaining the catalogue

The first 152 existing records remain in their original order. New records follow in their original source order. The editor still keeps local browser drafts only; it does not push to GitHub. Seed revision **3** appends these records to older valid user drafts, preserving saved edits and respecting previously deleted revision-2 activities. Once migrated, a removed imported activity stays removed.

To reproduce the import locally (optional developer tools required):

```bash
python -m pip install beautifulsoup4 pillow
python tools/import_learning_hub.py --hub-zip /path/to/aropl-kids-learning-hub-main.zip
python tools/validate.py
python tools/build.py
python tools/test_hub_import.py
```

On GitHub Pages, the deployment workflow builds `index.html` from `src/` and `data/` on every push to `main`. Confirm external destinations and suitability with a teacher before distributing the public site to children.
