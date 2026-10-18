# Wonderwood: privacy-first visitor analytics

Wonderwood is a site for children, so its analytics are restricted to **aggregate website traffic and performance**. The chosen service is [Cloudflare Web Analytics](https://developers.cloudflare.com/web-analytics/about/), with a cookie-free beacon. The optional script **does not run until connected**.

## What you can see

- Visits and page views (site-wide traffic, not a child-by-child counter).
- Referring websites and popular site paths.
- Approximate country, desktop/mobile/tablet and browser breakdowns.
- Page load times and Core Web Vitals.

These live numbers are available **inside your private Cloudflare dashboard**. Wonderwood's Parent/Teacher → **📊 Analytics** explains the categories and opens that dashboard. The page does not show fake zeroes or publicly expose private data. Cloudflare Web Analytics does not provide a public read-only stats API for our static site. To show real numbers directly on Wonderwood in the future, a separate secure server-side aggregate endpoint would be needed.

## Connect Cloudflare to the existing GitHub Pages site

1. Sign in or register at [dash.cloudflare.com](https://dash.cloudflare.com/).
2. Go to **Web Analytics → Add a site**.
3. Enter the hostname **`sabersara.github.io`** (do not include `https://` or `/website-games-catalogue/`). This website is hosted on GitHub Pages, not proxied through Cloudflare; you **do not** need to change DNS or hosting.
4. From the new site's **Manage site**, copy the **site token from the JavaScript beacon snippet** (the value of `token` in `data-cf-beacon`). **Do not copy an API secret or account token**.
5. In GitHub, open [repository Settings → Secrets and variables → Actions → Variables](https://github.com/SaberSara/website-games-catalogue/settings/variables/actions), and add a **repository variable** named `CF_WEB_ANALYTICS_TOKEN` with the site's beacon token. This browser token is intentionally public, unlike API credentials.
6. Open [Actions → Deploy Wonderwood to GitHub Pages](https://github.com/SaberSara/website-games-catalogue/actions/workflows/deploy-pages.yml), select **Run workflow** on `main` (or commit a normal change to trigger deployment).
7. Visit **https://sabersara.github.io/website-games-catalogue/** and open the website yourself; allow a few minutes, then check **Cloudflare → Web Analytics** for the new visit and performance statistics. Analytics starts from activation, not retroactively.

## Privacy safeguards

- When the variable is absent, **no analytics script or network requests** are added by Wonderwood.
- When present, the script loads **only** over HTTPS on `sabersara.github.io` at `/website-games-catalogue/`. Local HTML previews, offline portable copies and other GitHub Pages projects do **not** report traffic.
- No **cookies**, tracking localStorage, fingerprinting, names, logins, search text, age/grade selections, game clicks, favorite actions, video views or individual learning progress are logged by our analytics integration.
- No advertising trackers, social pixels or Google Analytics.
- The Cloudflare dashboard is account-controlled. Never put Cloudflare API credentials inside source JavaScript or public GitHub variables.
- External learning-game providers may have their own privacy policies and analytics, which are not controlled by Wonderwood.
- Before inviting children, review your disclosure and compliance duties for child-directed sites; cookie-free does not replace a legal review.

## Uninstall

Delete the `CF_WEB_ANALYTICS_TOKEN` repository Actions variable and rerun `Deploy Wonderwood to GitHub Pages`. Future pages will contain no Cloudflare script, but already-collected aggregate data remains in the Cloudflare account subject to its retention controls.

## Technical details

`tools/build.py` validates the optional token and injects the Cloudflare beacon only into generated `index.html`. The workflow builds and deploys that page and assets. `wonderwood-play.html` is always offline/untracked. Source changes and game editorial data do not require a new analytics token. Internal catalogue interactions are intentionally **not** converted into events, to protect young visitors.

References: [Cloudflare setup](https://developers.cloudflare.com/web-analytics/get-started/), [traffic metrics](https://developers.cloudflare.com/web-analytics/data-metrics/high-level-metrics/), and [privacy statement](https://www.cloudflare.com/web-analytics/).
