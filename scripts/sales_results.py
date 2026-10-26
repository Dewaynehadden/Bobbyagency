from playwright.sync_api import sync_playwright
from pathlib import Path
import subprocess,json
root=Path('/workspace/new-portfolio')
for i in range(1,9):
 path=root/f'assets/sales/store-report-{i:02}.mp4'
 d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,width,height','-of','json',str(path)]))
 assert float(d['format']['duration'])>0
 assert any(s.get('codec_name')=='h264' for s in d['streams'])
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
 page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda req:requests.append(req.url))
 assert page.goto('http://127.0.0.1:3001/',wait_until='networkidle').status==200
 assert page.locator('.sales-video-card').count()==8
 assert page.locator('.story-card').count()==9
 assert page.locator('.sales-summary-card').count()==4
 assert not any('.mp4' in u for u in requests),'Video content should not preload'
 section=page.locator('#sales-proof')
 assert section.locator('h2').inner_text()=='Real Stores. Real Sales.'
 assert not any(t in section.inner_text() for t in ['2M+','850%','50K+','100+','VERIFIED'])
 for i,video in enumerate(section.locator('video').all()):
  video.evaluate('(v)=>{v.preload="metadata";v.load()}')
  page.wait_for_function('(i)=>document.querySelectorAll(".sales-video-card video")[i].readyState>=1',arg=i,timeout=20000)
  assert video.evaluate('(v)=>v.duration>0 && v.videoWidth>0 && !v.autoplay && v.controls && v.playsInline')
  assert page.request.get('http://127.0.0.1:3001/'+video.get_attribute('poster')).status==200
  print('PASS report playback metadata/poster:',i+1,flush=True)
 first=section.locator('video').nth(0);second=section.locator('video').nth(1)
 first.scroll_into_view_if_needed()
 first.evaluate('(v)=>v.play()')
 page.wait_for_function('document.querySelectorAll(".sales-video-card video")[0].currentTime>0.1')
 second.evaluate('(v)=>v.play()')
 page.wait_for_function('document.querySelectorAll(".sales-video-card video")[0].paused && !document.querySelectorAll(".sales-video-card video")[1].paused')
 second.evaluate('(v)=>v.pause()')
 # Verify the shared playback rule includes the testimonial players.
 page.locator('.story-card video').first.evaluate('(v)=>v.play()')
 second.evaluate('(v)=>v.play()')
 assert page.locator('.story-card video').first.evaluate('(v)=>v.paused')
 second.evaluate('(v)=>v.pause()')
 page.locator('#sales-proof .section-heading').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 page.screenshot(path='/tmp/new-portfolio-validation/sales-desktop.png')
 for width in [320,390,600,768,950,1051,1440]:
  page.set_viewport_size({'width':width,'height':844})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size({'width':390,'height':844})
 page.locator('#sales-proof .section-heading').evaluate('(e)=>e.scrollIntoView({block:"start"})')
 page.screenshot(path='/tmp/new-portfolio-validation/sales-mobile.png')
 page.locator('.menu-toggle').click()
 page.locator('#main-navigation a[href="#sales-proof"]').click()
 assert page.evaluate('location.hash')=='#sales-proof'
 assert page.locator('.menu-toggle').get_attribute('aria-expanded')=='false'
 assert not errors,errors
 b.close()
print('PASS: eight reports, nine testimonials retained, four honest summary cards, no preloading, metadata/posters, actual playback, global pause rule, mobile navigation, responsive layout, no JavaScript errors.')
