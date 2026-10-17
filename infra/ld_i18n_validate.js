/* 校验站点全部 i18n 词条文件。两类格式都要管，缺一个就是"半瞎门禁"：
   A) 竖线表式（i18n_lat.js / i18n_more.js）：var L = [...]; var T = { "en": "a|b|c" }
      列数必须等于声明的语种数、每列非空、声明的语种码必须在白名单内。
      （"某列译文等于英文原串"故意不判错：Status→Status 在印尼语里本来就是这个词，
        判了全是假阳性。上一版注释写了这条规则但代码里从来没有——注释撒谎比没注释更糟，
        这次一并改成注释与代码一致。）
   B) 词条式（i18n_core.js / i18n_pages_en*.js / i18n_gov_labels.js）：E("中文键", {en:"…", …})
      语种码必须在白名单内（写错成 german: 永远不会命中，等于悄悄没有该语种）、
      值非空、zh 值必须等于键本身、非 zh/ja 值不得仍含汉字（ja 与中文共用汉字，判了全是假阳性）、
      【每条译文里的 {占位符} 集合必须与中文键完全一致】——治理页的计票行/倒计时
      是模板拼出来的，少一个 {h} 就会把花括号原样显示给用户。

   为什么 B 类不能再用正则：词条文件的 E() 里做了"缺键就新建、同名就合并"，
   正则看不到运行时真正落进词典的东西。这里直接在 vm 里跑文件、用 Proxy 截听
   LDI18N 的每一次写入——测的是真实结果，不是文本长相。

   为什么必须进发布流水线：本工具上一版只查 A 类，而且根本没接执行点
   （promote.py 里没有它）——"写了校验器但从不在上线时跑"等于没有校验器。
   现在它是 promote.py 的 g12 门。

   用法：node ld_i18n_validate.js [js目录]   （默认 /var/www/lightdao/js）*/
const fs = require("fs");
const vm = require("vm");
const cp = require("child_process");
const ROOT = process.argv[2] || "/var/www/lightdao/js";
const LOCALES = ["zh", "en", "es", "fr", "de", "pt", "ru", "ja", "ko", "ar", "hi", "tr", "vi", "id", "fil"];
const LSET = new Set(LOCALES);
let bad = 0, checkedA = 0, checkedB = 0;

function phSet(s) {
  const out = new Set();
  const re = /\{([A-Za-z_][A-Za-z0-9_]*)\}/g;
  let m;
  while ((m = re.exec(String(s))) !== null) out.add(m[1]);
  return out;
}
function sameSet(a, b) {
  if (a.size !== b.size) return false;
  for (const x of a) if (!b.has(x)) return false;
  return true;
}

const allFiles = fs.readdirSync(ROOT).filter(f => /^i18n.*\.js$/.test(f)).sort();

/* ---------- 文字/脚本判据：抓住"手打错字"这类只有门禁能发现的问题 ----------
   本轮实测我自己就打错两处：ar 值里冒出汉字（مused用的）和拉丁字母
   （المفاتيh）。这类错误在页面上极难看，只能靠"值里必须有本语种文字、
   且不得混进别的文字"来拦。 */
const BLOCK = {
  cyr: new RegExp("[\\u0400-\\u04ff]"),      // 西里尔
  arab: new RegExp("[\\u0600-\\u06ff]"),     // 阿拉伯
  deva: new RegExp("[\\u0900-\\u097f]"),     // 天城（印地）
  /* 韩文必须精确到音节/字母区。曾用 [\\u3130-\\ud7bf] 是错的：
     这一大段把汉字区 U+4E00-U+9FFF 整个包了进去，于是 ja 的「終了」被判成
     "混进韩文"、一次假警报 97 条。范围写宽了的判据比没有判据更有害。 */
  hangul: new RegExp("[\\uac00-\\ud7af]|[\\u3130-\\u318f]|[\\u1100-\\u11ff]"),
  kana: new RegExp("[\\u3040-\\u30ff]"),     // 日文假名（平假名+片假名）
  cjk: new RegExp("[\\u4e00-\\u9fff]")       // 汉字
};
const OWN = { ru: ["cyr"], ar: ["arab"], hi: ["deva"], ko: ["hangul"], ja: ["kana", "cjk"] };
const FORBID = {
  ar: ["cyr", "deva", "hangul", "cjk", "kana"],
  ru: ["arab", "deva", "hangul", "cjk", "kana"],
  hi: ["arab", "cyr", "hangul", "cjk", "kana"],
  ko: ["arab", "cyr", "deva", "cjk", "kana"],
  ja: ["arab", "cyr", "deva", "hangul"],
};
function scriptIssue(loc, v) {
  const own = OWN[loc];
  if (own && !own.some(b => BLOCK[b].test(v))) return "值里没有本语种(" + loc + ")文字";
  for (const b of (FORBID[loc] || [])) if (BLOCK[b].test(v)) return "值里混进了其它文字 " + b + "(" + loc + ")";
  return null;
}

/* ---------- 站内真实存在的源串集合（判断表式行是不是"死行"的唯一依据） ----------
   表式文件的键要么就是中文源串（批次 2 起用中文键），要么是某个中文键的 en 值
   （lat/more 的旧写法）。两种都对不上号 = 这条译文永远不会被用上，必须点名。
   中文源串集合来自所有【词条式】文件在 vm 里跑完后的落地结果，不靠正则猜。 */
const ZH = new Map();     // 中文键 → {locale: value}
const ENSET = new Set();  // 能被表式英文键回指的 en 值集合
(function buildZhUniverse() {
  const sb = { console: { log() { }, error() { } },
               document: { documentElement: { dataset: {}, lang: "" }, addEventListener() { }, readyState: "complete" },
               localStorage: { getItem() { return null; }, setItem() { } },
               location: { search: "", pathname: "/", origin: "https://lightdao.net" },
               navigator: { language: "en" }, setTimeout() { return 0; },
               URLSearchParams: function () { this.get = () => null; },
               WeakSet: function () { this.add = () => { }; this.has = () => false; },
               MutationObserver: function () { this.observe = () => { }; this.disconnect = () => { }; } };
  sb.window = sb;
  const ctx = vm.createContext(sb);
  const isE = (f) => {
    try { const s = fs.readFileSync(ROOT + "/" + f, "utf8");
          return /function\s+E\s*\(/.test(s) && !/var T\s*=\s*\{/.test(s); }
    catch (e) { return false; }
  };
  /* 加载顺序必须与浏览器一致（后者覆盖前者），所以从页面 <script> 标签实测推导，
     而不是按文件名字母序——字母序会把 i18n_pages_en3.js 排到 lat/more 之后，
     与真实覆盖顺序不同，en 集合就会算错。 */
  let efiles;
  try {
    const h = fs.readFileSync("/var/www/lightdao/governance.html", "utf8");
    const seq = [], re = /<script[^>]+\bsrc="\/js\/(i18n[^"?]+\.js)"/g;
    let m2; while ((m2 = re.exec(h)) !== null) if (!seq.includes(m2[1])) seq.push(m2[1]);
    efiles = seq.filter(isE);
    const extra = allFiles.filter(f => isE(f) && !efiles.includes(f));
    if (extra.length) { console.log("注意：" + extra.join(",") + " 没出现在页面脚本顺序里，按字母序追加"); efiles = efiles.concat(extra.sort()); }
  } catch (e) {
    console.log("注意：读不到页面脚本顺序（" + e.message + "），退回字母序");
    efiles = allFiles.filter(isE);
  }
  for (const f of efiles) {
    try { vm.runInContext(fs.readFileSync(ROOT + "/" + f, "utf8"), ctx, { filename: f }); }
    catch (e) { console.log("FAIL 源串集合加载 " + f + " 抛错: " + String(e.message).slice(0, 90)); bad++; }
  }
  const D = sb.LDI18N || {};
  /* 合并语义必须与浏览器里一致：后加载覆盖先加载。
     这里曾写成"先到先得"，于是同一个中文键在 pages_en 里是
     "Back to main app"、在后面的文件里被改成 "Back to app" 时，
     门禁看到的 en 集合与线上不一致——判据本身失真比没判据更危险。 */
  for (const zh of Object.keys(D)) {
    if (!ZH.has(zh)) ZH.set(zh, Object.assign({}, D[zh]));
    else Object.assign(ZH.get(zh), D[zh]);
  }
  for (const [, e] of ZH) { const en = String(e.en || "").trim(); if (en) ENSET.add(en); }
})();
const CJK_RE = new RegExp("[\\u4e00-\\u9fff]");
console.log("站内源串：中文键 " + ZH.size + " 个，可被表式英文键回指的 en 值 " + ENSET.size + " 个");

/* ---------------- A) 竖线表式 ---------------- */
for (const f of allFiles) {
  const p = ROOT + "/" + f;
  let src;
  try { src = fs.readFileSync(p, "utf8"); } catch (e) { console.log("FAIL " + f + " 读不到: " + e.message); bad++; continue; }
  if (!/var L\s*=/.test(src) || !/var T\s*=\s*\{/.test(src)) continue;
  const lm = src.match(/var L = \[([^\]]+)\]/);
  if (!lm) { console.log("FAIL " + f + " 找不到 var L = [...]"); bad++; continue; }
  const langMatches = lm[1].match(/"([a-z]{2,3})"/g);
  if (!langMatches) {
    // 校验器不能被被检查的内容弄崩（上一版就是被单字母语种码打崩、崩溃又被下游 grep 吞掉，
    // 看起来像"没问题"）。报成问题、继续跑。
    console.log("FAIL " + f + " 的 var L 里找不到合法语种码（应为 2-3 位小写字母）");
    bad++; continue;
  }
  const L = langMatches.map(x => x.replace(/"/g, ""));
  for (const l of L) if (!LSET.has(l)) { console.log("FAIL " + f + " 声明了白名单外的语种码 " + l); bad++; }
  const ti = src.indexOf("var T = {");
  const rows = [];
  const re = /^\s{4}"((?:[^"\\]|\\.)+)"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,?\s*$/gm;
  let m;
  while ((m = re.exec(src.slice(ti))) !== null) rows.push([m[1], m[2]]);
  const chk = cp.spawnSync("node", ["--check", p], { encoding: "utf8" });
  if (chk.status !== 0) {
    console.log("FAIL " + f + " 语法不通过: " + String(chk.stderr || "").split("\n")[0].slice(0, 100));
    bad++;
  }
  /* 同一个表里键重复 = JS 对象后者静默覆盖前者，少一条译文且毫无报错 */
  const keyHits = new Map();
  for (const [en] of rows) keyHits.set(en, (keyHits.get(en) || 0) + 1);
  for (const [k, v] of keyHits) if (v > 1) {
    console.log("FAIL [表式] " + f + " 键 [" + k.slice(0, 34) + "] 重复 " + v + " 次 —— 后者静默覆盖前者");
    bad++;
  }
  console.log("== [表式] " + f + "：声明语种 " + L.length + " 个，解析到 " + rows.length + " 行");
  for (const [en, val] of rows) {
    checkedA++;
    /* 死行检查：键必须是站内真实存在的源串（中文键），或某个中文键的 en 值。
       对不上号 = 这条译文永远不会被用上；批次 2 起键是手打的中文，
       打错一个字就会静默失效，必须由门禁点名。 */
    if (CJK_RE.test(en)) {
      if (!ZH.has(en)) { console.log("   死行 [" + en.slice(0, 30) + "] 不是站内已有的中文源串 —— 键打错了，译文永远不会生效"); bad++; }
    } else if (!ENSET.has(en.trim())) {
      console.log("   死行 [" + en.slice(0, 30) + "] 没有任何中文键的 en 等于它 —— 译文永远不会生效"); bad++;
    }
    const parts = val.split("|");
    if (parts.length !== L.length) {
      console.log("   行 [" + en.slice(0, 30) + "] 列数 " + parts.length + " ≠ " + L.length + " —— 会整体错位，必须修");
      console.log("      值: " + val.slice(0, 70));
      bad++; continue;
    }
    for (let i = 0; i < parts.length; i++) {
      if (!parts[i].trim()) { console.log("   行 [" + en.slice(0, 28) + "] 第 " + (i + 1) + " 列(" + L[i] + ") 为空 —— 会回落英文"); bad++; continue; }
      const si = scriptIssue(L[i], parts[i]);
      if (si) { console.log("   行 [" + en.slice(0, 28) + "] 第 " + (i + 1) + " 列 " + si + "：" + parts[i].slice(0, 34)); bad++; }
    }
  }
}

/* ---------------- B) 词条式（在 vm 里真跑，再读回落地的词典） ----------------
   注意别用 Proxy 截听赋值：E() 里写的是 `var k = LDI18N[zh] || (LDI18N[zh] = {})`，
   而 `(x = {})` 表达式的值永远是右边那个新对象，Proxy 换不动它——截听会静默丢掉全部写入，
   看起来就是"0 条词条，问题 0 处"的假绿。所以这里老老实实跑完后读 W.LDI18N 的真值。 */
for (const f of allFiles) {
  const p = ROOT + "/" + f;
  let src;
  try { src = fs.readFileSync(p, "utf8"); } catch (e) { continue; }
  if (!/function\s+E\s*\(/.test(src) || /var T\s*=\s*\{/.test(src)) continue;
  const chk = cp.spawnSync("node", ["--check", p], { encoding: "utf8" });
  if (chk.status !== 0) {
    console.log("FAIL [词条] " + f + " 语法不通过: " + String(chk.stderr || "").split("\n")[0].slice(0, 100));
    bad++; continue;
  }
  const W = { LDI18N: {}, document: { documentElement: { dataset: {}, lang: "" }, addEventListener() { }, readyState: "complete" },
              localStorage: { getItem() { return null; }, setItem() { } }, location: { search: "", href: "https://lightdao.net/", origin: "https://lightdao.net" },
              navigator: { language: "en" }, console: { log() { }, error() { } }, setTimeout() { return 0; },
              URLSearchParams: function (s) { this.get = () => null; }, CustomEvent: function () { }, WeakSet: function () { this.add = () => { }; this.has = () => false; } };
  W.window = W;
  const ctx = vm.createContext(W);
  try { vm.runInContext(fs.readFileSync(p, "utf8"), ctx, { filename: f }); }
  catch (e) { console.log("FAIL [词条] " + f + " 加载即抛错: " + String(e.message).slice(0, 120)); bad++; continue; }
  const dict = W.LDI18N || {};
  const keys = Object.keys(dict);
  let n = 0;
  console.log("== [词条] " + f + "：落地 " + keys.length + " 个中文键");
  for (const zh of keys) {
    const e = dict[zh] || {};
    for (const loc of Object.keys(e)) {
      const v = e[loc];
      checkedB++; n++;
      if (!LSET.has(loc)) { console.log("   键 [" + zh.slice(0, 26) + "] 用了白名单外语种码 " + loc + " —— 永远不会命中"); bad++; continue; }
      if (typeof v !== "string" || !v.trim()) { console.log("   键 [" + zh.slice(0, 26) + "] 的 " + loc + " 值为空"); bad++; continue; }
      if (loc === "zh") { if (v !== zh) { console.log("   键 [" + zh.slice(0, 26) + "] 的 zh 值与键本身不一致 —— 键是唯一事实源"); bad++; } continue; }
      /* "等于中文原串"这条判据差点做成假阳性：正常/一致/成功/理由 在日语里就是这么写的，
         线上 5 条"问题"全是这种。改成按字符判定"值里是否仍含汉字"，并且完全放过 ja
         （ja 与中文共用汉字，任何判据都会真假难分）——宁可少判一类，也不要用假警报
         把真问题淹掉。 */
      if (loc !== "ja" && CJK_RE.test(v)) { console.log("   键 [" + zh.slice(0, 26) + "] 的 " + loc + " 值里仍含中文 —— 等于没译"); bad++; continue; }
      const si = scriptIssue(loc, v);
      if (si) { console.log("   键 [" + zh.slice(0, 26) + "] " + si + "：" + String(v).slice(0, 34)); bad++; }
      if (!sameSet(phSet(zh), phSet(v))) {
        console.log("   键 [" + zh.slice(0, 26) + "] 的 " + loc + " 占位符与中文键不一致（会把 {x} 显示给用户或漏掉数字）");
        console.log("      键: " + zh.slice(0, 60) + "\n      值: " + String(v).slice(0, 60));
        bad++;
      }
    }
  }
  if (!keys.length) { console.log("FAIL [词条] " + f + " 跑完一个键都没落地——文件白加载了"); bad++; }
  /* 完备性（opt-in）：文件头写了 LD-I18N-COMPLETE 标记的，每个键必须 15 个语种齐全。
     为什么需要：lookup() 找不到本语种时会静默回落英文——页面不报错、用户看到英文、
     所有静态门禁全绿。这正是我这次要修的 bug 的成因，必须有一道门堵住它。
     pages_en 那类"只登记英文"的历史文件不带标记，不受影响。 */
  if (/LD-I18N-COMPLETE/.test(src)) {
    for (const zh of keys) {
      const e = dict[zh] || {};
      const miss = LOCALES.filter(l => !(typeof e[l] === "string" && e[l].trim()));
      if (miss.length) {
        console.log("   [完备] 键 [" + zh.slice(0, 26) + "] 缺 " + miss.length + " 个语种: " + miss.join(",")
                    + " —— 该语种用户会静默看到英文");
        bad++;
      }
    }
    console.log("   [完备] " + f + " 带 LD-I18N-COMPLETE 标记，已按 15 语种逐一核对");
  }
}

console.log("\ni18n 校验：表式 " + checkedA + " 行 + 词条式 " + checkedB + " 条，问题 " + bad + " 处");
if (checkedA + checkedB === 0) {
  // 一条都没解析到 = 量具坏了（目录错/格式变了），绝不能当成"全绿"
  console.log("FAIL 一个词条都没解析到——量具自己坏了，不接受“0 问题”当成通过");
  bad++;
}
console.log("I18N-VALIDATE FAILS: " + bad);
process.exit(bad ? 1 : 0);
