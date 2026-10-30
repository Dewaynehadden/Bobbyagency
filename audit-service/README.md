# Bobbyagency automated audit service

This service checks the HTML of one public webpage and sends a one-time report to the address entered with consent. Any valid recipient provider is supported (Gmail, Yahoo, Outlook, etc.). One sender must be configured. No email credentials or secrets belong in GitHub, frontend JavaScript, or chat.

## What is implemented

- Read-only checks for HTTPS, title, description, mobile viewport, H1 count, canonical link, and missing image alt attributes.
- Evidence and suggested next steps, as HTML observations, without an overall website score. This is NOT a Lighthouse, sales, design, full-site accessibility, or security score.
- Public URL validation, private/reserved network rejection, DNS address pinning with TLS hostname verification, per-redirect validation, bounded HTML size/time, and limited parallel scans.
- Email recipient validation, consent, honeypot, origin restrictions, in-memory cooldowns, and a default 30-request daily limit. These safeguards are a small-pilot baseline, not durable abuse protection.
- No contact/report database. Temporary request details and rate limits live in process memory. Email providers retain/report mail according to their policies. The host may retain ordinary request logs.
- No passwords, admin access, payment details, form submissions on the scanned site, or active vulnerability tests are requested.
- The website retains its personal-review workflow until audit-config.js contains a tested backend URL. It never claims reports were emailed while unconfigured. SMTP/connector acceptance does not guarantee inbox delivery.

## Free pilot setup: Render + Gmail through Google Apps Script

Use a NEW Render Web Service from the Bobbyagency repository. Do not change the Bobby Dating service.

- Runtime: Python 3; Branch: main
- Root Directory: `audit-service`
- Build Command: `pip install -r requirements.txt`
- Start Command: `waitress-serve --listen=0.0.0.0:$PORT --threads=4 app:application`
- Plan: Free, $0/month (verify the displayed plan; no disk or database needed)
- Health Check Path: `/healthz`

Set variables:

| Key | Value |
| --- | --- |
| AUDIT_ALLOWED_ORIGIN | https://dewaynehadden.github.io |
| AUDIT_DAILY_LIMIT | 30 |
| EMAIL_PROVIDER | google_script |
| GOOGLE_MAIL_URL | Your deployed Apps Script web app URL ending in /exec |
| GOOGLE_MAIL_TOKEN | A generated private token, at least 24 characters; match the script property below |

### Google account setup

1. Open https://script.google.com while signed into the Gmail account you want to send from. Create a new project named `Bobbyagency Audit Mailer`.
2. Copy google-mailer.gs into its editor. The code requests permission to send emails with MailApp, not to read the mailbox.
3. In Project Settings → Script Properties, add `AUDIT_MAIL_TOKEN`. Generate a long random token privately (Render's Generate button can create one). Store the same value as Render's GOOGLE_MAIL_TOKEN. Do not send it in chat or commit it.
4. Deploy → New deployment → Web app. Execute as **Me**; access **Anyone** so Render can call it. The private token protects the send function. Review the source/permissions and authorize only your own project. If your Workspace administrator prohibits public web apps, use an authorized provider instead.
5. Copy its /exec deployment URL into Render's GOOGLE_MAIL_URL. Keep all credentials private. Redeploy/update the Apps Script deployment if its code changes; saving the editor alone does not update a deployed version.
6. Deploy the Render service and confirm /healthz returns {"ok":true}. Google daily sending quotas and account restrictions apply; this is for a low-volume pilot, not bulk email. Free Render can sleep and take time to wake.

Standard SMTP is also implemented, but some free hosts block SMTP ports. To use SMTP on a compatible host, set EMAIL_PROVIDER=smtp and SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD and SMTP_FROM. A Gmail app password is required instead of a normal Google password when using Gmail SMTP; an eligible account and two-step verification are required.

## Activate the website only after delivery is tested

1. Set audit-config.js to `{ endpoint: 'https://YOUR-AUDIT-SERVICE.onrender.com/audit' }` (the URL is public; no keys).
2. Test with your OWN email: a real public homepage should produce evidence-based results and a report email. Check inbox and spam. A bad/private URL must fail; the UI must not claim success on failure.
3. Publish that endpoint configuration. The homepage changes to an automated-audit form and requests name, email, public URL and one-time consent.
4. Backend errors, blocked scanners, quota/provider failures and network errors remain visible. If email fails after a scan, results and download are still available. Contact/quote follow-up is initiated by the buyer; no marketing subscription is created.

Before scaling: use durable rate limits and CAPTCHA/abuse protection, monitor sending reputation and provider quotas, add queueing/retries with idempotency, and review privacy/data retention. Do not send repeated reports or marketing without the appropriate consent.

## Validation

`python3 -m unittest discover -s tests -v` tests findings, missing evidence, URL rejection, private networks, redirects, DNS pinning/TLS, origin/cooldown restrictions, email formatting, successful delivery responses and email failure behavior. No real email is sent by tests.


Accuracy correction: the document title excludes SVG icon titles; template/noscript content is excluded from active markup observations. Multiple H1 elements and a missing canonical are review suggestions, not automatic defects. Likely client-rendered app shells return inconclusive missing-content findings. Recognizable bot-challenge responses are not scored as the actual website. Every report states that rendered layout, speed and metadata quality have not been measured.
