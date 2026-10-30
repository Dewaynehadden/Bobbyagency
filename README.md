# Bobbyagency — new portfolio website

This is a **separate new website**, built from scratch using Detruth Agency as the visual and structural reference. It lives in `/workspace/new-portfolio` and is independent of the existing `/workspace/Bobby` checkout. No symlinks or shared source files connect the two sites. The previous BobbyDev files have been restored.

## Run

```sh
cd /workspace/new-portfolio
python3 -m http.server 3001 --bind 0.0.0.0
```

No installation, build, API keys, database, or external fonts are required. Use any static web host. Keep this site's server on port 3001 so it does not conflict with the original website on port 3000.

## Included

- Bobbyagency name and a new gold monogram.
- Black and gold sticky navigation, a three-slide responsive banner carousel, and platform strip.
- A personal store-review request with public URL validation.
- Twelve service cards with detail dialogs and service-specific enquiries.
- Founder and expertise orbit, with a full founder profile dialog.
- Searchable portfolio, category filters, pagination, and keyboard-accessible project walkthrough tabs.
- Existing demo links, founder photos, testimonial video, and attributed review excerpts from the previous public portfolio.
- FAQs, contact channel cards, floating contact shortcuts, and factual privacy/process information.
- Native dialog focus management, mobile navigation, reduced-motion support, and local assets.

## Enquiries and store reviews

The forms validate input and prepare an email in the visitor's email application. The visitor must send the email. The website does not submit, store, or upload form details. WhatsApp is also available directly.

The store-review form requests a **personal review**. It does not automatically crawl, score, or audit the submitted website. Never request passwords or store admin access through these forms.

The existing email, WhatsApp, Upwork, Fiverr, LinkedIn, and Telegram links are retained from the earlier portfolio. Change them in `index.html` and the email destination in `app.js` if the new brand will use different contacts.

## Files

- `index.html`: page structure, service cards, contact details, dialogs, FAQs, and metadata.
- `styles.css`: responsive layout, design tokens, and animations.
- `terms.html`: full terms, deposits, refund, privacy, and contact policy, copied from the existing terms page with the Bobbyagency name.
- `terms.js`: independent terms-page mobile navigation and footer year.
- `app.js`: navigation, carousel, search/filtering, dialogs, and email briefs.
- `site-data.js`: service detail content and portfolio records. When changing service names, keep the corresponding static card text and enquiry options in `index.html` consistent.
- `assets/`: locally served images, SVG illustrations, monogram, and existing testimonial video.
- `scripts/smoke.py`: functional browser validation.

## Content provenance

Detruth Agency was inspected on desktop and mobile to guide the navigation, banner arrangement, gold accents, section order, service card hierarchy, portfolio controls, FAQs, and contact layout. Its source code, company identity, staff, client statistics, revenue claims, and review counts are not reproduced.

Founder photos, demo screenshots, testimonial video, review excerpts, and public project/profile links come from `Dewaynehadden/dewaynehadden.github.io`, as requested. Demos are explicitly labeled. Review excerpts link to their original published source; they have not been independently authenticated. The orbit shows the real founder's service areas, rather than invented team members.

## Browser checks

With Playwright and system Chromium available, run:

```sh
python3 scripts/smoke.py
```

The server must already be running. The test uses `/usr/bin/chromium`; adjust that path if your machine installs Chromium elsewhere. Optional overrides: `PORTFOLIO_BASE_URL` and `PORTFOLIO_ARTIFACTS`.

The checks exercise all service dialogs, enquiry validation and encoded email briefs, review requests, carousel controls, portfolio filters/search/pagination, walkthrough keyboard controls, FAQs, founder profile, local images, video metadata, responsive widths, mobile navigation, and dialog focus handling. Screenshots and a JSON report are written outside the project under `/tmp/new-portfolio-validation` by default. Email delivery and third-party account ownership are outside these local checks.

## Publish separately

This website uses its own repository: `https://github.com/Dewaynehadden/Bobbyagency`. Its files belong at that repository’s root. Do not upload them into the existing Bobby repository.

For GitHub Pages, select the new repository's chosen branch and root directory in Settings → Pages. The site is static and needs no build command. The source repository is separate from Bobby. Uploading the source does not enable GitHub Pages; that publishing setting must be configured separately.

## Paystack payments

The announcement bar’s **Make a Payment** link on the homepage and terms page opens the public Paystack-hosted payment page at `https://paystack.shop/pay/wd0c70e6o9` in a new tab. No Paystack API keys are included or required. Payment processing happens on Paystack, outside this static website.

## Video success stories

The Success Stories navigation link opens the client-feedback section. Eight user-uploaded videos live in `assets/stories/`, alongside locally generated poster images; the prior testimonial remains as the ninth story. All videos retain their original H.264/AAC tracks and are remuxed for fast-start playback. Videos have native controls, do not autoplay or preload their content, and pause when another video starts or they leave the visible gallery. Both video sections use manual carousels with two horizontal 16:9 players side by side on desktop/tablet and one readable player on phones. Previous/next buttons, page dots, position counters, swiping, and arrow/Home/End keys support browsing. Portrait footage is contained without cropping. Run `python3 scripts/success_stories.py` against the local server on port 3001 for targeted functional checks.

## Sales-results draft

The `#sales-proof` section contains eight uploaded Shopify dashboard recordings with local poster images and native playback controls. Its four summary cards show the actual recording count, platform, report focus, and on-demand viewing; the reference site’s aggregate revenue, growth, order totals, and verification claims are not copied. Identifying browser and customer-table areas are blurred in the website copies of desktop recordings; the uploaded originals remain outside the repository and are unchanged. This section is included in the website release. Run `python3 scripts/sales_results.py` against the local server on port 3001 to validate the section. The sales reports use the same responsive carousel pattern as client recommendations.

## Service images and rotating expertise wheel

All 28 service cards and detail dialogs use locally hosted photographic images, with credits in `assets/services/photos/ATTRIBUTION.md`. These are illustrative stock and previously supplied founder photographs, not claimed client projects. The earlier generated image sheet is retained as an unused historical asset.

The outer expertise wheel rotates once every 60 seconds (about 10 seconds between the six service positions); the founder stays fixed and each service label counter-rotates to stay upright. Hovering or focusing within the wheel pauses it. A Pause/Resume control is provided, and system reduced-motion preferences disable rotation. Skill buttons continue to open service details. These updates are included in the website release.

## Homepage photographic banners

The three homepage banners use locally hosted photography: an ecommerce product arrangement, a laptop workspace, and the existing founder photograph. Source links and the Start Bootstrap MIT notice are retained in `assets/banners/ATTRIBUTION.md`. Text overlays and responsive crops keep the content readable. The carousel automatically advances every six seconds, wraps after the third slide, and retains manual arrows, dots, and a pause control. Automatic movement pauses on hover, keyboard focus, hidden tabs, and reduced-motion preference. Validate with `python3 scripts/banner.py`.

## Expanded platforms and service quotes

The Platforms section lists 39 tools across advertising/social, email/SEO/analytics, marketplaces, CMS/ecommerce, CRM/sales, and SaaS/automation. Two logo marquees pause on hover or focus, respect reduced motion, and are supplemented by an expandable category directory. The catalog and icon attribution are in `assets/platforms/`. No external APIs or account credentials are needed to display this section.

Services includes all 24 offerings reviewed on the reference site plus four retained platform-specific, migration, and local-business services. Cards show estimated delivery, 2–5 revision allowances, and links to the existing Fiverr/Upwork profiles for reviews. The numbers supplied for review counts are awaiting a service-by-service match; no arbitrary counts or copied reference ratings are displayed. Service quote buttons open a choice of Fiverr, Upwork, Paystack for an agreed payment, or an email brief. The selected service is retained throughout the local quote flow.

## Client-journey polish

The service finder groups all 28 services into five categories, with text search and an expand/collapse control. Nine cards are initially shown; every service remains available and the full catalogue is visible without JavaScript. Prominent project buttons share the Fiverr/Upwork/Paystack quote-choice dialog, with an optional email brief. The floating WhatsApp action opens the real chat link. A three-step project process explains discovery, agreed scope/build, and launch/handover. Mobile contact clutter is reduced, and sharing metadata identifies the canonical public website and founder image. Run `python3 scripts/client_journey.py` for targeted validation.

## Trust cards, business summary, and motion

The trust section uses six white cards with filled gold/charcoal badge images and links to real payment, scope, contact, revision, and refund information. The portfolio summary uses owner-provided figures: 250+ projects across previous client engagements and a 100% Upwork Job Success score. No country count was supplied, so reach remains “Global.” These are owner-provided claims, not independently audited metrics.

Nine photographic service cards are initially visible; all 28 remain available through the finder. Cards reveal in staggered groups, badge images bounce on entry and flip on hover, and the project/Upwork counters count up once in view to their supplied values. Text and action targets stay readable. Reduced-motion preferences show the final values and disable these effects. Validation is in `scripts/trust_portfolio.py` and `scripts/motion.py`.


Portfolio photo update (2026-10-26): all 20 gallery cards use real photographic covers with local image assets. The eight existing demo/Upwork destinations are preserved; twelve prospective industry ideas are explicitly labeled and open relevant service quote dialogs. Twelve cards display initially, with filters, search, and load-more support. Stock photo covers illustrate themes and do not claim to be screenshots of client work. Photo sources and MIT license are recorded in assets/portfolio/ATTRIBUTION.md. Verified with scripts/portfolio_photos.py and scripts/smoke.py, including every idea quote action and 320–1440px layouts.


Original sales recordings restored (2026-10-26): all eight sales videos are byte-identical copies of the original user uploads, without added blur or recompression. Posters were regenerated from those originals; video/poster URLs include a new cache version. Original resolution and audio are preserved.


Client review layout (2026-10-26): reference-inspired gold summary cards and source-linked written review carousel. Uses the three existing review excerpts unchanged, nine existing video stories, owner-reported Upwork Job Success, and global remote collaboration. No third-party names, ratings, flags, dates, or review totals were invented. Browser verification: scripts/reviews_layout.py covers arrows, keyboard End, responsive widths, image loading, and preservation of existing videos.


Day/night mode (2026-10-26): shared theme.js applies the saved preference before CSS, defaults to the device color scheme, and synchronizes tabs. A labeled header button is available on desktop and mobile on both homepage and policy page. Photos and video pixels remain unchanged. Verified with scripts/theme.py: persistence, both pages, quote dialog, mobile menu, and ten widths from 320 to 1920px.


## Installable website app

The manifest and scope are relative to /Bobbyagency/, so the app installs from GitHub Pages without taking over other sites on the same origin. The footer Install Bobbyagency App button uses an available browser installation prompt or opens platform instructions. On iPhone, open in Safari, choose Share → Add to Home Screen, and confirm. On Android Chrome, use Install app / Add to Home screen. No store listing or native package is included.

The service worker always fetches live pages and media. It caches only an offline reconnect page, its retry script, and its icon. Video playback, external payment pages, and enquiries require an internet connection. Updating page content does not require reinstalling the app. Day/night preferences are shared with the website. App icons are rasterized from the existing Bobbyagency brand SVG.


Pricing and payments (28 October 2026): payment.html adapts the owner’s BobbyDev pricing/payment reference into Bobbyagency styling, with Basic $250, Standard $500 and Premium $1,500 starting packages, a prepared-email message form, deposit/balance reference amounts, public Paystack checkout, original Wema Bank details, refund links and four payment steps. Homepage/policy Pricing and Make a Payment links and quote-dialog payment action now lead to the dedicated page. PayPal/crypto are explicitly request-only because no destinations are configured. No fixed FX conversion, secret API key, automatic payment verification, or unconfirmed discount is used. scripts/payments.py passed pricing, selected-package email, reference amount controls, hosted checkout destination, request-only options, keyboard tabs, day/night and 320–1440px layouts. No real transaction was attempted.


Automated audit preparation (30 October 2026): audit-service contains a separate read-only public homepage scanner and WSGI API, email delivery through a Gmail Apps Script connector or optional SMTP, consent/rate limits, DNS-pinned fetches, and evidence-based reports. audit-client.js provides the consent form, on-screen findings, downloadable report and quote follow-up. audit-config.js intentionally has no endpoint until a real backend and sender are deployed/tested; the existing manual review workflow remains active meanwhile. No real report emails have been sent. Backend tests cover private-address/redirect rejection, report observations, origin restrictions, rate limits, provider acceptance/failure and Google connector formatting; scripts/automatic_audit.py covers UI integration with mocked email delivery and responsive layouts. Setup/activation instructions are in audit-service/README.md. No sender keys are stored in website code.
