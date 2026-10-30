"""Synthetic API fixtures: no external measurement or actual email is sent."""
from playwright.sync_api import sync_playwright
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'audit-service/tests'))
from test_pagespeed import fixture
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'audit-service'))
from pagespeed import normalize
mobile=fixture();desktop=fixture('desktop',.98)
report={'source':'google_pagespeed','schema_version':3,'url':'https://example.com/','checked_at':'2026-10-30T12:00:00Z','devices':{'mobile':normalize(mobile,'mobile'),'desktop':normalize(desktop,'desktop')},'errors':{},'google_url':'https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fexample.com','limitations':'Synthetic test fixture. Real production reports contain measured Google responses, not this fixture.'}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(e.stack))
 page.route('**/audit-config.js*',lambda r:r.fulfill(content_type='text/javascript',body="window.BOBBY_AUDIT={endpoint:'https://audit.example/audit'};"))
 payload=[]
 page.route('https://audit.example/audit',lambda r:(payload.append(r.request.post_data_json),r.fulfill(status=202,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps({'job_id':'fixture-job-token-test-only-1234567890'})))[-1])
 page.route('https://audit.example/audit/jobs/*',lambda r:r.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps({'status':'complete','stage':'Report ready','completed_steps':['mobile','desktop'],'report':report,'delivery':'submitted','message':'Synthetic test: provider accepted report.'})))
 page.route('https://audit.example/audit/jobs/*/raw/*',lambda r:r.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps(mobile)))
 page.goto('http://127.0.0.1:3003/',wait_until='networkidle')
 page.locator('#store-url').fill('example.com');page.locator('#audit-form button').click()
 page.locator('#audit-name').fill('Test Buyer');page.locator('#audit-email').fill('buyer@example.test');page.locator('[name="consent"]').check();page.locator('#run-audit').click();page.locator('#pagespeed-report h3').first.wait_for()
 assert payload[0]['engine']=='pagespeed'
 assert page.locator('.psi-device:not([hidden]) .psi-ring').first.inner_text()=='77'
 assert page.locator('.psi-device:not([hidden]) .psi-ring').nth(1).inner_text()=='—'
 assert '6.6 s' in page.locator('.psi-device:not([hidden]) .psi-metrics').inner_text()
 page.locator('.psi-device:not([hidden]) .psi-audit>summary',has_text='Improve image delivery').click()
 assert 'https://example.com/image.jpg' in page.locator('.psi-device:not([hidden]) .psi-details').first.inner_text()
 page.locator('.psi-device-tabs button',has_text='Desktop').click()
 assert page.locator('.psi-device:not([hidden]) .psi-ring').first.inner_text()=='98'
 page.locator('.psi-device:not([hidden]) .psi-score').nth(1).click();assert 'Contrast needs review' in page.locator('.psi-device:not([hidden]) .psi-findings').inner_text()
 with page.expect_download() as download:page.locator('#download-audit').click()
 assert download.value.suggested_filename.endswith('.json')
 with page.expect_download() as download:page.locator('[data-raw-report="mobile"]').click()
 assert download.value.suggested_filename=='google-pagespeed-mobile.json'
 with page.expect_popup() as popup:page.locator('#print-audit').click()
 popup.value.wait_for_load_state();assert popup.value.locator('.psi-device').count()==2
 page.locator('#audit-results [data-enquire]').click();assert 'Performance 77' in page.locator('#client-message').input_value();assert 'Performance 98' in page.locator('#client-message').input_value();page.keyboard.press('Escape');page.locator('#audit-form button').click()
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.locator('.psi-device-tabs button',has_text='Mobile').click();page.locator('#pagespeed-report').scroll_into_view_if_needed();page.screenshot(path='/tmp/pagespeed-report-test-desktop.png')
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path='/tmp/pagespeed-report-test-mobile.png')
 # A setup error may not leave an old report visible or invent new scores.
 page.route('https://audit.example/audit',lambda r:r.fulfill(status=503,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps({'error':'Add PAGESPEED_API_KEY to Render.'})))
 page.locator('#run-audit').click();page.wait_for_function('document.querySelector("#automatic-audit-status").textContent.includes("PAGESPEED_API_KEY")');assert not page.locator('#audit-results').is_visible()
 assert not errors,errors
 b.close()
print('PASS: real-value preservation via fixture, mobile/desktop tabs, missing-score state, metrics, insight detail tables, category filtering, original JSON, printable two-device report, quote evidence, responsive widths, configuration failure; no real Google call/email')
