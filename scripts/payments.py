"""Payment page interaction checks. No real payment is submitted."""
from playwright.sync_api import sync_playwright
from urllib.parse import unquote
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=b.new_context(reduced_motion='reduce',viewport={'width':1440,'height':1000});page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(e.stack))
 page.goto('http://127.0.0.1:3002/payment.html',wait_until='networkidle')
 # Capture outgoing destinations without opening a payment or email application.
 page.evaluate('window.opened=[]; window.open=(url)=>{window.opened.push(url);return null}')
 assert page.locator('.payment-plan').count()==3
 assert page.locator('.payment-steps li').count()==4
 page.locator('[data-package="Standard"]').click()
 assert 'Standard' in page.locator('#selected-package').inner_text()
 form=page.locator('#payment-message-form');form.locator('[name="name"]').fill('A Buyer');form.locator('[name="email"]').fill('buyer@example.com');form.locator('button[type="submit"]').click()
 href=page.locator('#payment-email-fallback').get_attribute('href');assert 'Standard' in unquote(href) and 'buyer@example.com' in unquote(href)
 page.locator('#deposit-tab').click();assert page.locator('#deposit-panel').is_visible()
 page.locator('[data-amount="50"]').click();assert page.locator('#deposit-amount').input_value()=='50'
 form=page.locator('#deposit-form');form.locator('[name="name"]').fill('A Buyer');form.locator('[name="email"]').fill('buyer@example.com');form.locator('[name="agree"]').check()
 form.locator('button[type="submit"]').click()
 assert page.evaluate('window.opened.at(-1)')=='https://paystack.shop/pay/wd0c70e6o9'
 assert 'not passed' in page.locator('#payment-action-status').inner_text()
 page.locator('[data-method="paypal"]').click();assert not page.locator('#payment-bank').is_visible();form.locator('button[type="submit"]').click();assert 'PayPal' in unquote(page.evaluate('window.opened.at(-1)'))
 page.locator('[data-method="crypto"]').click();form.locator('button[type="submit"]').click();assert 'crypto' in unquote(page.evaluate('window.opened.at(-1)'))
 assert 'No payment' in page.locator('#payment-action-status').inner_text()
 page.locator('[data-method="card"]').click();assert page.locator('#bank-account').inner_text()=='0237437136'
 page.locator('#deposit-tab').focus();page.keyboard.press('ArrowLeft');assert page.locator('#message-tab').get_attribute('aria-selected')=='true'
 for width in [320,390,650,768,1024,1440]:
  page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size({'width':1440,'height':1000});page.locator('#pricing').scroll_into_view_if_needed();page.screenshot(path='/tmp/new-portfolio-validation/payment-pricing.png')
 page.locator('#deposit-tab').click();page.locator('#start-project').scroll_into_view_if_needed();page.screenshot(path='/tmp/new-portfolio-validation/payment-deposit.png')
 page.locator('.theme-toggle').click();page.screenshot(path='/tmp/new-portfolio-validation/payment-dark.png')
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.goto('http://127.0.0.1:3002/',wait_until='networkidle')
 assert page.locator('.announcement-links a',has_text='Pricing').get_attribute('href')=='payment.html#pricing'
 assert page.locator('.announcement-links a',has_text='Make a Payment').get_attribute('href')=='payment.html#start-project'
 assert page.locator('#quote-dialog .quote-payment a').get_attribute('href')=='payment.html#start-project'
 assert not errors,errors
 b.close()
print('PASS: pricing packages, quote selection, prepared email, deposit amounts, hosted Paystack destination, PayPal/crypto request-only flows, keyboard tabs, mobile/day-night, site payment links; no actual payment made')
