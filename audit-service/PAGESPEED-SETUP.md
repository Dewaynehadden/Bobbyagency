# Activate measured mobile and desktop audits

The new website report uses actual Google PageSpeed Insights API / Lighthouse responses. It does not turn the old HTML checklist into a performance score.

## One additional Render environment variable

Keep the existing mail connector settings unchanged. Add ONE new variable to the existing **bobbyagency-audit** service:

| Key | Value |
| --- | --- |
| PAGESPEED_API_KEY | A Google API key authorized for the PageSpeed Insights API |

Obtain the key from your own Google Cloud project:

1. Start with Google's official guide: https://developers.google.com/speed/docs/insights/v5/get-started
2. Select or create a Google Cloud project; enable **PageSpeed Insights API** in the API Library.
3. Under APIs & Services → Credentials, create an API key. Restrict its allowed API to **PageSpeed Insights API**. The caller is the Render backend, so a browser HTTP-referrer restriction will block this integration. If applying IP restrictions, use the host's documented outbound IP ranges.
4. Paste the key directly into Render as PAGESPEED_API_KEY. Do not put it in GitHub, frontend JavaScript, screenshots, or chat.
5. Save/deploy the existing service. Keep Python 3, root directory audit-service, the existing Waitress start command, free compute, mail connector variables and health check unchanged.
6. Review Google's current quota/terms and set an appropriate quota limit. This adds no new paid hosting component; do not purchase an upgrade just to configure the key.

The account owner must authorize this key; the assistant does not have access to the Google Cloud account. Until a usable key is configured, the website reports a configuration error and displays no substituted scores. Existing Gmail Apps Script authorization does NOT enable the separate PageSpeed API.

## What buyers receive

- Mobile then desktop Lighthouse measurements, with genuine completion stages (no fake progress percentages).
- Performance, Accessibility, Best Practices and SEO category scores when Google returns them. Null/missing scores are not zero or a pass.
- FCP, LCP, TBT, CLS and Speed Index values as provided by the API.
- Optional page- or origin-level CrUX field data, clearly separated from lab data. No data means unavailable, not no visitors.
- Provider insights, diagnostics, savings, details/tables, manual checks, passed audits, not-applicable items and errors. Tables show the first 50 rows; original JSON retains the full response.
- Lighthouse test date, version, strategy, final URL, warnings and test conditions.
- A normalized JSON download, original Google JSON for each device, a printable two-device view (browser Print → Save as PDF), and a one-time summary email through the existing connector.
- A buyer-initiated quote request populated with measured scores and findings. Fees and actual fixes must be agreed in writing; a score does not automatically establish a billable defect.

Google's PageSpeed website is not reproduced or embedded. It may expose newer features the v5 API does not return (for example an Agentic Browsing badge). Such results are never invented. Scores can differ between repeated tests because timing, Lighthouse version, device emulation and network conditions change. The same score as an earlier screenshot is not promised.

## Hosting and retention

API requests run asynchronously so a mobile+desktop scan need not stay in one long HTTP request. One scan runs at a time on the free pilot. Clients poll using an unguessable job token. Reports/raw measurements are held in process memory for up to 30 minutes and subject to a small completed-report capacity; a restart clears them. Download evidence immediately when needed. No email/name is returned by the status API or persisted in a contacts database.

The daily limit counts buyer audit requests, each of which can make two PageSpeed API calls. Gmail/Google provider quotas also apply. This is a low-volume pilot, not a durable queue or high-scale public audit platform.

## Validation before promotion

Run a report to your OWN email after key setup. Confirm both device results, raw JSON downloads, actual email delivery, and a missing-field-data state if appropriate. Compare each result to its captured Lighthouse response rather than a separate run on pagespeed.web.dev. Preserve downloaded reports for before/after comparisons with matching strategy/version and comparable conditions.


## Public store evidence and sales context

The report now adds optional requester-submitted order status and concern, public storefront link observations, and bounded Shopify/WooCommerce catalogue sampling. It never derives sales, orders or revenue from product counts or inventory changes. Catalogue sampling uses the existing DNS-pinned public fetcher (JSON content type allowed) and at most two pages of 50 stable product IDs; variants are not counted separately. Partial counts and empty/unavailable endpoints carry explicit limitations. Public links are observed, not visited or verified as functional. Checkout, payment, order/customer data and inventory are never modified or accessed through authenticated APIs.

Sales status is always unknown in the verified-data field until an owner-authorized analytics integration exists. Requester answers remain unverified. No PPSPY account/API/scraping integration is configured: public documentation could not be retrieved from this environment, so its availability/permission was not assumed. A future estimated-sales provider requires documented access rights, attribution, timestamp and clear estimated/unverified labeling.

No new environment variables, paid provider or additional user account setup is required for these public observations. Existing Render auto-deploy should pick up the code update; if disabled, manually deploy the latest commit.
