# Validation

Functional Chromium checks passed for the new Bobbyagency website.

- Page, 12 service cards, unique IDs, and all local navigation targets
- Banner navigation, slide dots, previous/next, and reduced-motion pause
- All 12 service dialogs and service-specific quote selection
- Founder profile, expertise orbit, and Escape dismissal
- Invalid URL rejection and review request with normalized public URL
- Required fields, unsafe URL rejection, encoded email brief, and honest submission status
- Portfolio pagination, category filters, search, empty state, and reset
- Walkthrough tabs and arrow/Home/End keyboard navigation
- All 10 FAQs and information dialogs
- All local images decode and testimonial video metadata loads
- No horizontal overflow at 13 widths from 320px to 1920px
- Mobile navigation, Escape focus restoration, chat launcher, and dialog keyboard focus
- No failed local resources or JavaScript errors

Desktop and mobile screenshots were inspected, including the service cards, founder orbit, hero banners, contact section, and enquiry dialog. The browser tests run against the locally served website; actual email delivery and third-party profile availability are not claimed.

The existing `/workspace/Bobby` tracked files have no changes. Its pre-redesign HTML, CSS, JavaScript, and README match the preserved backup byte for byte.

## Terms page update

The terms and refund policy text was compared against the original published terms page and matches after updating the business name to Bobbyagency. Browser checks passed for all five policy anchors, both homepage footer links, the privacy dialog link, mobile navigation, return links to the homepage, layouts at 320/390/768/1440px, and absence of JavaScript errors.

## Announcement bar

Verified email, project availability, pricing/payment/terms/contact links on the homepage and policy page. Browser checks passed at 320/390/700/768/900/1051/1440px, including sticky bar and header alignment, mobile navigation, terms navigation, and no JavaScript errors. Pricing and payment links intentionally point to the existing published pages.

## Client success stories

All nine video files loaded valid metadata and all poster requests succeeded. Chromium exercised actual playback on two videos and confirmed that starting the second pauses the first. Gallery arrows, end states, mobile position indicators, keyboard navigation, responsive widths from 320 to 1440px, and JavaScript errors were checked. Desktop and mobile screenshots were inspected.

## Sales-results draft

Eight H.264 recordings and all posters were validated. Browser checks exercised metadata and real playback, single-player behavior across both video sections, no video content preloading on initial page load, four summary cards without unconfirmed aggregate claims, mobile navigation, and responsive widths at 320/390/600/768/950/1051/1440px. Existing nine testimonial videos remain. Desktop/mobile screenshots were reviewed. This batch has not been published.

## Two-column video layout

Both testimonial and sales-report sections use exactly two columns at 320/390/600/768/1051/1440px. Each player is 16:9 and retains the full source frame. There are nine testimonial videos and eight sales recordings. Carousel controls have been removed from the testimonial section. Layout, screenshots, playback, resource loading, and JavaScript errors were checked for the final presentation.

## Service images and expertise rotation

All twelve image regions and matching detail-dialog images were checked. Browser tests confirmed moving outer wheel transforms, a fixed founder, counter-rotating labels, pause/resume, hover/focus pausing, and functional skill buttons. Reduced-motion behavior, four responsive widths at four rotation angles, image loading, and absence of JavaScript errors passed. Final service-card and wheel screenshots were inspected.

## Carousel review update

Client recommendations and sales proof now use separate manual carousels. Both retain their full video sets (nine and eight), display two columns above 600px and one player at smaller widths, and include previous/next controls, dots, counters, scroll/swipe, and keyboard navigation. Browser checks passed for arrows, end states, dots, Home/End controls, retained non-autoplay/preload settings, responsive widths at 320/390/600/768/1051/1440px, and no overflow or JavaScript errors. Desktop/mobile screenshots were reviewed. This update remains unpublished.

## Publication checks — October 26, 2026

Re-ran both carousel and sales-playback checks, and the service-image/wheel checks. Fixed the rotating wheel’s empty transformed corners causing horizontal overflow on 320px screens by clipping within the full-width team section. All affected checks passed, including four rotation angles, all service detail images, 17 retained videos, carousel controls, metadata/playback, reduced motion, and mobile layout. Versioned CSS/JavaScript asset URLs help returning visitors receive the new release.

## Photographic banner correction

Validated all three images, actual six-second transitions and wraparound, pause behavior, manual slide selection, enquiry CTA, and reduced-motion pause. Text, images, and buttons fit at 320/390/600/768/1440px with no horizontal overflow or JavaScript errors. Desktop/mobile screenshots were inspected after transition animations settled.

## Platform directory and expanded service quotes

Checked all 39 tools, every specifically requested platform, six category groups, logo decoding, marquee hover/focus pause, reduced-motion scrolling, six responsive widths, and no failed local assets or JavaScript errors. Checked 28 service detail dialogs and quote destinations, revision values 2/3/4/5, corresponding photo regions, the selected-service email option, wheel service links, and mobile/desktop layout. Disabled service hover displacement on narrow screens to keep quote buttons stable. Screenshot reviews covered the platform rows, directory, service cards, and channel-selection dialog.

## Client-journey polish

Validated category filtering, search, all-service expansion/collapse, empty-state recovery, retained service-specific quotes, general project quotes and email fallback, mobile menu dismissal, three-step process, canonical/social metadata, WhatsApp destination, all 28 services without JavaScript, and six responsive widths. All 28 service detail/quote flows and service images passed. Wheel motion, pause, reduced-motion, and responsive checks passed. Service hover displacement was replaced with a stable highlight so quote buttons remain steady.

## Trust, portfolio summary, real photos, and motion

Validated six illustrated trust cards and their policy/contact/payment destinations; owner-provided 250+ project and 100% Upwork Job Success values; a nonnumeric Global reach card; nine initial service cards with all 28 retained; more than four distinct photographic images; matching service detail images; and layouts at six responsive widths. Motion checks covered reveal, bounce/flip behavior, count-up to accurate endpoints, no repeat counting, constant accessible labels, reduced-motion visibility, and no JavaScript/resource errors. All 28 quote/detail flows also passed after the image change.


Portfolio photo update (2026-10-26): all 20 gallery cards use real photographic covers with local image assets. The eight existing demo/Upwork destinations are preserved; twelve prospective industry ideas are explicitly labeled and open relevant service quote dialogs. Twelve cards display initially, with filters, search, and load-more support. Stock photo covers illustrate themes and do not claim to be screenshots of client work. Photo sources and MIT license are recorded in assets/portfolio/ATTRIBUTION.md. Verified with scripts/portfolio_photos.py and scripts/smoke.py, including every idea quote action and 320–1440px layouts.


Original sales recordings restored (2026-10-26): all eight sales videos are byte-identical copies of the original user uploads, without added blur or recompression. Posters were regenerated from those originals; video/poster URLs include a new cache version. Original resolution and audio are preserved.


Client review layout (2026-10-26): reference-inspired gold summary cards and source-linked written review carousel. Uses the three existing review excerpts unchanged, nine existing video stories, owner-reported Upwork Job Success, and global remote collaboration. No third-party names, ratings, flags, dates, or review totals were invented. Browser verification: scripts/reviews_layout.py covers arrows, keyboard End, responsive widths, image loading, and preservation of existing videos.


Day/night mode (2026-10-26): shared theme.js applies the saved preference before CSS, defaults to the device color scheme, and synchronizes tabs. A labeled header button is available on desktop and mobile on both homepage and policy page. Photos and video pixels remain unchanged. Verified with scripts/theme.py: persistence, both pages, quote dialog, mobile menu, and ten widths from 320 to 1920px.


Installable app (2026-10-26): scripts/pwa.py passed manifest/icon checks, worker activation, install guide on homepage/policy pages, 320–1440px layouts, offline fallback and successful retry after reconnection, with no JavaScript errors. scripts/theme.py also passed. Physical Android/iPhone installation was not performed in this environment.


Pricing and payments (28 October 2026): payment.html adapts the owner’s BobbyDev pricing/payment reference into Bobbyagency styling, with Basic $250, Standard $500 and Premium $1,500 starting packages, a prepared-email message form, deposit/balance reference amounts, public Paystack checkout, original Wema Bank details, refund links and four payment steps. Homepage/policy Pricing and Make a Payment links and quote-dialog payment action now lead to the dedicated page. PayPal/crypto are explicitly request-only because no destinations are configured. No fixed FX conversion, secret API key, automatic payment verification, or unconfirmed discount is used. scripts/payments.py passed pricing, selected-package email, reference amount controls, hosted checkout destination, request-only options, keyboard tabs, day/night and 320–1440px layouts. No real transaction was attempted.
