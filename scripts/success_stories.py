"""Check both video carousels against the running development server."""
from pathlib import Path
from playwright.sync_api import sync_playwright
Path('/tmp/new-portfolio-validation').mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1440,'height':1000}, reduced_motion='reduce')
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    assert page.goto('http://127.0.0.1:3001/',wait_until='networkidle').status == 200
    assert page.locator('.story-card').count() == 9
    assert page.locator('.sales-video-card').count() == 8
    for width in [320,390,600,768,1051,1440]:
        page.set_viewport_size({'width':width,'height':1000})
        visible=1 if width<=600 else 2
        for carousel in page.locator('[data-video-carousel]').all():
            track=carousel.locator('.media-track')
            cards=track.locator(':scope > article')
            count=cards.count()
            track.evaluate('(e)=>e.scrollTo({left:0,behavior:"instant"})')
            page.wait_for_function('(a)=>document.getElementById(a).scrollLeft<2',arg=track.get_attribute('id'))
            carousel.locator('.media-prev').wait_for(state='visible')
            assert abs(cards.nth(0).bounding_box()['y']-cards.nth(2).bounding_box()['y'])<2
            ratio=track.evaluate('(e)=>e.clientWidth/e.firstElementChild.getBoundingClientRect().width')
            assert (ratio>1.9 if visible==2 else .99<ratio<1.02),(width,ratio)
            carousel.locator('.media-next').click()
            page.wait_for_function('(a)=>document.getElementById(a).scrollLeft>20',arg=track.get_attribute('id'))
            track.focus()
            page.keyboard.press('End')
            page.wait_for_function('(id)=>document.getElementById(id).parentElement.querySelector(".media-next").disabled',arg=track.get_attribute('id'))
            assert carousel.locator('.media-position').inner_text()==f'{count-visible+1}–{count} of {count} videos'
            page.keyboard.press('Home')
            page.wait_for_function('(id)=>document.getElementById(id).parentElement.querySelector(".media-prev").disabled',arg=track.get_attribute('id'))
            carousel.locator('.media-dots button').nth(1).click()
            page.wait_for_function('(id)=>document.getElementById(id).parentElement.querySelectorAll(".media-dots button")[1].getAttribute("aria-current")==="true"',arg=track.get_attribute('id'))
            for video in carousel.locator('video').all():
                assert video.get_attribute('preload')=='none'
                assert video.get_attribute('autoplay') is None
            track.evaluate('(e)=>e.scrollTo({left:0,behavior:"instant"})')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
    for width,suffix in [(1440,'desktop'),(390,'mobile')]:
        page.set_viewport_size({'width':width,'height':1000})
        for section,name in [('#testimonials','client'),('#sales-proof','sales')]:
            page.locator(section+' .section-heading').evaluate('(e)=>e.scrollIntoView({block:"start"})')
            page.screenshot(path=f'/tmp/new-portfolio-validation/{name}-carousel-{suffix}.png')
    assert not errors,errors
    browser.close()
print('PASS: both carousels; 17 videos retained; two desktop/one mobile; arrows, boundaries, dots, keyboard, non-autoplay and six responsive widths; no errors.')
