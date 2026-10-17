/* LightDAO 全站语言层（机制，不含词条）
   为什么用"按原文查表"而不是给每个元素加 data-i：
   内页有上千处中文是 JS 运行时渲染出来的（浏览器页的标签、治理页的状态字），
   逐个加属性既改不完也会漏。这里改为遍历文本节点 + 常见属性查表，配合 MutationObserver，
   动态内容一样被翻译；字典按页拆文件，覆盖率可以逐页增长，未覆盖的串保持中文（诚实降级，
   绝不机翻一个错句子冒充翻译）。
   ⚠ 不碰任何按钮 handler、不改 DOM 结构，只改文本与少数属性。 */
(function () {
  "use strict";
  var W = window;
  var STORE = "ld_lang";
  var SUPPORTED = ["zh", "en", "es", "fr", "de", "pt", "ru", "ja", "ko", "ar", "hi", "tr", "vi", "id", "fil"];
  var NAMES = {
    zh: "中文", en: "English", es: "Español", fr: "Français", de: "Deutsch", pt: "Português",
    ru: "Русский", ja: "日本語", ko: "한국어", ar: "العربية", hi: "हिन्दी", tr: "Türkçe",
    vi: "Tiếng Việt", id: "Bahasa Indonesia", fil: "Filipino"
  };
  var RTL = { ar: 1 };
  var done = (W.__ldI18nSeen = W.__ldI18nSeen || (typeof WeakSet === "function" ? new WeakSet() : null));
  var seenAttr = {};

  W.LDI18N = W.LDI18N || {};          // { "中文原文": { en: "...", ... } }

  function urlLang() {
    // ?lang=en 之类的分享链接直达指定语言，并记住它（内页与外页共用同一个键）
    try {
      var m = location.search.match(/[?&]lang=([a-z]{2,3})/i);
      if (m) {
        var l = m[1].toLowerCase();
        if (SUPPORTED.indexOf(l) >= 0) { try { localStorage.setItem(STORE, l); } catch (e) { } return l; }
      }
    } catch (e) { }
    return null;
  }

  function cur() {
    var u = urlLang();
    if (u) return u;
    var l = "zh";
    try { l = localStorage.getItem(STORE) || "zh"; } catch (e) { l = W.__ldLang0 || "zh"; }
    return SUPPORTED.indexOf(l) >= 0 ? l : "zh";
  }

  /* LD-I18N-FALLBACK-20261015 缺该语种词条时回退英文，而不是把中文留给外国用户。
     实测：?lang=fil 以及部分词条在 de 下直接把中文显示给了用户。 */
  function lookup(txt, lang) {
    var e = W.LDI18N[txt];
    if (!e) return null;
    var v = e[lang];
    if (typeof v === "string" && v) return v;
    var f = e.en;                                   /* 英文回退 */
    return (typeof f === "string" && f) ? f : null;
  }

  /* LD-I18N-RUNTIME-20261017 运行时取词：专门服务 JS 现拼的文案（票数/百分比/剩余小时
     每次都变，DOM 遍历那种"整句精确匹配"命中不了）。治理页过去因此在网件里自带一张
     只覆盖 zh/es/pt/id/vi 的小表，成为第二份译文事实源——实测 de/ar/ja 下页面本地化了、
     按钮还是英文。现在取词与 DOM 遍历共用同一份 window.LDI18N。
     两种降级分开登记，因为危害不同：
       __ldTgaps   该语种与英文都没有 → 用户看到中文（硬缺词）
       __ldTgapFb  该语种没有、英文顶上 → 用户看到英文（静默降级，最容易被忽略）
     两者都写进 <html> 的 data-ld-tgaps / data-ld-tgap-fb，由真机渲染巡检取走报警。
     绝不用机翻凑一个可能错的句子冒充翻译。 */
  function countKeys(o) {
    var n = 0;
    for (var k in o) { if (Object.prototype.hasOwnProperty.call(o, k)) n++; }
    return n;
  }
  function publishGaps() {
    try {
      var d = document.documentElement.dataset;
      d.ldTgaps = String(countKeys(W.__ldTgaps || {}));
      d.ldTgapFb = String(countKeys(W.__ldTgapFb || {}));
    } catch (e) { }
  }
  W.__ldT = function (zh, vars) {
    var out = zh;
    try {
      var lang = W.__ldLang || cur();
      if (lang && lang !== "zh") {
        var e = (W.LDI18N || {})[zh];
        var v = e && e[lang];
        if (typeof v === "string" && v) {
          out = v;
        } else {
          var gk = lang + "|" + zh;
          if (e && typeof e.en === "string" && e.en) {
            out = e.en;
            W.__ldTgapFb = W.__ldTgapFb || {};
            W.__ldTgapFb[gk] = (W.__ldTgapFb[gk] || 0) + 1;
          } else {
            W.__ldTgaps = W.__ldTgaps || {};
            W.__ldTgaps[gk] = (W.__ldTgaps[gk] || 0) + 1;
          }
          publishGaps();
        }
      }
    } catch (er) { /* 取词异常绝不能打断渲染 */ }
    if (vars) {
      for (var k in vars) {
        if (Object.prototype.hasOwnProperty.call(vars, k)) {
          out = out.split("{" + k + "}").join(String(vars[k]));
        }
      }
    }
    return out;
  };

  var stats = { writes: 0, skips: 0, same: 0, loopGuard: 0 };
  W.__ldI18nStats = stats;
  function publish() {
    /* 把计数写进 <html> 的 data 属性：无头浏览器 --dump-dom 就能看到，
       这样"翻译器自激循环"这类问题可以在批量测试里被抓到，而不是等用户浏览器卡死。 */
    try {
      var d = document.documentElement.dataset;
      d.ldI18n = "w" + stats.writes + " s" + stats.skips + " same" + stats.same + " guard" + stats.loopGuard;
    } catch (e) { }
  }

  function trNode(n, lang) {
    var raw = n.nodeValue;
    if (raw == null) return;
    /* 关键防循环：这个节点上一次我们看过/写过的值就是它现在的内容 → 不再处理。
       否则「写文本 → characterData 变更 → 观察器回调 → 再写」会自激，
       字典里的恒等译文（Stake→Stake、Txs→Txs、Pool→Pool）必然触发，页面直接卡死。 */
    if (n.__ldv === raw) { stats.skips++; return; }
    n.__ldv = raw;
    var key = raw.trim();
    if (key.length < 2 || !/[\u4e00-\u9fff]/.test(key)) return;
    var hit = lookup(key, lang);
    if (!hit) return;
    var lead = raw.slice(0, raw.length - raw.replace(/^\s+/, "").length);
    var tail = raw.slice(raw.replace(/\s+$/, "").length);
    var outv = lead + hit + tail;
    if (outv === raw) { stats.same++; publish(); return; }   // 译文与原文相同：不写，避免触发 mutation
    n.nodeValue = outv;
    n.__ldv = outv;
    stats.writes++;
    if (done) { try { done.add(n); } catch (e) { } }
  }

  var ATTRS = ["placeholder", "title", "aria-label", "alt"];
  function trEl(el, lang) {
    if (!el || el.nodeType !== 1) return;
    if (done && done.has(el)) return;
    if (el.tagName === "SCRIPT" || el.tagName === "STYLE" || el.tagName === "TEXTAREA") {
      if (el.tagName === "TEXTAREA") {
        for (var i2 = 0; i2 < ATTRS.length; i2++) { trAttr(el, ATTRS[i2], lang); }
      }
      if (done) { try { done.add(el); } catch (e) { } }
      return;
    }
    for (var i = 0; i < ATTRS.length; i++) { trAttr(el, ATTRS[i], lang); }
    if (done) { try { done.add(el); } catch (e) { } }
  }

  function trAttr(el, a, lang) {
    var v = el.getAttribute && el.getAttribute(a);
    if (!v || !/[\u4e00-\u9fff]/.test(v)) return;
    var k = el.tagName + "#" + a + "|" + v;
    if (seenAttr[k]) return;
    var hit = lookup(v.trim(), lang);
    if (!hit) return;
    seenAttr[k] = 1;
    el.setAttribute(a, hit);
  }

  function walk(root, lang) {
    if (!root) return;
    if (root.nodeType === 3) { trNode(root, lang); return; }
    if (root.nodeType !== 1 && root.nodeType !== 9 && root.nodeType !== 11) return;
    var tw;
    try {
      if (typeof document.createTreeWalker !== "function") return;
      tw = document.createTreeWalker(root, 4 /*SHOW_TEXT*/, null, false);
    } catch (e) { return; }
    var n, budget = 4000;
    while ((n = tw.nextNode()) && budget-- > 0) {
      if (done && done.has(n)) continue;
      trNode(n, lang);
    }
    var els = (root.querySelectorAll ? root.querySelectorAll("*") : []);
    for (var i = 0; i < els.length && i < 4000; i++) { trEl(els[i], lang); }
  }

  var obs = null;
  function observe(lang) {
    if (typeof MutationObserver !== "function") return;
    if (obs) { try { obs.disconnect(); } catch (e) { } }
    var burst = 0, burstAt = 0;
    obs = new MutationObserver(function (ms) {
      /* 熔断：一批里处理量异常大 = 我们在自己触发自己。立刻停掉观察器并记账，
         宁可少翻译一些，也绝不能把用户浏览器卡死（explorer 页就是这么挂的）。 */
      var now = Date.now();
      if (now - burstAt > 1000) { burst = 0; burstAt = now; }
      burst += ms.length;
      if (burst > 600) {
        stats.loopGuard += ms.length;
        publish();
        try { obs.disconnect(); } catch (e) { }
        obs = null;
        return;
      }
      for (var i = 0; i < ms.length; i++) {
        var a = ms[i];
        for (var j = 0; j < a.addedNodes.length; j++) { walk(a.addedNodes[j], lang); }
        if (a.type === "characterData" && a.target) { trNode(a.target, lang); }
      }
      publish();
    });
    try { obs.observe(document.documentElement, { childList: true, subtree: true, characterData: true }); } catch (e) { }
  }

  function apply(lang) {
    W.__ldLang = lang;
    document.documentElement.lang = lang;
    // 不设 dir="rtl"：站内其它页（首页/落地页/挖矿页）都只设 lang，翻了布局会让阿拉伯语
    // 页面整片空白（实测回归）。阿拉伯语句内的右到左由浏览器 bidi 自动处理，无需翻转版式。
    try { localStorage.setItem(STORE, lang); } catch (e) { }
    var s = document.getElementById("ld-lang-sw");
    if (s) { s.value = lang; }
    /* 中文是源语言：不需要任何遍历、重扫或常驻观察器。
       之前中文用户也在付「全页 walk + 4 次重扫 + MutationObserver」的代价，收益为零 ——
       这就是「页面没以前流畅」的直接原因（而默认语言恰恰是中文）。 */
    if (lang === "zh") {
      if (obs) { try { obs.disconnect(); } catch (e) { } obs = null; }
      publish();
      document.dispatchEvent(new CustomEvent("ldlang", { detail: { lang: lang } }));
      return;
    }
    walk(document.body, lang);
    observe(lang);
    publish();   // 必须在这里也写一次：否则没有 mutation 的页面读不到计数，
                 // 批量交叉测试会把"仪器没上报"误判成"翻译器没运行"。
    document.dispatchEvent(new CustomEvent("ldlang", { detail: { lang: lang } }));
  }

  function mountSwitcher() {
    if (document.getElementById("ld-lang-sw")) return;
    var host = document.querySelector("header") || document.body;
    var box = document.createElement("span");
    box.className = "ld-sw";
    box.style.cssText = "margin-left:auto;display:inline-flex;gap:6px;align-items:center";
    var sel = document.createElement("select");
    sel.id = "ld-lang-sw";
    sel.setAttribute("aria-label", "选择语言 / Choose language");
    for (var i = 0; i < SUPPORTED.length; i++) {
      var o = document.createElement("option");
      o.value = SUPPORTED[i];
      o.textContent = NAMES[SUPPORTED[i]];
      sel.appendChild(o);
    }
    sel.value = cur();
    sel.addEventListener("change", function () { seenAttr = {}; if (done) { done = W.__ldI18nSeen = new WeakSet(); } apply(sel.value); });
    box.appendChild(sel);
    host.appendChild(box);
  }

  function boot() {
    try {
      // 与首页/挖矿页共用同一个键，切语言不会"进内页就退回中文"
      mountSwitcher();
      apply(cur());
      /* 补扫：页面自己的脚本会异步重写表格/标题（innerHTML 一覆盖，翻译就丢了），
         观察器能抓到大部分但实测仍有漏网，所以延迟重扫几次。
         中文下完全跳过（源语言没有可翻内容），避免无谓的主线程占用。 */
      if (cur() !== "zh") {
        [500, 1800, 4000].forEach(function (ms) {
          setTimeout(function () {
            try { if (cur() === "zh") return;
                  if (done) { done = W.__ldI18nSeen = (typeof WeakSet === "function" ? new WeakSet() : null); }
                  seenAttr = {}; walk(document.body, cur()); publish(); } catch (e) { }
          }, ms);
        });
      }
    } catch (e) { /* 语言层坏了不能影响页面本身 */ }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else { boot(); }

  W.__ldApplyLang = apply;
})();
