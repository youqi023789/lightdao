// LD-LANG-COVERAGE-20261017  语种覆盖率棘轮（不需要浏览器，直接读词典真值）。
// 为什么需要：现有语种门禁只量"英文页里有多少汉字"，看不见"下拉里列着 15 种语言、
// 其中 9 种其实只给了英文"。绿灯只覆盖它检查的那一维。
// 口径：按生产脚本顺序在 node 桩里加载词典，统计每个语种覆盖多少条中文原文；
// 覆盖率低于阈值（默认 50%）的语种列为"未达标"；只对【比上次新增的未达标语种】告警
// （棘轮），存量问题每天在日志里报一行状态，不重复刷屏——因为"要不要收下拉"
// 是产品决策，不该由机器天天报红逼用户做决定。
const fs = require("fs");
const vm = require("vm");

// 可指向候选目录（默认线上）：发布前就该能量候选的覆盖率，而不是只能量已上线的。
const ROOT = process.env.LD_JS_ROOT || "/var/www/lightdao/js";
// 加载顺序必须来自页面里真实的 script 顺序，不能在工具里再写死一份：
// 写死的那份不会随新语种文件加入而更新，结果就是"文件已上线、监控仍报 10%"
// （本次加 i18n_more.js 时正好撞上）。
function orderFromHtml() {
  const cands = [require("path").join(ROOT, "..", "funds.html"),
                 require("path").join(ROOT, "..", "governance.html"),
                 require("path").join(ROOT, "..", "contracts.html")];
  for (const p of cands) {
    try {
      const h = fs.readFileSync(p, "utf8");
      const seq = [...h.matchAll(/src="[^"]*\/(i18n[a-zA-Z0-9_.-]*\.js)/g)].map(m => m[1]);
      const uniq = [...new Set(seq)];
      if (uniq.length >= 2) {
        /* LD-COV-ORDER-20261017 这里原本还要把 lat/more 重排到"最后"，理由是
           "展开器依赖前面已填好的 en"——这个前提是错的，而且后果静默：
           __ldExpandLangs 定义在 i18n_lat.js 末尾，lat 被排到最后时
           i18n_more.js / i18n_b2.js 加载时展开器还不存在，它们的守卫触发、
           一条都不落地，监控于是永远报"9 语种 20%"。
           实测：真页面顺序 de=204/551，重排后 de=110/551。
           顺序的唯一真值就是页面里的顺序，工具没有资格再改一遍。 */
        return uniq;
      }
    } catch (e) { }
  }
  return ["i18n.js", "i18n_core.js", "i18n_pages_en.js", "i18n_pages_en2.js",
          "i18n_pages_en3.js", "i18n_lat.js", "i18n_more.js"];   // 兜底：读不到页面时
}
const ORDER = orderFromHtml();
const ALERTS = process.env.LD_ALERTS || "/home/ubuntu/ld_alerts.log";
const STATE = process.env.LD_LANG_STATE || "/var/lib/ld_lang_coverage/state.json";
const LIMIT = parseFloat(process.env.LD_LANG_LIMIT || "50");

const sb = {
  window: {}, document: { documentElement: { dataset: {} }, querySelectorAll: () => [],
    addEventListener: () => {}, createTextNode: () => ({}), readyState: "complete" },
  localStorage: { getItem: () => null, setItem: () => {} },
  navigator: { language: "en-US" }, console,
  location: { search: "", pathname: "/index.html", origin: "https://lightdao.net" },
  MutationObserver: function () { this.observe = () => {}; this.disconnect = () => {}; },
  fetch: () => Promise.resolve({ json: () => Promise.resolve({}) }),
  setTimeout, setInterval, clearTimeout,
};
sb.window = sb; sb.globalThis = sb;
for (const f of ORDER) {
  try { vm.runInNewContext(fs.readFileSync(ROOT + "/" + f, "utf8"), sb, { timeout: 8000 }); }
  catch (e) { console.log("加载 " + f + " 异常: " + String(e.message).slice(0, 60)); }
}
const D = sb.LDI18N || sb.window.LDI18N || {};
const keys = Object.keys(D);
/* LD-COV-STATS-20261017 加载顺序坏了的时候，词典照样"非空"、覆盖率照样能算出个数，
   所以必须直接看展开器自己的回执：expander-missing 或 missing>0 都说明
   有一批译文根本没落地。以前这里什么都不看，才让"20%"演了三周。 */
const tblStats = ["__ldLatStats", "__ldMoreStats", "__ldB2Stats"]
  .filter(k => sb[k]).map(k => k + "=" + JSON.stringify({
    applied: sb[k].applied, missing: sb[k].missing, already: sb[k].already, error: sb[k].error }));
for (const k of ["__ldLatStats", "__ldMoreStats", "__ldB2Stats"]) {
  if (sb[k] && sb[k].error) {
    const msg = "ALERT [lang-coverage] " + k + " 报 " + sb[k].error
      + "：展开器没就位，本文件译文一条都没生效（顺序或挂载点错了）";
    console.log(msg);
    try { fs.appendFileSync(ALERTS, new Date().toISOString() + " " + msg + "\n"); } catch (e) { }
    process.exit(6);
  }
}
console.log("展开器回执：" + (tblStats.join("  ") || "（无表式文件）"));
if (!keys.length) {
  const msg = "ALERT [lang-coverage] 词典为空或加载失败，本次判定作废（不是【没问题】）";
  console.log(msg);
  try { fs.appendFileSync(ALERTS, new Date().toISOString() + " " + msg + "\n"); } catch (e) { }
  process.exit(5);
}
// 下拉里承诺的语种（从 i18n.js 的 SUPPORTED 读，不写死第二份清单）
const src = fs.readFileSync(ROOT + "/i18n.js", "utf8");
const m = src.match(/SUPPORTED\s*=\s*\[([^\]]+)\]/);
const advertised = m ? m[1].match(/"([a-z]{2,3})"/g).map(x => x.replace(/"/g, "")) : [];

const cov = {};
for (const l of advertised) {
  let n = 0;
  for (const k of keys) { const v = D[k] || {}; if (typeof v[l] === "string" && v[l].trim()) n++; }
  cov[l] = { pct: +(100 * n / keys.length).toFixed(1), n };
}
const below = advertised.filter(l => l !== "zh" && cov[l].pct < LIMIT);
console.log("中文原文 " + keys.length + " 条；下拉承诺 " + advertised.length + " 种语言");
for (const l of advertised) {
  console.log("   " + l + " 覆盖 " + cov[l].pct + "% (" + cov[l].n + ")");
}
let prev = { below: [] };
try { prev = JSON.parse(fs.readFileSync(STATE, "utf8")); } catch (e) { }
const worse = below.filter(l => !prev.below.includes(l));
fs.mkdirSync("/var/lib/ld_lang_coverage", { recursive: true });
fs.writeFileSync(STATE, JSON.stringify({ ts: new Date().toISOString(), below, cov }));
const line = "未达标语种（<" + LIMIT + "%）: " + (below.join(", ") || "无");
console.log(line);
if (worse.length) {
  const msg = "ALERT [lang-coverage] 语种覆盖率恶化，新增未达标 " + worse.join(",")
    + "（下拉仍在承诺这些语言，用户点进去看到的是英文）";
  console.log(msg);
  try { fs.appendFileSync(ALERTS, new Date().toISOString() + " " + msg + "\n"); }
  catch (e) { console.log("WARN 告警没落盘: " + e.message); }
  process.exit(1);
}
console.log("棘轮未恶化（存量未达标已记录，是否收下拉属产品决策）");
