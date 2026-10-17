/* 把 <script src="/js/i18n_more.js"> 插到每个页面 i18n_lat.js 之后（顺序敏感：
   展开器要先定义、后调用）。幂等：已存在就跳过。改完打印受影响页面与总数。 */
const fs = require("fs");
const path = require("path");
const DIR = process.argv[2] || "/home/ubuntu/repo/client";
const TAG = '<script src="/js/i18n_more.js"></script>';
let n = 0, skipped = 0;
for (const f of fs.readdirSync(DIR).filter(x => x.endsWith(".html"))) {
  const p = path.join(DIR, f);
  let s = fs.readFileSync(p, "utf8");
  if (s.indexOf("i18n_more.js") >= 0) { skipped++; continue; }
  const m = s.match(/<script src="\/js\/i18n_lat\.js"[^>]*><\/script>/);
  if (!m) continue;                      // 这页没挂展开器，跳过（不硬塞）
  s = s.replace(m[0], m[0] + "\n" + TAG);
  fs.writeFileSync(p, s);
  n++;
  console.log("  注入 " + f);
}
console.log("已注入 " + n + " 页；已存在跳过 " + skipped + " 页；"
  + "（未挂 i18n_lat.js 的页面不动，避免把展开器塞到不相关页面）");
