/* xchain_1.js —— 客户端"跨链"面板：只读地展示链间通道、锁仓、行情与外部兑换入口。
   数据来源一律是同源 /xchain/ 只读代理（服务端一处算，浏览器不复制查询逻辑），
   拿不到数据就明写"读不到"，绝不显示上一次的颜色假装正常（本项目栽过"缓存冒充实时"）。 */
(function () {
  "use strict";
  var API = "/xchain";
  var REFRESH = 30000;
  function T(zh, vars) {
    try { if (typeof window.__ldT === "function") return window.__ldT(zh, vars); } catch (e) { }
    var s = zh;
    if (vars) { for (var k in vars) s = s.split("{" + k + "}").join(String(vars[k])); }
    return s;
  }
  function n0(x) { try { return Number(x).toLocaleString(undefined, { maximumFractionDigits: 0 }); } catch (e) { return String(x); } }
  function el(id) { return document.getElementById(id); }
  function set(id, html) { var e = el(id); if (e) { if (html === undefined || html === null) html = ""; e.innerHTML = html; } }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function ago(utc) {
    if (!utc) return "—";
    var t = Date.parse(utc); if (!t) return "—";
    var d = Math.max(0, Math.round((Date.now() - t) / 1000));
    return T("{n} 秒前", { n: d }) + " / " + d + "s";
  }
  function fail(what, err) {
    var e = el("xcLive");
    if (e) { e.textContent = T("读不到", {}) + " / offline"; e.className = "st"; e.style.color = "#ff7b7b"; }
    set("xcIbc", '<span style="color:#ff9a9a">' + esc(what) + ' ' + T("读不到", {}) + '：' + esc(String(err || "").slice(0, 90)) + '</span>');
  }
  function gj(path, ms) {
    var ctl = ("timeout" in AbortController) ? new AbortController() : null;
    var to = ctl ? setTimeout(function () { try { ctl.abort(); } catch (e) { } }, ms || 12000) : null;
    return fetch(path, { cache: "no-store", signal: ctl ? ctl.signal : undefined })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .finally(function () { if (to) clearTimeout(to); });
  }
  function chainRow(label, c) {
    if (!c) return "<tr><td>" + esc(label) + "</td><td colspan=2 style='color:#ff9a9a'>" + esc(T("读不到", {})) + "</td></tr>";
    return "<tr><td>" + esc(label) + "</td><td class='num'>" + n0(c.height) + "</td><td class='mini'>" + esc(c.chain_id || "?")
      + (c.catching_up ? " · " + esc(T("同步中", {})) : "") + "</td></tr>";
  }
  function renderIbc(d) {
    var pend = (d.pending_a2b || []).length, pend2 = (d.pending_b2a || []).length;
    var rows = [];
    rows.push("<table class='ub2e01b'><thead><tr><th>" + esc(T("链", {})) + "</th><th>" + esc(T("区块高度", {})) + "</th><th>Chain ID</th></tr></thead><tbody>");
    rows.push(chainRow(T("测试网 A", {}), d.a));
    rows.push(chainRow(T("测试网 B", {}), d.b));
    rows.push(chainRow(T("主网", {}), d.main));
    rows.push("</tbody></table>");
    var st = (d.channel_a || {}).state || "?";
    var okish = st === "STATE_OPEN" || st === "OPEN";
    rows.push("<p class='mini'>" + esc(T("通道", {})) + "：A " + esc("channel-2") + " ↔ B " + esc("channel-0")
      + " · <span style='color:" + (okish ? "#7ddc9b" : "#ff9a9a") + "'>" + esc(st) + "</span>"
      + " ｜ " + esc(T("未确认包", {})) + " A→B " + pend + " · B→A " + pend2
      + " ｜ " + esc(T("锁仓", {})) + " " + n0(d.escrow_a) + " stake"
      + " ｜ " + esc(T("中继账户", {})) + " A " + n0(d.relayer_gas_a) + " / B " + n0(d.relayer_gas_b) + "</p>");
    var m = d.mainnet_ibc || {};
    /* 原因文案走本站词典（服务端只给 reason_code），否则非中文语种会看到一长串中文 ——
       这是"同一事实两份表达"的第三种写法，服务端出中文 prose 是最难治的那种。 */
    var REASON = { no_channel_yet:
      "主网跨链未开通：链上实测 0 个 IBC 轻客户端、0 条通道" };
    var why = REASON[m.reason_code] || (m.enabled ? "" : T("未开通", {}));
    rows.push("<p class='mini' style='color:#ffcf8a'>" + esc(T("主网跨链", {})) + "："
      + esc(m.enabled ? T("已开通", {}) : T("未开通", {}))
      + (why ? " — " + esc(why) : "")
      + (m.mainnet_clients != null ? " ｜ " + esc(T("主网 IBC 轻客户端数", {})) + "=" + m.mainnet_clients : "")
      + "</p>");
    if (d.errors && d.errors.length) {
      rows.push("<p class='mini' style='color:#ff9a9a'>" + esc(T("探针读数有缺口", {})) + "：" + esc(d.errors.slice(0, 3).join(" ｜ ")) + "</p>");
    }
    rows.push("<p class='mini' style='color:#7c88ad'>" + esc(T("数据由本站只读探针每 {n} 秒取样", { n: 20 }))
      + " ｜ " + esc(T("更新时间", {})) + " " + ago(d.utc) + (d.cached ? " (cached)" : "") + "</p>");
    set("xcIbc", rows.join(""));
    var e = el("xcLive");
    if (e) { e.textContent = okish ? (T("已连通", {}) + " / live") : (T("异常", {}) + " / " + st); e.className = "st live"; e.style.color = ""; }
  }
  var ASSET = [
    ["lightdao", "LIGHT", "lightdao"],
    ["bitcoin", "BTC", "bitcoin"], ["ethereum", "ETH", "ethereum"],
    ["binancecoin", "BNB", "coin/bnb"], ["solana", "SOL", "solana"],
    ["uniswap", "UNI", "coin/uni"], ["ripple", "XRP", "coin/xrp"], ["dogecoin", "DOGE", "coin/doge"]
  ];
  function renderPrices(d) {
    var u = d.usd || {}, rows = [];
    rows.push("<table class='ub2e01b'><thead><tr><th>" + esc(T("资产", {})) + "</th><th>" + esc(T("价格（美元）", {})) + "</th><th>" + esc(T("24 小时涨跌", {})) + "</th></tr></thead><tbody>");
    var missing = [];
    ASSET.forEach(function (a) {
      var v = u[a[0]];
      if (!v) { missing.push(a[1]); return; }
      var ch = v.chg24h;
      var col = ch == null ? "#7c88ad" : (ch >= 0 ? "#7ddc9b" : "#ff9a9a");
      rows.push("<tr><td>" + esc(a[1]) + "</td><td class='num'>$" + (Math.abs(v.usd) >= 1 ? n0(v.usd) : Number(v.usd).toFixed(4))
        + "</td><td style='color:" + col + "'>" + (ch == null ? "—" : (ch >= 0 ? "+" : "") + ch.toFixed(2) + "%") + "</td></tr>");
    });
    rows.push("</tbody></table>");
    if (missing.length) rows.push("<p class='mini' style='color:#ffcf8a'>" + esc(T("这些资产行情取不到", {})) + "：" + esc(missing.join(", ")) + "</p>");
    rows.push("<p class='mini' style='color:#7c88ad'>" + esc(T("行情来源 CoinGecko，经本站缓存 60 秒", {}))
      + " ｜ " + esc(T("更新时间", {})) + " " + ago(d.utc) + "</p>");
    set("xcPrice", rows.join(""));
  }
  function routes() {
    var h = [];
    h.push("<p class='mini'>" + esc(T("外部跨链交易入口", {})) + "</p>");
    h.push("<div class='row' style='gap:8px;flex-wrap:wrap'>");
    h.push("<a class='btn ghost' rel='noopener nofollow' target='_blank' href='https://li.fi/swap?fromChain=1&toChain=56&fromToken=ETH&toToken=BNB'>" + esc(T("EVM 跨链兑换（Li.Fi）", {})) + "</a>");
    h.push("<a class='btn ghost' rel='noopener nofollow' target='_blank' href='https://jup.ag/'>" + esc(T("Solana 兑换（Jupiter）", {})) + "</a>");
    h.push("<a class='btn ghost' rel='noopener nofollow' target='_blank' href='https://coinmarketcap.com/currencies/lightdao/'>" + esc(T("LIGHT 行情页", {})) + "</a>");
    h.push("</div>");
    h.push("<p class='mini' style='color:#7c88ad'>" + esc(T("这些是第三方聚合器：交易在你的钱包与他们的路由里完成，LightDAO 不托管资产、不参与撮合，也不保证成交结果。", {})) + "</p>");
    set("xcRoutes", h.join(""));
  }
  /* 演示按钮：只发固定金额/固定收款人，服务端还另有 chain-id、通道、在途包、额度四道拒绝条件。
     前端这里不做安全判断（前端的判断从来不算数），只负责把服务端的拒绝原因原样显示出来。 */
  function wireDemo() {
    var b = el("xcDemo"), out = el("xcDemoOut");
    if (!b || !out || b.dataset.wired) return;
    b.dataset.wired = "1";
    b.onclick = function () {
      b.disabled = true;
      out.textContent = T("发送中…", {});
      fetch(API + "/v1/transfer", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ direction: "ab", amount: 20000 }), cache: "no-store"
      }).then(function (r) {
        return r.json().then(function (j) { return { st: r.status, j: j }; }).catch(function () { return { st: r.status, j: {} }; });
      }).then(function (x) {
        b.disabled = false;
        var j = x.j || {};
        if (j.ok !== true) {
          out.textContent = T("失败：{e}", { e: j.error || ("HTTP " + x.st) });
          tick();
          return;
        }
        out.innerHTML = esc(T("已上链，等中继搬运：tx {h}", { h: "" }))
          + " <code style='font-size:12px'>" + esc(String(j.txhash).slice(0, 16)) + "…</code>"
          + " · " + esc(j.channel) + " · " + n0(j.amount) + " stake";
        tick();
      }).catch(function (e) {
        b.disabled = false;
        out.textContent = T("失败：{e}", { e: String((e && e.message) || e).slice(0, 70) });
      });
    };
  }
  function quote() {
    gj(API + "/v1/quote?fromChain=1&toChain=10&fromToken=ETH&toToken=USDC&fromAmount=1000000000000000000", 16000)
      .then(function (d) {
        /* 时长是接口原值（单位由对方定义）：不做换算，避免编出一个看起来很精确的假数字 */
        var eta = d.etaSec == null ? "?" : (d.etaSec + " (Li.Fi raw)");
        set("xcQuote", "<p class='mini'>" + esc(T("跨链报价（1 ETH → USDC，Ethereum → Optimism）", {})) + "：<b>"
          + esc(String(d.tool || "?")) + "</b> · "
          + esc(T("经 {t} 路由，预计到账 {a}，油钱 ${g}，耗时约 {d}",
                  { t: d.tool || "?", a: (d.to && d.to.amount != null ? d.to.amount + " " + (d.to.symbol || "") : "?"),
                    g: d.gasUsd == null ? "?" : d.gasUsd, d: eta }))
          + " <a class='lnk' rel='noopener nofollow' target='_blank' href='" + esc(d.deeplink) + "'>"
          + esc(T("在聚合器打开该笔", {})) + "</a></p>");
      })
      .catch(function (e) {
        set("xcQuote", "<p class='mini' style='color:#ff9a9a'>" + esc(T("失败：{e}", { e: String((e && e.message) || e).slice(0, 70) })) + "</p>");
      });
  }
  function tick() {
    gj(API + "/v1/ibc").then(function (d) { renderIbc(d); wireDemo(); }).catch(function (e) { fail(T("链间状态", {}), e); });
    gj(API + "/v1/prices").then(renderPrices).catch(function (e) {
      set("xcPrice", '<span style="color:#ff9a9a">' + esc(T("行情", {})) + ' ' + esc(T("读不到", {})) + '：' + esc(String(e).slice(0, 70)) + '</span>');
    });
    quote();
  }
  function boot() {
    if (!el("xcIbc")) return;
    routes();
    tick();
    setInterval(tick, REFRESH);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
