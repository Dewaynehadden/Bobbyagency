"""Service discovery and general project flow checks."""
from playwright.sync_api import sync_playwright
from pathlib import Path
Path('/tmp/new-portfolio-validation').mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 assert page.goto('http://127.0.0.1:3001/',wait_until='networkidle').status==200
 assert page.locator('.service-card').count()==28
 assert page.locator('.service-card:visible').count()==6
 assert page.locator('#service-results-count').inner_text()=='Showing 6 of 28 services'
 page.locator('#service-show-all').click()
 assert page.locator('.service-card:visible').count()==28
 page.locator('#service-show-all').click()
 assert page.locator('.service-card:visible').count()==6
 page.locator('[data-service-filter="AI & Automation"]').click()
 assert page.locator('.service-card:visible').count()==2
 assert not page.locator('#service-show-all').is_visible()
 page.locator('[data-service-filter="Marketing & Growth"]').click()
 assert page.locator('.service-card:visible').count()==6
 page.locator('#service-show-all').click()
 assert page.locator('.service-card:visible').count()==9
 page.locator('#service-search').fill('not-matching-123')
 assert page.locator('.service-empty').is_visible()
 assert page.locator('.service-card:visible').count()==0
 page.locator('#reset-services').click()
 assert page.locator('.service-card:visible').count()==6
 page.locator('#service-search').fill('migration')
 assert page.locator('.service-card:visible').count()==1
 assert page.locator('.service-card:visible h3').inner_text()=='Website & Store Migration'
 page.locator('.service-card:visible .service-quote').click()
 assert page.locator('#quote-service-name').inner_text()=='Website & Store Migration'
 page.keyboard.press('Escape')
 page.locator('#service-search').fill('')
 page.locator('.header-actions [data-quote="general"]').click()
 assert page.locator('#quote-service-name').inner_text()=='New website project'
 page.locator('#quote-email-option').click()
 assert page.locator('#client-service').input_value()=='New website project'
 page.keyboard.press('Escape')
 assert page.locator('.project-process-grid article').count()==3
 assert page.locator('link[rel="canonical"]').get_attribute('href')=='https://dewaynehadden.github.io/Bobbyagency/'
 assert page.locator('meta[property="og:image"]').count()==1
 assert page.locator('.chat-launcher').get_attribute('href')=='https://wa.me/message/BYC7YFBUX4QGG1'
 for width in [320,390,600,768,1024,1440]:
  page.set_viewport_size({'width':width,'height':1000})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size({'width':390,'height':1000})
 page.locator('.menu-toggle').click()
 page.locator('.mobile-nav-actions [data-quote="general"]').click()
 assert page.locator('#quote-dialog').is_visible()
 assert page.locator('.menu-toggle').get_attribute('aria-expanded')=='false'
 page.keyboard.press('Escape')
 for width,suffix in [(1440,'desktop'),(390,'mobile')]:
  page.set_viewport_size({'width':width,'height':1000})
  for section,name in [('#services','service-finder'),('#process','process')]:
   page.locator(section).evaluate('(e)=>e.scrollIntoView({block:"start"})')
   page.screenshot(path=f'/tmp/new-portfolio-validation/{name}-{suffix}.png')
 nojs=browser.new_page(java_script_enabled=False)
 nojs.goto('http://127.0.0.1:3001/')
 assert nojs.locator('.service-card:visible').count()==28
 assert not errors,errors
 browser.close()
print('PASS: service filters/search/expand/reset, all 28 services retained, specific/general quotes, mobile navigation, project process, social metadata, WhatsApp link, no-JS catalogue, six responsive widths, and no JavaScript errors.')
