"""Functional browser checks. Requires Playwright and a running local server.

Run: python3 scripts/smoke.py
Optional: PORTFOLIO_BASE_URL=http://127.0.0.1:3001 PORTFOLIO_ARTIFACTS=/tmp/portfolio-checks
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

base = os.environ.get('PORTFOLIO_BASE_URL', 'http://127.0.0.1:3001').rstrip('/')
artifacts = Path(os.environ.get('PORTFOLIO_ARTIFACTS', '/tmp/new-portfolio-validation'))
artifacts.mkdir(parents=True, exist_ok=True)
checks = []

def passed(name):
    checks.append(name)
    print('PASS:', name, flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1440,'height':1000}, reduced_motion='reduce')
    errors = []
    failed_resources = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: failed_resources.append(f'{response.status}: {response.url}') if response.status >= 400 and response.url.startswith(base) else None)
    response = page.goto(base, wait_until='networkidle')
    assert response.status == 200
    assert page.title().startswith('Bobbyagency')
    assert page.locator('h1').count() == 1
    assert page.locator('.service-card').count() == 28
    ids = page.locator('[id]').evaluate_all('(elements)=>elements.map(e=>e.id)')
    assert len(ids) == len(set(ids)), 'duplicate IDs'
    for href in page.locator('a[href^="#"]').evaluate_all('(links)=>links.map(a=>a.getAttribute("href"))'):
        assert page.locator(href).count() == 1, href
    passed('Page, 28 service cards, unique IDs, and all local navigation targets')

    # Reduced-motion visitors should not be forced into automatic banner changes.
    assert page.locator('.carousel-pause').get_attribute('aria-pressed') == 'true'
    page.get_by_role('button', name='Next banner', exact=True).click()
    assert page.locator('[data-slide="1"]').is_visible()
    page.get_by_role('button', name='Show banner 3', exact=True).click()
    assert page.locator('[data-slide="2"]').is_visible()
    page.get_by_role('button', name='Previous banner', exact=True).click()
    assert page.locator('[data-slide="1"]').is_visible()
    page.get_by_role('button', name='Show banner 1', exact=True).click()
    assert page.locator('[data-slide="0"]').is_visible()
    passed('Banner navigation, slide dots, previous/next, and reduced-motion pause')

    page.locator('#service-show-all').click()
    # Test every service detail, not just the first card.
    for index in range(28):
        page.locator('.service-card .learn-more').nth(index).click()
        dialog = page.locator('#service-dialog')
        assert dialog.is_visible()
        title = page.locator('.service-card h3').nth(index).inner_text()
        assert page.locator('#service-title').inner_text() == title
        assert page.locator('#service-includes li').count() == 4
        if index == 0:
            page.locator('#service-modal-quote').click()
            assert page.locator('#quote-dialog').is_visible()
            page.locator('#quote-email-option').click()
            assert page.locator('#enquiry-dialog').is_visible()
            assert page.locator('#client-service').input_value() == title
            page.keyboard.press('Escape')
        else:
            dialog.get_by_role('button', name='Close service details').click()
    assert not page.locator('body').evaluate('(b)=>b.classList.contains("modal-open")')
    passed('All 28 service dialogs and service-specific quote selection')

    page.locator('#meet-founder').click()
    assert page.locator('#founder-dialog').is_visible()
    page.keyboard.press('Escape')
    assert not page.locator('#founder-dialog').is_visible()
    page.locator('.skill-node').nth(2).click()
    assert page.locator('#service-dialog').is_visible()
    page.keyboard.press('Escape')
    passed('Founder profile, expertise orbit, and Escape dismissal')

    page.locator('#store-url').fill('not-a-website')
    page.locator('#audit-form button').click()
    assert page.locator('#store-url').get_attribute('aria-invalid') == 'true'
    assert page.locator('#audit-error').inner_text()
    assert not page.locator('#enquiry-dialog').is_visible()
    page.locator('#store-url').fill('example.com/store')
    page.locator('#audit-form button').click()
    assert page.locator('#enquiry-dialog').is_visible()
    assert page.locator('#client-service').input_value() == 'Free store review'
    assert page.locator('#client-site').input_value() == 'https://example.com/store'
    assert not page.locator('#enquiry-form').evaluate('(f)=>f.checkValidity()')
    passed('Invalid URL rejection and review request with normalized public URL')

    page.locator('#client-name').fill('Alex & Partners')
    page.locator('#client-email').fill('alex@example.com')
    page.locator('#client-message').fill('A store redesign with product discovery & a clearer checkout.')
    page.locator('#client-site').fill('javascript:alert(1)')
    page.locator('#enquiry-form button[type=submit]').click()
    assert not page.locator('#email-fallback').is_visible()
    assert page.locator('#client-site').evaluate('(i)=>!!i.validationMessage')
    page.locator('#client-site').fill('https://example.com/store')
    assert page.locator('#enquiry-form').evaluate('(f)=>f.checkValidity()')
    page.locator('#enquiry-form button[type=submit]').click()
    fallback = page.locator('#email-fallback')
    fallback.wait_for(state='visible')
    href = fallback.get_attribute('href')
    assert href.startswith('mailto:dewaynehadden11@gmail.com?')
    assert 'Alex%20%26%20Partners' in href and 'Free%20store%20review' in href
    assert 'https%3A%2F%2Fexample.com%2Fstore' in href
    assert 'has not been sent' in page.locator('#enquiry-status').inner_text()
    page.keyboard.press('Escape')
    passed('Required fields, unsafe URL rejection, encoded email brief, and honest submission status')

    assert page.locator('#project-grid .project-card').count() == 12
    page.locator('#load-more').click()
    assert page.locator('#project-grid .project-card').count() == 20
    assert not page.locator('#load-more').is_visible()
    page.locator('[data-filter="Shopify"]').click()
    assert page.locator('#project-grid .project-card').count() == 1
    assert page.locator('#project-grid').inner_text().find('Shopify Store Design') >= 0
    page.locator('[data-filter="Web design"]').click()
    assert page.locator('#project-grid .project-card').count() == 4
    page.locator('[data-filter="All"]').click()
    page.locator('#project-search').fill('Service Booking Website')
    assert page.locator('#project-grid .project-card').count() == 1
    page.locator('#project-search').fill('no-matching-project-123')
    assert page.locator('#project-empty').is_visible()
    assert page.locator('#project-grid .project-card').count() == 0
    page.locator('#reset-projects').click()
    assert page.locator('#project-grid .project-card').count() == 12
    assert page.locator('#project-search').input_value() == ''
    passed('Portfolio pagination, category filters, search, empty state, and reset')

    tabs = page.get_by_role('tab')
    tabs.nth(0).focus()
    page.keyboard.press('ArrowRight')
    assert tabs.nth(1).get_attribute('aria-selected') == 'true'
    assert page.locator('#panel-booking').is_visible()
    page.keyboard.press('End')
    assert page.locator('#panel-realestate').is_visible()
    page.keyboard.press('Home')
    assert page.locator('#panel-marketplace').is_visible()
    passed('Walkthrough tabs and arrow/Home/End keyboard navigation')

    for detail in page.locator('.faq-list details').all():
        detail.locator('summary').click()
        assert detail.get_attribute('open') is not None
        assert detail.locator('p').is_visible()
        detail.locator('summary').click()
    page.locator('[data-legal="privacy"]').first.click()
    assert page.locator('#information-title').inner_text() == 'Privacy information'
    page.keyboard.press('Escape')
    assert page.locator('.site-footer a[href="terms.html"]').count() == 2
    passed('All 10 FAQs, privacy dialog, and terms page links')

    # Decode lazy images so screenshots show actual content throughout the page.
    for img in page.locator('img').all():
        img.evaluate('(i)=>{i.loading="eager"; return i.decode()}')
    assert page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.complete && i.naturalWidth>0)')
    video = page.locator('video').first
    video.evaluate('(v)=>{v.preload="metadata";v.load()}')
    page.wait_for_function('document.querySelector("video").readyState>=1', timeout=15000)
    assert video.evaluate('(v)=>v.duration>0 && v.videoWidth>0')
    passed('All local images decode and testimonial video metadata loads')

    # Known responsive breakpoints plus small and wide screens.
    for width in [320,375,390,480,600,760,768,1024,1051,1100,1280,1440,1920]:
        page.set_viewport_size({'width':width,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Horizontal overflow at {width}'
    page.set_viewport_size({'width':1440,'height':1000})
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(artifacts/'desktop-top.png'))
    page.screenshot(path=str(artifacts/'desktop-full.png'),full_page=True)
    passed('No horizontal overflow at 13 widths from 320px to 1920px')

    page.set_viewport_size({'width':390,'height':844})
    page.evaluate('window.scrollTo(0,0)')
    toggle = page.locator('.menu-toggle')
    toggle.click()
    assert toggle.get_attribute('aria-expanded') == 'true'
    page.locator('#main-navigation').get_by_role('link',name='Services',exact=True).click()
    assert toggle.get_attribute('aria-expanded') == 'false'
    assert page.evaluate('location.hash') == '#services'
    toggle.click()
    page.keyboard.press('Escape')
    assert toggle.get_attribute('aria-expanded') == 'false'
    assert toggle.evaluate('(b)=>document.activeElement===b')
    page.locator('.header-actions [data-quote="general"]').click()
    page.locator('#quote-email-option').click()
    assert page.locator('#enquiry-dialog').is_visible()
    # Native dialog must keep keyboard focus within itself.
    for _ in range(18):
        page.keyboard.press('Tab')
        assert page.evaluate('document.querySelector("#enquiry-dialog").contains(document.activeElement)')
    page.screenshot(path=str(artifacts/'mobile-enquiry.png'))
    page.keyboard.press('Escape')
    assert not page.locator('#enquiry-dialog').is_visible()
    assert not page.locator('body').evaluate('(b)=>b.classList.contains("modal-open")')
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(artifacts/'mobile-top.png'))
    page.screenshot(path=str(artifacts/'mobile-full.png'),full_page=True)
    passed('Mobile navigation, Escape focus restoration, general project enquiry, and dialog keyboard focus')

    assert not failed_resources, failed_resources
    assert not errors, errors
    passed('No failed local resources or JavaScript errors')
    browser.close()

report={'result':'PASS','checks':checks,'base_url':base,'screenshots':['desktop-top.png','desktop-full.png','mobile-top.png','mobile-full.png','mobile-enquiry.png']}
(artifacts/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
