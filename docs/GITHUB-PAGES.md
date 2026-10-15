# Publish Wonderwood on GitHub Pages

The repository contains a no-backend, static site. The workflow [deploy-pages.yml](../.github/workflows/deploy-pages.yml) validates the curriculum and game catalogue, rebuilds `index.html`, and automatically publishes **only** the generated HTML, the runtime JavaScript/CSS, and illustration assets.

## One-time GitHub Pages activation

1. Open [repository Settings → Pages](https://github.com/SaberSara/website-games-catalogue/settings/pages) while signed into the repository owner account.
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Open [Actions → Deploy Wonderwood to GitHub Pages](https://github.com/SaberSara/website-games-catalogue/actions/workflows/deploy-pages.yml). If the first run failed before Pages was enabled, select **Run workflow** on `main` or rerun the failed run.
4. Wait for a successful **Deploy to GitHub Pages** job; use the live URL shown under **Settings → Pages** (usually `https://sabersara.github.io/website-games-catalogue/`).

### Repository visibility and access

The repository is currently **private**. GitHub Pages for private repositories requires an eligible plan (GitHub Pro, Team or Enterprise). Free accounts can use GitHub Pages in **public** repositories. Do **not** change repository visibility without deciding whether to publish its code and documentation. A GitHub Pages website is normally **publicly accessible even when the repository is private**.

## Updating the website

Edit `data/games.json`, `data/curriculum.json`, `src/`, or `assets/`, and commit to `main`. The workflow validates and rebuilds the site from tracked source so the latest games are published automatically. You can also click **Run workflow** to republish.

The browser's Parent / Teacher editor stores local drafts only. To publish an edit for all visitors, export `games.json`, review it carefully, replace the repository's `data/games.json`, and commit. There is no login, database, or server-side admin area.

## Safety and scope

Only `index.html`, `src/styles.css`, `src/app.js`, and `assets/*` become site files. Source documentation, scripts and JSON files are not deployed separately (although catalogue data necessarily appears inside the generated HTML so browsers can render it).

Links may lead to third-party websites with distinct privacy practices. Some reviews are documentary rather than hands-on. Verify exact external games and age suitability before distributing this publicly to children. No child's personal data is collected by this site.

## Troubleshooting

- **Pages unavailable:** check repository plan/visibility eligibility in Settings → Pages.
- **No site yet:** enable Source → GitHub Actions, then manually run/re-run the workflow.
- **404 after successful deploy:** give GitHub a few minutes, then check the Pages settings' actual URL and the workflow run.
- **Broken assets:** confirm the deployment artifact contains `index.html`, `src/` and `assets/`; this workflow preserves their relative paths for GitHub project URLs.
- **Build error:** the workflow checks curriculum-link validation before deployment. Fix any invalid records and push again.
