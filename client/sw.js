/* LightDAO PWA service worker: shell 缓存优先,链/网关/信令接口走网络 */
const CACHE = "lightdao-v1";
const SHELL = ["/", "/index.html", "/manifest.json", "/og.png", "/passkey-wallet.js", "/webrtc-relay.js"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => clients.claim())
  );
});
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  // 链/网关/信令/凭证:永远走网络(数据必须实时)
  if (u.pathname.startsWith("/rpc/") || u.pathname.startsWith("/gw/") || u.pathname.startsWith("/signal") || u.pathname.startsWith("/turn/")) return;
  e.respondWith(
    caches.match(e.request).then(
      (hit) =>
        hit ||
        fetch(e.request)
          .then((r) => {
            const cp = r.clone();
            caches.open(CACHE).then((c) => c.put(e.request, cp));
            return r;
          })
          .catch(() => caches.match("/index.html"))
    )
  );
});
