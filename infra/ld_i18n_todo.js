// 导出"需要补 9 个语种"的英文原串，按被引用次数排序（先做最常露面的）。
// 为什么以英文为键而不是中文：站内已有 zh→en 全映射，用英文作键可以零手抄中文，
// 避免手打中文产生错字变成"永远不会命中的死键"（这是 i18n_lat.js 已经踩过的坑）。
//
// LD-TODO-TOOL-FIX-20261017 这个工具自己有三处量具缺陷，全部修掉——
// 拿一把刻度错的尺子排产，等于把 方案 B 的剩余工作量算错：
//   1) 判定"要不要补"时只看 de/fr 两个语种，ja/ko/ar/hi/tr/fil/ru 缺了也算"已完成"
//      → 严重少报。现在按 9 个语种逐一核对，并把每个串缺哪几个语种一起导出。
//   2) 打印长度用了 r.len（rows 上根本没这个字段）→ 满屏"长度undefined"。
//   3) 加载清单硬编码 6 个文件，漏了 i18n_more.js → 那 50 条 × 9 语种的译文
//      不被计入，又会反向多报。加载顺序现在从 governance.html 的 <script> 标签
//      实测推导（与 ld_lang_coverage.js 同一口径），不再手写。
const fs = require("fs");
const vm = require("vm");
const ROOT = process.argv[2] || "/var/www/lightdao/js";
const PAGE_HTML = process.argv[3] || "/var/www/lightdao/governance.html";
const ALL_LOCALES = ["zh", "en", "es", "fr", "de", "pt", "ru", "ja", "ko", "ar", "hi", "tr", "vi", "id", "fil"];
const NEW = ["fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil"];

/* 加载顺序：优先按页面里真实的 <script src="/js/i18n*.js"> 顺序；
   拿不到页面时退回"文件名拓扑"（i18n.js → core → pages_en* → lat → 其余），
   并明确喊出来，绝不静默用一套可能错的顺序。 */
function loadOrder() {
  try {
    const h = fs.readFileSync(PAGE_HTML, "utf8");
    const seq = [];
    const re = /<script[^>]+\bsrc="\/js\/(i18n[^"?]+\.js)"/g;
    let m;
    while ((m = re.exec(h)) !== null) if (!seq.includes(m[1])) seq.push(m[1]);
    const have = new Set(fs.readdirSync(ROOT));
    const ord = seq.filter(f => have.has(f));
    for (const f of [...have].sort()) if (/^i18n.*\.js$/.test(f) && !ord.includes(f)) ord.push(f);
    if (ord[0] !== "i18n.js" && ord.includes("i18n.js")) { ord.splice(ord.indexOf("i18n.js"), 1); ord.unshift("i18n.js"); }
    return { ord, src: "页面实测 " + PAGE_HTML };
  } catch (e) {
    const ord = fs.readdirSync(ROOT).filter(f => /^i18n.*\.js$/.test(f))
      .sort((a, b) => (a === "i18n.js" ? -1 : b === "i18n.js" ? 1 : a.localeCompare(b)));
    return { ord, src: "退回文件名拓扑（读不到页面：" + e.message + "）" };
  }
}
const LO = loadOrder();

const sb = {
  window: {}, document: { documentElement: { dataset: {} }, querySelectorAll: () => [],
    addEventListener: () => {}, createTextNode: () => ({}), readyState: "complete" },
  localStorage: { getItem: () => null, setItem: () => {} },
  navigator: { language: "en" }, console,
  location: { search: "", pathname: "/", origin: "https://lightdao.net" },
  MutationObserver: function () { this.observe = () => {}; this.disconnect = () => {}; },
  fetch: () => Promise.resolve({ json: () => Promise.resolve({}) }),
  setTimeout, setInterval, clearTimeout,
};
sb.window = sb; sb.globalThis = sb;
let loadFails = 0;
for (const f of LO.ord) {
  try { vm.runInNewContext(fs.readFileSync(ROOT + "/" + f, "utf8"), sb, { timeout: 8000 }); }
  catch (e) { console.log("加载 " + f + " 异常: " + String(e.message).slice(0, 80)); loadFails++; }
}
if (loadFails) console.log("注意：有 " + loadFails + " 个词条文件没加载成功，下面的数字偏保守（会多报待译，不会少报）");

const D = sb.LDI18N || {};
const byEn = new Map();
for (const zh of Object.keys(D)) {
  const e = D[zh] || {};
  const en = (e.en || "").trim();
  if (!en) continue;
  if (!byEn.has(en)) byEn.set(en, { en, zhCount: 0, miss: [], hasEs: false, zhs: [] });
  const r = byEn.get(en);
  r.zhCount++;
  if (r.zhs.length < 4) r.zhs.push(zh);
  r.hasEs = r.hasEs || !!(e.es && String(e.es).trim());
}
/* 语种是否齐，按"同一个中文键下"核对才有意义：一个 en 可能对应多个中文键
   （例：赞成 / 同意 都译成 Yes），只要有一个键缺该语种，那条译文就有露馅的机会。 */
for (const zh of Object.keys(D)) {
  const e = D[zh] || {};
  const en = (e.en || "").trim();
  if (!en || !byEn.has(en)) continue;
  const r = byEn.get(en);
  for (const l of NEW) if (!(e[l] && String(e[l]).trim()) && !r.miss.includes(l)) r.miss.push(l);
}
const rows = [...byEn.values()].sort((a, b) => b.zhCount - a.zhCount || a.en.length - b.en.length);
const need = rows.filter(r => r.miss.length);
const done = rows.length - need.length;

const lenBucket = { "<=40": 0, "41-120": 0, ">120": 0 };
for (const r of need) {
  const n = r.en.length;
  if (n <= 40) lenBucket["<=40"]++; else if (n <= 120) lenBucket["41-120"]++; else lenBucket[">120"]++;
}
console.log("加载顺序（" + LO.src + "）: " + LO.ord.join(" → "));
console.log("唯一英文串 " + rows.length + " 条；9 个新语种全齐的 " + done + " 条；至少缺一个语种的 " + need.length + " 条");
console.log("按长度分桶（长句机翻风险高，单独批次）:", JSON.stringify(lenBucket));
fs.writeFileSync("/home/ubuntu/i18n_todo.json",
  JSON.stringify({ total: rows.length, need: need.length, locales: ALL_LOCALES,
    list: need.map(r => ({ en: r.en, zhCount: r.zhCount, hasEs: r.hasEs,
                           len: r.en.length, miss: r.miss, zhs: r.zhs })) }, null, 1));
console.log("\n前 25 条高频待译英文串：");
need.slice(0, 25).forEach((r, i) => console.log("  " + String(i + 1).padStart(2)
  + ". [引用" + r.zhCount + " 长度" + r.en.length + " 缺" + r.miss.length + "] " + r.en.slice(0, 72)));
console.log("\n清单已写 /home/ubuntu/i18n_todo.json");
