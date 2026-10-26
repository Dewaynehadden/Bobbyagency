from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=b.new_context(color_scheme='dark',reduced_motion='reduce',viewport={'width':1440,'height':1000})
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:3001/',wait_until='networkidle')
 assert page.locator('html').get_attribute('data-theme')=='dark'
 toggle=page.locator('.theme-toggle');toggle.click()
 assert page.locator('html').get_attribute('data-theme')=='light'
 page.reload();assert page.locator('html').get_attribute('data-theme')=='light'
 toggle.click();page.goto('http://127.0.0.1:3001/terms.html',wait_until='networkidle')
 assert page.locator('html').get_attribute('data-theme')=='dark'
 page.locator('.theme-toggle').click();assert page.locator('html').get_attribute('data-theme')=='light'
 page.goto('http://127.0.0.1:3001/',wait_until='networkidle');page.locator('.theme-toggle').click()
 for w in [320,390,480,600,768,1024,1100,1280,1440,1920]:
  page.set_viewport_size({'width':w,'height':1000})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),w
  assert page.locator('.theme-toggle').is_visible()
 page.set_viewport_size({'width':1440,'height':1000})
 page.locator('#client-reviews').scroll_into_view_if_needed();page.screenshot(path='/tmp/new-portfolio-validation/dark-reviews.png')
 page.locator('.header-actions [data-quote="general"]').click();assert page.locator('#quote-dialog').is_visible();page.keyboard.press('Escape')
 page.set_viewport_size({'width':390,'height':844});page.evaluate('scrollTo(0,0)');page.screenshot(path='/tmp/new-portfolio-validation/dark-mobile.png')
 page.locator('.menu-toggle').click();assert page.locator('.menu-toggle').get_attribute('aria-expanded')=='true'
 assert not errors,errors
 b.close()
print('PASS: device theme, manual toggle, persistence, policy page, 10 widths, mobile menu, dark quote modal, no JavaScript errors')
