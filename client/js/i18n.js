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

  function lookup(txt, lang) {
    var e = W.LDI18N[txt];
    if (!e) return null;
    var v = e[lang];
    return (typeof v === "string" && v) ? v : null;
  }

  function trNode(n, lang) {
    var raw = n.nodeValue;
    if (!raw) return;
    var key = raw.trim();
    if (key.length < 2 || !/[\u4e00-\u9fff]/.test(key)) return;   // 没有汉字就别白跑一趟
    var hit = lookup(key, lang);
    if (!hit) return;
    // 保留原文前后空白，避免挤压排版
    var lead = raw.slice(0, raw.length - raw.replace(/^\s+/, "").length);
    var tail = raw.slice(raw.replace(/\s+$/, "").length);
    n.nodeValue = lead + hit + tail;
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
    obs = new MutationObserver(function (ms) {
      for (var i = 0; i < ms.length; i++) {
        var a = ms[i];
        for (var j = 0; j < a.addedNodes.length; j++) { walk(a.addedNodes[j], lang); }
        if (a.type === "characterData" && a.target) { trNode(a.target, lang); }
      }
    });
    try { obs.observe(document.documentElement, { childList: true, subtree: true, characterData: true }); } catch (e) { }
  }

  function apply(lang) {
    W.__ldLang = lang;
    document.documentElement.lang = lang;
    // 不设 dir="rtl"：站内其它页（首页/落地页/挖矿页）都只设 lang，翻了布局会让阿拉伯语
    // 页面整片空白（实测回归）。阿拉伯语句内的右到左由浏览器 bidi 自动处理，无需翻转版式。
    try { localStorage.setItem(STORE, lang); } catch (e) { }
    walk(document.body, lang);
    observe(lang);
    var s = document.getElementById("ld-lang-sw");
    if (s) { s.value = lang; }
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
    } catch (e) { /* 语言层坏了不能影响页面本身 */ }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else { boot(); }

  W.__ldApplyLang = apply;
})();
