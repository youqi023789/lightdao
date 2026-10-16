// 方案 B 工作清单生成器：把指定页面"英文态仍显示中文"的片段，
// 与真实词典（按生产顺序加载）做差集，输出确实缺 en 词条的清单。
// 目的：不翻译已经有的（白干），不漏掉真缺的（用户看见中文）。
const fs = require("fs");
const vm = require("vm");

const ROOT = "/var/www/lightdao/js";
const ORDER = ["i18n.js", "i18n_core.js", "i18n_pages_en.js", "i18n_pages_en2.js",
               "i18n_pages_en3.js", "i18n_lat.js"];
const page = process.argv[2] || "/funds.html";
const outFile = process.argv[3] || "/home/ubuntu/gap_" + page.replace(/\W+/g, "") + ".json";

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
  catch (e) { console.log("加载 " + f + " 异常: " + String(e.message).slice(0, 70)); }
}
const D = sb.LDI18N || sb.window.LDI18N || {};
const gap = JSON.parse(fs.readFileSync("/home/ubuntu/ld_i18n_gap.json", "utf8"));
const rec = gap[page];
if (!rec) { console.log("清单里没有这一页：" + page); process.exit(2); }
const frags = rec.frags || [];
const missing = frags.filter(s => {
  const e = D[s];
  return !(e && typeof e.en === "string" && e.en.trim());
});
fs.writeFileSync(outFile, JSON.stringify({ page, total: frags.length,
  missingCount: missing.length, frags: missing }, null, 1));
console.log(page + "：英文态显示中文 " + frags.length + " 段，其中词典确实缺 en 词条 "
  + missing.length + " 段（其余是已译但被标签切断的碎片）");
console.log("清单已写 " + outFile);
missing.slice(0, 12).forEach(s => console.log("   · " + s.slice(0, 96)));
