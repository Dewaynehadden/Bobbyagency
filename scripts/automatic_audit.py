"""Browser integration with mocked API: no real buyer email is sent."""
from playwright.sync_api import sync_playwright
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'audit-service'))
from auditor import analyse
report=analyse('https://example.com/','<title>Example</title><h1>Welcome</h1><img src="x">')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(e.stack))
 page.goto('http://127.0.0.1:3003/',wait_until='networkidle')
 assert 'personal review' in page.locator('#audit-note').inner_text().lower()
 page.locator('#store-url').fill('example.com');page.locator('#audit-form button').click();assert page.locator('#enquiry-dialog').is_visible();page.keyboard.press('Escape')
 page.route('**/audit-config.js*',lambda route:route.fulfill(content_type='text/javascript',body="window.BOBBY_AUDIT={endpoint:'https://audit.example/audit'};"))
 calls=[]
 def respond(route):
  calls.append(route.request.post_data_json)
  route.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps({'report':report,'delivery':'submitted','message':'Email provider accepted the report. Check your inbox or spam folder.'}))
 page.route('https://audit.example/audit',respond)
 page.reload(wait_until='networkidle')
 assert 'automated' in page.locator('#audit-note').inner_text().lower()
 page.locator('#store-url').fill('example.com');page.locator('#audit-form button').click();assert page.locator('#audit-dialog').is_visible()
 page.locator('#audit-name').fill('Alex Buyer');page.locator('#audit-email').fill('buyer@gmail.com');page.locator('[name="consent"]').check();page.locator('#run-audit').click();page.locator('#audit-results:not([hidden])').wait_for()
 assert calls[0]['website']=='https://example.com/' and calls[0]['consent'] is True
 assert page.locator('.audit-check').count()==7
 assert '3 of 7' in page.locator('#audit-result-summary').inner_text()
 assert 'Meta description' in page.locator('#audit-checks').inner_text()
 assert 'accepted' in page.locator('#automatic-audit-status').inner_text()
 with page.expect_download() as download:page.locator('#download-audit').click()
 assert download.value.suggested_filename=='bobbyagency-website-audit.txt'
 page.locator('#audit-results [data-enquire]').click();assert page.locator('#enquiry-dialog').is_visible();assert page.locator('#client-email').input_value()=='buyer@gmail.com';assert 'Meta description' in page.locator('#client-message').input_value();page.keyboard.press('Escape');page.locator('#audit-form button').click()
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path='/tmp/automatic-audit-mobile.png')
 # A backend error must never display a new successful report.
 page.route('https://audit.example/audit',lambda route:route.fulfill(status=429,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps({'error':'Please wait before requesting another report.'})))
 page.locator('#run-audit').click();page.wait_for_function('document.querySelector("#automatic-audit-status").textContent.includes("Please wait")');assert not page.locator('#audit-results').is_visible()
 assert page.locator('#run-audit').is_enabled()
 assert not errors,errors
 b.close()
print('PASS: unconfigured manual fallback, configured audit consent, request payload, real report rendering, download, mobile layout, API error handling, no JavaScript errors; email mocked')
