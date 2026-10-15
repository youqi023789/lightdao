// 用【真实网关响应】验证前端映射：字段名不匹配会在这里暴露，而不是等用户看下拉框
const https = require("https");

function get(url) {
  return new Promise((res, rej) => {
    https.get(url, { timeout: 40000 }, r => {
      let s = ""; r.on("data", d => s += d); r.on("end", () => res(JSON.parse(s)));
    }).on("error", rej);
  });
}

(async () => {
  const j = await get("https://lightdao.net/gw/v1/validators");
  console.log("端点返回: chain_id=%s count=%s bonded=%s", j.chain_id, j.count, j.bonded);

  // ---- 完全照 app_2.js 里的映射逻辑跑一遍 ----
  const CFG_CHAIN = "lightdao-mainnet-1";
  if (j.chain_id && j.chain_id !== CFG_CHAIN) { console.log("FAIL 链ID不符，前端会拒绝显示"); process.exit(1); }
  const vs = (j.validators || []).filter(v => v.operator_address && /^wasmvaloper1/.test(v.operator_address));
  console.log("通过 operator 地址过滤的条数:", vs.length);
  if (vs.length !== 10) { console.log("FAIL 期望 10 个，实际", vs.length); process.exit(1); }

  let bad = 0;
  vs.slice(0, 3).forEach(v => {
    // 修复前：只认 description.moniker
    const oldMon = (v.description && v.description.moniker) || v.operator_address.slice(0, 16);
    // 修复后：兼容扁平 moniker
    const newMon = (v.description && v.description.moniker) || v.moniker || v.operator_address.slice(0, 16);
    const oldLabel = oldMon + " · " + (Number(v.tokens || 0) / 1e6).toFixed(0) + "L";
    const newLabel = newMon + " · " + (Number(v.tokens || 0) / 1e6).toFixed(0) + "L";
    console.log("   旧映射 -> %s", oldLabel);
    console.log("   新映射 -> %s", newLabel);
    if (!/^val/.test(newMon)) { console.log("   FAIL 新映射仍拿不到 moniker"); bad++; }
    if (!/^wasmvaloper1/.test(v.operator_address)) { console.log("   FAIL operator 地址异常"); bad++; }
  });
  // 委托金额换算自检：tokens 是 ulight
  const t0 = Number(vs[0].tokens);
  console.log("   首个验证者质押 = %d ulight = %s LIGHT（应为 50 万级）", t0, (t0 / 1e6).toLocaleString());
  if (!(t0 / 1e6 > 1000)) { console.log("   FAIL 质押量换算不合理（单位错？）"); bad++; }

  console.log(bad ? "\nSHAPE_FAIL " + bad : "\nSHAPE_OK 前端映射与真实网关响应一致");
  process.exit(bad ? 1 : 0);
})().catch(e => { console.log("HARNESS ERROR", e.message); process.exit(2); });
