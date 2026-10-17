/* LD-I18N-MORE-20261017  第二批语种（法/德/俄/日/韩/阿/印地/土/菲律宾）。
   与 i18n_lat.js 同一套设计：以"英文原串"为键，避免手抄中文产生死键；
   展开器复用 i18n_lat.js 抽出的 window.__ldExpandLangs（只留一份实现）。
   列顺序必须与 L 完全一致：fr | de | ru | ja | ko | ar | hi | tr | fil
   —— 少一个 | 会让后面所有语种整体错位一格（俄语被当成日语显示），
   所以 infra/ld_i18n_validate.js 逐行校验列数与非空，纳入发布前检查。
   只收短标签与中等长度句；长段落不机翻冒充翻译（沿用 i18n_lat.js 的原则）。 */
(function () {
  "use strict";
  var L = ["fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil"];
  var T = {
    "Stake": "Staker|Staken|Стейкинг|ステーク|스테이킹|الرهن|स्टेक|Stake Et|Mag-stake",
    "Unstake": "Déstaker|Abstaken|Разстейкинг|ステーク解除|스테이킹 해제|إلغاء الرهن|अनस्टेक|Stake Kaldır|I-unstake",
    "Amount (LIGHT)": "Montant (LIGHT)|Betrag (LIGHT)|Сумма (LIGHT)|金額 (LIGHT)|금액 (LIGHT)|المبلغ (LIGHT)|राशि (LIGHT)|Tutar (LIGHT)|Halaga (LIGHT)",
    "Live": "En direct|Live|В эфире|ライブ|실시간|مباشر|लाइव|Canlı|Live",
    "Ecosystem fund": "Fonds écosystémique|Ökosystemfonds|Фонд экосистемы|エコシステムファンド|생태계 기금|صندوق النظام البيئي|इकोसिस्टम कोष|Ekosistem Fonu|Pondo ng ekosistema",
    "← Back to app": "← Retour à l'app|← Zurück zur App|← Назад в приложение|← アプリへ戻る|← 앱으로 돌아가기|→ العودة إلى التطبيق|← ऐप पर वापस|← Uygulamaya dön|← Bumalik sa app",
    "Back to app": "Retour à l'app|Zurück zur App|Назад в приложение|アプリへ戻る|앱으로 돌아가기|العودة إلى التطبيق|ऐप पर वापस|Uygulamaya dön|Bumalik sa app",
    "Skip to content": "Aller au contenu|Zum Inhalt|Перейти к содержимому|ここから本文|본문으로 건너뛰기|تخطي إلى المحتوى|सामग्री पर जाएँ|İçeriğe geç|Tumakbo sa nilalaman",
    "Sub-tokens": "Sous-tokens|Sub-Token|Субтокены|サブトークン|서브 토큰|الرموز الفرعية|सब-टोकन|Alt semboller|Mga sub-token",
    "Wallet": "Portefeuille|Wallet|Кошелёк|ウォレット|지갑|المحفظة|वॉलेट|Cüzdan|Wallet",
    "Import seed phrase": "Importer la phrase de récupération|Seed-Phrase importieren|Импортировать сид-фразу|シードフレーズをインポート|시드 문구 가져오기|استيراد عبارة الاسترداد|सीड फ़्रेज़ आयात करें|Kurtarma ifadesini içe aktar|I-import ang seed phrase",
    "LIGHT balance": "Solde LIGHT|LIGHT-Guthaben|Баланс LIGHT|LIGHT 残高|LIGHT 잔액|رصيد LIGHT|LIGHT शेष राशि|LIGHT bakiyesi|LIGHT balanse",
    "Staked (governance)": "Joué (gouvernance)|Gestakt (Governance)|Застейкано (управление)|ステーク中（ガバナンス）|스테이킹(거버넌스)|المرهون (الحوكمة)|स्टेक (गवर्नेंस)|Stake edilen (yönetişim)|Na-stake (governance)",
    "Stake / Unstake": "Staker / Déstaker|Staken / Abstaken|Стейкинг / Разстейкинг|ステーク / 解除|스테이킹 / 해제|الرهن / إلغاء الرهن|स्टेक / अनस्टेक|Stake Et / Kaldır|Mag-stake / Mag-unstake",
    "Active proposals": "Propositions actives|Aktive Anträge|Активные предложения|進行中の提案|진행 중인 제안|المقترحات النشطة|सक्रिय प्रस्ताव|Aktif öneriler|Mga aktibong panukala",
    "Refresh proposals": "Actualiser les propositions|Anträge aktualisieren|Обновить предложения|提案を更新|제안 새로고침|تحديث المقترحات|प्रस्ताव रीफ़्रेश करें|Önerileri yenile|I-refresh ang mga panukala",
    "Micro (55% threshold)": "Micro (seuil 55 %)|Mikro (55 %-Schwelle)|Микро (порог 55 %)|マイクロ（55% 閾値）|마이크로(55% 기준)|مصغّر (حد 55%)|माइक्रो (55% देहली)|Mikro (%55 eşik)|Maliliit (55% threshold)",
    "Emergency (75%, 1 day)": "Urgence (75 %, 1 jour)|Notfall (75 %, 1 Tag)|Чрезвычайное (75 %, 1 день)|緊急（75%、1日）|비상(75%, 1일)|طارئ (75%، يوم واحد)|आपातकाल (75%, 1 दिन)|Acil (%75, 1 gün)|Emergency (75%, 1 araw)",
    "Investment (mint sub-token)": "Investissement (créer un sous-token)|Investition (Sub-Token prägen)|Инвестиция (выпуск субтокена)|投資（サブトークン発行）|투자(서브 토큰 발행)|استثمار (إصدار رمز فرعي)|निवेश (सब-टोकन जारी करना)|Yatırım (alt sembol bas)|Pag-invest (gumawa ng sub-token)",
    "Query treasury": "Interroger la trésorerie|Tresorerie abfragen|Запросить казну|トレジャリー照会|재고 조회|الاستعلام عن الخزانة|ट्रेजरी क्वेरी|Hazineyi sorgula|Tanungin ang treasury",
    "Title": "Titre|Titel|Название|タイトル|제목|العنوان|शीर्षक|Başlık|Pamagat",
    "Description": "Description|Beschreibung|Описание|説明|설명|الوصف|विवरण|Açıklama|Paglalarawan",
    "Investment size (USD)": "Montant de l'investissement (USD)|Investitionsgröße (USD)|Размер инвестиции (USD)|投資額（USD）|투자 금액(USD)|حجم الاستثمار (دولاري)|निवेश आकार (USD)|Yatırım tutarı (USD)|Laki ng investment (USD)",
    "Target contract address (optional)": "Adresse du contrat cible (facultatif)|Ziel-Vertragsadresse (optional)|Адрес целевого контракта (необязательно)|対象コントラクトアドレス（任意）|대상 컨트랙트 주소(선택)|عنوان العقد المستهدف (اختياري)|लक्ष्य अनुबंध पता (वैकल्पिक)|Hedef sözleşme adresi (isteğe bağlı)|Target contract address (opsyonal)",
    "Cancelled: security check not passed": "Annulé : contrôle de sécurité non réussi|Abgebrochen: Sicherheitsprüfung nicht bestanden|Отменено: проверка безопасности не пройдена|キャンセル：セキュリティ確認を通過していません|취소: 보안 확인 통과되지 않음|أُلغي: لم يجتز فحص الأمان|रद्द: सुरक्षा जाँच उत्तीर्ण नहीं हुई|İptal: güvenlik kontrolü geçilmedi|Kinansela: hindi lumipas ang security check",
    "Connected:": "Connecté :|Verbunden:|Подключено:|接続済み:|연결됨:|متصل:|कनेक्ट हुआ:|Bağlandı:|Konektado:",
    "Connection failed:": "Échec de connexion :|Verbindung fehlgeschlagen:|Ошибка подключения:|接続に失敗しました:|연결 실패:|فشل الاتصال:|कनेक्शन विफल:|Bağlantı başarısız:|Nabigo ang koneksyon:",
    "h until deadline": "h avant la date limite|h bis Frist|h до дедлайна|期限まで 時間|마감까지 시간|ساعة حتى الموعد النهائي|देनटाइन तक घंटे|son tarihe kadar saat|oras hanggang deadline",
    "Voting closed": "Vote clôturé|Abstimmung beendet|Голосование завершено|投票終了|투표 종료|أُغلق التصويت|मतदान बंद|Oylama kapandı|Tapos na ang botohan",
    "Failed to read your stake:": "Impossible de lire votre jeton mis :|Delegierter Betrag konnte nicht gelesen werden:|Не удалось прочитать ваш стейк:|ステークの読み取りに失敗:|스테이킹 읽기 실패:|فشل قراءة الرهن الخاص بك:|आपका स्टेक पढ़ने में विफल:|Stake okunamadı:|Nabigong basahin ang stake mo:",
    "Governance vote #": "Vote de gouvernance #|Governance-Abstimmung #|Голосование управления #|ガバナンス投票 #|거버넌스 투표 #|تصويت الحوكمة #|गवर्नेंस मत #|Yönetişim oylaması #|Boto sa governance #",
    "Vote #": "Vote #|Abstimmung #|Голосование #|投票 #|투표 #|تصويت #|मत #|Oylama #|Boto #",
    "Vote failed:": "Échec du vote:|Abstimmung fehlgeschlagen:|Ошибка голосования:|投票に失敗:|투표 실패:|فشل التصويت:|मतदान विफल:|Oylama başarısız:|Nabigo ang boto:",
    "Execute proposal #": "Exécuter la proposition #|Antrag ausführen #|Исполнить предложение #|提案を実行 #|제안 실행 #|تنفيذ المقترح #|प्रस्ताव निष्पादित करें #|Öneriyi yürüt #|Isagawa ang panukala #",
    "Execute #": "Exécuter #|Ausführen #|Исполнить #|実行 #|실행 #|تنفيذ #|निष्पादित करें #|Yürüt #|Isagawa #",
    "✓ Voted": "✓ A voté|✓ Abgestimmt|✓ Проголосовано|✓ 投票済み|✓ 투표함|✓ صُوِّت|✓ मत दिया|✓ Oy verildi|✓ Bumoto",
    "✓ Executed": "✓ Exécuté|✓ Ausgeführt|✓ Исполнено|✓ 実行済み|✓ 실행됨|✓ نُفِّذ|✓ निष्पादित|✓ Yürütüldü|✓ Isinagawa",
    "LightDAO explorer": "Explorateur LightDAO|LightDAO-Explorer|Обозреватель LightDAO|LightDAO エクスプローラー|LightDAO 익스플로러|متصفح LightDAO|LightDAO एक्सप्लोरर|LightDAO Gezgini|LightDAO explorer",
    "← App": "← App|← App|← Приложение|← アプリ|← 앱|→ التطبيق|← ऐप|← Uygulama|← App",
    "Latest blocks": "Derniers blocs|Neueste Blöcke|Последние блоки|直近のブロック|최근 블록|أحدث الكتل|नवीनतम ब्लॉक|Son bloklar|Mga pinakabagong block",
    "Height": "Hauteur|Höhe|Высота|高さ|높이|الارتفاع|ऊँचाई|Yükseklik|Taas",
    "Time (UTC)": "Heure (UTC)|Zeit (UTC)|Время (UTC)|時刻 (UTC)|시간 (UTC)|الوقت (ت ع م)|समय (UTC)|Saat (UTC)|Oras (UTC)",
    "Txs": "Transactions|Transaktionen|Транзакции|取引|거래|العمليات|लेन-देन|İşlemler|Mga transaksyon",
    "Proposer": "Proposant|Vorschlagender|Предлагающий|提案者|제안자|المقترح|प्रस्तावक|Öneren|Nagpanukala",
    "Bonded": "Verrouillé|Gebunden|Заблокировано|ボンデッド|본디드|مرهون|बॉन्डेड|Bonded|Naka-bond",
    "Other": "Autre|Sonstige|Прочее|その他|기타|أخرى|अन्य|Diğer|Iba pa",
    "Beneficiary": "Bénéficiaire|Begünstigter|Бенефициар|受益者|수혜자|المستفيد|लाभार्थी|Lehirda|Benepisyaryo",
    "Total (LIGHT)": "Total (LIGHT)|Gesamt (LIGHT)|Всего (LIGHT)|合計 (LIGHT)|총량 (LIGHT)|الإجمالي (LIGHT)|कुल (LIGHT)|Toplam (LIGHT)|Kabuuan (LIGHT)",
    "Vested": "Acquis|Erworben|Приобретено|権利確定|권리 확정|مُستحق|वस्टेड|Kazanılmış|Naka-vest",
    "Claimed": "Réclamé|Abgeholt|Заявлено|請求済み|청구됨|تم استلامه|दावा किया|Talep edildi|Na-claim"
  };
  if (typeof window.__ldExpandLangs !== "function") {
    window.__ldMoreStats = { error: "expander-missing" };
    try { console.error("[i18n_more] 展开器缺失：i18n_lat.js 必须先于本文件加载"); } catch (e) { }
    return;
  }
  window.__ldMoreStats = window.__ldExpandLangs(L, T);
})();
