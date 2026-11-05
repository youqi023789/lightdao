/* nav.js — 全站吸顶导航 + 每页三个返回按钮 + 出块时间实测
   为什么不用硬编码：出块间隔此前写死 1.75s，实测 5.55~5.58s，差 3 倍。
   现在改成浏览器直连节点，取最近 30 个区块的实测平均；取不到就显示"取不到"，
   绝不退回一个没有依据的数字。 */
(function () {
  "use strict";
  var LINKS = [
    ["/index.html", "首页"],
    ["/app.html#sec-main", "挖矿"],
    ["/app.html", "客户端"],
    ["/contracts.html", "合约与地址"],
    ["/institutions.html", "治理制度"],
    ["/funds.html", "资金与释放"],
    ["/nodes.html", "节点与验证者"],
    ["/governance.html", "治理提案"],
    ["/explorer.html", "浏览器"],
    ["/whitepaper.html", "白皮书"],
    ["/search.html", "搜索"]
  ];
  var HERE = location.pathname.replace(/\/$/, "") || "/index.html";
  if (HERE === "/" || HERE === "") HERE = "/index.html";

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function same(a) {
    var p = a.split("#")[0];
    return p === HERE || (p + "/") === HERE || (p === "/index.html" && HERE === "/index.html");
  }

  function build() {
    var bar = el("div", "ldnav");
    var inr = el("div", "ldnav-in");
    bar.appendChild(inr);

    var brand = el("a", "ldnav-brand", "◈ LightDAO");
    brand.href = "/index.html";
    inr.appendChild(brand);

    var links = el("nav", "ldnav-links");
    links.setAttribute("aria-label", "主导航 / Main navigation");
    LINKS.forEach(function (L) {
      var a = el("a", null, L[1]);
      a.href = L[0];
      if (same(L[0])) a.setAttribute("aria-current", "page");
      links.appendChild(a);
    });
    inr.appendChild(links);

    var back = el("nav", "ldnav-back");
    back.setAttribute("aria-label", "返回导航 / Back navigation");

    var b1 = el("button", "ldnav-b", "← 返回上一页");
    b1.type = "button";
    b1.title = "没有上一页时会自动回首页（直接打开链接时历史是空的，不会点了没反应）";
    b1.onclick = function () {
      try {
        if (window.history && window.history.length > 1) { window.history.back(); return; }
      } catch (e) { }
      location.href = "/index.html";
    };
    back.appendChild(b1);

    var b2 = el("a", "ldnav-b", "返回挖矿页");
    b2.href = "/app.html#sec-main";
    b2.title = "挖矿面板（客户端内 sec-main）";
    back.appendChild(b2);

    var b3 = el("a", "ldnav-b", "返回主客户端");
    b3.href = "/app.html";
    back.appendChild(b3);

    inr.appendChild(back);

    /* 首页/落地页自带导航，这里就不重复列一遍链接 */
    if (document.querySelector("header nav, .nav, nav.top")) bar.setAttribute("data-own-nav", "1");

    var skip = document.querySelector(".skip");
    if (skip && skip.parentNode === document.body && skip.nextSibling) {
      document.body.insertBefore(bar, skip.nextSibling);
    } else {
      document.body.insertBefore(bar, document.body.firstChild);
    }

    /* 页内原来那行"返回上一页 · 合约与地址…"和吸顶导航内容重复，
       有 JS 时收起它；没 JS 时它仍在，功能不丢。 */
    try {
      var rows = document.querySelectorAll("p [data-back]");
      for (var i = 0; i < rows.length; i++) {
        var p = rows[i].closest ? rows[i].closest("p") : null;
        if (p) { p.setAttribute("data-ldnav-hidden", "1"); p.style.display = "none"; break; }
      }
    } catch (e) { }
  }

  /* ---------- 出块时间：实测最近 30 块平均 ---------- */
  function btime() {
    var els = [].slice.call(document.querySelectorAll("[data-btime]"));
    if (!els.length) return;
    var rpc = location.origin + "/rpc/";
    fetch(rpc + "status", { cache: "no-store" })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (j) {
        var h = Number(j.result.sync_info.latest_block_height);
        if (!(h > 31)) throw new Error("高度异常");
        return Promise.all([
          fetch(rpc + "block?height=" + (h - 30), { cache: "no-store" }).then(function (x) { return x.json(); }),
          fetch(rpc + "block?height=" + (h - 1), { cache: "no-store" }).then(function (x) { return x.json(); })
        ]);
      })
      .then(function (a) {
        var t0 = Date.parse(a[0].result.block.header.time);
        var t1 = Date.parse(a[1].result.block.header.time);
        var s = (t1 - t0) / 1000 / 30;
        if (!(s > 0.2 && s < 60)) throw new Error("间隔异常 " + s);
        els.forEach(function (e) {
          e.textContent = s.toFixed(2) + "s";
          e.title = "实测：最近 30 个区块的平均出块间隔（区块高度 "
            + (Number(a[1].result.block.header.height) - 30) + "→" + a[1].result.block.header.height + "）";
        });
      })
      .catch(function (err) {
        els.forEach(function (e) {
          e.textContent = "取不到";
          e.title = "实测失败：" + String((err && err.message) || err) + " —— 宁可不显示，也不写一个没有依据的数字";
        });
      });
  }

  /* LD-NAV-I18N-20261016 非中文语种下把导航与返回按钮换成英文。
     实测（2026-10-16）：英文首页仍有 21 处中文可见文字，其中 14 处就是这套
     全站共用导航——它出现在 18 个页面上，一处改完全站生效。 */
  var NAVEN = {
    "首页": "Home", "挖矿": "Mining", "客户端": "Client",
    "合约与地址": "Contracts", "治理制度": "Governance", "资金与释放": "Funds & Vesting",
    "节点与验证者": "Nodes & Validators", "治理提案": "Proposals", "浏览器": "Explorer",
    "白皮书": "Whitepaper", "搜索": "Search",
    "← 返回上一页": "← Back", "返回上一页": "Back",
    "返回挖矿页": "Mining panel", "返回主客户端": "Client",
    "语言": "Language", "出块时间": "Block time", "取不到": "n/a"
  };
  var NAVTIP = {
    "没有上一页时会自动回首页（直接打开链接时历史是空的，不会点了没反应）":
      "Goes back; falls back to the home page when there is no history",
    "挖矿面板（客户端内 sec-main）": "Mining panel (sec-main inside the client)",
    "主客户端": "Main client"
  };
  /* LD-NAV-USE-SHARED-DICT-20261105 导航文字优先走全站 14 语种词典。
     旧写法只有一张中英对照小表：德语页 = 德语正文 + 英语导航（漏翻普查看不见，
     因为里面没有汉字）。现在先问全站词典，问不到才退回小表，并计数供巡检发现。 */
  window.__ldNavFallback = 0;
  function navT(zh) {
    try {
      var l = navLang();
      if (!l || l.indexOf("zh") === 0) return zh;
      /* 不含汉字就说明这句已经是译文（或本来就是英文/数字），再拿去问词典只会记成假缺口 */
      if (typeof zh !== "string" || !/[\u4e00-\u9fff]/.test(zh)) return zh;
      if (typeof window.__ldT === "function") {
        var v = window.__ldT(zh);
        if (v && v !== zh) return v;
      }
      if (typeof zh === "string" && NAVEN[zh]) { window.__ldNavFallback++; return NAVEN[zh]; }
    } catch (e) { }
    return zh;
  }
  function navLang() {
    var l = "";
    try { l = (new URLSearchParams(location.search).get("lang") || "").toLowerCase(); } catch (e) { }
    if (!l) { try { l = (localStorage.getItem("ld_lang") || "").toLowerCase(); } catch (e) { l = ""; } }
    if (!l) { l = (document.documentElement.lang || "").toLowerCase(); }
    return l;
  }
  function navI18n() {
    var l = navLang();
    if (!l || l.indexOf("zh") === 0) return;      /* 中文与"没表态"都不动 */
    var nodes = document.querySelectorAll(".ldnav a, .ldnav button, .ldnav-b, .ldnav span, .ldnav b");
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i], t = (n.textContent || "").trim();
      var v = navT(t);
      if (v !== t) n.textContent = v;
      if (n.title && NAVTIP[n.title] !== undefined) n.title = NAVTIP[n.title];
    }
  }
  /* boot 阶段不要急着换导航文字：那时 i18n 还没 __ldExpandAll，本语种列是空的，
     查表只能退到英文小表 → 用户看到"德语正文 + 英语导航"（实测 __ldTgapFb 11 条）。
     现在只在词典已就绪时做一次，其余交给 i18n 应用完成后派发的 ldlang 事件。 */
  function boot() { try { build(); if (window.__ldLang) navI18n(); } catch (e) { } btime(); setInterval(btime, 60000); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
  /* 切语种后重贴导航：i18n.js 应用完会派发 ldlang */
  try { document.addEventListener("ldlang", function () { try { navI18n(); } catch (e) { } }); } catch (e) { }
})();
