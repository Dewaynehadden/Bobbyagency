from playwright.sync_api import sync_playwright
from pathlib import Path
Path("/tmp/new-portfolio-validation").mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:3001/',wait_until='networkidle')
 images=page.locator('.service-card img.service-photo')
 assert images.count()==12
 for i,img in enumerate(images.all()):
  img.evaluate('(i)=>{i.loading="eager";return i.decode()}')
  assert img.evaluate('(i)=>i.naturalWidth===1536 && i.naturalHeight===1024')
  assert img.evaluate('(i)=>i.style.getPropertyValue("--photo-col")')==str(i%3)
  assert img.evaluate('(i)=>i.style.getPropertyValue("--photo-row")')==str(i//3)
  page.locator('.service-card .learn-more').nth(i).click()
  modal=page.locator('#service-dialog-image')
  modal.evaluate('(i)=>i.decode()')
  assert modal.evaluate('(i)=>i.style.getPropertyValue("--photo-col")')==str(i%3)
  assert modal.evaluate('(i)=>i.style.getPropertyValue("--photo-row")')==str(i//3)
  page.keyboard.press('Escape')
 print('PASS: 12 matching service photos and modal views.',flush=True)
 page.locator('#team').scroll_into_view_if_needed()
 page.mouse.move(0,0)
 rotor=page.locator('.orbit-rotor')
 t0=rotor.evaluate('(e)=>getComputedStyle(e).transform')
 page.wait_for_timeout(250)
 assert rotor.evaluate('(e)=>getComputedStyle(e).transform')!=t0
 assert page.locator('.founder-center').evaluate('(e)=>getComputedStyle(e).transform')=='none'
 assert page.locator('.skill-node').first.evaluate('(e)=>getComputedStyle(e).animationName')=='expertise-counterspin'
 page.locator('.orbit-toggle').click()
 assert rotor.evaluate('(e)=>getComputedStyle(e).animationPlayState')=='paused'
 t0=rotor.evaluate('(e)=>getComputedStyle(e).transform');page.wait_for_timeout(200)
 assert rotor.evaluate('(e)=>getComputedStyle(e).transform')==t0
 page.locator('.orbit-toggle').click();page.mouse.move(0,0)
 assert rotor.evaluate('(e)=>getComputedStyle(e).animationPlayState')=='running'
 page.locator('.founder-center').hover()
 assert rotor.evaluate('(e)=>getComputedStyle(e).animationPlayState')=='paused'
 page.mouse.move(0,0)
 page.locator('.skill-node').first.focus()
 assert rotor.evaluate('(e)=>getComputedStyle(e).animationPlayState')=='paused'
 page.locator('.skill-node').first.click()
 assert page.locator('#service-dialog').is_visible()
 page.keyboard.press('Escape')
 print('PASS: automatic rotation, upright-label animation, fixed founder, pause/resume, hover/focus pause, and clickable skills.',flush=True)
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000})
  for animation in [0,18000,36000,54000]:
   page.locator('.orbit-rotor').evaluate('(e,t)=>e.getAnimations().forEach(a=>a.currentTime=t)',animation)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,animation)
 page.emulate_media(reduced_motion='reduce')
 assert rotor.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
 assert page.locator('.orbit-toggle').is_disabled()
 for width,suffix in [(1440,'desktop'),(390,'mobile')]:
  page.set_viewport_size({'width':width,'height':1000})
  page.locator('#services .section-heading').evaluate('(e)=>e.scrollIntoView({block:"start"})')
  page.screenshot(path=f'/tmp/new-portfolio-validation/service-photos-{suffix}.png')
  page.locator('.expertise-orbit').evaluate('(e)=>e.scrollIntoView({block:"center"})')
  page.screenshot(path=f'/tmp/new-portfolio-validation/spinning-wheel-{suffix}.png')
 assert not errors,errors
 b.close()
print('PASS: reduced motion, four responsive widths at four wheel angles, no overflow or JavaScript errors.')
