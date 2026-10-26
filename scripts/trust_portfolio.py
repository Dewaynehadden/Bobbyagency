"""Trust-card, photographic service-image, and portfolio-summary checks."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
Path('/tmp/new-portfolio-validation').mkdir(exist_ok=True)
catalog=json.loads(Path('/workspace/new-portfolio/site-data.js').read_text().split('=',1)[1].strip().removesuffix(';'))
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 errors=[];bad=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:bad.append(r.url) if r.status>=400 and r.url.startswith('http://127.0.0.1') else None)
 assert page.goto('http://127.0.0.1:3001/',wait_until='networkidle').status==200
 assert page.locator('.trust-card').count()==6
 assert page.locator('.trust-card img').count()==6
 assert page.locator('.trust-card a').count()==6
 assert 'Why Clients Trust Us'==page.locator('#trust h2').inner_text()
 assert page.locator('[data-business-metric="totalProjects"] [data-metric-value]').inner_text()=='250+'
 assert page.locator('[data-business-metric="successRate"] [data-metric-value]').inner_text()=='100%'
 assert page.locator('[data-business-metric="successRate"] [data-metric-label]').inner_text()=='Upwork Job Success'
 assert page.locator('[data-business-metric="countriesServed"] [data-metric-value]').inner_text()=='Global'
 assert page.locator('.service-card:visible').count()==9
 assert page.locator('.service-card').count()==28
 assert len(set(x['image'] for x in catalog['services']))>4
 page.locator('#service-show-all').click()
 for i,img in enumerate(page.locator('.service-card img').all()):
  img.evaluate('(i)=>{i.loading="eager";return i.decode()}')
  assert img.get_attribute('src')==catalog['services'][i]['image']
  assert 'service-photography.png' not in img.get_attribute('src')
  page.locator('.service-card .learn-more').nth(i).click()
  modal=page.locator('#service-dialog-image')
  modal.evaluate('(i)=>i.decode()')
  assert modal.get_attribute('src')==img.get_attribute('src')
  page.keyboard.press('Escape')
 for img in page.locator('.trust-card img, .portfolio-stat-card img').all():img.evaluate('(i)=>{i.loading="eager";return i.decode()}')
 for width in [320,390,600,768,1024,1440]:
  page.set_viewport_size({'width':width,'height':1000})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  values=page.locator('.portfolio-stat-card [data-metric-value]')
  for value in values.all():assert value.evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
 for width,suffix in [(1440,'desktop'),(390,'mobile')]:
  page.set_viewport_size({'width':width,'height':1000})
  for section,name in [('#trust','trust-cards'),('#portfolio','portfolio-summary'),('#services','real-service-photos')]:
   page.locator(section).evaluate('(e)=>e.scrollIntoView({block:"start"})')
   page.screenshot(path=f'/tmp/new-portfolio-validation/{name}-{suffix}.png')
 assert not errors,errors
 assert not bad,bad
 b.close()
print('PASS: six illustrated trust cards, owner-provided 250+/100% Upwork summary, no invented country count, nine services visible/28 retained, more than four real photos, all matching modal images, six responsive widths, no resource or JavaScript errors.')
