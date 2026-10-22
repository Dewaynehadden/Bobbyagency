"""Check the two-column testimonial and sales-results layouts on a running site."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1440,'height':1000}, reduced_motion='reduce')
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    assert page.goto('http://127.0.0.1:3001/').status == 200
    assert page.locator('.story-card').count() == 9
    assert page.locator('.sales-video-card').count() == 8
    assert page.locator('.stories-controls').count() == 0
    for width in [320,390,600,768,1051,1440]:
        page.set_viewport_size({'width':width,'height':900})
        for selector in ['.stories-track', '.sales-video-grid']:
            cards = page.locator(selector + ' > article')
            first, second, third = [cards.nth(i).bounding_box() for i in range(3)]
            assert abs(first['y'] - second['y']) < 2, (width, selector)
            assert second['x'] > first['x'], (width, selector)
            assert third['y'] > first['y'], (width, selector)
            assert abs(third['x'] - first['x']) < 2, (width, selector)
            video = cards.first.locator('video').bounding_box()
            assert abs(video['width'] / video['height'] - 16/9) < .03
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    for width, suffix in [(1440,'desktop'),(390,'mobile')]:
        page.set_viewport_size({'width':width,'height':1000})
        for section, name in [('#testimonials','testimonials'),('#sales-proof','sales')]:
            page.locator(section + ' .section-heading').evaluate('(e)=>e.scrollIntoView({block:"start"})')
            page.screenshot(path=f'/tmp/new-portfolio-validation/{name}-two-columns-{suffix}.png')
    assert not errors, errors
    browser.close()
print('PASS: both sections use two columns at all six widths; 16:9 players; 17 videos retained; no carousel controls, page overflow, or JavaScript errors.')
