/* LD-GOV-LABELS-20261017 LD-I18N-COMPLETE 治理页运行时文案的词条（中文为键，存进全站同一份 window.LDI18N）。
   LD-I18N-COMPLETE 是给 g12 门（ld_i18n_validate.js）看的标记：
   带这个标记的文件里，每个键必须 15 个语种齐全、非空。
   少一个语种时 lookup() 会静默回落英文——页面不报错、门禁全绿、用户看到的是英文，
   这恰恰是本轮要根除的那个毛病（治理按钮在 de/ar/ja 下一直是英文）。
   为什么单独成文，而不是在 governance_2.js 里再写一张表：
     上一版就是这么做的，后果是"第二份译文事实源"——同一句话在两处各译一遍，迟早不一致。
     实测证据：de/ar/ja 下页面其余部分已经本地化，赞成/反对/弃权按钮却还是英文，
     因为那张表只覆盖 zh/es/pt/id/vi + 英文兜底。现在 governance_2.js 只按中文键取词，
     取词函数是 i18n.js 暴露的 __ldT（与 DOM 遍历共用同一份词典、同一套回退策略）。
   带 {n}/{h}/{y} 这类花括号占位符的整句模板：各语言数字与词的位置不同，
   所以模板本身按语言整条给出，而不是把词拼在数字前后。
   覆盖 14 个非中文语种 + zh 原串。缺项由 __ldT 回落英文、再回落中文原串
   （诚实降级），并把"缺哪一条"记进 window.__ldTgaps 供巡检门禁报警。 */
(function () {
  "use strict";
  window.LDI18N = window.LDI18N || {};
  function E(zh, m) {
    var k = window.LDI18N[zh] || (window.LDI18N[zh] = {});
    for (var p in m) { if (Object.prototype.hasOwnProperty.call(m, p)) { k[p] = m[p]; } }
  }

  E("赞成", { zh: "赞成", en: "Yes", es: "A favor", fr: "Pour", de: "Dafür", pt: "A favor",
    ru: "За", ja: "賛成", ko: "찬성", ar: "موافق", hi: "पक्ष में", tr: "Kabul",
    id: "Setuju", vi: "Đồng ý", fil: "Sumuporta" });

  E("反对", { zh: "反对", en: "No", es: "En contra", fr: "Contre", de: "Dagegen", pt: "Contra",
    ru: "Против", ja: "反対", ko: "반대", ar: "معارض", hi: "विपक्ष में", tr: "Karşı",
    id: "Tolak", vi: "Phản đối", fil: "Tumutol" });

  E("弃权", { zh: "弃权", en: "Abstain", es: "Abstención", fr: "Abstention", de: "Enthaltung",
    pt: "Abstenção", ru: "Воздержался", ja: "棄権", ko: "기권", ar: "امتناع",
    hi: "विरत", tr: "Çekimser", id: "Abstain", vi: "Bỏ phiếu trắng", fil: "Mag-abstain" });

  E("执行", { zh: "执行", en: "Execute", es: "Ejecutar", fr: "Exécuter", de: "Ausführen",
    pt: "Executar", ru: "Исполнить", ja: "実行", ko: "실행", ar: "تنفيذ",
    hi: "निष्पादित", tr: "Yürüt", id: "Jalankan", vi: "Thực thi", fil: "Isagawa" });

  /* en 与 i18n_pages_en.js 已登记的 "Voting closed" 逐字一致（不是另起一个说法）：
     同一键在两个文件里给两个英文值，就会变成"谁后加载谁赢"的隐性漂移。
     这里带 en 只为满足 LD-I18N-COMPLETE（每键 15 语种齐全）。 */
  E("已截止", { zh: "已截止", en: "Voting closed", es: "Cerrado", fr: "Clôturé", de: "Frist abgelaufen",
    pt: "Encerrado", ru: "Голосование закрыто", ja: "締切", ko: "마감", ar: "مغلق",
    hi: "बंद हो गया", tr: "Kapatıldı", id: "Ditutup", vi: "Đã đóng", fil: "Isara na" });

  E("已结束", { zh: "已结束", en: "Ended", es: "Finalizada", fr: "Terminée", de: "Beendet",
    pt: "Finalizada", ru: "Завершено", ja: "終了", ko: "종료", ar: "انتهت",
    hi: "समाप्त", tr: "sona erdi", id: "Selesai", vi: "Đã kết thúc", fil: "Tapos na" });

  E("已作废/已过期", { zh: "已作废/已过期", en: "Voided/expired", es: "Anulada/vencida",
    fr: "Annullée/expirée", de: "Ungültig/abgelaufen", pt: "Anulada/vencida",
    ru: "Аннулировано/просрочено", ja: "無効/期限切れ", ko: "무효/만료", ar: "ملغاة/منتهية",
    hi: "अमान्य/समाप्त", tr: "Geçersiz/süresi doldu", id: "Batal/kedaluwarsa",
    vi: "Hủy/hết hạn", fil: "Walang bisa/paso na" });

  E("{h} 小时后截止", { zh: "{h} 小时后截止", en: "{h}h left", es: "cierra en {h} h",
    fr: "se termine dans {h} h", de: "noch {h} h", pt: "encerra em {h} h", ru: "ещё {h} ч",
    ja: "残り{h}時間", ko: "{h}시간 남음", ar: "متبقٍ {h} ساعة", hi: "{h} घंटे शेष",
    tr: "{h} saat kaldı", id: "tersisa {h} jam", vi: "còn {h} giờ",
    fil: "{h} oras na ang natitira" });

  E("赞成 {y}%（{ya} 人） · 反对 {n}%（{na} 人） · 弃权 {a}% · {tail}",
    { zh: "赞成 {y}%（{ya} 人） · 反对 {n}%（{na} 人） · 弃权 {a}% · {tail}",
      en: "Yes {y}% ({ya} voters) · No {n}% ({na}) · Abstain {a}% · {tail}",
      es: "A favor {y}% ({ya} dir.) · En contra {n}% ({na}) · Abstención {a}% · {tail}",
      fr: "Pour {y}% ({ya} adresses) · Contre {n}% ({na}) · Abstention {a}% · {tail}",
      de: "Dafür {y}% ({ya} Wähler) · Dagegen {n}% ({na}) · Enthaltung {a}% · {tail}",
      pt: "A favor {y}% ({ya} end.) · Contra {n}% ({na}) · Abstenção {a}% · {tail}",
      ru: "За {y}% ({ya} адресов) · Против {n}% ({na}) · Воздержался {a}% · {tail}",
      ja: "賛成 {y}%（{ya}アドレス）· 反対 {n}%（{na}）· 棄権 {a}% · {tail}",
      ko: "찬성 {y}%({ya}개 주소) · 반대 {n}%({na}) · 기권 {a}% · {tail}",
      ar: "موافق {y}% ({ya} عنوان) · معارض {n}% ({na}) · امتناع {a}% · {tail}",
      hi: "पक्ष में {y}% ({ya} पते) · विपक्ष में {n}% ({na}) · विरत {a}% · {tail}",
      tr: "Kabul {y}% ({ya} adres) · Karşı {n}% ({na}) · Çekimser {a}% · {tail}",
      id: "Setuju {y}% ({ya} alamat) · Tolak {n}% ({na}) · Abstain {a}% · {tail}",
      vi: "Đồng ý {y}% ({ya} địa chỉ) · Phản đối {n}% ({na}) · Bỏ phiếu trắng {a}% · {tail}",
      fil: "Sumuporta {y}% ({ya} address) · Tumutol {n}% ({na}) · Mag-abstain {a}% · {tail}" });

  E("{n} 个提案已作废或已过期，不计入进行中，也不可再操作",
    { zh: "{n} 个提案已作废或已过期，不计入进行中，也不可再操作",
      en: "{n} proposals voided or expired — not counted as active, actions disabled",
      es: "{n} propuestas anuladas o vencidas: no cuentan como activas ni admiten acciones",
      fr: "{n} propositions annulées ou expirées : non comptées comme actives, actions désactivées",
      de: "{n} Anträge ungültig oder abgelaufen — nicht als aktiv gezählt, Aktionen deaktiviert",
      pt: "{n} propostas anuladas ou vencidas: não contam como ativas nem aceitam ações",
      ru: "{n} предложений аннулировано или просрочено — не считаются активными, действия отключены",
      ja: "{n} 件の提案は無効または期限切れ — 進行中として数えられず、操作も不可",
      ko: "{n}개 제안이 무효이거나 만료됨 — 진행 중으로 집계되지 않으며 조작 불가",
      ar: "{n} مقترحات ملغاة أو منتهية الصلاحية — لا تُحتسب نشطة ولا تُقبل إجراءاتها",
      hi: "{n} प्रस्ताव अमान्य या समाप्त — सक्रिय में नहीं गिने जाएँगे, क्रियाएँ निष्क्रिय",
      tr: "{n} öneri geçersiz veya süresi doldu — aktif sayılmaz, işlemler kapalıdır",
      id: "{n} usulan batal atau kedaluwarsa — tidak dihitung aktif, tindakan dinonaktifkan",
      vi: "{n} đề xuất đã hủy hoặc hết hạn — không tính là đang mở, không thao tác được",
      fil: "{n} panukala na walang bisa o pasong na — hindi bilang aktibo, sarado ang aksyon" });

  E("暂无进行中提案", { zh: "暂无进行中提案", en: "No active proposals",
    es: "No hay propuestas activas", fr: "Aucune proposition active", de: "Keine aktiven Anträge",
    pt: "Nenhuma proposta ativa", ru: "Нет активных предложений", ja: "進行中の提案はありません",
    ko: "진행 중인 제안이 없습니다", ar: "لا توجد مقترحات نشطة", hi: "कोई सक्रिय प्रस्ताव नहीं",
    tr: "Etkin öneri yok", id: "Tidak ada usulan aktif", vi: "Không có đề xuất đang mở",
    fil: "Walang aktibong panukala" });

  E("暂无可投票的进行中提案", { zh: "暂无可投票的进行中提案",
    en: "No active proposals available to vote on", es: "No hay propuestas activas en las que votar",
    fr: "Aucune proposition active soumise au vote", de: "Keine aktiven Anträge zur Abstimmung",
    pt: "Nenhuma proposta ativa para votar", ru: "Нет активных предложений для голосования",
    ja: "投票できる進行中の提案はありません", ko: "투표할 진행 중인 제안이 없습니다",
    ar: "لا توجد مقترحات نشطة قابلة للتصويت", hi: "मतदान हेतु कोई सक्रिय प्रस्ताव नहीं",
    tr: "Oylanacak etkin öneri yok", id: "Tidak ada usulan aktif untuk dipilih",
    vi: "Không có đề xuất đang mở để bỏ phiếu", fil: "Walang aktibong panukala na botohan" });
})();
