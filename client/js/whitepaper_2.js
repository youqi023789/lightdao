/* LD-WP-LOCALE-20261105 白皮书按语种取整篇译文文件。
   为什么不是逐句塞词典：白皮书 fetch 回来的是 84,499 字节 / 1,147 行的整篇 markdown，
   真机普查数过：每个语种仍有 2,608 处中文 —— 逐句进词典要几万条键，页面体积也扛不住。
   现在：zh 用 /whitepaper.md，其它语种用 /wp/whitepaper.<lang>.md（由 ld_wp_build.py 生成）。
   取不到本版译文时：明确写出"暂无本语种译文，以下为中文原文"，绝不静默换成中文假装已译。
   切语种（i18n.js 派发 ldlang）后重新取文件。 */
(function () {
  "use strict";
  var SRC = "/whitepaper.md";
  var FB = {
    en: "No English translation of the whitepaper is available yet — the Chinese original follows.",
    fr: "Pas encore de version française du livre blanc — le texte chinois original suit.",
    de: "Noch keine deutsche Übersetzung des Whitepapers — es folgt das chinesische Original.",
    ru: "Русская версия white paper ещё не готова — ниже приведён китайский оригинал.",
    ja: "Whitepaper の該当言語版はまだ無いため、以下は中国語原文です。",
    ko: "해당 언어의 백서 번역이 아직 없어 아래는 중국어 원문입니다.",
    ar: "لا تتوفر بعد ترجمة رسمية لهذا الدليل — النص الصيني أدناه هو الأصل.",
    hi: "श्वेतपत्र का इस भाषा में अनुवाद उपलब्ध नहीं — नीचे चीनी मूल पाठ है।",
    tr: "Bu kitabın bu dilde çevirisi henüz yok — aşağıda Çinçe orijinal metin yer alıyor.",
    fil: "Wala pang pagsasalin ng whitepaper sa wikang ito — ang orihinal na Tsino ang sumusunod.",
    es: "Aún no hay traducción al español del libro blanco — a continuación el original en chino.",
    pt: "Ainda não há tradução para o português do livro branco — abaixo o original em chinês.",
    id: "Terjemahan buku putih dalam bahasa ini belum tersedia — berikut teks asli Mandarin.",
    vi: "Chưa có bản dịch sách trắng ngôn ngữ này — phía dưới là nguyên bản tiếng Trung."
  };
  function langNow() {
    var l = "zh";
    try { l = (document.documentElement.getAttribute("lang") || "zh").toLowerCase().split("-")[0]; } catch (e) { }
    return l;
  }
  function render(t) {
    var el = document.getElementById("md");
    if (!el) return;
    try {
      if (window.marked) { el.innerHTML = window.marked.parse(t); }
      else { el.innerHTML = "<pre>" + t.replace(/</g, "&lt;") + "</pre>"; }
    } catch (e) {
      el.innerHTML = "<pre>" + t.replace(/</g, "&lt;") + "</pre>";
    }
  }
  function load() {
    var l = langNow();
    if (l === "zh" || l === "zh-cn") {
      fetch(SRC).then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
        .then(render)
        .catch(function () { var e = document.getElementById("md"); if (e) e.innerHTML = "<p>加载失败，请用页面上的 GitHub 源。</p>"; });
      return;
    }
    var url = "/wp/whitepaper." + l + ".md";
    fetch(url).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.text();
    }).then(function (t) {
      /* 太短 = 被截断；像 HTML = 拿回了站点首页（nginx try_files 对缺失文件给 200+index.html）。
         两种都必须当成"本语种文件不可用"，退回中文原文 + 明确提示，绝不把首页当白皮书渲染。 */
      if (t.length < 6000) throw new Error("译文过短 " + t.length);
      if (/^\s*<(!DOCTYPE|html|HTML)/i.test(t) || /<script\s/i.test(t.slice(0, 4000)))
        throw new Error("拿回的是 HTML 而不是 markdown（多半是本语种文件不存在）");
      render(t);
    }).catch(function (err) {
      fetch(SRC).then(function (r) { return r.text(); }).then(function (t) {
        var note = FB[l] || FB.en;
        render("> " + note + " / 暂无本语种译文，以下为中文原文。\n\n" + t);
      }).catch(function () {
        var e = document.getElementById("md");
        if (e) e.innerHTML = "<p>" + (FB[l] || FB.en) + "</p>";
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", load);
  else load();
  try { document.addEventListener("ldlang", load); } catch (e) { }
})();
