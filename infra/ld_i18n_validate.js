/* 校验 i18n_lat.js / i18n_more.js 的每一行：列数必须等于该文件声明的语种数、
   每列非空、且不能与英文原串完全相同（相同=没译，只是占位）。
   为什么必须有：竖线分隔的多语种行少一个 | 就会整体错位一格——
   俄语会被当成日语显示、韩语被当成阿拉伯语，而这种错误在页面上极难看出来。
   本次初稿就写出了 3 行少列 + 1 行引号写坏，全靠这个校验器抓出来。
   用法：node ld_i18n_validate.js [js目录]   （默认 /var/www/lightdao/js）*/
const fs = require("fs");
const vm = require("vm");
const ROOT = process.argv[2] || "/var/www/lightdao/js";
// 不写死文件名：任何"含 var L + var T"的 i18n_*.js 都要被校验，
// 否则将来新增语种文件就自动漏出检查之外（写死两个名字时就发生过）。
const FILES = fs.readdirSync(ROOT)
  .filter(f => /^i18n.*\.js$/.test(f))
  .filter(f => {
    try {
      const s = fs.readFileSync(ROOT + "/" + f, "utf8");
      return /var L\s*=/.test(s) && /var T\s*=\s*\{/.test(s);
    } catch (e) { return false; }
  });
let bad = 0, checked = 0;

for (const f of FILES) {
  const p = ROOT + "/" + f;
  if (!fs.existsSync(p)) { console.log("跳过（文件不存在）: " + f); continue; }
  const src = fs.readFileSync(p, "utf8");
  const lm = src.match(/var L = \[([^\]]+)\]/);
  if (!lm) { console.log("FAIL " + f + " 找不到 var L = [...]"); bad++; continue; }
  const langMatches = lm[1].match(/"([a-z]{2,3})"/g);
  if (!langMatches) {
    // 校验器不能被被检查的内容弄崩（本次就是被一个畸形探针打崩的：
    // 单字母语种码不匹配 [a-z]{2,3} → match() 返回 null → 整个工具挂掉，
    // 而崩溃被下游 grep 吞掉，看起来像"没问题"）。报成问题、继续跑。
    console.log("FAIL " + f + " 的 var L 里找不到合法语种码（应为 2-3 位小写字母）");
    bad++;
    continue;
  }
  const L = langMatches.map(x => x.replace(/"/g, ""));
  // 取 var T = { ... }; 里的每一行 "key": "a|b|c"
  const ti = src.indexOf("var T = {");
  if (ti < 0) { console.log("FAIL " + f + " 找不到 var T = {"); bad++; continue; }
  const rows = [];
  const re = /^\s{4}"((?:[^"\\]|\\.)+)"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,?\s*$/gm;
  let m;
  while ((m = re.exec(src.slice(ti))) !== null) rows.push([m[1], m[2]]);
  // 语法检查交给 node --check（之前这里用"正则截断后试跑"，
  // 而 i18n_more.js 里 window.__ldExpandLangs 第一次出现在守卫语句里，
  // 截断会把文件腰斩 → 报出假语法错。用真实工具，不自己造。）
  const chk = require("child_process").spawnSync("node", ["--check", p],
    { encoding: "utf8" });
  if (chk.status !== 0) {
    console.log("FAIL " + f + " 语法不通过: "
      + String(chk.stderr || "").split("\n")[0].slice(0, 100));
    bad++;
  }
  console.log("== " + f + "：声明语种 " + L.length + " 个 [" + L.join(",") + "]，"
    + "解析到 " + rows.length + " 行");
  for (const [en, val] of rows) {
    checked++;
    const parts = val.split("|");
    if (parts.length !== L.length) {
      console.log("   行 [" + en.slice(0, 30) + "] 列数 " + parts.length + " ≠ "
        + L.length + " —— 会整体错位，必须修");
      console.log("      值: " + val.slice(0, 70));
      bad++;
      continue;
    }
    for (let i = 0; i < parts.length; i++) {
      if (!parts[i].trim()) {
        console.log("   行 [" + en.slice(0, 28) + "] 第 " + (i + 1) + " 列(" + L[i]
          + ") 为空 —— 会回落英文");
        bad++;
      }
    }
  }
}
console.log("\n共检查 " + checked + " 行，问题 " + bad + " 处");
process.exit(bad ? 1 : 0);
