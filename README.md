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

The Success Stories navigation link opens the client-feedback section. Eight user-uploaded videos live in `assets/stories/`, alongside locally generated poster images; the prior testimonial remains as the ninth story. All videos retain their original H.264/AAC tracks and are remuxed for fast-start playback. Videos have native controls, do not autoplay or preload their content, and pause when another video starts or they leave the visible gallery. The videos are presented in a two-column grid with horizontal 16:9 players, including on phones, as requested. Portrait footage is contained without cropping. Run `python3 scripts/success_stories.py` against the local server on port 3001 for targeted functional checks.

## Sales-results draft

The `#sales-proof` section contains eight uploaded Shopify dashboard recordings with local poster images and native playback controls. Its four summary cards show the actual recording count, platform, report focus, and on-demand viewing; the reference site’s aggregate revenue, growth, order totals, and verification claims are not copied. Identifying browser and customer-table areas are blurred in the website copies of desktop recordings; the uploaded originals remain outside the repository and are unchanged. This batch is saved locally for publication with later changes, not pushed to the live branch. Run `python3 scripts/sales_results.py` against the local server on port 3001 to validate the section. The sales-report grid also uses two columns and 16:9 players at every screen size.
