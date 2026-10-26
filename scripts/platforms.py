from playwright.sync_api import sync_playwright
from pathlib import Path
import json
catalog=json.loads(Path('/workspace/new-portfolio/assets/platforms/catalog.json').read_text())
expected=[i['name'] for g in catalog for i in g['items']]
required=['Klaviyo','Google Ads','Meta Ads','Google Analytics 4 (GA4)','Google Tag Manager','TikTok Ads','Semrush','SEO','Google Merchant Center','Etsy','eBay','Amazon','Walmart','HubSpot','GoHighLevel (GHL)','Zapier','Make.com']
assert all(name in expected for name in required)
Path('/tmp/new-portfolio-validation').mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
 errors=[];failed=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:failed.append(r.url) if r.status>=400 and r.url.startswith('http://127.0.0.1') else None)
 page.goto('http://127.0.0.1:3001/',wait_until='networkidle')
 section=page.locator('#platforms')
 assert section.locator('.platform-row').count()==2
 assert section.locator('.platform-set:not([aria-hidden]) .platform-tile').count()==39
 for img in section.locator('img').all():img.evaluate('(i)=>{i.loading="eager";return i.decode()}')
 for row in section.locator('.platform-row').all():
  track=row.locator('.platform-track')
  assert track.evaluate('(e)=>getComputedStyle(e).animationName')=='platform-scroll'
  row.locator('.platform-marquee').hover()
  assert track.evaluate('(e)=>getComputedStyle(e).animationPlayState')=='paused'
  row.locator('.platform-marquee').focus()
  assert track.evaluate('(e)=>getComputedStyle(e).animationPlayState')=='paused'
 section.locator('.platform-directory summary').click()
 assert section.locator('.platform-directory[open]').count()==1
 assert section.locator('.platform-directory-grid article').count()==6
 actual=section.locator('.platform-directory li').all_text_contents()
 assert actual==expected
 for width in [320,390,600,768,1024,1440]:
  page.set_viewport_size({'width':width,'height':1000})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size({'width':1440,'height':1200})
 section.locator('h2').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 page.screenshot(path='/tmp/new-portfolio-validation/platforms-desktop.png')
 page.set_viewport_size({'width':390,'height':1000})
 section.locator('h2').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 page.screenshot(path='/tmp/new-portfolio-validation/platforms-mobile.png')
 page.emulate_media(reduced_motion='reduce')
 for row in section.locator('.platform-row').all():
  assert row.locator('.platform-track').evaluate('(e)=>getComputedStyle(e).animationName')=='none'
  marquee=row.locator('.platform-marquee')
  marquee.evaluate('(e)=>e.scrollLeft=e.scrollWidth')
  assert marquee.evaluate('(e)=>e.scrollLeft>0')
 assert not errors,errors
 assert not failed,failed
 b.close()
print('PASS: all 39 tools, all requested brands, 6 directory groups, logo loading, marquee/focus pause, reduced-motion scrolling, six responsive widths, no failed resources or JavaScript errors.')
