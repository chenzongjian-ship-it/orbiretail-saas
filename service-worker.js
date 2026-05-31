const CACHE_NAME = 'aurevia-pwa-v55';
self.addEventListener('install', event => {
  self.skipWaiting();
});
self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});
self.addEventListener('fetch', event => {
  // Streamlit apps are dynamic; keep network-first behavior.
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
