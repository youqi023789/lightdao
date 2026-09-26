/* LightDAO PWA service worker v2: shell 网络优先(部署即生效),静态媒体缓存优先,离线回退 */
const CACHE = "lightdao-v5";
const SHELL = ["/", "/index.html", "/app.html", "/manifest.json", "/passkey-wallet.js", "/webrtc-relay.js"];
const NET_FIRST = ["/", "/index.html", "/app.html", "/passkey-wallet.js", "/webrtc-relay.js", "/governance.html", "/explorer.html", "/season.html", "/whitepaper.html"];

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
  // HTML/JS 壳:网络优先(bypass HTTP cache),失败回退缓存 => 部署立即生效
  if (u.pathname.startsWith("/js/") && !u.pathname.startsWith("/js/vendor/")) { e.respondWith(fetch(e.request,{cache:"no-store"}).then(r=>{const cp=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));return r;}).catch(()=>caches.match(e.request))); return; }
  if (u.pathname.startsWith("/css/")) { e.respondWith(fetch(e.request,{cache:"no-store"}).then(r=>{const cp=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));return r;}).catch(()=>caches.match(e.request))); return; }
  if (NET_FIRST.some((p) => u.pathname === p)) {
    e.respondWith(
      fetch(e.request, { cache: "no-store" })
        .then((r) => { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, cp)); return r; })
        .catch(() => caches.match(e.request).then((hit) => hit || caches.match("/index.html")))
    );
    return;
  }
  // 其余静态(图片/manifest):缓存优先
  e.respondWith(
    caches.match(e.request).then(
      (hit) =>
        hit ||
        fetch(e.request)
          .then((r) => { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, cp)); return r; })
          .catch(() => caches.match("/index.html"))
    )
  );
});
