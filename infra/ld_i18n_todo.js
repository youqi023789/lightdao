// 导出"需要补 9 个语种"的英文原串，按被引用次数排序（先做最常露面的）。
// 为什么以英文为键而不是中文：站内已有 zh→en 全映射，用英文作键可以零手抄中文，
// 避免手打中文产生错字变成"永远不会命中的死键"（这是 i18n_lat.js 已经踩过的坑）。
const fs = require("fs");
const vm = require("vm");
const ROOT = "/var/www/lightdao/js";
const ORDER = ["i18n.js", "i18n_core.js", "i18n_pages_en.js", "i18n_pages_en2.js",
               "i18n_pages_en3.js", "i18n_lat.js"];
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
for (const f of ORDER) {
  try { vm.runInNewContext(fs.readFileSync(ROOT + "/" + f, "utf8"), sb, { timeout: 8000 }); }
  catch (e) { console.log("加载 " + f + " 异常"); }
}
const D = sb.LDI18N || {};
const NEW = ["fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil"];
const byEn = new Map();
for (const zh of Object.keys(D)) {
  const e = D[zh] || {};
  const en = (e.en || "").trim();
  if (!en) continue;
  if (!byEn.has(en)) byEn.set(en, { en, zhCount: 0, have: {}, hasEs: false });
  const r = byEn.get(en);
  r.zhCount++;
  r.hasEs = r.hasEs || !!(e.es && String(e.es).trim());
  for (const l of NEW) { if (e[l] && String(e[l]).trim()) r.have[l] = true; }
}
const rows = [...byEn.values()].sort((a, b) => b.zhCount - a.zhCount);
const need = rows.filter(r => !r.have.de || !r.have.fr);
console.log("唯一英文串 " + rows.length + " 条；已有 es/pt/id/vi 的 "
  + rows.filter(r => r.hasEs).length + " 条；缺 9 语种之一的 " + need.length + " 条");
const lenBucket = { "<=40": 0, "41-120": 0, ">120": 0 };
for (const r of need) {
  const n = r.en.length;
  if (n <= 40) lenBucket["<=40"]++; else if (n <= 120) lenBucket["41-120"]++; else lenBucket[">120"]++;
}
console.log("按长度分桶（长句机翻风险高，单独批次）:", JSON.stringify(lenBucket));
fs.writeFileSync("/home/ubuntu/i18n_todo.json",
  JSON.stringify({ total: rows.length, need: need.length,
    list: need.map(r => ({ en: r.en, zhCount: r.zhCount, hasEs: r.hasEs,
                           len: r.en.length })) }, null, 1));
console.log("\n前 25 条高频待译英文串：");
need.slice(0, 25).forEach((r, i) => console.log("  " + String(i + 1).padStart(2)
  + ". [引用" + r.zhCount + " 长度" + r.len + "] " + r.en.slice(0, 78)));
console.log("\n清单已写 /home/ubuntu/i18n_todo.json");
