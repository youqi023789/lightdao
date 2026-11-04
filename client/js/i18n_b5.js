/* LD-I18N-B5-20261104  客户端短标签人工译表（9 语，列序同 i18n_b2.js）
   这批不交给机翻：按钮/表头错一个词用户就会点错。 */
(function () {
  "use strict";
  var L = ["fr","de","ru","ja","ko","ar","hi","tr","fil"];
  var T = {
    "解除": "Délier|Entbinden|Отвязать|解除|해제|إلغاء الارتباط|अनलिंक|Bağlantıyı kaldır|I-undelegate",
    "验证": "Vérification|Verifiziert|Проверено|検証|검증|تحقّق|सत्यापन|Doğrulama|Na-verify",
    "定稿": "Réglé|Abgerechnet|Рассчитано|確定|정산|تمت التسوية|निपटान|Hesaplandı|Nait settle",
    "带宽kbps": "Bande passante kbit/s|Bandbreite kbit/s|Пропускная способность кбит/с|帯域 kbps|대역폭 kbps|عرض النطاق كبت/ث|बैंडविड्थ kbps|Bant genişliği kbps|Bandwidth na kbps",
    "在线s": "Présence (s)|Onlinezeit (s)|Онлайн (с)|オンライン秒|온라인 초|وقت التشغيل (ث)|ऑनलाइन सेकंड|Çevrimiçi sn|Oras online (s)",
    "稳定%": "Stabilité %|Stabilität %|Стабильность %|安定性 %|안정성 %|الاستقرار %|स्थिरता %|Kararlılık %|Katatagan %",
    "应得LIGHT": "LIGHT gagnés|Erhaltene LIGHT|Заработано LIGHT|獲得LIGHT|획득 LIGHT|LIGHT المكتسبة|अर्जित LIGHT|Kazanılan LIGHT|Kinitang LIGHT",
    "保存委托": "Enregistrer la délégation|Delegierung speichern|Сохранить делегирование|委託を保存|위임 저장|احفظ التفويض|डिगेशन सहेजें|Delegasyonu kaydet|I-save ang delegasyon",
    "查询中…": "Recherche…|Abfrage…|Запрос…|照会中…|조회 중…|جارٍ الاستعلام…|क्वेरी हो रही…|Sorgulanıyor…|Nagqi-query…",
    "加载可领历史": "Charger l'historique revendicable|Verfügbare Historie laden|Загрузить историю выплат|受取可能履歴を読み込み|수령 가능 기록 불러오기|حمّل سجل المستحقات|प्राप्य इतिहास लोड करें|Talep edilebilir geçmişi yükle|I-load ang historyang maaaring ireclaim",
    "等待全网数据…": "En attente des données réseau…|Warte auf Netzwerkdaten…|Ожидание данных сети…|ネットワークデータ待機中…|네트워크 데이터 대기 중…|بانتظار بيانات الشبكة…|नेटवर्क डेटा की प्रतीक्षा…|Ağ verileri bekleniyor…|Hinihintay ang datos ng network…",
    "社交恢复(分片)": "Récupération sociale (fragments)|Soziale Wiederherstellung (Teile)|Социальное восстановление (части)|ソーシャル復元（分割）|소셜 복구(분할)|استعادة اجتماعية (أجزاء)|सामाजिक पुनर्प्राप्ति (खंड)|Sosyal kurtarma (parçalar)|Social recovery (mga shard)",
    "未委托(自己在线)": "Non délégué (en ligne vous-même)|Nicht delegiert (selbst online)|Не делегировано (вы в сети)|未委託（自分でオンライン）|위임 안 함 (직접 온라인)|غير فوّض (متصل بنفسك)|अन-डिगेट (स्वयं ऑनलाइन)|Delege edilmedi (kendin çevrimiçisin)|Hindi na-delegate (online ka mismo)",
    "请勿重复点击,以免误操作": "Ne cliquez pas deux fois pour éviter les erreurs|Nicht erneut klicken, um Fehler zu vermeiden|Не нажимайте повторно, чтобы не ошибиться|誤操作防止のため連打しないでください|오작동을 막으려면 연속 클릭을 하지 마세요|الرجاء عدم النقر المتكرر لتفادي الخطأ|कृपया दोबारा न क्लिक करें, गलती से बचने के लिए|Hata yapmamak için lütfen tekrar tıklamayın|Huwang ulit-mindig para maiwasan ang mali",
    "一键领取验证者/质押收益": "Réclamer les récompenses validateur / staking en un clic|Validator-/Staking-Erträge mit einem Klick beanspruchen|Собрать награды валидатора/стекинга одним нажатием|バリデータ／ステーク報酬をワンタップで受取|검증자/스테이킹 보상 원클릭 수령|استلقِ مكافآت المُدقّق/التخزين بنقرة|वैलिडेटर/स्टेकिंग पुरस्कार एक क्लिक से पाएँ|Doğrulayıcı / stake ödüllerini tek tıkla al|I-claim ang validator / staking rewards sa isang pindot",
    "钱包安全 / Wallet security": "Sécurité du portefeuille|Wallet-Sicherheit|Безопасность кошелька|ウォレットのセキュリティ|지갑 보안|أمان المحفظة|वॉलेट सुरक्षा|Cüzdan güvenliği|Seguridad ng wallet",
    "治理 · Governance(投票/提案/金库)": "Gouvernance (vote / propositions / trésorerie)|Governance (Abstimmung / Anträge / Treasury)|Управление (голосование / предложения / казна)|ガバナンス（投票/提案/金庫）|거버넌스(투표/제안/금고)|الحوكمة (تصويت/مقترحات/خزنة)|गवर्नेंस (मतदान/प्रस्ताव/कोष)|Yönetişim (oy / öneri / hazine)|Governance (boto / panukala / treasury)",
    "空投中心 / Airdrops(白皮书 §5.7)": "Airdrops (livre blanc §5.7)|Airdrops (Whitepaper §5.7)|Airdrop (белая книга §5.7)|エアドロップ（白茶書 §5.7）|에어드랍(백서 §5.7)|إيردروب (الورقة البيضاء §5.7)|एयरड्रॉप (श्वेतपत्र §5.7)|Airdrop (beyaz paper §5.7)|Airdrops (whitepaper §5.7)",
    "反女巫提示 / Anti-sybil notice": "Note anti-Sybil|Anti-Sybil-Hinweis|Примечание Anti-Sybil|アンチ Sybil 注意|안티-시빌 안내|تنويه مناهضة السيبل|एंटी-सिबिल सूचना|Sybil karşıtı uyarı|Pautang Anti-Sybil",
    "子代币兑换 / Sub-token exchange": "Échange de sous-jetons|Sub-Token-Tausch|Обмен субтокенов|サブトークン交換|서브토큰 교환|تبديل الرموز الفرعية|सब-टोकन एक्सचेंज|Alt-token değişimi|Palitan ng sub-token",
    "委托在线 / Delegate uptime (70/30)": "Délégation de présence (70/30)|Delegierte Onlinezeit (70/30)|Делегирование аптайма (70/30)|オンラインの委託 (70/30)|위임 업타임 (70/30)|تفويض التشغيل (70/30)|डिगेग अपटाइम (70/30)|Delege çevrimiçi süre (70/30)|I-delegate ang uptime (70/30)",
    "我的贡献历史 / My contribution history": "Mon historique de contribution|Meine Beitrags-Historie|Моя история вклада|自分の貢献履歴|내 기여 기록|سجل مساهماتي|मेरा योगदान इतिहास|Katkı geçmişim|Aking historya ng ambag",
    "我的头衔与成就 / Titles & Achievements": "Titres et distinctions|Titel und Erfolge|Звания и достижения|称号と実績|칭호 및 업적|الألقاب والإنجازات|उपाधि और उपलब्धियाँ|Unvanlar ve başarılar|Mga titulo at tagumpay",
    "移除本机登录信息 / Remove this device's login": "Retirer la connexion de cet appareil|Login dieses Geräts entfernen|Удалить вход с этого устройства|この端末のログイン情報を削除|이 기기 로그인 정보 삭제|إزالة تسجيل الدخول لهذا الجهاز|इस डिवाइस का लॉगिन हटाएँ|Bu cihazın girişini kaldır|Alisin ang login ng device na ito",
    "我的安全与邀请 / My security & referrals": "Ma sécurité et mes parrainages|Meine Sicherheit und Empfehlungen|Моя безопасность и рефералы|自分の安全と紹介|내 보안 및 추천|أمانتي وإحالاتي|मेरी सुरक्षा और रेफरल|Güvenliğim ve davetlerim|Aking seguridad at mga referral",
    "正在恢复登录状态,请稍候… / Restoring session…": "Restauration de la session…|Sitzung wird wiederhergestellt…|Восстановление сессии…|ログイン状態を復元中…|세션 복원 중…|جارٍ استعادة الجلسة…|सत्र बहाल हो रहा…|Oturum geri yükleniyor…|Ipinapawi ang session…",
    "机器翻译 · 未人工校对（点此看中文）": "Traduction automatique · non relue (cliquer pour le chinois)|Maschinell übersetzt · ungeprüft (Klick für Chinesisch)|Машинный перевод · без вычитки (нажмите для китайского)|機械翻訳 · 未人手校閲（クリックで中国語）|기계 번역 · 사람 검수 없음 (중국어 보기)|ترجمة آلية · غير مدقّقة (اضغط للصينية)|मशीनी अनुवाद · बिना मानव समीक्षा (चीनी देखें)|Otomatik çeviri · insan onayı yok (Çince için tıklayın)|Machine translation · hindi na-review (i-click para sa Chinese)",
    "资金池": "Pool du trésor|Treasury-Pool|Пул казны|資金プール|자금 풀|خزنة الأموال|कोष पूल|Hazine havuzu|Pool ng yaman",
  };
  if (typeof window.__ldExpandLangs !== "function") {
    window.__ldB5Stats = { error: "expander-missing" }; return;
  }
  window.__ldB5Stats = window.__ldExpandLangs(L, T);
})();
