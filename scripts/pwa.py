"""Install metadata, service worker, offline recovery, and browser guide checks."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path('/workspace/new-portfolio');manifest=json.loads((root/'manifest.webmanifest').read_text())
assert manifest['scope']=='./' and manifest['display']=='standalone'
for icon in manifest['icons']:assert (root/icon['src']).exists()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=b.new_context(reduced_motion='reduce');page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(e.stack))
 page.goto('http://127.0.0.1:3001/',wait_until='networkidle')
 page.evaluate('navigator.serviceWorker.ready.then(()=>true)')
 page.wait_for_function('navigator.serviceWorker.controller !== null')
 page.locator('.pwa-install').click();assert page.locator('#install-dialog').is_visible()
 assert 'iPhone' in page.locator('#install-dialog').inner_text()
 page.locator('[data-install-close]').click();assert not page.locator('#install-dialog').is_visible()
 for w in [320,390,768,1440]:
  page.set_viewport_size({'width':w,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.goto('http://127.0.0.1:3001/terms.html',wait_until='networkidle');page.locator('.pwa-install').click();assert page.locator('#install-dialog').is_visible();page.keyboard.press('Escape')
 context.set_offline(True)
 page.goto('http://127.0.0.1:3001/?source=app',wait_until='load')
 assert page.get_by_role('heading',name='You’re offline').is_visible()
 assert page.locator('img').evaluate('(i)=>i.complete && i.naturalWidth===192')
 context.set_offline(False);page.locator('#retry').click();page.wait_for_selector('#services')
 assert not errors,errors
 b.close()
print('PASS: app manifest/icons, service worker, install guide on both pages, responsive layout, offline fallback and reconnect')
