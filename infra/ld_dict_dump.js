// 用 node 在桩环境里真实加载 i18n 词典，导出"中文原文 -> 已有语种"的全量映射。
// 为什么不用正则：词典条目跨行、含嵌套括号与超长文本，正则只认出 55/403 条，
// 导致"缺哪个语种"的判断整体失真（今天就是这么差点白干一轮翻译）。
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = "/var/www/lightdao/js";
// 必须按生产页面的真实脚本顺序加载：i18n_lat.js 排在最后（它把 en 展开成 es/pt/id/vi）。
// 按字母序加载会让它在 pages_en* 之前跑，展开只覆盖到 55 条，
// 于是得出"其它语种只有 55 条"这种假结论（本次就是这么差点白干一轮翻译）。
// 顺序取自 funds.html 的 script 标签实际顺序。
const ORDER = ["i18n.js", "i18n_core.js", "i18n_pages_en.js", "i18n_pages_en2.js",
               "i18n_pages_en3.js", "i18n_lat.js"];
const present = fs.readdirSync(ROOT).filter(f => /^i18n/.test(f) && f.endsWith(".js"));
const files = ORDER.filter(f => present.includes(f))
  .concat(present.filter(f => !ORDER.includes(f)));
const sandbox = {
  window: {}, document: { documentElement: { dataset: {} },
    querySelectorAll: () => [], addEventListener: () => {},
    createTextNode: () => ({}), readyState: "complete" },
  localStorage: { getItem: () => null, setItem: () => {} },
  navigator: { language: "en-US" },
  console, location: { search: "", pathname: "/index.html", origin: "https://lightdao.net" },
  MutationObserver: function () { this.observe = () => {}; this.disconnect = () => {}; },
  fetch: () => Promise.resolve({ json: () => Promise.resolve({}) }),
  setTimeout, setInterval, clearTimeout,
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
for (const f of files) {
  try {
    vm.runInNewContext(fs.readFileSync(path.join(ROOT, f), "utf8"), sandbox, { timeout: 8000 });
  } catch (e) {
    console.log("加载 " + f + " 失败: " + String(e.message).slice(0, 90));
  }
}
const D = sandbox.LDI18N || sandbox.window.LDI18N || {};
const keys = Object.keys(D);
let withEn = 0, noEn = [];
for (const k of keys) {
  const v = D[k] || {};
  if (typeof v.en === "string" && v.en.trim()) withEn++;
  else noEn.push(k);
}
console.log("词典加载文件: " + files.join(", "));
console.log("中文原文条数: " + keys.length + "  其中有 en: " + withEn + "  缺 en: " + noEn.length);
for (const l of ["es", "pt", "id", "vi", "fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil"]) {
  let n = 0;
  for (const k of keys) { const v = D[k] || {}; if (typeof v[l] === "string" && v[l].trim()) n++; }
  console.log("   语种 " + l + " 已覆盖 " + n + " / " + keys.length);
}
fs.writeFileSync("/home/ubuntu/ld_dict_dump.json",
  JSON.stringify({ keys: keys.length, withEn, missingEn: noEn.slice(0, 400) }));
console.log("明细已写 /home/ubuntu/ld_dict_dump.json");
