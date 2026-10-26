"""Check card reveals, badge flip effects, truthful counter endpoints, and reduced motion."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:3001/',wait_until='networkidle')
 page.locator('#trust').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 first=page.locator('.trust-card').first
 page.wait_for_function('document.querySelector(".trust-card").classList.contains("is-revealed")')
 page.wait_for_function('getComputedStyle(document.querySelector(".trust-card")).opacity==="1"')
 first.hover()
 assert first.locator('img').evaluate('(e)=>getComputedStyle(e).animationName')=='badge-flip'
 assert first.locator('h3').inner_text()=='Secure Checkout'
 page.mouse.move(0,0)
 assert first.locator('img').evaluate('(e)=>getComputedStyle(e).animationName')=='badge-bounce'
 page.locator('#portfolio').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 page.wait_for_function('document.querySelector("[data-business-metric=totalProjects]").dataset.counted==="true"')
 page.wait_for_timeout(100)
 output=page.locator('[data-business-metric="totalProjects"] [data-metric-value]')
 assert int(output.inner_text().removesuffix('+'))<250
 page.wait_for_function('document.querySelector("[data-business-metric=totalProjects] [data-metric-value]").textContent==="250+"',timeout=3500)
 page.wait_for_function('document.querySelector("[data-business-metric=successRate] [data-metric-value]").textContent==="100%"')
 assert output.get_attribute('aria-label')=='250+'
 page.locator('#trust').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 page.locator('#portfolio').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 assert output.inner_text()=='250+'
 page.emulate_media(reduced_motion='reduce')
 assert first.evaluate('(e)=>getComputedStyle(e).opacity')=='1'
 assert first.locator('img').evaluate('(e)=>getComputedStyle(e).animationName')=='none'
 assert page.locator('[data-business-metric="successRate"] [data-metric-value]').inner_text()=='100%'
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert not errors,errors
 b.close()
print('PASS: staggered reveals, badge flip/bounce, counters ending at 250+/100%, no repeat counts, stable text, accessible counter label, reduced-motion behavior, responsive widths, and no JavaScript errors.')
