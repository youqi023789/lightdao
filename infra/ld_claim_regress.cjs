#!/usr/bin/env node
/* LD-CLAIM-TRUTH 回归测试：用真实链上/网关数据验证修复
   T1 claimedOnChain 必须从链上认出"第 33 天已领"
   T2 scanClaimable 不得再把第 33 天算成可领（幽灵数字根因）
   T3 每个可领日的估算必须等于 池×w/total（独立复算，容差 0.01）
   T4 链上历史查询失败时必须给 warn（不知道 ≠ 没领过），不得静默谎报 */
const fs = require("fs");
const cp = require("child_process");
const vm = require("vm");

const CAND = process.argv[2];
const USER = "wasm19g2hgc28u9c0xxkeyf0fu2dg9k9d8wh8m3fc9v";
const MINING = "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx";
const GW = "https://lightdao.net/gw";
const RPC = "https://lightdao.net/rpc/";

const src = fs.readFileSync(CAND + "/js/app_2.js", "utf8");
const a = src.indexOf("function claimedKey(){");
const b = src.indexOf("window.scanClaimable=scanClaimable;");
if (a < 0 || b < 0) { console.log("FAIL: 取不到补丁代码区间"); process.exit(2); }
const slice = src.slice(a, b);
console.log("取补丁区间 %d 字符 (%s ... scanClaimable)", slice.length, "claimedKey");

function wasmdQuery(msg) {
  const p = cp.spawnSync("wasmd", ["q", "wasm", "contract-state", "smart",
    MINING, JSON.stringify(msg), "--node", "http://127.0.0.1:26657",
    "-o", "json"], { encoding: "utf8", timeout: 60000 });
  const i = p.stdout.indexOf("{");
  if (i < 0) throw new Error("wasmd 无输出: " + (p.stderr || "").slice(0, 140));
  return JSON.parse(p.stdout.slice(i)).data;
}
async function gj(url) {
  const r = await fetch(url, { headers: { "User-Agent": "ld-regress" } });
  if (!r.ok) throw new Error("HTTP " + r.status + " " + url);
  return r.json();
}

const truth = { epoch: null, root: {}, pool: {} };

(async () => {
  truth.epoch = wasmdQuery({ epoch_info: {} });
  const cd = Number(truth.epoch.day_in_epoch);
  console.log("链上真实日号: 第 %d 天 (epoch %s)", cd, truth.epoch.epoch);

  async function mrqStub(m) {
    if (m.epoch_info) return truth.epoch;
    if (m.root_submitted) {
      const d = m.root_submitted.day;
      if (!(d in truth.root)) truth.root[d] = wasmdQuery({ root_submitted: { day: d } });
      return truth.root[d];
    }
    if (m.daily_miner_pool) {
      const d = m.daily_miner_pool.day;
      if (!(d in truth.pool)) truth.pool[d] = wasmdQuery({ daily_miner_pool: { day: d } });
      return truth.pool[d];
    }
    throw new Error("未预期查询 " + JSON.stringify(m));
  }

  const store = {};
  const mk = new Function("window", "myAddr", "CFG", "lsGet", "lsSet",
    slice +
    "\n; return {claimedOnChain: typeof claimedOnChain!==\"undefined\"?claimedOnChain:null," +
    " claimedSet: typeof claimedSet!==\"undefined\"?claimedSet:null," +
    " scanClaimable: typeof scanClaimable!==\"undefined\"?scanClaimable:null};");

  function build(rpcUrl, ls) {
    const win = { __mrq: mrqStub };
    const M = mk(win, USER, { gw: GW, rpc: rpcUrl },
      (k) => (k in ls ? ls[k] : null), (k, v) => { ls[k] = v; });
    return M;
  }

  let bad = 0;
  const M = build(RPC, store);
  if (!M.claimedOnChain || !M.scanClaimable) {
    console.log("FAIL: 补丁函数缺失", JSON.stringify(M)); process.exit(2);
  }

  /* T1 */
  const on = await M.claimedOnChain(USER);
  console.log("\nT1 claimedOnChain -> ok=%s 已领天=%s err=%s",
    on.ok, JSON.stringify(on.days), on.err || "(无)");
  if (!on.ok) { console.log("   FAIL: 链上历史查询失败，测试前提不成立"); bad++; }
  else if (on.days.indexOf(33) < 0) { console.log("   FAIL: 没认出第 33 天已领"); bad++; }
  else console.log("   PASS: 认出第 33 天已在链上领取");

  /* T2 + T3 */
  const r = await M.scanClaimable(30);
  console.log("\nT2 scanClaimable(30) -> ok=%s conflict=%s warn=%s",
    r.ok, r.conflict || "(无)", r.warn || "(空)");
  console.log("   可领天: %s", JSON.stringify(r.days.map(x => x.d)));
  if (!r.ok) { console.log("   FAIL: scanClaimable 未成功"); bad++; }
  if (r.days.some(x => x.d === 33)) {
    console.log("   FAIL: 第 33 天仍被当成可领（幽灵未消除）"); bad++;
  } else console.log("   PASS: 第 33 天已从可领中剔除");

  for (const x of r.days) {
    if (!(x.d in truth.pool)) await mrqStub({ daily_miner_pool: { day: x.d } });
    const pool = Number(truth.pool[x.d]);
    const sc = await gj(GW + "/v1/scores?day=" + x.d);
    const exp = pool / 1e6 * sc.scores[USER].w / sc.total;
    const diff = Math.abs(exp - x.est);
    const tag = diff <= 0.01 ? "PASS" : "FAIL";
    if (tag === "FAIL") bad++;
    console.log("   T3 第 %d 天 est=%s 独立复算=%s 差=%s -> %s",
      x.d, x.est.toFixed(3), exp.toFixed(3), diff.toFixed(5), tag);
  }

  /* T4：把 RPC 指向死端口 => 链上历史查不到 */
  const M2 = build("http://127.0.0.1:1/", {});      /* 空 localStorage，逼它只能靠链上 */
  const r2 = await M2.scanClaimable(30);
  console.log("\nT4 RPC 不可达 + 本机无记录 -> ok=%s warn=%s",
    r2.ok, JSON.stringify(r2.warn || ""));
  console.log("   可领天: %s", JSON.stringify(r2.days.map(x => x.d)));
  if (!r2.warn) { console.log("   FAIL: 查询失败却没有任何警示（会静默谎报）"); bad++; }
  else if (r2.days.some(x => x.d === 33)) {
    console.log("   判定：无链上记录时第 33 天会重新列出，但已带 warn —— 状态是\"未核对\"而不是\"已知可领\"");
  } else console.log("   PASS: 带警示且未谎报");

  console.log("\n=== %s (bad=%d) ===", bad ? "REGRESS FAIL" : "REGRESS PASS", bad);
  process.exit(bad ? 1 : 0);
})().catch(e => { console.log("HARNESS ERROR", (e && e.stack) || e); process.exit(3); });
