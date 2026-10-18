# Wonderwood: privacy-first visitor analytics

Wonderwood is a site for children, so its analytics are restricted to **aggregate website traffic and performance**. The chosen service is [Cloudflare Web Analytics](https://developers.cloudflare.com/web-analytics/about/), with a cookie-free beacon. The optional script **does not run until connected**.

## What you can see

- Visits and page views (site-wide traffic, not a child-by-child counter).
- Referring websites and popular site paths.
- Approximate country, desktop/mobile/tablet and browser breakdowns.
- Page load times and Core Web Vitals.

These live numbers are available **inside your private Cloudflare dashboard**. Wonderwood's Parent/Teacher → **📊 Analytics** explains the categories and opens that dashboard. The page does not show fake zeroes or publicly expose private data. Cloudflare Web Analytics does not provide a public read-only stats API for our static site. To show real numbers directly on Wonderwood in the future, a separate secure server-side aggregate endpoint would be needed.

## Activated on Wonderwood

The site owner supplied the Cloudflare Web Analytics site beacon token on 18 October 2026. The [GitHub Pages deployment workflow](../.github/workflows/deploy-pages.yml) now has this **public site token** as a fallback, so deploying `main` inserts exactly one Cloudflare beacon. The optional GitHub Actions repository variable `CF_WEB_ANALYTICS_TOKEN`, if set, takes precedence. The beacon token is intentionally visible in website HTML; it is **not** an API key.

1. Visit [Wonderwood](https://sabersara.github.io/website-games-catalogue/) after a successful deployment, using a browser that allows the Cloudflare beacon.
2. Open [Cloudflare Web Analytics](https://dash.cloudflare.com/) for the `sabersara.github.io` hostname; reports may take several minutes to appear and are **not retroactive**.
3. To rotate the public beacon token, set a new `CF_WEB_ANALYTICS_TOKEN` Actions variable in [repository variables](https://github.com/SaberSara/website-games-catalogue/settings/variables/actions), or change the workflow fallback. [Deploy again](https://github.com/SaberSara/website-games-catalogue/actions/workflows/deploy-pages.yml).

If the Cloudflare site's hostname differs from `sabersara.github.io`, use **Manage site** in Cloudflare Web Analytics to correct it. No DNS changes are required for GitHub Pages.

## Privacy safeguards

- The deployment currently uses a public site-token fallback even if the Actions variable is absent; the beacon can be disabled by removing both the fallback and the optional variable, then redeploying.
- When present, the script loads **only** over HTTPS on `sabersara.github.io` at `/website-games-catalogue/`. Local HTML previews, offline portable copies and other GitHub Pages projects do **not** report traffic.
- No **cookies**, tracking localStorage, fingerprinting, names, logins, search text, age/grade selections, game clicks, favorite actions, video views or individual learning progress are logged by our analytics integration.
- No advertising trackers, social pixels or Google Analytics.
- The Cloudflare dashboard is account-controlled. Never put Cloudflare API credentials inside source JavaScript or public GitHub variables.
- External learning-game providers may have their own privacy policies and analytics, which are not controlled by Wonderwood.
- Before inviting children, review your disclosure and compliance duties for child-directed sites; cookie-free does not replace a legal review.

## Uninstall

Remove the public token fallback from `.github/workflows/deploy-pages.yml` **and** delete any `CF_WEB_ANALYTICS_TOKEN` Actions variable, then rerun `Deploy Wonderwood to GitHub Pages`. Future builds will omit the beacon, but previously collected aggregate data remains in Cloudflare subject to its retention controls.

## Technical details

`tools/build.py` validates the optional token and injects the Cloudflare beacon only into generated `index.html`. The workflow builds and deploys that page and assets. `wonderwood-play.html` is always offline/untracked. Source changes and game editorial data do not require a new analytics token. Internal catalogue interactions are intentionally **not** converted into events, to protect young visitors.

References: [Cloudflare setup](https://developers.cloudflare.com/web-analytics/get-started/), [traffic metrics](https://developers.cloudflare.com/web-analytics/data-metrics/high-level-metrics/), and [privacy statement](https://www.cloudflare.com/web-analytics/).
