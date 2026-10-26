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
