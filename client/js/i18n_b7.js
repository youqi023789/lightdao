/* LD-I18N-B7-20261105  跨链面板与短标签的人工 9 语（列序同 b2/b5/b6）。 */
(function () {
  "use strict";
  var L = ["fr","de","ru","ja","ko","ar","hi","tr","fil"];
  var T = {
    "检测中": "vérification|Prüfung|проверка|確認中|확인 중|جارٍ الفحص|जाँच जारी|kontrol ediliyor|sinusuri",
    "读不到": "indisponible|nicht abrufbar|недоступно|取得できない|읽을 수 없음|غير متاح|उपलब्ध नहीं|okunamıyor|hindan mabasa",
    "区块高度": "hauteur de bloc|Blockhöhe|высота блока|ブロック高|블록 높이|ارتفاع الكتلة|ब्लॉक ऊँचाई|blok yüksekliği|taas ng block",
    "通道": "canal|Kanal|канал|チャネル|채널|القناة|चैनल|kanal|channel",
    "未确认包": "paquets non confirmés|unbestätigte Pakete|неподтверждённые пакеты|未確認パケット|미확인 패킷|حزم غير مؤكدة|अपुष्टि पैकेट|doğrulanmamış paketler|hindi nakumpirmang packet",
    "锁仓": "séquestre|Verwahrung (Escrow)|эскроу|エスクロー|에스크로|حجز طرف ثالث|एस्क्रो|emanet (escrow)|escrow",
    "中继账户": "compte du relai|Relayer-Konto|счёт ретранслятора|リレーヤー口座|릴레이어 계정|حساب المعيد|रिलेयर खाता|yönlendirici hesabı|account ng relayer",
    "主网跨链": "interchaîne du réseau principal|Mainnet-Brücken|межсеточность основной сети|メインネットのクロスチェーン|메인넷 크로스체인|التقاطع عبر السلاسل في الشبكة الرئيسية|मेननेट क्रॉस-चेन|ana ağ zincirler arası|cross-chain sa mainnet",
    "已开通": "activé|aktiviert|включено|有効|활성화됨|مُفعَّل|सक्रिय|etkin|ni-activate",
    "未开通": "non activé|nicht aktiviert|не включено|未有効化|비활성|غير مُفعَّل|निष्क्रिय|etkin değil|hindi pa aktibo",
    "更新时间": "mis à jour|aktualisiert|обновлено|更新時刻|갱신 시각|وقت التحديث|अपडेट समय|güncellenme|na-update",
    "已连通": "connecté|verbunden|подключено|接続済み|연결됨|متصل|कनेक्टेड|bağlı|konektado",
    "异常": "anomalie|Störung|сбой|異常|이상|خلل|खराबी|arıza|hindi normal",
    "资产": "actif|Vermögenswert|актив|資産|자산|أصل|संपत्ति|varlık|asset",
    "价格（美元）": "prix (USD)|Preis (USD)|цена (USD)|価格（USD）|가격(USD)|السعر (دولار)|मूल्य (USD)|fiyat (USD)|presyo (USD)",
    "24 小时涨跌": "variation 24 h|24-Stunden-Veränderung|изменение за 24 ч|24 時間変動|24시간 변동|التغير خلال 24 ساعة|24 घंटे बदलाव|24 saatlik değişim|pagbabago sa 24h",
    "外部跨链交易入口": "accès aux échanges interchaînes externes|Externe Cross-Chain-Börsen|внешние межсеточные обмены|外部クロスチェーン取引|외부 크로스체인 거래|منصات التقاطع الخارجي|बाहरी क्रॉस-चेन ट्रेडिंग|harici zincirler arası işlem|panlabas na cross-chain trading",
    "行情": "données de marché|Marktdaten|рыночные данные|市況|시세|بيانات السوق|बाज़ार डेटा|piyasa verisi|data ng merkado",
    "链间状态": "état interchaîne|Chain-übergreifender Status|межсеточное состояние|チェーン間状態|체인 간 상태|حالة التقاطع|क्रॉस-चेन स्थिति|zincirler arası durum|status ng cross-chain",
    "语言": "langue|Sprache|язык|言語|언어|اللغة|भाषा|dil|wika",
    "出块时间": "temps de bloc|Blockzeit|время блока|ブロック時間|블록 시간|زمن الكتلة|ब्लॉक समय|blok süresi|oras ng block",
    "取不到": "n.d.|k. A.|н/д|取得不可|없음|غير متاح|अनुपलब्ध|yok|walang datos",
    "测试网 A": "testnet A|Testnet A|тестнет A|テストネット A|테스트넷 A|شبكة الاختبار A|टेस्टनेट A|testnet A|testnet A",
    "测试网 B": "testnet B|Testnet B|тестнет B|テストネット B|테스트넷 B|شبكة الاختبار B|टेस्टनेट B|testnet B|testnet B",
    "主网": "réseau principal|Hauptnetz|основная сеть|メインネット|메인넷|الشبكة الرئيسية|मेननेट|ana ağ|mainnet",
    "同步中": "synchronisation|synchronisiert|синхронизация|同期中|동기화 중|جارٍ المزامنة|सिंक जारी|eşitleniyor|nagsisi-sync",
    "{n} 秒前": "il y a {n} s|vor {n} s|{n} с назад|{n} 秒前|{n}초 전|منذ {n} ثانية|{n} सेकंड पहले|{n} sn önce|{n} s ang nakalipas",
    "这些资产行情取不到": "pas de données de marché pour ces actifs|für diese Vermögenswerte liegen keine Marktdaten vor|нет рыночных данных по этим активам|これら資産の市況を取得できません|해당 자산의 시세를 불러올 수 없음|لا تتوفر بيانات عن هذه الأصول|इन संपत्तियों का बाज़ार डेटा नहीं|bu varlıklar için piyasa verisi yok|walang market data sa asset na ito",
    "EVM 跨链兑换（Li.Fi）": "échange interchaîne EVM (Li.Fi)|EVM-Chain-übergreifender Tausch (Li.Fi)|межсеточный обмен EVM (Li.Fi)|EVM クロスチェーン交換（Li.Fi）|EVM 크로스체인 스왑(Li.Fi)|مبادلة عبر سلاسل EVM (Li.Fi)|EVM क्रॉस-चेन स्वैप (Li.Fi)|EVM zincirler arası takas (Li.Fi)|EVM cross-chain swap (Li.Fi)",
    "Solana 兑换（Jupiter）": "échange Solana (Jupiter)|Solana-Tausch (Jupiter)|обмен Solana (Jupiter)|Solana 交換（Jupiter）|Solana 스왑(Jupiter)|مبادلة Solana (Jupiter)|Solana स्वैप (Jupiter)|Solana takas (Jupiter)|Solana swap (Jupiter)",
    "LIGHT 行情页": "page de marché LIGHT|LIGHT-Marktseite|страница рынка LIGHT|LIGHT 市況ページ|LIGHT 시세 페이지|صفحة سوق LIGHT|LIGHT बाज़ार पृष्ठ|LIGHT piyasa sayfası|pahina ng merkado ng LIGHT",
    "跨链": "interchaîne|Chain-übergreifend|межсеточность|クロスチェーン|크로스체인|عبر السلاسل|क्रॉस-चेन|zincirler arası|cross-chain",
    "这些是第三方聚合器：交易在你的钱包与他们的路由里完成，LightDAO 不托管资产、不参与撮合，也不保证成交结果。": "Ce sont des agrégateurs tiers : la transaction se conclut dans votre portefeuille et sur leurs routes ; LightDAO ne détient pas d'actifs, n'apparie pas les ordres et ne garantit aucun résultat.|Dies sind Dritt-Aggregatoren: Die Transaktion läuft über Ihre eigene Wallet und deren Routen. LightDAO verwahrt keine Assets, vermittelt keine Orders und garantiert keine Ergebnisse.|Это сторонние агрегаторы: сделка исполняется в вашем кошельке и по их маршрутам. LightDAO не хранит активы, не сводит ордера и не гарантирует результат.|これらは第三者アグリゲーターです。取引はお客様自身のウォレットと相手側の経路で成立します。LightDAO は資産を預からず、約定仲介もせず、結果も保証しません。|제외집합 애그리게이터입니다: 거래는 사용자 지갑과 해당 라우팅에서 체결됩니다. LightDAO는 자산을 보관하거나 주문을 중개하지 않으며 결과를 보장하지 않습니다.|هذه مجمّعات طرف ثالث: تتم الصفقة في محفظتك وعبر مساراتهم؛ لا تحتفظ LightDAO بالأصول ولا توسّط في الأوامر ولا تضمن أي نتيجة.|ये तृतीय-पक्ष एग्रीगेटर हैं: लेन-देन आपके अपने वॉलेट और उनके रूट में पूरा होता है। LightDAO संपत्ति नहीं संभालता, ऑर्डर मिलाता नहीं, और परिणाम की गारंटी नहीं देता।|Bunlar üçüncü taraf toplayıcılardır: işlem kendi cüzdanınız ve onların rotalarında gerçekleşir. LightDAO varlık saklamaz, emir eşleştirmesi yapmaz ve sonuç garanti etmez.|Mga third-party aggregator ang mga ito: ang trade ay natutupusan sa sarili mong wallet at sa routes nila. Hindi nagda-custody ng asset ang LightDAO, hindi ito tagapamagitan ng order, at walang garantiya sa resulta.",
    "行情来源 CoinGecko，经本站缓存 60 秒": "prix issus de CoinGecko, mis en cache 60 s par ce site|Kursdaten von CoinGecko, von dieser Site 60 Sekunden gecacht|цены из CoinGecko, кэшируются этим сайтом 60 секунд|相場は CoinGecko 製、本サイトで 60 秒キャッシュ|시세는 CoinGecko 제공, 이 사이트에서 60초 캐시|الأسعار من CoinGecko وتخزَّن مؤقتًا لدينا 60 ثانية|मूल्य CoinGecko से, इस साइट पर 60 सेकंड कैश|fiyatlar CoinGecko'dan, bu site tarafından 60 sn önbelleğe alınır|galing sa CoinGecko ang presyo, 60s cache ng site na ito",
    "数据由本站只读探针每 {n} 秒取样": "données échantillonnées toutes les {n} s par la sonde en lecture seule de ce site|Daten werden alle {n} Sekunden von unserem schreibgeschützten Sensor erhoben|данные опрашиваются каждые {n} с нашим модулем только для чтения|データは当サイトの読み取り専用プローブが {n} 秒ごとに取得|데이터는 이 사이트의 읽기 전용 프로브가 {n}초마다 가져옵니다|تُؤخذ البيانات كل {n} ثانية عبر مسبار القراءة فقط لدينا|डेटा इस साइट के रीड-ओनली प्रोब द्वारा हर {n} सेकंड नेया जाता है|veriler bu sitedeki salt-okunur probla her {n} sendede bir alınır|ang data ay kinukuha ng read-only probe ng site na ito every {n}s",
    "链": "chaîne|Kette|сеть|チェーン|체인|السلسلة|चेन|zincir|chain",
    "主网 IBC 轻客户端数": "clients légers IBC du réseau principal|IBC-Leichtklienten des Hauptnetzes|лёгкие клиенты IBC основной сети|メインネットの IBC ライトクライアント数|메인넷 IBC 라이트 클라이언트 수|عدد عملاء IBC الخفيفة في الشبكة الرئيسية|मेननेट IBC लाइट क्लाइंट संख्या|ana ağ IBC hafif İstemci sayısı|bilang ng mainnet IBC light clients",
    "探针读数有缺口": "la sonde signale des manques|der Sensor meldet Lücken|зонд сообщил о пробелах|プローブに欠測があります|프로브에 누락이 있습니다|المسبار يبلغ عن فجوات|प्रोब ने अंतर बताया|prob boşluk bildirdi|may gaps ang probe",
    "主网跨链未开通：链上实测 0 个 IBC 轻客户端、0 条通道": "Le cross-chain du réseau principal n'est pas actif : la sonde relève 0 client léger IBC et 0 canal|Mainnet-Cross-Chain ist nicht aktiv: die Sonde misst 0 IBC-Leichtklienten und 0 Kanäle|Межсеточность основной сети не запущена: зонд показывает 0 лёгких клиентов IBC и 0 каналов|メインネットのクロスチェーンは未開通：オンチェーン実測で IBC ライトクライアント 0 件、チャネル 0 本|메인넷 크로스체인 미개통: 온체인 실측 IBC 라이트 클라이언트 0개, 채널 0개|الربط بين السلاسل على الشبكة الرئيسية غير مُفعَّل: القياس على السلسلة يُظهر 0 عملاء IBC و0 قنوات|मेननेट क्रॉस-चेन सक्षम नहीं: ऑन-चेन माप में 0 IBC लाइट क्लाइंट, 0 चैनल|Ana ağ zincirler arası etkin değil: zincir üstü ölçüm 0 IBC hafif istemci ve 0 kanal gösteriyor|Hindi pa naka-enable ang cross-chain sa mainnet: 0 IBC light clients at 0 channel ang sukat on-chain",
    "加载中…": "chargement…|wird geladen…|загрузка…|読み込み中…|로드 중…|جارٍ التحميل…|लोड हो रहा है…|yükleniyor…|naglo-load…",
    "发起一笔测试网跨链（A→B）": "Envoyer un virement interchaîne de testnet (A→B)|Testnetz-Überweisung (A→B) senden|Отправить межсеточный перевод тестнета (A→B)|テストネットのクロスチェーン送金を試す（A→B）|테스트넷 크로스체인 송금 시도(A→B)|أرسل تحويلًا عبر السلاسل على شبكة الاختبار (A→B)|टेस्टनेट क्रॉस-चेन ट्रांसफर भेजें (A→B)|Testnet zincirler arası transfer gönder (A→B)|Magpadala ng cross-chain transfer sa testnet (A→B)",
    "发送中…": "envoi…|senden…|отправка…|送信中…|전송 중…|جارٍ الإرسال…|भेजा जा रहा है…|gönderiliyor…|nagpapadala…",
    "失败：{e}": "échec : {e}|fehlgeschlagen: {e}|сбой: {e}|失敗：{e}|실패: {e}|فشل: {e}|विफल: {e}|başarısız: {e}|nabigo: {e}",
    "已上链，等中继搬运：tx {h}": "confirmé on-chain, le relai-transfert travaille : tx {h}|on-chain, Relay arbeitet noch: tx {h}|в блоке, ждём ретранслятор: tx {h}|オンチェーン済み、中継を待機中：tx {h}|온체인 완료, 릴레이 대기: tx {h}|على السلسلة، بانتظار المعيد: tx {h}|ऑन-चेन, रिलेयर की प्रतीक्षा: tx {h}|zincire yazıldı, relayer bekleniyor: tx {h}|naka-chain, hinihintay ang relayer: tx {h}",
    "本小时演示额度剩余 {n}": "il reste {n} transferts de démonstration cette heure|in dieser Stunde noch {n} Demo-Überweisungen|осталось {n} демо-переводов в этом часе|今時間のデモ送金は残り {n} 件|이번 시간 데모 송금 남은 횟수: {n}|المتبقي من تحويلات العرض هذه الساعة: {n}|इस घंटे शेष डेमो ट्रांसफर: {n}|bu saat kalan demo transfer: {n}|{n} natitirang demo transfer sa oras na ito",
    "跨链报价（1 ETH → USDC，Ethereum → Optimism）": "cotation interchaîne (1 ETH → USDC, Ethereum → Optimism)|Cross-Chain-Angebot (1 ETH → USDC, Ethereum → Optimism)|межсеточный котировочный расчёт (1 ETH → USDC, Ethereum → Optimism)|クロスチェーン見積り（1 ETH → USDC、Ethereum → Optimism）|크로스체인 견적(1 ETH → USDC, Ethereum → Optimism)|عرض سعر عبر السلاسل (1 ETH → USDC، Ethereum → Optimism)|क्रॉस-चेन कोट (1 ETH → USDC, Ethereum → Optimism)|zincirler arası fiyat teklifi (1 ETH → USDC, Ethereum → Optimism)|cross-chain quote (1 ETH → USDC, Ethereum → Optimism)",
    "经 {t} 路由，预计到账 {a}，油钱 ${g}，耗时约 {d}": "via {t}, réception estimée {a}, gas {dollar}{g}, durée ~{d}|über {t}, erwartete Gutschrift {a}, Gas ${g}, Dauer ~{d}|через {t}, ожидается {a}, газ ${g}, время ~{d}|{t} 経由、受取見込 {a}、ガス代 ${g}、所要 {d} 程度|{t} 경유, 예상 입금 {a}, 가스비 ${g}, 소요 {d}|عبر {t}، المتوقع {a}، الغاز ${g}، المدة ~{d}|{t} के माध्यम, अपेक्षित {a}, गैस ${g}, समय ~{d}|{t} üzerinden, beklenen {a}, gas ${g}, süre ~{d}|via {t}, inaasahang {a}, gas ${g}, mga {d}",
    "在聚合器打开该笔": "ouvrir cette route dans l'agrégateur|diese Route im Aggregator öffnen|открыть этот маршрут в агрегаторе|アグリゲーターでこの経路を開く|애그리게이터에서 이 경로 열기|افتح هذا المسار في المجمّع|एग्रीगेटर में यह रूट खोलें|bu rotu toplayıcıda aç|buksan ang route sa aggregator",
  };
  /* 与页面脚本顺序解绑：展开器还没定义时先把这张表登记进 __ldTables，
     i18n.js 的 boot 会统一 __ldExpandAll 补灌一遍。实测按字母序把本片排到 i18n_lat.js
     之前时，直接 return 会让 9 语一列都不灌（德语页面显示英文，静默降级）。 */
  if (typeof window.__ldExpandLangs !== "function") {
    var tb = (window.__ldTables = window.__ldTables || []);
    var has = false;
    for (var qi = 0; qi < tb.length; qi++) { if (tb[qi][1] === T) { has = true; break; } }
    if (!has) tb.push([L, T]);
    window.__ldB7Stats = { pending: "expander-not-yet-defined；boot 时统一展开" };
  } else {
    window.__ldB7Stats = window.__ldExpandLangs(L, T);
  }
})();
