// Shows the "No dial tone" screen when a page can't load because the visitor is offline.
// Pages always come from the network; only the offline screen and its files are cached.
// Bump VERSION whenever offline.html or anything in OFFLINE changes.
const VERSION = "offline-v1";
const OFFLINE = [
  "/offline.html",
  "/assets/css/error-screen.css",
  "/assets/js/error-screen.js",
  "/assets/images/dialing-offline.gif",
  "/assets/images/dialing-offline-loop.gif",
  "/assets/images/dialing-offline-end.png",
  "/assets/images/favicon.svg",
  "/assets/images/favicon-32.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(OFFLINE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  if (req.mode === "navigate") {
    // Network first; the offline screen only when the network fails outright
    e.respondWith(fetch(req).catch(() => caches.match("/offline.html")));
  } else if (OFFLINE.includes(new URL(req.url).pathname)) {
    // The offline screen's own files, which can't come from the network when it's showing
    e.respondWith(fetch(req).catch(() => caches.match(req, { ignoreSearch: true })));
  }
});
