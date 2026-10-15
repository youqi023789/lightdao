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

  function boot() { try { build(); } catch (e) { } btime(); setInterval(btime, 60000); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
