/* LightDAO 多语种词条 · 方案 B 批次 2（第 1 段：短标签 95 条） LD-I18N-B2-20261017
   LD-I18N-B2-ZHKEY
   与 i18n_lat.js / i18n_more.js 的区别：本表【以中文源串为键】。
   为什么不再用英文作键：同一个英文词可能来自含义不同的中文源串——实测
     "Live" 同时来自「即时」与「已上线」；"No." 其实来自「不需要。」；
     "Pay" 来自「报酬」；"Role" 来自「作用」。
   按英文回填必然给其中一个中文场景安上错译，而且页面上完全看不出错。
   中文键不会串味；代价是手打中文可能写错字，这由展开器的"回填不中即死行"
   统计 + g12 门（missing 必须为 0、且能点名）兜住。
   语种列序固定为下方 L 的 9 个语种，用竖线分隔；值内不得出现竖线。
   待译清单不是凭记忆：由 infra/ld_i18n_todo.js 从全站词典实测算出
   （446 个中文键缺 9 语种之一，其中 ≤20 字的 370 个先做）。 */
(function () {
  "use strict";
  var L = ["fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil"];
  var T = {
    "池": "Pool|Pool|Пул|プール|풀|المجمع|पूल|Havuz|Pool",
    "悬崖": "Cliff|Cliff|Клифф|クリフ|클리프|كليف|क्लिफ|Cliff|Cliff",
    "线性": "Linéaire|Linear|Линейно|リニア|선형|خطي|रैखिक|Doğrusal|Linear",
    "进度": "Progression|Fortschritt|Прогресс|進行状況|진행|التقدّم|प्रगति|İlerleme|Progreso",
    "作用": "Rôle|Funktion|Роль|役割|역할|الدور|भूमिका|Rol|Tungkulin",
    "准入": "Admission|Zugang|Допуск|参加条件|진입|شرط الدخول|प्रवेश|Giriş|Papasok",
    "收益": "Récompense|Ertrag|Доход|リターン|수익|العائد|अपेक्षित लाभ|Getiri|Kita",
    "准备": "Préparer|Vorbereiten|Подготовить|準備|준비|التحضير|तैयारी|Hazırla|Ihanda",
    "待签": "À signer|Zu signieren|Ожидает подписи|署名待ち|서명 대기|بانتظار التوقيع|हस्ताक्षर प्रतीक्षित|imza bekliyor|Hihihintay na pirmahan",
    "已签": "Signé|Signiert|Подписано|署名済み|서명됨|موقّع|हस्ताक्षरित|imzalandı|Pirmado na",
    "活跃": "Actif|Aktiv|Активен|アクティブ|활성|نشط|सक्रिय|etkin|Aktibo",
    "总量": "Offre totale|Gesamtmenge|Общий выпуск|総発行量|총 공급량|إجمالي المعروض|कुल आपूर्ति|Toplam arz|Kabuuang supply",
    "打开": "Ouvrir|Öffnen|Открыть|開く|열기|فتح|खोलें|Aç|Buksan",
    "均分": "Part égale|Gleiche Aufteilung|Поровну|均等分配|균등 분배|توزيع متساوٍ|समान वितरण|eşit paylaşım|Pantay na bahagi",
    "结论": "Conclusion|Fazit|Вывод|結論|결론|الخلاصة|निष्कर्ष|sonuç|Konklusyon",
    "发现": "Constat|Befund|Находка|発見事項|발견|ملاحظة|खोज|bulgu|Nakita",
    "级别": "Gravité|Schweregrad|Серьёзность|深刻度|심각도|الخطورة|गंभीरता|şiddet|Bigat",
    "处置": "Traitement|Behandlung|Обработка|対処|조치|المعالجة|निपटारा|müdahale|Aksyon",
    "用途": "Usage|Verwendung|Назначение|用途|용도|الاستخدام|उपयोग|kullanım|Paggamit",
    "说明": "Remarques|Hinweise|Примечания|説明|설명|ملاحظات|टिप्पणियाँ|açıklama|Mga tala",
    "服务": "Service|Dienst|Сервис|サービス|서비스|الخدمة|सेवा|hizmet|Serbisyo",
    "地址": "Adresse|Adresse|Адрес|アドレス|주소|العنوان|पता|adres|Address",
    "部分": "Partiel|Teilweise|Частично|一部|부분|جزئي|आंशिक|kısmi|Bahagyan",
    "未到": "Pas encore dû|Noch nicht fällig|Ещё не наступил|まだ到来せず|아직 미도래|لم يستحق بعد|अभी नहीं पहुँचा|henüz vadesi gelmedi|Hindi pa takbo",
    "阶段": "Étape|Phase|Этап|段階|단계|المرحلة|चरण|aşama|Yugto",
    "时间": "Heure|Zeit|Время|時間|시간|الوقت|समय|zaman|Oras",
    "机制": "Mécanisme|Mechanismus|Механизм|メカニズム|메커니즘|الآلية|तंत्र|mekanizma|Mekanismo",
    "多签": "Multisig|Multisig|Мультисиг|マルチシグ|멀티시그|تعدّد التواقيع|मल्टीसिग|çoklu imza|Multisig",
    "情形": "Cas|Szenario|Сценарий|ケース|상황|الحالة|परिस्थिति|durum|Sitwasyon",
    "预案": "Plan de réponse|Notfallplan|План действий|対応計画|비상 계획|خطة الطوارئ|आपात योजना|acil eylem planı|Plan sa emergencya",
    "维度": "Dimension|Dimension|Измерение|評価軸|차원|البُعد|आयाम|boyut|Sukatan",
    "组成": "Composition|Zusammensetzung|Состав|構成|구성|التركيب|गठन|bileşim|Binubuo",
    "任期": "Mandat|Amtszeit|Срок полномочий|任期|임기|الولاية|कार्यकाल|görev süresi|Termino",
    "职责": "Responsabilités|Aufgaben|Обязанности|職務|직무|المهام|कर्तव्य|görevler|Mga tungkulin",
    "流程": "Processus|Ablauf|Процесс|プロセス|절차|الإجراء|प्रक्रिया|süreç|Proseso",
    "回避": "Récusation|Ausschließung|Отвод|職務回避|기피|تنحٍّ|परिहार|çekinme|Pagretiro",
    "报酬": "Rémunération|Vergütung|Вознаграждение|報酬|보상|المكافأة|पारिश्रमिक|ücret|Sahod",
    "项目": "Élément|Posten|Пункт|項目|항목|البند|आइटम|kalem|Ayon",
    "遗留": "Hérité|Legacy|Наследие|レガシー|레거시|قديم|विरासत|eski sistem|Lumang sistema",
    "首页": "Accueil|Startseite|Главная|ホーム|홈|الرئيسية|होम|ana sayfa|Home",
    "搜索": "Rechercher|Suchen|Поиск|検索|검색|بحث|खोजें|ara|Maghanap",
    "账户": "Compte|Konto|Счёт|アカウント|계정|الحساب|खाता|hesap|Account",
    "剩余": "Restant|Verbleibend|Осталось|残り|잔여|المتبقي|शेष|kalan|Natitira",
    "快照": "Instantané|Snapshot|Снимок|スナップショット|스냅샷|لقطة|स्नैपशॉट|anlık görüntü|Snapshot",
    "(空)": "(vide)|(leer)|(пусто)|(空)|(비어 있음)|(فارغ)|(खाली)|(boş)|(walang laman)",
    "免许可": "Sans permission|Erlaubnisfrei|Без разрешений|パーミッションレス|허가 불필요|بدون إذن|अनुमति-मुक्त|izinsiz|Walang permiso",
    "协议层": "Couche protocole|Protokollebene|Слой протокола|プロトコル層|프로토콜 계층|طبقة البروتوكول|प्रोटोकॉल परत|protokol katmanı|Layer ng protocol",
    "已清算": "Liquidé|Liquidiert|Ликвидировано|清算済み|청산됨|تمت التصفية|परिसमाप्त|likide edildi|Nalikwida na",
    "已执行": "Exécuté|Ausgeführt|Исполнено|実行済み|실행됨|تم التنفيذ|निष्पादित|yürütüldü|Isinasagawa na",
    "怎么玩": "Comment ça marche|So funktioniert's|Как это работает|仕組み|작동 방식|كيف يعمل|कैसे काम करता है|nasıl çalışır|Paano ito gumagana",
    "2 份": "2 parts|2 Anteile|2 доли|2 口|2 지분|حصتان|2 हिस्से|2 pay|2 bahagi",
    "已转义": "Échappé|Escaped|Экранировано|エスケープ済み|이스케이프됨|مهرّب|एस्केप किया गया|escape edildi|na-escape",
    "已上线": "En ligne|Live|Запущено|稼働中|운영 중|قيد التشغيل|लाइव|yayında|Live na",
    "未激活": "Non activé|Nicht aktiviert|Не активирован|未有効化|비활성|غير مفعّل|निष्क्रिय|etkin değil|Hindi aktibo",
    "未开始": "Non démarré|Nicht begonnen|Не начато|未開始|미시작|لم يبدأ|आरंभ नहीं हुआ|başlamadı|Hindi nagsimula",
    "进行中": "En cours|Läuft|Выполняется|進行中|진행 중|قيد التنفيذ|प्रगति पर|devam ediyor|Isinasagawa",
    "已实测": "Testé en réel|Live getestet|Проверено на практике|実測済み|실측 완료|تم الاختبار فعليًا|लाइव परीक्षित|canlı test edildi|Nasubok sa totoong sistema",
    "已提案": "Proposé|Eingereicht|Внесено|提案済み|제안됨|تم الاقتراح|प्रस्तावित|önerildi|Imungkahi na",
    "未完成": "Inachevé|Nicht abgeschlossen|Не завершено|未完了|미완료|غير مكتمل|अपूर्ण|tamamlanmadı|Hindi kumpleto",
    "未开放": "Non ouvert|Nicht geöffnet|Не открыто|未公開|미개방|غير مفتوح|बंद है|açık değil|Hindi bukas",
    "运行中": "En fonctionnement|In Betrieb|Работает|稼働中|실행 중|قيد التشغيل|चालू|çalışıyor|Gumagana",
    "未挂牌": "Non listé|Nicht gelistet|Не листится|上場なし|미상장|غير مُدرجة|सूचीबद्ध नहीं|listelenmedi|Hindi naka-lista",
    "未建立": "Non établi|Nicht eingerichtet|Не создано|未設定|미구성|غير قائمة|स्थापित नहीं|kurulmadı|Hindi natataguyod",
    "未演练": "Non exercé|Nicht geprobt|Не отработано|未訓練|비연습|غير مُتدرَّب عليه|अभ्यास नहीं|tatbik edilmedi|Hindi pa nasanay",
    "可执行": "Exécutable|Ausführbar|Исполняемый|実行可能|실행 가능|قابل للتنفيذ|निष्पादन-योग्य|uygulanabilir|Maaaring patakbuhin",
    "已满足": "Satisfait|Erfüllt|Выполнено|達成|충족|مستوفى|पूरा हुआ|karşılandı|Nakatugon",
    "已动用": "Utilisé|Genutzt|Использовано|使用済み|사용됨|مستخدم|उपयोग हुआ|kullanıldı|Nagamit na",
    "创世期": "Période de genèse|Genesis-Phase|Период генезиса|ジェネシス期間|제네시스 기간|فترة التكوين|जेनेसिस अवधि|genesis dönemi|Panahon ng genesis",
    "过渡期": "Période de transition|Übergangsphase|Переходный период|移行期間|전이 기간|فترة الانتقالي|संक्रमण काल|geçiş dönemi|Panahon ng transisyon",
    "成熟期": "Période de maturité|Reifephase|Период зрелости|成熟期間|성숙 기간|فترة النضج|परिपक्व अवधि|olgunluk dönemi|Panahon ng pagkahinog",
    "自治期": "Période d'autonomie|Selbstverwaltungsphase|Период самоуправления|自治期間|자치 기간|فترة الحكم الذاتي|स्वायत्त अवधि|özyönetim dönemi|Panahon ng self-governance",
    "时间锁": "Verrou temporel|Timelock|Таймлок|タイムロック|타임록|قفل زمني|समय-लॉक|zaman kilidi|Time lock",
    "低波动": "Faible volatilité|Geringe Volatilität|Низкая волатильность|低ボラティリティ|저변동성|تقلّب منخفض|अल्प अस्थिरता|düşük volatilite|Mababang volatility",
    "中波动": "Volatilité modérée|Mittlere Volatilität|Средняя волатильность|中ボラティリティ|중간 변동성|تقلّب متوسط|मध्यम अस्थिरता|orta volatilite|Katamtamang volatility",
    "高波动": "Forte volatilité|Hohe Volatilität|Высокая волатильность|高ボラティリティ|고변동성|تقلّب مرتفع|अधिक अस्थिरता|yüksek volatilite|Mataas na volatility",
    "前置项": "Prérequis|Voraussetzung|Предварительное условие|前提条件|전제 조건|شرط مسبق|पूर्वापेक्षा|ön koşul|Paunang kondisyon",
    "触发线": "Seuil de déclenchement|Auslösungslinie|Порог срабатывания|トリガー水準|트리거 기준선|خط التفعيل|ट्रिगर सीमा|tetik seviyesi|Trigger level",
    "客户端": "Client|Client|Клиент|クライアント|클라이언트|العميل|क्लाइंट|istemci|Client",
    "已释放": "Libéré|Freigegeben|Высвобождено|リリース済み|해제됨|تم التحرير|रिलीज़ हुआ|serbest bırakıldı|Nailaya na",
    "提案号": "N° de proposition|Vorschlagsnummer|Номер предложения|提案番号|제안 번호|رقم المقترح|प्रस्ताव संख्या|öneri no|Blg. ng panukala",
    "收款方": "Bénéficiaire|Empfänger|Получатель|受取人|수취인|المستلم|प्राप्तकर्ता|alıcı|Tatanggap",
    "待执行": "En attente d'exécution|Zur Ausführung|Ожидает исполнения|実行待ち|실행 대기|بانتظار التنفيذ|निष्पादन प्रतीक्षित|yürütme bekliyor|Hinihintay gampanan",
    "非免申请": "Demande requise|Antrag erforderlich|Нужна заявка|申請が必要|신청 필요|يلزم تقديم طلب|आवेदन आवश्यक|başvuru gerekir|Kailangan ng aplikasyon",
    "不需要。": "Non.|Nicht nötig.|Нет.|不要です。|불필요합니다.|لا.|ज़रूरी नहीं।|gerekmez.|Hindi kailangan.",
    "我的余额": "Mon solde|Mein Guthaben|Мой баланс|私の残高|내 잔액|رصيدي|मेरा शेष|bakiyem|Aking balanse",
    "全部销毁": "Entièrement brûlé|Komplett verbrannt|Полностью сожжено|全量バーン済み|전량 소각|مُحرق بالكامل|पूर्णतः भस्तीकृत|tamamen yakıldı|Nasunog lahat",
    "只看带宽": "Bande passante uniquement|Nur Bandbreite|Только пропускная способность|帯域のみ|대역폭 전용|نطاق ترددي فقط|केवल बैंडविड्थ|yalnız bant genişliği|Bandwidth lang",
    "提交答案": "Envoyer les réponses|Antworten absenden|Отправить ответы|解答を送信|답변 제출|إرسال الإجابات|उत्तर भेजें|yanıtları gönder|Ipadala ang mga sagot",
    "链上实测": "Mesure on-chain|On-Chain-Messung|Замер в блокчейне|オンチェーン実測|온체인 실측|قياس على السلسلة|ऑन-चेन मापन|zincir üstü ölçüm|On-chain na sukat",
    "分配方式": "Mode de distribution|Verteilungsmodus|Способ распределения|分配方法|분배 방식|طريقة التوزيع|वितरण विधि|dağıtım yöntemi|Paraan ng pamimigay",
    "密钥托管": "Gestion des clés|Schlüsselverwahrung|Хранение ключей|鍵の管理|키 수탁|حفظ المفاتيح|कुंजी संरक्षण|anahtar saklama|Pag-iingat ng susi",
    "读取中…": "Lecture…|Lädt…|Чтение…|読み込み中…|읽는 중…|جارٍ القراءة…|पढ़ा जा रहा है…|okunuyor…|Nagbabasa…",
    "销毁地址": "Adresse de brûlage|Burn-Adresse|Адрес сжигания|バーンアドレス|소각 주소|عنوان الإحراق|बर्न पता|yakma adresi|Burn address",
    "代付账户": "Compte payeur de frais|Fremdzahlungskonto|Счёт оплаты за других|手数料代理払いアカウント|대리 지불 계정|حساب دفع الرسوم|शुल्क-भुगतान खाता|ücret ödeyen hesap|Account na nagbabayad ng fee",
    "不是合约": "Pas un contrat|Kein Vertrag|Не контракт|コントラクトではありません|컨트랙트 아님|ليس عقدًا|अनुबंध नहीं|sözleşme değil|Hindi kontrata",
  };
  if (typeof window.__ldExpandLangs !== "function") {
    window.__ldB2Stats = { error: "expander-missing" };
    try { console.error("[i18n_b2] 展开器缺失：i18n_lat.js 必须先于本文件加载"); } catch (e) { }
    return;
  }
  window.__ldB2Stats = window.__ldExpandLangs(L, T);
})();
