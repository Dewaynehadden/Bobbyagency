'use strict';
const CACHE = 'bobbyagency-offline-v1';
const FALLBACK = new URL('offline.html', self.registration.scope).href;
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll([FALLBACK, 'offline.js', 'assets/app/icon-192.png'])).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('bobbyagency-offline-') && key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  if (event.request.url === new URL('offline.js', self.registration.scope).href || event.request.url === new URL('assets/app/icon-192.png', self.registration.scope).href) {
    event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request)));
  }
});
// Always fetch live pages and media. Only navigation gets an offline fallback.
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || event.request.mode !== 'navigate' || !event.request.url.startsWith(self.registration.scope)) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(FALLBACK)));
});
