from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:3001/',wait_until='networkidle')
 assert page.locator('.review-summary-card').count()==4
 assert page.locator('.featured-review').count()==3
 assert page.locator('.story-card').count()==9
 c=page.locator('.reviews-carousel');c.scroll_into_view_if_needed()
 assert c.locator('.media-position').inner_text()=='1–2 of 3 reviews'
 c.locator('.media-next').click()
 page.wait_for_function('document.querySelector(".reviews-carousel .media-position").textContent==="2–3 of 3 reviews"')
 assert c.locator('.media-next').is_disabled()
 c.locator('.media-prev').click()
 page.locator('#client-reviews').scroll_into_view_if_needed()
 page.screenshot(path='/tmp/new-portfolio-validation/reviews-layout.png')
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  for img in page.locator('.review-summary-card img').all():img.evaluate('(i)=>i.decode()')
 page.set_viewport_size({'width':390,'height':844})
 track=page.locator('#featured-review-track');track.focus();page.keyboard.press('End')
 page.wait_for_function('document.querySelector(".reviews-carousel .media-position").textContent==="3–3 of 3 reviews"')
 assert not errors,errors
 b.close()
print('PASS review cards, counts, video preservation, carousel controls, keyboard, responsive layout, icons and JavaScript')
