"""POD discovery, details and quote journey; no external messages sent."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(e.stack))
 page.goto('http://127.0.0.1:3003/',wait_until='networkidle')
 total=page.evaluate('BOBBY_DATA.services.length');assert total==29
 cards=page.locator('.service-card');assert cards.count()==total
 assert page.locator('.service-card:visible').count()==9
 card=page.locator('#print-on-demand');assert card.is_visible()
 titles=page.evaluate('[...document.querySelectorAll(".service-card h3")].map(e=>e.textContent)')
 assert titles==page.evaluate('BOBBY_DATA.services.map(s=>s.title)')
 page.locator('#service-search').fill('Printify');assert page.locator('.service-card:visible').count()==1
 assert card.is_visible();card.locator('img').evaluate('(img)=>img.decode()')
 card.locator('.learn-more').click();assert page.locator('#service-title').inner_text()=='Print on Demand (POD)'
 assert 'Printful' in page.locator('#service-includes').inner_text();assert page.locator('#service-includes li').count()==4
 page.locator('#service-modal-quote').click();assert page.locator('#quote-service-name').inner_text()=='Print on Demand (POD)'
 assert page.locator('.quote-fiverr').get_attribute('href')=='https://www.fiverr.com/emiloloruntinmy'
 assert page.locator('.quote-upwork').get_attribute('href')=='https://www.upwork.com/freelancers/~01d8f8c1ff8dccffea'
 assert page.locator('#quote-dialog .quote-payment a').get_attribute('href')=='payment.html#start-project'
 page.locator('#quote-email-option').click();assert page.locator('#client-service').input_value()=='Print on Demand (POD)';page.keyboard.press('Escape')
 page.locator('#service-search').fill('');assert card.is_visible()
 page.locator('[data-service-filter="Websites & Stores"]').click();assert card.is_visible()
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert not errors,errors
 b.close()
print('PASS: 29 indexed services, POD visible initially, provider search, image, details, all quote channels, email service selection, category filter, 320–1440px layouts, no JavaScript errors')
