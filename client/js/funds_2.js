/* 资金与释放页：实时链高 + 个人解锁进度查询（只读）
   复用站内既有的 vendored cosmjs 加载方式（app_3.js 的 loadCosmjs 同一套），
   只建只读 CosmWasmClient，不建签名客户端、不导入任何密钥。
   ⚠ 领取（Claim）按钮故意不做：那是签名动钱的操作，等创始人在线确认后再开。
      本页只回答"你该拿多少、现在能拿多少"，不替你动钱。 */
(function () {
  "use strict";
  var RPC = location.origin + "/rpc/";
  var VAULTS = [
    { id: "wasm16l8mdmawaq4538ajr89dpfxh7cyll584yw7jqnhgmp5clwp6m8fqtwkz4x", name: "vesting" },
    { id: "wasm1njjtphj6pkvvcrlu4mzf7qy3clhkl7lysu0v2xsdau6dwj4u2r6qvpvwl6", name: "vesting-v2" }
  ];
  var U = 1000000;

  function loadCosmjs() {
    if (window.__c) return Promise.resolve(window.__c);
    var src = "/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2";
    return import(src).then(function (cs) {
      window.__c = { cs: cs };
      return window.__c;
    }).catch(function () { return null; });
  }

  function fmt(n) {
    var v = Number(n) / U;
    return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function out(html) {
    var box = document.getElementById("vestOut");
    if (box) box.innerHTML = html;
  }

  function render(rows) {
    if (!rows.length) {
      out('<p class="note">这个地址在两个锁仓合约里都没有排期（也可能是查询失败）。' +
        '<span class="en">No schedule found for this address in either vesting contract.</span></p>');
      return;
    }
    var html = "<table><tr><th>合约</th><th>总额</th><th>已归属</th><th>已领取</th><th>可领取（估）</th><th>进度</th></tr>";
    rows.forEach(function (r) {
      var claimable = Math.max(0, r.vested - r.claimed);
      var pctv = r.total ? Math.min(100, Math.round(r.vested / r.total * 100)) : 0;
      html += "<tr><td>" + esc(r.name) + "</td><td class='num'>" + fmt(r.total) + "</td>" +
        "<td class='num'>" + fmt(r.vested) + "</td><td class='num'>" + fmt(r.claimed) + "</td>" +
        "<td class='num'><b>" + fmt(claimable) + "</b></td>" +
        "<td><div class='bar' aria-hidden='true'><i style='width:" + pctv + "%'></i></div>" + pctv + "%</td></tr>";
    });
    html += "</table><p class='note'>“可领取”按 <code>已归属 − 已领取</code> 现算，仅供参考；" +
      "<b>本页不提供领取按钮</b>——领取是签名动钱的操作，尚未开放。要立刻核对，用下方命令直接查链。" +
      "<span class='en'>Claimable is computed as vested minus claimed, informational only; this page deliberately offers no claim button.</span></p>";
    out(html);
  }

  function lookup(addr) {
    out('<p class="note">查询中… / Querying…</p>');
    loadCosmjs().then(function (c) {
      if (!c) {
        out('<p class="note">链上查询组件加载失败（网络受限）。你仍可用页面下方的命令自行核对。' +
          '<span class="en">Query library failed to load (network).</span></p>');
        return null;
      }
      return c.cs.CosmWasmClient.connect(RPC).then(function (client) {
        var now = Math.floor(Date.now() / 1000);
        return Promise.all(VAULTS.map(function (v) {
          return client.queryContractSmart(v.id, { schedule: { address: addr } })
            .then(function (d) {
              if (!d || !d.total) return null;
              return client.queryContractSmart(v.id, { vested: { address: addr, at_time: now } })
                .then(function (vested) {
                  return { name: v.name, total: Number(d.total), claimed: Number(d.claimed || 0),
                           vested: Number(vested || 0) };
                });
            })
            .catch(function () { return null; });   // 该合约里没有这个地址，属正常
        })).then(function (res) { render(res.filter(Boolean)); });
      });
    }).catch(function (e) {
      out('<p class="note">查询失败：' + esc(String((e && e.message) || e)) + '</p>');
    });
  }

  function boot() {
    var btn = document.getElementById("vestBtn"), inp = document.getElementById("vestAddr");
    if (!btn || !inp) return;
    btn.addEventListener("click", function () {
      var a = (inp.value || "").trim();
      if (!/^wasm1[02-9ac-hj-np-z]{39,59}$/.test(a)) {
        out('<p class="note">地址格式不对：应为 wasm1… 开头的链上地址。' +
          '<span class="en">Invalid address: expected a wasm1… bech32 address.</span></p>');
        return;
      }
      lookup(a);
    });
    inp.addEventListener("keydown", function (e) { if (e.key === "Enter") btn.click(); });
    try {
      var m = location.search.match(/[?&]addr=(wasm1[0-9a-z]{20,})/i);
      if (m) { inp.value = m[1]; lookup(m[1]); }
    } catch (e) { }
  }

  function refresh() {
    var el = document.getElementById("ldHeight"), elT = document.getElementById("ldTime");
    if (!el) return;
    fetch(RPC + "status", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (j) {
      var si = j && j.result && j.result.sync_info;
      if (si && si.latest_block_height) {
        el.textContent = Number(si.latest_block_height).toLocaleString();
        el.style.color = "var(--ok,#39d98a)";
        if (elT && si.latest_block_time) elT.textContent = String(si.latest_block_time).replace("T", " ").slice(0, 19) + " UTC";
      } else { el.textContent = "取不到（离线）"; el.style.color = "var(--warn,#ffb454)"; }
    }).catch(function () { el.textContent = "取不到（离线）"; el.style.color = "var(--warn,#ffb454)"; });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
  refresh(); setInterval(refresh, 60000);
  document.addEventListener("visibilitychange", function () { if (!document.hidden) refresh(); });
})();
