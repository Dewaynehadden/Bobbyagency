"""Validate real photo covers, preserved links, and industry idea enquiries."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:3001/',wait_until='networkidle')
    assert page.locator('#project-grid .project-card').count()==12
    page.locator('#load-more').click()
    assert page.locator('#project-grid .project-card').count()==20
    assert page.locator('#project-grid a.project-card').count()==8
    assert page.locator('#project-grid .portfolio-art').count()==0
    for image in page.locator('#project-grid img').all():
        image.scroll_into_view_if_needed()
        image.evaluate('(img) => img.decode()')
        assert image.evaluate('(img) => img.naturalWidth > 300 && img.src.endsWith(".jpg")')
    page.locator('[data-filter="Industry ideas"]').click()
    assert page.locator('#project-grid .project-card').count()==12
    for button in page.locator('.project-idea-quote').all():
        index=int(button.get_attribute('data-quote'))
        button.click()
        expected=page.evaluate('(i) => BOBBY_DATA.services[i].title',index)
        assert page.locator('#quote-service-name').inner_text()==expected
        page.keyboard.press('Escape')
    page.locator('[data-filter="All"]').click()
    for width in [320,390,768,1440]:
        page.set_viewport_size({'width':width,'height':1000})
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.set_viewport_size({'width':1440,'height':1000})
    page.locator('#portfolio').scroll_into_view_if_needed()
    page.screenshot(path='/tmp/new-portfolio-validation/portfolio-photos.png')
    assert not errors,errors
    browser.close()
print('PASS: 20 photo covers, 8 original links, 12 idea quote journeys, responsive layouts, no JavaScript errors')
