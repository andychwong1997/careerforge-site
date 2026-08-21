// CareerForge Service Worker — auto-update on new deploy
// Version bump this on every release to force fresh-fetch for returning users.

const VERSION = 'v18.6';
const CACHE_NAME = `cf-${VERSION}`;

// Minimal precache so first install doesn't break offline nav.
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/audit.html',
];

// ============ INSTALL ============
// skipWaiting() so the new SW takes control immediately on update
// (paired with clients.claim() in activate below).
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

// ============ ACTIVATE ============
// Wipe any old-version caches, then claim open clients so the new
// SW starts intercepting fetches right away (no need to reload twice).
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((names) =>
        Promise.all(
          names.filter((name) => name !== CACHE_NAME).map((name) => caches.delete(name))
        )
      )
      .then(() => self.clients.claim())
  );
});

// ============ FETCH ============
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Only handle same-origin requests (skip CDN fonts, analytics, etc.)
  if (url.origin !== self.location.origin) return;

  // Navigation requests (HTML pages): network-first so user always
  // gets the freshest deploy. Fall back to cache only when offline.
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response && response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() =>
          caches.match(event.request).then((cached) => cached || caches.match('/index.html'))
        )
    );
    return;
  }

  // Static assets (CSS, JS, images, fonts): cache-first for speed,
  // but always revalidate in background so updates land next reload.
  event.respondWith(
    caches.match(event.request).then((cached) => {
      const networkFetch = fetch(event.request)
        .then((response) => {
          if (response && response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => cached);

      return cached || networkFetch;
    })
  );
});
