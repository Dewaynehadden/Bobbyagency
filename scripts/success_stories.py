from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 assert page.goto('http://127.0.0.1:3001/').status==200
 assert page.locator('.story-card').count()==9
 assert page.locator('#testimonials h2').inner_text()=='Hear It From Our Clients'
 assert 'REAL VOICES, REAL RESULTS' in page.locator('#testimonials').inner_text()
 page.locator('#testimonials').scroll_into_view_if_needed()
 page.locator('.stories-position').get_by_text('1–3 / 9',exact=True).wait_for()
 page.locator('.stories-next').click()
 page.wait_for_function("document.querySelector('.stories-position').textContent==='4–6 / 9'")
 page.locator('.stories-next').click()
 page.wait_for_function("document.querySelector('.stories-next').disabled")
 assert page.locator('.stories-position').inner_text()=='7–9 / 9'
 page.locator('.stories-prev').click()
 page.locator('.stories-prev').click()
 page.wait_for_function("document.querySelector('.stories-prev').disabled")
 videos=page.locator('.story-card video')
 for i in range(9):
  video=videos.nth(i)
  video.evaluate('(v)=>{v.preload="metadata";v.load()}')
  page.wait_for_function('(i)=>document.querySelectorAll(".story-card video")[i].readyState>=1',arg=i,timeout=20000)
  assert video.evaluate('(v)=>v.duration>0 && v.videoWidth>0 && v.paused && !v.autoplay')
  print('Playable metadata:',i+1,flush=True)
 for image in page.locator('.story-card video').all():
  poster=image.get_attribute('poster')
  assert page.request.get('http://127.0.0.1:3001/'+poster).status==200
 # Exercise actual audio/video decoding on two visible cards and the pause rule.
 videos.nth(0).evaluate('(v)=>v.play()')
 page.wait_for_function('document.querySelectorAll(".story-card video")[0].currentTime>0.1')
 videos.nth(1).evaluate('(v)=>v.play()')
 page.wait_for_function('document.querySelectorAll(".story-card video")[0].paused && !document.querySelectorAll(".story-card video")[1].paused')
 videos.nth(1).evaluate('(v)=>v.pause()')
 page.locator('#testimonials .section-heading').scroll_into_view_if_needed()
 page.screenshot(path='/tmp/new-portfolio-validation/stories-desktop.png')
 for width in [320,390,600,768,950,1440]:
  page.set_viewport_size({'width':width,'height':844})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size({'width':390,'height':844})
 page.locator('.stories-track').evaluate('(t)=>t.scrollLeft=0')
 page.wait_for_function("document.querySelector('.stories-position').textContent==='1–1 / 9'")
 page.locator('.stories-next').click()
 page.wait_for_function("document.querySelector('.stories-position').textContent==='2–2 / 9'")
 page.locator('.stories-track').focus()
 page.keyboard.press('ArrowRight')
 page.wait_for_function("document.querySelector('.stories-position').textContent==='3–3 / 9'")
 page.locator('#testimonials .section-heading').scroll_into_view_if_needed()
 page.screenshot(path='/tmp/new-portfolio-validation/stories-mobile.png')
 assert not errors,errors
 b.close()
print('PASS: nine videos, all metadata/posters, actual playback, single playback rule, gallery arrows/end states, keyboard browsing, mobile position counter, no overflow, no JavaScript errors.')
