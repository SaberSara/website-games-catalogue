# Wonderwood K–12 resource expansion — verification

Updated 15 October 2026.

## Confirmed in local build

- JSON schema/source validator: 13 grades, 433 topic shelves, 152 resource records.
- 118 publisher-policy-backed records visible; 34 pending records are withheld from child browsing.
- Every grade K–12 has visible curated resources; 225 of 433 editorial topic shelves have at least one visible mapped resource.
- 293 UI checks passed in local headless Chromium, including 320–1920px responsive layouts, navigation, cards, popup, edit/review, and import/export.
- 15 in-memory draft migration checks passed. Previous user edits and deletions are preserved, and new K–12 seeds append to legacy drafts.
- Rebuilt index.html and portable HTML locally. GitHub main contains the revised catalogue and embedded homepage data.

## Not independently verified

No third-party external games were play-tested for live advertising, account requirements, in-app payments, accessibility, browser/mobile support, safety, or age-appropriate controls. Publisher no-ad statements are not runtime certification; Khan Academy may display labeled sponsorships. California grade/topic matches are editorial guidance, not full standards certification.

These browser tests use Playwright set_content with mocked storage. Real hosted-origin persistence, production deployment, Safari/Firefox and assistive technology were not tested.

See docs/CURATION.md, docs/RESOURCE-COVERAGE.md, docs/coverage-test-report.json, docs/ui-test-report.json and docs/migration-test-report.json.
