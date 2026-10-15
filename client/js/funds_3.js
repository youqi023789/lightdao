/* funds_3.js — 资金页实时链上取数 + 资金变动记录（浏览器直连主网，只读）
   为什么存在：本页 10-14 的手工快照在 10-15 之后变成了假话（4 亿已从金库转入
   生态基金合约，快照仍写着"投资金库+生态基金 1,242,000,092"）。规则是
   "公开页面不得用旧数字冒充现状"，所以这里做到：
   1) 每个余额都从链上现查，并显示同步时刻；
   2) 查不到就显示"取数失败 + 原因"，绝不回落到旧数字；
   3) 资金变动记录直接读多签合约 {"tx":{"id":N}}，不是我抄的一份台账；
   4) 生态基金合约自己的 unlocked/released/remaining 一并读出来。
   不做任何签名操作。 */
(function () {
  "use strict";
  var RPC = location.origin + "/rpc/";
  var U = 1000000;
  var DENOM = "ulight";
  var POOLS = [
    { k: "mining_reward", a: "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx", zh: "挖矿奖励池", en: "Mining reward pool", cap: 1000000000 },
    { k: "treasury", a: "wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u", zh: "投资金库（多签）", en: "Investment treasury (multisig)", cap: 850000000 },
    { k: "ecofund", a: "wasm1j0rhxwwcys2rewlvssylwrf24ghyvxhhzjr47nsx8q8mechp3x0qztt835", zh: "生态发展基金", en: "Ecosystem fund", cap: 400000000 },
    { k: "insurance", a: "wasm1wj3369pug9sdn5wcqu74yr00vtcntqvwgqrmcs0k0twwnvgm8m2qu77ewf", zh: "保险基金", en: "Insurance fund", cap: 0 },
    { k: "vesting", a: "wasm16l8mdmawaq4538ajr89dpfxh7cyll584yw7jqnhgmp5clwp6m8fqtwkz4x", zh: "锁仓 v1（TGE 释放）", en: "Vesting v1", cap: 0 },
    { k: "vesting2", a: "wasm1njjtphj6pkvvcrlu4mzf7qy3clhkl7lysu0v2xsdau6dwj4u2r6qvpvwl6", zh: "锁仓 v2（工作包 54）", en: "Vesting v2", cap: 0 }
  ];
  var TREASURY = POOLS[1].a;
  var ECO = POOLS[2].a;
  /* 进度埋点：出问题时一眼看到卡在第几步（<html data-live-step>），
     非技术同学不用开控制台，我远程看 DOM 属性就能定位。 */
  function step(s) { try { document.documentElement.setAttribute("data-live-step", s); } catch (e) { } }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function fmt(v) {
    return (Number(v) / U).toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  function stamp() {
    var d = new Date();
    function p(n) { return (n < 10 ? "0" : "") + n; }
    return d.getUTCFullYear() + "-" + p(d.getUTCMonth() + 1) + "-" + p(d.getUTCDate())
      + " " + p(d.getUTCHours()) + ":" + p(d.getUTCMinutes()) + ":" + p(d.getUTCSeconds()) + " UTC";
  }
  function box(id, html) { var e = document.getElementById(id); if (e) e.innerHTML = html; }
  function failCell(why) {
    return "<td class='num' style='color:var(--warn,#ffb454)'>取数失败<span class='en'>"
      + esc(String(why).slice(0, 60)) + "</span></td>";
  }

  function loadCosmjs() {
    return import("/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2")
      .then(function (cs) { return cs; }).catch(function () { return null; });
  }

  /* ---------- 实时余额表 ---------- */
  function renderBal(rows, errs, ok) {
    var h = "<table><tr><th>账户</th><th>链上余额（LIGHT）</th><th>白皮书额度</th></tr>";
    rows.forEach(function (r) {
      h += "<tr><td>" + esc(r.zh) + " <span class='en'>" + esc(r.en) + "</span>"
        + "<br><code style='font-size:11px;opacity:.7'>" + esc(r.a.slice(0, 18)) + "…" + esc(r.a.slice(-6)) + "</code></td>";
      h += (r.balance === null) ? failCell(r.err) : "<td class='num'><b>" + fmt(r.balance) + "</b></td>";
      /* cap 本身就是 LIGHT 单位，绝不能再除 1e6（上一版就是这么把 10 亿显示成 1,000 的） */
      var capTxt = r.cap ? r.cap.toLocaleString() : "—";
      var over = r.cap && r.balance !== null && Number(r.balance) > r.cap * 1000000 * 1.001;
      if (over) {
        capTxt += " <span class='st part'>超出额度</span>";
        r.over = true;
      }
      h += "<td class='num'>" + capTxt + "</td></tr>";
    });
    var overN = rows.filter(function (r) { return r.over; }).length;
    if (overN) {
      h += "<p class='note' style='color:var(--warn,#ffb454)'>⚠ 有 " + overN +
        " 个账户的链上余额高于白皮书额度，请核对是额度口径变化还是显示口径出错。" +
        "<span class='en'>On-chain balance exceeds the documented allocation — verify before trusting the table.</span></p>";
    }
    h += "</table>";
    var sum = 0, anyBad = false;
    rows.forEach(function (r) { if (r.balance === null) anyBad = true; else sum += Number(r.balance); });
    h += "<p class='note'>以上 6 个账户合计 <b>" + (anyBad && !errs.length ? "—" : fmt(sum))
      + " LIGHT</b>。" + (anyBad ? "<span style='color:var(--warn,#ffb454)'>有账户取数失败，合计不含失败项，勿当作准确总数。</span>" : "")
      + "<span class='en'>Live per-account balances; failed rows are excluded from the total and labelled as failures.</span></p>";
    box("liveBal", h);
  }

  /* ---------- 生态基金合约自身的释放口径 ----------
     合约返回的是字符串形式的 ulight（实测 balance="400000000000000"），
     所以直接交给 fmt（它负责除以 1e6），这里绝对不能再乘 U。 */
  function renderEco(o) {
    if (!o) return;
    var h = "<table><tr><th>生态基金合约自报</th><th>数值（LIGHT）</th></tr>";
    h += "<tr><td>合约内余额 <span class='en'>balance</span></td><td class='num'>" + (o.balance === null ? "—" : fmt(o.balance)) + "</td></tr>";
    h += "<tr><td>已解锁（可动用）<span class='en'>unlocked</span></td><td class='num'>" + (o.unlocked === null ? "—" : fmt(o.unlocked)) + "</td></tr>";
    h += "<tr><td>已释放 <span class='en'>released</span></td><td class='num'>" + (o.released === null ? "—" : fmt(o.released)) + "</td></tr>";
    h += "<tr><td>剩余 <span class='en'>remaining</span></td><td class='num'>" + (o.remaining === null ? "—" : fmt(o.remaining)) + "</td></tr>";
    h += "</table>";
    box("liveEco", h);
  }

  /* ---------- 金库多签的变动记录（读合约，不是抄台账） ---------- */
  function renderLedger(signers, txs) {
    var h = "<p class='note'>签名人共 <b>" + signers.length + "</b> 个（地址来自链上查询）：";
    signers.forEach(function (s, i) {
      h += "<br><code style='font-size:11px'>" + (i + 1) + " · " + esc(s) + "</code>";
    });
    h += "</p>";
    if (!txs.length) {
      h += "<p class='note'>未读到任何动账提案。</p>";
    } else {
      h += "<table><tr><th>提案号</th><th>金额（LIGHT）</th><th>收款方</th><th>审批（门槛 "
        + Math.ceil(signers.length * 3 / 5) + "/" + signers.length + "）</th><th>入队时刻</th><th>状态</th></tr>";
      txs.forEach(function (t) {
        var q = Number(t.queued_at || 0);
        var lock = q ? new Date((q + 259200) * 1000).toISOString().replace("T", " ").slice(0, 19) + "Z" : "—";
        h += "<tr><td>#" + esc(t.id) + "</td><td class='num'>" + fmt(t.amount) + "</td>"
          + "<td><code style='font-size:11px'>" + esc(String(t.recipient).slice(0, 16)) + "…</code></td>"
          + "<td>" + (t.approvals || []).length + " 票：" + (t.approvals || []).map(function (a) {
            return "<code style='font-size:11px'>" + esc(String(a).slice(0, 14)) + "…</code>";
          }).join("<br>") + "</td>"
          + "<td>" + (q ? new Date(q * 1000).toISOString().replace("T", " ").slice(0, 19) + "Z" : "—")
          + "<br><span class='en'>72h 时间锁到期 " + lock + "</span></td>"
          + "<td>" + (t.executed ? "<span class='st live'>已执行</span>" : "<span class='st part'>待执行</span>") + "</td></tr>";
      });
      h += "</table>";
    }
    h += "<p class='note'>完整可读版台账见仓库 <code>docs/TREASURY_MOVEMENT_LEDGER.md</code>；"
      + "任何动用金库的操作都会在执行前后即时告知所有者，而不是等有人来问。"
      + "<span class='en'>Every treasury action is reported to the owner before and after execution.</span></p>";
    box("liveLedger", h);
  }

  async function refresh() {
    step("1 加载查询组件");
    var cs = await loadCosmjs();
    step(cs ? "2 组件就绪" : "2 组件加载失败");
    if (!cs) {
      box("liveBal", "<p class='note'>链上查询组件加载失败（网络受限），<b>不会显示旧数字冒充现状</b>。"
        + "可用本页下方命令自行核对。<span class='en'>Query library failed to load; no stale numbers are shown.</span></p>");
      return;
    }
    var client;
    step("3 连接主网节点");
    try { client = await cs.CosmWasmClient.connect(RPC); step("4 已连接"); }
    catch (e) {
      step("4 连接失败: " + String((e && e.message) || e).slice(0, 70));
      box("liveBal", "<p class='note'>连不上主网节点：" + esc(String((e && e.message) || e).slice(0, 80))
        + "，本页拒绝显示任何数字。</p>");
      return;
    }
    var rows = await Promise.all(POOLS.map(function (p) {
      return client.getBalance(p.a, DENOM).then(function (b) {
        return { zh: p.zh, en: p.en, a: p.a, cap: p.cap, balance: Number(b.amount || 0), err: "" };
      }).catch(function (e) {
        return { zh: p.zh, en: p.en, a: p.a, cap: p.cap, balance: null, err: String((e && e.message) || e) };
      });
    }));
    step("5 余额已取回");
    renderBal(rows);

    var q1 = function (addr, m) { return client.queryContractSmart(addr, m).then(function (v) { return v; }).catch(function () { return null; }); };
    var eco = await Promise.all([q1(ECO, { balance: {} }), q1(ECO, { unlocked: {} }),
                                q1(ECO, { released: {} }), q1(ECO, { remaining: {} })]);
    function num(x) { return x === null ? null : Number(typeof x === "object" ? (x.amount || x.value || 0) : x); }
    step("6 生态基金已查");
    renderEco({ balance: num(eco[0]), unlocked: num(eco[1]), released: num(eco[2]), remaining: num(eco[3]) });

    var sg = await q1(TREASURY, { signers: {} });
    var signers = Array.isArray(sg) ? sg : [];
    var txs = [];
    if (signers.length) {
      for (var id = 1; id <= 12; id++) {
        var t = await q1(TREASURY, { tx: { id: id } });
        if (t && t.id) txs.push(t); else if (!t) break;      /* 合约对不存在的号报错即停 */
      }
    }
    step("7 台账已读: 签名人 " + signers.length + " 个 / 提案 " + txs.length + " 笔");
    renderLedger(signers, txs);

    var el = document.getElementById("liveSync");
    if (el) el.textContent = "最后同步 " + stamp();
  }

  function boot() {
    var host = document.getElementById("liveBal");
    if (!host) return;
    function run() { refresh().catch(function (e) {
      step("X 异常: " + String((e && e.message) || e).slice(0, 90));
    }); }
    run();
    setInterval(run, 60000);
    document.addEventListener("visibilitychange", function () { if (!document.hidden) run(); });
    var b = document.getElementById("liveReload");
    if (b) b.onclick = function () { b.disabled = true; b.textContent = "同步中…";
      refresh().then(function () { b.disabled = false; b.textContent = "立即重新同步 / Re-sync now"; })
        .catch(function () { b.disabled = false; b.textContent = "立即重新同步 / Re-sync now"; }); };
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
