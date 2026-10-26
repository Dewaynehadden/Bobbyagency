"""Validate photographic banner layout, links, automatic timing, and pause controls."""
from pathlib import Path
from playwright.sync_api import sync_playwright
Path('/tmp/new-portfolio-validation').mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    assert page.goto('http://127.0.0.1:3001/',wait_until='networkidle').status==200
    for image in page.locator('.banner-photo').all():
        image.evaluate('(i)=>i.decode()')
        assert image.evaluate('(i)=>i.naturalWidth>800')
    page.mouse.move(0,0)
    page.wait_for_function('!document.querySelector("[data-slide=\\"1\\"]").hidden',timeout=7500)
    before=page.evaluate('performance.now()')
    page.wait_for_function('!document.querySelector("[data-slide=\\"2\\"]").hidden',timeout=7500)
    duration=page.evaluate('performance.now()')-before
    assert 5000<duration<7100,duration
    before=page.evaluate('performance.now()')
    page.wait_for_function('!document.querySelector("[data-slide=\\"0\\"]").hidden',timeout=7500)
    duration=page.evaluate('performance.now()')-before
    assert 5000<duration<7100,duration
    print('PASS: automatic 6-second progression through all three slides and wraparound.',flush=True)
    page.locator('.carousel-pause').click()
    assert page.locator('.carousel-pause').get_attribute('aria-pressed')=='true'
    page.mouse.move(0,0)
    page.wait_for_timeout(6300)
    assert page.locator('[data-slide="0"]').is_visible()
    for width in [320,390,600,768,1440]:
        page.set_viewport_size({'width':width,'height':1000})
        for i in range(3):
            page.locator(f'[data-goto="{i}"]').click()
            slide=page.locator(f'[data-slide="{i}"]')
            assert slide.is_visible()
            assert slide.locator('.banner-photo').is_visible()
            content=slide.locator('.photo-banner-content').bounding_box()
            bounds=slide.bounding_box()
            for selector in ['h2','p','.button']:
                box=slide.locator(selector).bounding_box()
                assert box['x']>=bounds['x']-1 and box['x']+box['width']<=bounds['x']+bounds['width']+1,(width,i,selector)
                assert box['y']>=bounds['y'] and box['y']+box['height']<=bounds['y']+bounds['height'],(width,i,selector)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,i)
            if width in [390,1440]:
                page.wait_for_function('(selector)=>getComputedStyle(document.querySelector(selector)).opacity==="1"', arg=f'[data-slide="{i}"] .photo-banner-content')
                page.screenshot(path=f'/tmp/new-portfolio-validation/banner-{i+1}-{width}.png')
    page.set_viewport_size({'width':1440,'height':1000})
    page.locator('[data-goto="0"]').click()
    page.locator('[data-slide="0"] [data-quote]').click()
    assert page.locator('#quote-dialog').is_visible()
    page.locator('#quote-email-option').click()
    assert page.locator('#enquiry-dialog').is_visible()
    page.keyboard.press('Escape')
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('.carousel-pause').get_attribute('aria-pressed')=='true'
    assert not errors,errors
    browser.close()
print('PASS: image decoding, pause, manual navigation, responsive photo/text/CTA bounds, enquiry CTA, reduced motion, and no JavaScript errors.')
