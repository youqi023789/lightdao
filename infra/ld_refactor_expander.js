// 把 i18n_lat.js 的展开循环抽成一个共享函数 window.__ldExpandLangs(L, T)，
// 原文件行为不变（仍用自己的 L/T 调它），新增的 9 语种文件复用同一实现。
// 为什么非要共享而不是复制一份：两处平行逻辑迟早不一致（今天已经为这类问题修了三次），
// 而"展开是否生效"只能靠覆盖率监控发现，复制一份等于多一个静默失效点。
const fs = require("fs");
const P = "/home/ubuntu/repo/client/js/i18n_lat.js";
let s = fs.readFileSync(P, "utf8");
if (s.indexOf("__ldExpandLangs") >= 0) { console.log("已重构，跳过"); process.exit(0); }

const OLD_TAIL = `  var dict = window.LDI18N || (window.LDI18N = {});`;
if (s.indexOf(OLD_TAIL) < 0) { console.log("FAIL 找不到展开段锚点"); process.exit(1); }

// 找到从 "var dict = ..." 到文件末尾的展开循环，整段换成"定义共享函数 + 调用"
const i = s.indexOf(OLD_TAIL);
let j = s.lastIndexOf("})();");           // 文件末尾的 IIFE 收尾
if (j < i) { console.log("FAIL 找不到 IIFE 收尾"); process.exit(1); }

const NEW_TAIL = `  /* 共享展开器：按"英文原串"回填到每个中文键上。
     返回 {applied, missing} 供监控判断是否真的生效（applied=0 就是白干）。 */
  if (typeof window.__ldExpandLangs !== "function") {
    window.__ldExpandLangs = function (langs, table) {
      var dict = window.LDI18N || (window.LDI18N = {});
      var applied = 0, missing = 0;
      for (var en in table) {
        if (!Object.prototype.hasOwnProperty.call(table, en)) continue;
        var parts = String(table[en]).split("|");
        var hit = 0;
        for (var zh in dict) {
          /* 必须用 hasOwnProperty：for-in 会把原型链上的键也带进来（旧注释里就写过
             所以看起来"部分生效"） */
          if (!Object.prototype.hasOwnProperty.call(dict, zh)) continue;
          var e = dict[zh] && dict[zh].en;
          if (!e) continue;
          if (e !== en && String(e).trim() !== en) continue;
          for (var k = 0; k < langs.length && k < parts.length; k++) {
            if (!dict[zh][langs[k]] && parts[k]) { dict[zh][langs[k]] = parts[k]; hit++; }
          }
        }
        if (hit) applied++; else missing++;
      }
      return { applied: applied, missing: missing };
    };
  }
  var stats = window.__ldExpandLangs(L, T);
  window.__ldLatStats = stats;
`;
s = s.slice(0, i) + NEW_TAIL + s.slice(j);
fs.writeFileSync(P, s);
console.log("已抽出共享展开器 __ldExpandLangs");
if (s.indexOf("window.__ldExpandLangs = function") < 0 || s.indexOf("__ldExpandLangs(L, T)") < 0) {
  console.log("FAIL 自检：共享函数或调用点缺失"); process.exit(2);
}
console.log("自检通过");
