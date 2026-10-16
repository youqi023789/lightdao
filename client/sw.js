/* LightDAO PWA service worker v3：外壳网络优先（部署即生效），静态资源缓存优先，离线兜底。
   LD-SW-20261014（三处如实性修正）：
   1) /status.json 与链/网关/信令路径一律不拦截。之前 /status.json 落到“缓存优先”分支，
      落地页又是裸 URL 请求，断网或缓存过期时页面会把旧的健康状态当成实时状态显示——
      即“系统正常”可能是昨天读出来的。现在不拦截，取不到就如实显示“—”。
   2) 根目录脚本（passkey-wallet.js / webrtc-relay.js）现在带 ?v= 版本号，按“网络优先+按完整
      URL 缓存”处理，保证离线也能拿到与页面版本号一致的那一份。
   3) 离线兜底只给“导航请求”返回首页；给 JSON/JS 请求返回 HTML 会让前端拿到一坨解析不了的文本。 */
const CACHE = "lightdao-v187";
const SHELL = ["/", "/index.html", "/app.html", "/manifest.json", "/passkey-wallet.js", "/webrtc-relay.js"];
const NET_FIRST = ["/", "/index.html", "/app.html", "/passkey-wallet.js", "/webrtc-relay.js", "/governance.html", "/explorer.html", "/season.html", "/whitepaper.html"];
/* 实时数据：永不走缓存（宁可报错，不可撒谎） */
const NEVER = ["/status.json", "/rpc/", "/gw/", "/signal", "/turn/"];

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
  if (NEVER.some((p) => u.pathname.startsWith(p))) return;
  // JS（含根目录脚本）：网络优先（绕过 HTTP 缓存），失败回退同 URL 缓存 => 部署立即生效
  if ((u.pathname.startsWith("/js/") && !u.pathname.startsWith("/js/vendor/")) || u.pathname.endsWith(".js")) {
    e.respondWith(fetch(e.request, { cache: "no-store" }).then((r) => { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, cp)); return r; }).catch(() => caches.match(e.request)));
    return;
  }
  if (u.pathname.startsWith("/css/")) { e.respondWith(fetch(e.request,{cache:"no-store"}).then(r=>{const cp=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));return r;}).catch(()=>caches.match(e.request))); return; }
  if (NET_FIRST.some((p) => u.pathname === p)) {
    e.respondWith(
      fetch(e.request, { cache: "no-store" })
        .then((r) => { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, cp)); return r; })
        .catch(() => caches.match(e.request).then((hit) => hit || caches.match("/index.html")))
    );
    return;
  }
  // 其余静态（图片/manifest）：缓存优先；离线兜底仅对导航请求返回首页
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(
      (hit) =>
        hit ||
        fetch(e.request)
          .then((r) => { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, cp)); return r; })
          .catch(() => (e.request.mode === "navigate" ? caches.match("/index.html") : Response.error()))
    )
  );
});
