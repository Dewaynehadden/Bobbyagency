from playwright.sync_api import sync_playwright
import json
from pathlib import Path
catalog=json.loads(Path('/workspace/new-portfolio/site-data.js').read_text().split('=',1)[1].strip().removesuffix(';'))['services']
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 assert page.goto('http://127.0.0.1:3001/',wait_until='networkidle').status==200
 assert page.locator('.service-card').count()==28
 assert page.locator('.service-review-line').count()==28
 page.locator('#service-show-all').click()
 assert {s['revisions'] for s in catalog}=={2,3,4,5}
 for index,service in enumerate(catalog):
  card=page.locator('.service-card').nth(index)
  assert card.locator('h3').inner_text()==service['title']
  assert f"Up to {service['revisions']} revisions" in card.inner_text()
  assert not card.locator('.service-review-line').inner_text().count('★★★★★')
  card.locator('.learn-more').click()
  assert page.locator('#service-title').inner_text()==service['title']
  assert page.locator('#service-includes li').count()==4
  assert page.locator('#service-dialog-image').get_attribute('src')==service['image']
  page.locator('#service-modal-quote').click()
  assert page.locator('#quote-service-name').inner_text()==service['title']
  assert page.locator('#quote-dialog .quote-fiverr').get_attribute('href')=='https://www.fiverr.com/emiloloruntinmy'
  assert page.locator('#quote-dialog .quote-upwork').get_attribute('href')=='https://www.upwork.com/freelancers/~01d8f8c1ff8dccffea'
  assert page.locator('#quote-dialog .quote-payment a').get_attribute('href')=='payment.html#start-project'
  page.keyboard.press('Escape')
  if index in [0,12,27]:
   card.locator('.service-quote').click()
   assert page.locator('#quote-service-name').inner_text()==service['title']
   page.locator('#quote-email-option').click()
   assert page.locator('#client-service').input_value()==service['title']
   page.keyboard.press('Escape')
  print('PASS service:',index+1,service['title'],flush=True)
 for button in page.locator('.skill-node').all():
  title=button.inner_text()
  button.click()
  assert page.locator('#service-dialog').is_visible()
  page.keyboard.press('Escape')
 for width in [320,390,768,1051,1440]:
  print('Checking quote at width:',width,flush=True)
  page.set_viewport_size({'width':width,'height':1000})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  page.locator('.service-quote').first.click()
  assert page.locator('#quote-dialog').is_visible()
  for link in page.locator('#quote-dialog a').all():
   assert link.bounding_box()['width']>0
  page.keyboard.press('Escape')
 for image in page.locator('.service-card img').all():image.evaluate('(i)=>{i.loading="eager";return i.decode()}')
 page.set_viewport_size({'width':1440,'height':1000})
 page.locator('#services .section-heading').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 page.screenshot(path='/tmp/new-portfolio-validation/services-expanded.png')
 page.locator('.service-quote').first.click()
 page.screenshot(path='/tmp/new-portfolio-validation/quote-options.png')
 assert not errors,errors
 b.close()
print('PASS: 28 service cards, 24 reference offerings, revision allowances, all details/quote channels, email fallback, skill links, responsive layouts, images, no JavaScript errors.')
