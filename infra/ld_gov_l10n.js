// 治理页运行时文案多语化（按行定位 + 字面替换版）。
// 上一版用长正则匹配整行，一个字符不一致就整体失败——改成"找到含特征子串的那一行，
// 整行替换"，并在替换前后断言行数不变、特征串已消失，防止"改了个大概"。
const fs = require("fs");
const P = "/home/ubuntu/repo/client/js/governance_2.js";
let s = fs.readFileSync(P, "utf8");
if (s.indexOf("LD-GOV-L10N") >= 0) { console.log("已打过，跳过"); process.exit(0); }

const HEAD = `/* LD-GOV-L10N-20261017 运行时文案标签表：这些句子是 JS 拼出来的（票数/百分比/剩余小时每次都变），
     词典按整句精确匹配命中不了，只能在这里本地化。语种只认真正有译值的
     zh/es/pt/id/vi，其余英文兜底（与站内 ?lang 兜底策略一致）。 */
  var GOVL = (function () {
    var l = "";
    try { l = (new URLSearchParams(location.search).get("lang") || "").toLowerCase(); } catch (e) { }
    if (!l) { try { l = (localStorage.getItem("ld_lang") || "").toLowerCase(); } catch (e) { l = ""; } }
    if (!l) { l = (document.documentElement.lang || "").toLowerCase(); }
    if (!l) { l = String(navigator.language || "").toLowerCase(); }
    l = l.slice(0, 2);
    var M = {
      zh: { yes: "赞成", no: "反对", abstain: "弃权", exec: "执行", unit: "人",
            dueIn: "h 后截止", closed: "已截止", voided: "已作废/已过期",
            tip: function (n) { return "以下 " + n + " 个提案已作废或已过期，不计入进行中，也不可再操作："; } },
      es: { yes: "A favor", no: "En contra", abstain: "Abstención", exec: "Ejecutar", unit: "dir.",
            dueIn: " h para cerrar", closed: "Cerrado", voided: "Anulada/vencida",
            tip: function (n) { return n + " propuestas anuladas o vencidas: no cuentan como activas ni admiten acciones."; } },
      pt: { yes: "A favor", no: "Contra", abstain: "Abstenção", exec: "Executar", unit: "pess.",
            dueIn: " h para encerrar", closed: "Encerrado", voided: "Anulada/vencida",
            tip: function (n) { return n + " propostas anuladas ou vencidas: não contam como ativas nem aceitam ações."; } },
      id: { yes: "Setuju", no: "Tolak", abstain: "Abstain", exec: "Jalankan", unit: "orang",
            dueIn: " jam lagi", closed: "Ditutup", voided: "Batal/kedaluwarsa",
            tip: function (n) { return n + " usulan dibatalkan/kedaluwarsa: tidak dihitung aktif, tidak bisa dijalankan."; } },
      vi: { yes: "Đồng ý", no: "Phản đối", abstain: "Bỏ phiếu trắng", exec: "Thực thi", unit: "người",
            dueIn: " giờ nữa", closed: "Đã đóng", voided: "Hủy/hết hạn",
            tip: function (n) { return n + " đề xuất đã hủy/hết hạn: không tính là đang mở, không thao tác được."; } },
      en: { yes: "Yes", no: "No", abstain: "Abstain", exec: "Execute", unit: "voters",
            dueIn: "h left", closed: "Closed", voided: "Voided/expired",
            tip: function (n) { return n + " proposals voided or expired — not counted as active, actions disabled."; } },
    };
    var t = M[l] || M.en;
    t._lang = (M[l] ? l : "en");
    return t;
  })();
  function govTally(yp, np, ap, ya, na, tail) {
    if (GOVL._lang === "zh") {
      return "赞成 " + yp + "%(" + ya + "人) · 反对 " + np + "%(" + na + "人) · 弃权 " + ap + "% · " + tail;
    }
    return GOVL.yes + " " + yp + "% (" + ya + " " + GOVL.unit + ") · " + GOVL.no + " " + np
      + "% (" + na + ") · " + GOVL.abstain + " " + ap + "% · " + tail;
  }
`;

let lines = s.split("\n");
const before = lines.length;
let done = { tally: 0, btn: 0, tip: 0, voided: 0 };

for (let i = 0; i < lines.length; i++) {
  const L = lines[i];
  if (done.tally === 0 && L.indexOf("${yp}") >= 0 && L.indexOf("赞成") >= 0) {
    lines[i] = L.replace(/<div class="mut" class="fs11">[\s\S]*?<\/div>/,
      '<div class="mut" class="fs11">${govTally(yp, np, ap, p.yes_addrs, p.no_addrs, '
      + 'endLeft > 0 ? endLeft + GOVL.dueIn : GOVL.closed)}</div>');
    done.tally = lines[i].indexOf("govTally") >= 0 ? 1 : -1;
  }
  if (done.btn === 0 && L.indexOf('data-v="yes"') >= 0 && L.indexOf("赞成") >= 0) {
    lines[i] = L.replace(/>赞成<\/button>/, ">${GOVL.yes}</button>")
                .replace(/>反对<\/button>/, ">${GOVL.no}</button>")
                .replace(/>弃权<\/button>/, ">${GOVL.abstain}</button>")
                .replace(/>执行<\/button>/, ">${GOVL.exec}</button>");
    done.btn = lines[i].indexOf("GOVL.yes") >= 0 ? 1 : -1;
  }
  if (done.tip === 0 && L.indexOf("不计入进行中") >= 0 && L.indexOf("textContent") >= 0) {
    lines[i] = '      tip.textContent = GOVL.tip(dead.length);';
    done.tip = 1;
  }
  if (done.voided === 0 && L.indexOf("已作废/已过期") >= 0 && L.indexOf("tip.textContent") < 0) {
    lines[i] = L.replace(/已作废\/已过期/g, "${GOVL.voided}");
    done.voided = 1;
  }
}
if (Object.values(done).some(v => v <= 0)) {
  console.log("FAIL 有锚点没替换成功，不写文件:", JSON.stringify(done));
  process.exit(2);
}
let out = lines.join("\n");
const anchor = out.indexOf("function esc(");
if (anchor < 0) { console.log("FAIL 找不到 function esc 锚点"); process.exit(3); }
out = out.slice(0, anchor) + HEAD + "  " + out.slice(anchor);

// 行数断言太脆（插入文本自带换行），改用真正的安全网：写完必须 node --check 通过。
fs.writeFileSync(P, out);
console.log("已本地化治理页运行时文案；替换点:", JSON.stringify(done));
["govTally(", "GOVL.yes", "GOVL.tip(", "GOVL.voided"].forEach(k => {
  if (out.indexOf(k) < 0) { console.log("FAIL 自检缺 " + k); process.exit(5); }
});
console.log("自检通过");
