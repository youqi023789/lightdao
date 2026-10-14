window.LDBUILD="1.6.1";
function terr(e){ return "[" + window.LDBUILD + "] " + String(e.message||e).slice(0,300); }

window.CFG = {
  gw: location.origin + "/gw",
  rpc: location.origin + "/rpc/",
  chainId: "lightdao-mainnet-1", denom: "ulight", prefix: "wasm",
  miningReward: "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx",
  heartbeatSec: 20,
};
/* LD-SAFE-GLOBALS-20261014: these four names used to be top-level `const`/`let`.
   Two classic <script> files (or an injected page-world script) that declare the
   same name lexically make the *whole second file* die with a parse-time
   SyntaxError, which takes every handler in it down with it — a real user hit
   "Identifier 't' has already been declared" and lost the whole wallet page.
   Property writes on `window` can never collide at parse time, so the page now
   degrades instead of dying. Do not convert these back to const/let. */
window.I18N = {
 zh:{heroT:"把闲置设备变成收益",heroS:"运行轻节点贡献带宽与算力，赚取原生 LIGHT 代币",createW:"新建钱包",importW:"导入助记词",createHint:"将生成 12 词助记词，请务必离线备份——它是你资产的唯一凭证。",btnCreate:"生成新钱包",btnImport:"导入",warn:"⚠ 主网真实资产：助记词只存本机浏览器，丢失无法找回；请先做小额试转，确认地址无误。",idle:"未运行",running:"挖矿运行中",estLabel:"今日预计奖励 (LIGHT)",blkInfo:"每区块奖励池 ≈13.87 LIGHT（全网共享，按贡献比例分配）· 每日池 ≈650,685 LIGHT",startMining:"开始挖矿",stopMining:"停止挖矿",yourAddr:"你的地址",logout:"退出",balance:"余额 (LIGHT)",claimable:"可领取",claim:"领取奖励",contrib:"实时贡献",cBw:"带宽",cSess:"在线时长",cVerif:"验证任务",cStab:"稳定性",footer:"LightDAO 轻节点",claimed:"领取成功！",nothing:"暂无可领取奖励",saving:"请妥善保存助记词",walletFail:"钱包组件加载失败(网络受限)，挖矿/贡献仍可用，领取暂不可用",pkTab:"Passkey 钱包",pkHint:"用指纹/面容登录，无需助记词；可设 3-5 人社交恢复。",pkCreate:"创建 Passkey 钱包",pkUnlock:"Passkey 解锁",pkSocial:"社交恢复(分片)",pkCreated:"✓ Passkey 钱包已创建，助记词已加密(不落地)",pkUnlocked:"✓ 解锁成功",pkPinPrompt:"此浏览器不支持 Passkey PRF，请设 PIN(≥6位)作为加密密钥:",pkSocialHint:"已生成 5 份分片，任 3 份可恢复。请抄给 5 位监护人(本地不保存):",pkRecoverPrompt:"粘贴任意 ≥3 份分片(每行一份)以恢复:",pkRecoverOk:"✓ 重建成功，正在用恢复的助记词重设 Passkey…",pkFail:"Passkey 操作失败: ",pkUnsupported:"此浏览器不支持 WebAuthn，请改用「助记词」标签页",pkSocialFirst:"请先创建/解锁 Passkey 钱包再做社交恢复",inviteT:"邀请好友,赚 TA 首周贡献的 10%",copy:"复制",stOk:"正常",stBad:"异常",stSys:"系统状态"},
 en:{heroT:"Turn idle devices into yield",heroS:"Run a light node, contribute bandwidth & compute, earn native LIGHT",createW:"New Wallet",importW:"Import Seed",createHint:"A 12-word seed will be generated. Back it up offline — it is the only key to your funds.",btnCreate:"Generate Wallet",btnImport:"Import",warn:"⚠ Live mainnet with real funds: the seed exists only in this browser and cannot be recovered if lost. Send a small test amount first.",idle:"Idle",running:"Mining active",estLabel:"Est. reward today (pro-rata of network, live) (LIGHT)",blkInfo:"Per-block pool ≈13.87 LIGHT (shared network-wide, pro-rata by contribution) · daily pool ≈650,685 LIGHT",startMining:"Start Mining",stopMining:"Stop Mining",yourAddr:"Your address",logout:"Logout",balance:"Balance (LIGHT)",claimable:"Claimable",claim:"Claim Rewards",contrib:"Live contribution",cBw:"Bandwidth",cSess:"Uptime",cVerif:"Tasks",cStab:"Stability",footer:"LightDAO light node",claimed:"Claimed!",nothing:"Nothing to claim",saving:"Save your seed phrase",walletFail:"Wallet lib failed to load (network). Mining still works; claiming unavailable.",pkTab:"Passkey Wallet",pkHint:"Login with fingerprint/face, no seed phrase; optional 3-5 guardian social recovery.",pkCreate:"Create Passkey Wallet",pkUnlock:"Unlock with Passkey",pkSocial:"Social Recovery (shares)",pkCreated:"✓ Passkey wallet created, seed encrypted (never stored in plain)",pkUnlocked:"✓ Unlocked",pkPinPrompt:"This browser lacks Passkey PRF. Set a PIN (≥6) as encryption key:",pkSocialHint:"5 shares generated; any 3 recover. Give to 5 guardians (not stored locally):",pkRecoverPrompt:"Paste any ≥3 shares (one per line) to recover:",pkRecoverOk:"✓ Recovered! Re-creating Passkey with restored seed…",pkFail:"Passkey error: ",pkUnsupported:"WebAuthn unsupported here, use the Seed Phrase tab",pkSocialFirst:"Create/unlock a Passkey wallet first",inviteT:"Invite friends, earn 10% of their first-week contribution",copy:"Copy",stOk:"Normal",stBad:"Degraded",stSys:"System status"},
 es:{heroT:"Convierte dispositivos en ingresos",heroS:"Ejecuta un nodo ligero y gana LIGHT",createW:"Nueva cartera",importW:"Importar",createHint:"Se generará una frase de 12 palabras. Cópiala offline.",btnCreate:"Generar",btnImport:"Importar",warn:"⚠ Red principal real: la frase solo está en este navegador y no se puede recuperar si la pierdes. Haz antes una prueba con un importe pequeño.",idle:"Inactivo",running:"Minando",estLabel:"Recompensa est. hoy (LIGHT)",blkInfo:"Pool por bloque ≈13,87 LIGHT (compartido en toda la red, a prorrata por contribución) · pool diario ≈650.685 LIGHT",startMining:"Empezar",stopMining:"Parar",yourAddr:"Tu dirección",logout:"Salir",balance:"Saldo (LIGHT)",claimable:"Reclamable",claim:"Reclamar",contrib:"Contribución",cBw:"Banda",cSess:"Tiempo",cVerif:"Tareas",cStab:"Estab.",footer:"Nodo ligero LightDAO",claimed:"¡Reclamado!",nothing:"Nada que reclamar",saving:"Guarda tu frase",walletFail:"Lib de cartera no cargó. Minar funciona; reclamar no.",pkTab:"Cartera Passkey",pkHint:"Inicia con huella/rostro, sin frase semilla; recuperación social 3-5 opcional.",pkCreate:"Crear cartera Passkey",pkUnlock:"Desbloquear con Passkey",pkSocial:"Recuperación social",pkCreated:"✓ Cartera Passkey creada, semilla cifrada",pkUnlocked:"✓ Desbloqueado",pkPinPrompt:"Este navegador no soporta PRF. Define un PIN (≥6):",pkSocialHint:"5 fragmentos generados; 3 cualesquiera recuperan. Dalos a 5 guardianes:",pkRecoverPrompt:"Pega ≥3 fragmentos (uno por línea):",pkRecoverOk:"✓ Recuperado! Re-creando Passkey…",pkFail:"Error Passkey: ",pkUnsupported:"WebAuthn no soportado, usa la pestaña de semilla",pkSocialFirst:"Crea/desbloquea una cartera Passkey primero",inviteT:"Invita amigos y gana el 10% de su contribución de la 1ª semana",copy:"Copiar",stOk:"Normal",stBad:"Averiado",stSys:"Estado del sistema"},
 pt:{heroT:"Transforme dispositivos ociosos em renda",heroS:"Rode um nó leve, contribua banda e computação, ganhe LIGHT nativo",createW:"Nova carteira",importW:"Importar seed",createHint:"Uma seed de 12 palavras será gerada. Faça backup offline — é a única chave dos seus fundos.",btnCreate:"Gerar carteira",btnImport:"Importar",warn:"⚠ Mainnet real: a seed fica só neste navegador e não pode ser recuperada se perdida. Faça antes um envio pequeno de teste.",idle:"Parado",running:"Mineração ativa",estLabel:"Recompensa est. hoje (LIGHT)",blkInfo:"Pool por bloco ≈13,87 LIGHT (compartilhado em toda a rede, proporcional à contribuição) · pool diário ≈650.685 LIGHT",startMining:"Começar",stopMining:"Parar",yourAddr:"Seu endereço",logout:"Sair",balance:"Saldo (LIGHT)",claimable:"A receber",claim:"Resgatar",contrib:"Contribuição ao vivo",cBw:"Banda",cSess:"Uptime",cVerif:"Tarefas",cStab:"Estabilidade",footer:"Nó leve LightDAO",claimed:"Resgatado!",nothing:"Nada a resgatar",saving:"Guarde sua seed",walletFail:"Biblioteca da carteira falhou (rede). Mineração funciona; resgate indisponível.",pkTab:"Carteira Passkey",pkHint:"Entre com digital/rosto, sem seed; recuperação social 3-5 opcional.",pkCreate:"Criar carteira Passkey",pkUnlock:"Desbloquear com Passkey",pkSocial:"Recuperação social (partes)",pkCreated:"✓ Carteira Passkey criada, seed criptografada (nunca em texto puro)",pkUnlocked:"✓ Desbloqueado",pkPinPrompt:"Este navegador não tem PRF. Defina um PIN (≥6) como chave:",pkSocialHint:"5 partes geradas; quaisquer 3 recuperam. Dê a 5 guardiões (não guardadas localmente):",pkRecoverPrompt:"Cole ≥3 partes (uma por linha) para recuperar:",pkRecoverOk:"✓ Recuperado! Recriando Passkey com a seed restaurada…",pkFail:"Erro Passkey: ",pkUnsupported:"WebAuthn não suportado, use a aba de seed",pkSocialFirst:"Crie/desbloqueie uma carteira Passkey primeiro",inviteT:"Convide amigos e ganhe 10% da contribuição da 1ª semana",copy:"Copiar",stOk:"Normal",stBad:"Degradado",stSys:"Status do sistema"},
 id:{heroT:"Ubah perangkat menganggur jadi penghasilan",heroS:"Jalankan node ringan, sumbangkan bandwidth & komputasi, dapatkan LIGHT",createW:"Dompet baru",importW:"Impor seed",createHint:"Seed 12 kata akan dibuat. Simpan offline — itu satu-satunya kunci dana Anda.",btnCreate:"Buat dompet",btnImport:"Impor",warn:"⚠ Jaringan utama nyata: seed hanya ada di peramban ini dan tidak dapat dipulihkan bila hilang. Kirim jumlah kecil dulu sebagai uji coba.",idle:"Diam",running:"Menambang aktif",estLabel:"Perk. hadiah hari ini (LIGHT)",blkInfo:"Pool per blok ≈13,87 LIGHT (dibagi di seluruh jaringan, proporsional kontribusi)· pool harian ≈650.685 LIGHT",startMining:"Mulai",stopMining:"Berhenti",yourAddr:"Alamat Anda",logout:"Keluar",balance:"Saldo (LIGHT)",claimable:"Dapat diklaim",claim:"Klaim hadiah",contrib:"Kontribusi langsung",cBw:"Bandwidth",cSess:"Online",cVerif:"Tugas",cStab:"Stabilitas",footer:"Node ringan LightDAO",claimed:"Berhasil diklaim!",nothing:"Tidak ada untuk diklaim",saving:"Simpan frasa seed Anda",walletFail:"Pustaka dompet gagal dimuat (jaringan). Menambang tetap jalan; klaim tidak tersedia.",pkTab:"Dompet Passkey",pkHint:"Masuk dengan sidik jari/wajah, tanpa seed; pemulihan sosial 3-5 opsional.",pkCreate:"Buat dompet Passkey",pkUnlock:"Buka dengan Passkey",pkSocial:"Pemulihan sosial (bagian)",pkCreated:"✓ Dompet Passkey dibuat, seed terenkripsi (tak pernah tersimpan polos)",pkUnlocked:"✓ Terbuka",pkPinPrompt:"Browser ini tanpa PRF. Setel PIN (≥6) sebagai kunci enkripsi:",pkSocialHint:"5 bagian dibuat; 3 mana pun memulihkan. Berikan ke 5 wali (tak disimpan lokal):",pkRecoverPrompt:"Tempel ≥3 bagian (satu per baris) untuk memulihkan:",pkRecoverOk:"✓ Dipulihkan! Membuat ulang Passkey dengan seed…",pkFail:"Galat Passkey: ",pkUnsupported:"WebAuthn tak didukung, gunakan tab seed",pkSocialFirst:"Buat/buka dompet Passkey dulu",inviteT:"Undang teman, dapatkan 10% kontribusi minggu pertama mereka",copy:"Salin",stOk:"Normal",stBad:"Terganggu",stSys:"Status sistem"},
 vi:{heroT:"Biến thiết bị nhàn rỗi thành thu nhập",heroS:"Chạy node nhẹ, đóng góp băng thông & tính toán, nhận LIGHT",createW:"Ví mới",importW:"Nhập seed",createHint:"Một seed 12 từ sẽ được tạo. Hãy sao lưu ngoại tuyến — đó là chìa khóa duy nhất.",btnCreate:"Tạo ví",btnImport:"Nhập",warn:"⚠ Mainnet thật: seed chỉ nằm trong trình duyệt này và không thể khôi phục nếu mất. Hãy thử chuyển một khoản nhỏ trước.",idle:"Dừng",running:"Đang đào",estLabel:"Phần thưởng ước tính hôm nay (LIGHT)",blkInfo:"Mỗi block ≈13,87 LIGHT (chia trên toàn mạng, theo tỷ lệ đóng góp)· pool ngày ≈650.685 LIGHT",startMining:"Bắt đầu",stopMining:"Dừng",yourAddr:"Địa chỉ của bạn",logout:"Đăng xuất",balance:"Số dư (LIGHT)",claimable:"Có thể nhận",claim:"Nhận thưởng",contrib:"Đóng góp trực tiếp",cBw:"Băng thông",cSess:"Trực tuyến",cVerif:"Tác vụ",cStab:"Ổn định",footer:"Node nhẹ LightDAO",claimed:"Đã nhận!",nothing:"Không có gì để nhận",saving:"Hãy lưu cụm seed của bạn",walletFail:"Thư viện ví lỗi (mạng). Đào vẫn chạy; nhận thưởng tạm khóa.",pkTab:"Ví Passkey",pkHint:"Đăng nhập bằng vân tay/khuôn mặt, không cần seed; khôi phục xã hội 3-5 tùy chọn.",pkCreate:"Tạo ví Passkey",pkUnlock:"Mở khóa bằng Passkey",pkSocial:"Khôi phục xã hội (mảnh)",pkCreated:"✓ Ví Passkey đã tạo, seed đã mã hóa (không lưu dạng thô)",pkUnlocked:"✓ Đã mở khóa",pkPinPrompt:"Trình duyệt không hỗ trợ PRF. Đặt PIN (≥6) làm khóa mã hóa:",pkSocialHint:"Đã tạo 5 mảnh; bất kỳ 3 mảnh nào cũng khôi phục. Giao cho 5 người giám hộ (không lưu cục bộ):",pkRecoverPrompt:"Dán ≥3 mảnh (mỗi dòng một mảnh) để khôi phục:",pkRecoverOk:"✓ Đã khôi phục! Đang tạo lại Passkey với seed…",pkFail:"Lỗi Passkey: ",pkUnsupported:"WebAuthn không hỗ trợ, hãy dùng tab seed",pkSocialFirst:"Hãy tạo/mở khóa ví Passkey trước",inviteT:"Mời bạn bè, nhận 10% đóng góp tuần đầu của họ",copy:"Sao chép",stOk:"Bình thường",stBad:"Suy giảm",stSys:"Trạng thái hệ thống"},
 fil:{heroT:"Gawing kita ang mga tambak na device",heroS:"Magpatakbo ng light node, mag-ambag ng bandwidth at compute, kumita ng LIGHT",createW:"Bagong wallet",importW:"Mag-import ng seed",createHint:"Gagawa ng 12-salitang seed. I-backup offline — ito lang ang susi sa pondo mo.",btnCreate:"Gumawa ng wallet",btnImport:"I-import",warn:"⚠ Tunay na mainnet: ang seed ay nasa browser lang na ito at hindi maaaring maibalik kapag nawala. Mag-padala muna ng maliit na subok.",idle:"Idle",running:"Gumagana ang pagmimina",estLabel:"Tantyang gantimpala ngayong araw (LIGHT)",blkInfo:"Bawat block pool ≈13.87 LIGHT (hahati sa buong network, ayon sa ambag)· araw-araw na pool ≈650,685 LIGHT",startMining:"Simulan",stopMining:"Ihinto",yourAddr:"Ang iyong address",logout:"Mag-logout",balance:"Balanse (LIGHT)",claimable:"Pwedeng i-claim",claim:"I-claim",contrib:"Live na ambag",cBw:"Bandwidth",cSess:"Oras online",cVerif:"Mga gawain",cStab:"Katatagan",footer:"LightDAO light node",claimed:"Na-claim na!",nothing:"Walang pwedeng i-claim",saving:"Ingatan ang iyong seed phrase",walletFail:"Hindi nag-load ang wallet lib (network). Gumagana pa rin ang pagmimina; hindi pwede i-claim.",pkTab:"Passkey Wallet",pkHint:"Mag-login gamit ang fingerprint/mukha, walang seed; optional na 3-5 social recovery.",pkCreate:"Gumawa ng Passkey Wallet",pkUnlock:"I-unlock gamit ang Passkey",pkSocial:"Social Recovery (mga bahagi)",pkCreated:"✓ Nagawa na ang Passkey wallet, naka-encrypt ang seed (hindi nakaimbak nang plain)",pkUnlocked:"✓ Naka-unlock",pkPinPrompt:"Walang Passkey PRF ang browser na ito. Magtakda ng PIN (≥6) bilang encryption key:",pkSocialHint:"5 bahagi ang nagawa; kahit 3 ay nakababawi. Ibigay sa 5 tagapangalaga (hindi nakaimbak lokal):",pkRecoverPrompt:"I-paste ang kahit ≥3 bahagi (isa bawat linya) para mabawi:",pkRecoverOk:"✓ Nabawi na! Muling ginagawa ang Passkey gamit ang seed…",pkFail:"Passkey error: ",pkUnsupported:"Hindi sinusuportahan ang WebAuthn, gamitin ang Seed Phrase tab",pkSocialFirst:"Gumawa/mag-unlock muna ng Passkey wallet",inviteT:"Anyayahan ang mga kaibigan, kumita ng 10% ng kanilang unang-linggo na ambag",copy:"Kopyahin",stOk:"Normal",stBad:"May problema",stSys:"Status ng system"},
 fr:{heroT:"Transforme tes appareils inutilisés en rendement",heroS:"Fais tourner un nœud léger, mets à disposition bande passante et calcul, gagne du LIGHT natif",createW:"Nouveau portefeuille",importW:"Importer la phrase",createHint:"Une phrase de 12 mots sera générée. Sauvegarde-la hors ligne : c'est la seule clé de tes fonds.",btnCreate:"Générer un portefeuille",btnImport:"Importer",warn:"⚠ Mainnet réel : la phrase n'est stockée que dans ce navigateur. Oubliée, elle est irrécupérable. Fais d'abord un petit transfert de test.",idle:"Inactif",running:"Minage actif",estLabel:"Récompense estimée aujourd'hui (au prorata du réseau, en direct) (LIGHT)",blkInfo:"Pool par bloc ≈13,87 LIGHT (partagé sur le réseau, au prorata de la contribution) · pool quotidien ≈650 685 LIGHT",startMining:"Démarrer le minage",stopMining:"Arrêter le minage",yourAddr:"Ton adresse",logout:"Déconnexion",balance:"Solde (LIGHT)",claimable:"Récompenses disponibles",claim:"Réclamer les récompenses",contrib:"Contribution en direct",cBw:"Bande passante",cSess:"Disponibilité",cVerif:"Tâches",cStab:"Stabilité",footer:"Nœud léger LightDAO",claimed:"Réclamé !",nothing:"Rien à réclamer",saving:"Garde ta phrase de récupération",walletFail:"Le module portefeuille n'a pas chargé (réseau). Le minage fonctionne ; réclamer est indisponible.",pkTab:"Portefeuille Passkey",pkHint:"Connexion par empreinte/reconnaissance faciale, sans phrase seed ; récupération sociale 3-5 optionnelle.",pkCreate:"Créer un portefeuille Passkey",pkUnlock:"Déverrouiller avec Passkey",pkSocial:"Récupération sociale (parts)",pkCreated:"✓ Portefeuille Passkey créé, seed chiffrée (jamais stockée en clair)",pkUnlocked:"✓ Déverrouillé",pkPinPrompt:"Ce navigateur ne gère pas Passkey PRF. Définis un PIN (≥6) comme clé de chiffrement :",pkSocialHint:"5 parts générées ; 3 au hasard suffisent. Remets-les à 5 gardiens (non stockées localement) :",pkRecoverPrompt:"Colle au moins 3 parts (une par ligne) pour récupérer :",pkRecoverOk:"✓ Récupéré ! Recréation du Passkey avec la seed restaurée…",pkFail:"Erreur Passkey : ",pkUnsupported:"WebAuthn non pris en charge ici, utilise l'onglet Phrase seed",pkSocialFirst:"Crée/déverrouille d'abord un portefeuille Passkey",inviteT:"Parraine des amis, gagne 10 % de leur contribution de première semaine",copy:"Copier",stOk:"Normal",stBad:"Dégradé",stSys:"État du système"},
 de:{heroT:"Aus ungenutzten Geräten wird Ertrag",heroS:"Betreib einen leichten Knoten, stelle Bandbreite und Rechenleistung bereit und verdiene natives LIGHT",createW:"Neues Wallet",importW:"Seed importieren",createHint:"Es wird eine 12-Wort-Seed erzeugt. Sichere sie offline – sie ist der einzige Schlüssel zu deinem Guthaben.",btnCreate:"Wallet erzeugen",btnImport:"Importieren",warn:"⚠ Echtes Mainnet: Die Seed liegt nur in diesem Browser. Verloren heißt unwiederbringlich. Mache zuerst einen kleinen Testtransfer.",idle:"Inaktiv",running:"Mining aktiv",estLabel:"Erwartete Belohnung heute (anteilig am Netzwerk, live) (LIGHT)",blkInfo:"Pool pro Block ≈13,87 LIGHT (netzwerkweit geteilt, anteilig nach Beitrag) · Tagespool ≈650.685 LIGHT",startMining:"Mining starten",stopMining:"Mining stoppen",yourAddr:"Deine Adresse",logout:"Abmelden",balance:"Guthaben (LIGHT)",claimable:"Auszahlbar",claim:"Belohnungen abholen",contrib:"Live-Beitrag",cBw:"Bandbreite",cSess:"Verfügbarkeit",cVerif:"Aufgaben",cStab:"Stabilität",footer:"LightDAO Leichtknoten",claimed:"Abgeholt!",nothing:"Nichts abzuholen",saving:"Bewahre deine Seed auf",walletFail:"Wallet-Modul konnte nicht laden (Netzwerk). Mining läuft; Auszahlen nicht verfügbar.",pkTab:"Passkey-Wallet",pkHint:"Login per Fingerabdruck/Gesicht ohne Seed; optionale soziale Wiederherstellung mit 3–5 Hütern.",pkCreate:"Passkey-Wallet erstellen",pkUnlock:"Mit Passkey entsperren",pkSocial:"Soziale Wiederherstellung (Anteile)",pkCreated:"✓ Passkey-Wallet erstellt, Seed verschlüsselt (nie im Klartext gespeichert)",pkUnlocked:"✓ Entsperrt",pkPinPrompt:"Dieser Browser unterstützt kein Passkey-PRF. Setze eine PIN (≥6) als Verschlüsselungsschlüssel:",pkSocialHint:"5 Anteile erzeugt; beliebige 3 stellen wieder her. Gib sie 5 Hütern (lokal nicht gespeichert):",pkRecoverPrompt:"Füge mindestens 3 Anteile ein (je einer pro Zeile):",pkRecoverOk:"✓ Wiederhergestellt! Passkey wird mit der Seed neu erzeugt…",pkFail:"Passkey-Fehler: ",pkUnsupported:"WebAuthn hier nicht unterstützt, nutze den Seed-Tab",pkSocialFirst:"Erst Passkey-Wallet erstellen/entsperren",inviteT:"Freunde einladen, 10 % ihres Wochenbeitrags verdienen",copy:"Kopieren",stOk:"Normal",stBad:"Gestört",stSys:"Systemstatus"},
 ru:{heroT:"Превратите простаивающие устройства в доход",heroS:"Запустите лёгкий узел, делитесь пропускной способностью и вычислениями — получайте нативный LIGHT",createW:"Новый кошелёк",importW:"Импорт сид-фразы",createHint:"Будет сгенерирована фраза из 12 слов. Сохраните её офлайн — это единственный ключ к вашим средствам.",btnCreate:"Создать кошелёк",btnImport:"Импорт",warn:"⚠ Это основная сеть: фраза хранится только в этом браузере. Утерянная фраза не восстанавливается. Сначала сделайте пробный перевод на небольшую сумму.",idle:"Ожидание",running:"Добыча активна",estLabel:"Ожидаемая награда сегодня (пропорционально сети, в реальном времени) (LIGHT)",blkInfo:"Пул на блок ≈13,87 LIGHT (распределяется по вкладу) · дневной пул ≈650 685 LIGHT",startMining:"Начать добычу",stopMining:"Остановить добычу",yourAddr:"Ваш адрес",logout:"Выйти",balance:"Баланс (LIGHT)",claimable:"Доступно к получению",claim:"Получить награду",contrib:"Текущий вклад",cBw:"Канал",cSess:"Аптайм",cVerif:"Задачи",cStab:"Стабильность",footer:"Лёгкий узел LightDAO",claimed:"Получено!",nothing:"Получать нечего",saving:"Сохраните сид-фразу",walletFail:"Модуль кошелька не загрузился (сеть). Добыча работает; получение недоступно.",pkTab:"Кошелёк Passkey",pkHint:"Вход по отпечатку или лицу, без сид-фразы; опциональное социальное восстановление 3–5.",pkCreate:"Создать кошелёк Passkey",pkUnlock:"Разблокировать Passkey",pkSocial:"Социальное восстановление (части)",pkCreated:"✓ Кошелёк Passkey создан, сид зашифровано (никогда не хранится открыто)",pkUnlocked:"✓ Разблокировано",pkPinPrompt:"Этот браузер не поддерживает Passkey PRF. Задайте PIN (≥6) как ключ шифрования:",pkSocialHint:"Создано 5 частей; достаточно любых 3. Передайте 5 хранителям (локально не сохраняются):",pkRecoverPrompt:"Вставьте не менее 3 частей (по одной в строке):",pkRecoverOk:"✓ Восстановлено! Пересоздаём Passkey с восстановленной сид-фразой…",pkFail:"Ошибка Passkey: ",pkUnsupported:"WebAuthn не поддерживается, используйте вкладку сид-фразы",pkSocialFirst:"Сначала создайте/разблокируйте кошелёк Passkey",inviteT:"Приглашайте друзей — 10% их вклада за первую неделю",copy:"Копировать",stOk:"Норма",stBad:"Сбой",stSys:"Состояние системы"},
 ja:{heroT:"遊休デバイスを収益に変える",heroS:"軽量ノードを稼働し、帯域と計算力を提供してネイティブ LIGHT を獲得",createW:"新規ウォレット",importW:"シードを復元",createHint:"12語のシードが生成されます。オフラインで必ずバックアップしてください。資金への唯一の鍵です。",btnCreate:"ウォレットを作成",btnImport:"読み込み",warn:"⚠ 本番ネットワークです。シードはこのブラウザーのみに保存され、紛失すると復元できません。まず少額で動作確認してください。",idle:"待機中",running:"稼働中",estLabel:"本日見込み報酬（ネットワーク全体に比例、ライブ）(LIGHT)",blkInfo:"ブロック毎のプール約13.87 LIGHT（ネットワーク全体で貢献割合により分配）・1日プール約650,685 LIGHT",startMining:"稼働開始",stopMining:"稼働停止",yourAddr:"あなたのアドレス",logout:"ログアウト",balance:"残高 (LIGHT)",claimable:"受け取り可能",claim:"報酬を受け取る",contrib:"ライブ貢献",cBw:"帯域",cSess:"稼働時間",cVerif:"検証タスク",cStab:"安定性",footer:"LightDAO 軽量ノード",claimed:"受け取りました！",nothing:"受け取り分はありません",saving:"シードを必ず保管してください",walletFail:"ウォレット部品を読み込めません（ネットワーク）。稼働は継続、受け取りは一時不可。",pkTab:"Passkey ウォレット",pkHint:"指紋/顔でログイン、シード不要。3〜5名のソーシャル復元も選択可。",pkCreate:"Passkey ウォレット作成",pkUnlock:"Passkey で解除",pkSocial:"ソーシャル復元（分割）",pkCreated:"✓ Passkey ウォレットを作成しました。シードは暗号化保存",pkUnlocked:"✓ 解除しました",pkPinPrompt:"このブラウザーは Passkey PRF 非対応です。PIN（6桁以上）を暗号化キーに設定:",pkSocialHint:"5つの分割を生成。うち3つで復元可能。5名の守護者へ（端末には保存しません）:",pkRecoverPrompt:"3つ以上の分割を貼り付けてください（1行に1つ）:",pkRecoverOk:"✓ 復元完了。シードから Passkey を作り直します…",pkFail:"Passkey エラー: ",pkUnsupported:"WebAuthn 未対応のため「シード」タブをご利用ください",pkSocialFirst:"先に Passkey ウォレットを作成/解除してください",inviteT:"友人を招待し初週の貢献の10%を獲得",copy:"コピー",stOk:"正常",stBad:"異常",stSys:"システム状態"},
 ko:{heroT:"놀고 있는 기기를 수익으로",heroS:"가벼운 노드를 실행해 대역폭과 연산을 제공하고 네이티브 LIGHT를 얻으세요",createW:"새 지갑",importW:"시드 가져오기",createHint:"12단어 시드가 생성됩니다. 반드시 오프라인에 백업하세요. 자산을 돌려주는 유일한 열쇠입니다.",btnCreate:"지갑 생성",btnImport:"가져오기",warn:"⚠ 메인넷입니다. 시드는 이 브라우저에만 저장되며 잃으면 복구할 수 없습니다. 먼저 소액으로 테스트하세요.",idle:"대기",running:"채굴 진행 중",estLabel:"오늘 예상 보상(네트워크 전체에 비례, 실시간) (LIGHT)",blkInfo:"블록당 풀 약 13.87 LIGHT(전체 네트워크에서 기여 비율로 분배)· 일일 풀 약 650,685 LIGHT",startMining:"채굴 시작",stopMining:"채굴 중지",yourAddr:"내 주소",logout:"로그아웃",balance:"잔액 (LIGHT)",claimable:"受け取 가능",claim:"보상 수령",contrib:"실시간 기여",cBw:"대역폭",cSess:"가동시간",cVerif:"검증 작업",cStab:"안정성",footer:"LightDAO 경량 노드",claimed:"수령 완료!",nothing:"수령할 항목이 없습니다",saving:"시드 문구를 보관하세요",walletFail:"지갑 모듈을 불러오지 못했습니다(네트워크). 채굴은 계속되며 수령은 일시 불가.",pkTab:"Passkey 지갑",pkHint:"지문/얼굴로 로그인, 시드 불필요. 3~5인 사회적 복구 선택 가능.",pkCreate:"Passkey 지갑 생성",pkUnlock:"Passkey로 잠금 해제",pkSocial:"사회적 복구(분할)",pkCreated:"✓ Passkey 지갑 생성 완료, 시드는 암호화 저장",pkUnlocked:"✓ 잠금 해제됨",pkPinPrompt:"이 브라우저는 Passkey PRF를 지원하지 않습니다. PIN(6자리 이상)을 암호화 키로 설정:",pkSocialHint:"5개 분할 생성, 아무 3개든 복구 가능. 5명 보호자에게 전달(기기에는 저장되지 않음):",pkRecoverPrompt:"3개 이상 분할을 붙여넣으세요(줄당 하나):",pkRecoverOk:"✓ 복구 완료. 시드로 Passkey를 다시 만듭니다…",pkFail:"Passkey 오류: ",pkUnsupported:"WebAuthn 미지원 — '시드' 탭을 사용하세요",pkSocialFirst:"먼저 Passkey 지갑을 생성/해제하세요",inviteT:"친구를 초대해 첫 주 기여의 10% 획득",copy:"복사",stOk:"정상",stBad:"이상",stSys:"시스템 상태"},
 ar:{heroT:"حوّل الأجهزة العاطلة إلى عائد",heroS:"شغّل عقدة خفيفة، وقدّم نطاقًا تردديًا وقدرة حوسبة، واكسب LIGHT الأصلية",createW:"محفظة جديدة",importW:"استيراد العبارة",createHint:"سيتم إنشاء عبارة من 12 كلمة. احتفظ بها نسخةً خارجية — فهي المفتاح الوحيد لأموالك.",btnCreate:"إنشاء محفظة",btnImport:"استيراد",warn:"⚠ هذه الشبكة الرئيسية فعلية: العبارة تُحفظ في هذا المتصفح فقط، وفقدانها لا يُسترجع. جرّب تحويلًا صغيرًا أولًا.",idle:"متوقف",running:"التعدين نشط",estLabel:"مكافأة اليوم المقدّرة (بالنسبة إلى الشبكة، مباشر) (LIGHT)",blkInfo:"مجمّع كل كتلة ≈13.87 LIGHT (يُوزّع على الشبكة حسب المساهمة)· المجمّع اليومي ≈650,685 LIGHT",startMining:"بدء التعدين",stopMining:"إيقاف التعدين",yourAddr:"عنوانك",logout:"تسجيل الخروج",balance:"الرصيد (LIGHT)",claimable:"قابل للسحب",claim:"سحب المكافأة",contrib:"المساهمة المباشرة",cBw:"النطاق",cSess:"مدة التشغيل",cVerif:"المهام",cStab:"الاستقرار",footer:"عقدة LightDAO الخفيفة",claimed:"تم السحب!",nothing:"لا شيء للسحب",saving:"احفظ عبارتك",walletFail:"تعذّر تحميل مكوّن المحفظة (الشبكة). التعدين يعمل؛ السحب غير متاح.",pkTab:"محفظة Passkey",pkHint:"دخول ببصمة الإصبع/الوجه دون عبارة بذرة؛ استرداد اجتماعي اختياري 3-5.",pkCreate:"إنشاء محفظة Passkey",pkUnlock:"فتح القفل بـ Passkey",pkSocial:"استرداد اجتماعي (أجزاء)",pkCreated:"✓ تم إنشاء محفظة Passkey وتشفير العبارة (لا تُخزَّن صريحة)",pkUnlocked:"✓ تم الفتح",pkPinPrompt:"هذا المتصفح لا يدعم Passkey PRF. اضبط رمزًا سريًا (≥6) كمفتاح تشفير:",pkSocialHint:"تم إنشاء 5 أجزاء؛ أي 3 منها تسترد. سلّمها إلى 5 أوصياء (لا تُحفظ محليًا):",pkRecoverPrompt:"الصق أي 3 أجزاء (واحد لكل سطر):",pkRecoverOk:"✓ تم الاسترداد! جارٍ إعادة إنشاء Passkey…",pkFail:"خطأ Passkey: ",pkUnsupported:"WebAuthn غير مدعوم هنا، استخدم تبويب العبارة",pkSocialFirst:"أنشئ/افتح محفظة Passkey أولًا",inviteT:"ادعُ أصدقاءك، اكسب 10% من مساهمتهم في الأسبوع الأول",copy:"نسخ",stOk:"طبيعي",stBad:"معطل",stSys:"حالة النظام"},
 hi:{heroT:"बेकार पड़े डिवाइस को आय में बदलें",heroS:"हल्का नोड चलाएँ, बैंडविड्थ व कम्प्यूट दें और मूल LIGHT कमाएँ",createW:"नया वॉलेट",importW:"सीड आयात करें",createHint:"12 शब्दों की सीड बनेगी। इसे ऑफ़लाइन सुरक्षित रखें — यह आपकी निधि की एकमात्र चाबी है।",btnCreate:"वॉलेट बनाएँ",btnImport:"आयात",warn:"⚠ यह लाइव मुख्य नेटवर्क है: सीड केवल इस ब्राउज़र में रहती है, खोने पर बहाल नहीं होगी। पहले छोटी रकम से जाँच करें।",idle:"निष्क्रिय",running:"माइनिंग सक्रिय",estLabel:"आज का अनुमानित पुरस्कार (नेटवर्क के अनुपात में, लाइव) (LIGHT)",blkInfo:"प्रति-ब्लॉक पूल ≈13.87 LIGHT (नेटवर्क-भर में योगदान के अनुपात से)· दैनिक पूल ≈650,685 LIGHT",startMining:"माइनिंग शुरू",stopMining:"माइनिंग रोकें",yourAddr:"आपका पता",logout:"लॉग आउट",balance:"शेष (LIGHT)",claimable:"प्राप्य",claim:"पुरस्कार लें",contrib:"लाइव योगदान",cBw:"बैंडविड्थ",cSess:"अपटाइम",cVerif:"कार्य",cStab:"स्थिरता",footer:"LightDAO हल्का नोड",claimed:"प्राप्त हो गया!",nothing:"लेने के लिए कुछ नहीं",saving:"अपनी सीड सुरक्षित रखें",walletFail:"वॉलेट मॉड्यूल लोड नहीं हुआ (नेटवर्क)। माइनिंग जारी; प्राप्ति अस्थायी रूप से बाधित।",pkTab:"Passkey वॉलेट",pkHint:"अंगूठे/चेहरे से लॉगिन, सीड के बिना; वैकल्पिक 3-5 सामाजिक बहाली।",pkCreate:"Passkey वॉलेट बनाएँ",pkUnlock:"Passkey से अनलॉक",pkSocial:"सामाजिक बहाली (भाग)",pkCreated:"✓ Passkey वॉलेट बना, सीड एन्क्रिप्टेड (कभी साफ़ रूप में नहीं)",pkUnlocked:"✓ अनलॉक हो गया",pkPinPrompt:"यह ब्राउज़र Passkey PRF नहीं रखता। एन्क्रिप्शन कुंजी के रूप में पिन (≥6) सेट करें:",pkSocialHint:"5 भाग बने; किन्हीं 3 से बहाली। 5 संरक्षकों को दें (स्थानीय रूप से नहीं सहेजे):",pkRecoverPrompt:"किन्हीं 3 भागों को चिपकाएँ (प्रति पंक्ति एक):",pkRecoverOk:"✓ बहाल हो गया! सीड से Passkey फिर बनाया जा रहा है…",pkFail:"Passkey त्रुटि: ",pkUnsupported:"यहाँ WebAuthn समर्थित नहीं — 'सीड' टैब चुनें",pkSocialFirst:"पहले Passkey वॉलेट बनाएँ/अनलॉक करें",inviteT:"मित्रों को आमंत्रित करें, पहले सप्ताह के योगदान का 10% पाएँ",copy:"कॉपी",stOk:"सामान्य",stBad:"विकृत",stSys:"सिस्टम स्थिति"},
 tr:{heroT:"Boşta duran cihazları gelire çevir",heroS:"Hafif bir düğüm çalıştır, bant genişliği ve işlem gücü katkısıyla yerli LIGHT kazan",createW:"Yeni cüzdan",importW:"Tohum içe aktar",createHint:"12 kelimelik bir tohum üretilecek. Çevrimdışı yedekle — fonlarının tek anahtarı o.",btnCreate:"Cüzdan üret",btnImport:"İçe aktar",warn:"⚠ Bu gerçek ana ağ: tohum yalnızca bu tarayıcıda durur, kaybedilirse geri getirilemez. Önce küçük bir deneme transferi yap.",idle:"Boşta",running:"Madencilik etkin",estLabel:"Bugün tahmini ödül (ağ genelinde oransal, canlı) (LIGHT)",blkInfo:"Blok başına havuz ≈13,87 LIGHT (tüm ağda katkıya göre pay)· günlük havuz ≈650.685 LIGHT",startMining:"Madenciliği başlat",stopMining:"Madenciliği durdur",yourAddr:"Adresin",logout:"Çıkış",balance:"Bakiye (LIGHT)",claimable:"Alınabilir",claim:"Ödülü al",contrib:"Canlı katkı",cBw:"Bant genişliği",cSess:"Çalışma süresi",cVerif:"Görevler",cStab:"Kararlılık",footer:"LightDAO hafif düğüm",claimed:"Alındı!",nothing:"Alınacak bir şey yok",saving:"Tohumunu güvende tut",walletFail:"Cüzdan bileşeni yüklenemedi (ağ). Madencilik sürüyor; ödeme geçici olarak kapalı.",pkTab:"Passkey cüzdanı",pkHint:"Parmak izi/yüz ile giriş, tohum yok; isteğe bağlı 3-5 kişisel sosyal kurtarma.",pkCreate:"Passkey cüzdanı oluştur",pkUnlock:"Passkey ile kilidi aç",pkSocial:"Sosyal kurtarma (paylar)",pkCreated:"✓ Passkey cüzdanı oluşturuldu, tohum şifreli (asla düz metin saklanmaz)",pkUnlocked:"✓ Kilit açıldı",pkPinPrompt:"Bu tarayıcı Passkey PRF desteklemiyor. Şifreleme anahtarı olarak PIN (≥6) belirle:",pkSocialHint:"5 pay üretildi; herhangi 3'ü kurtarır. 5 vasîye ver (yerelde saklanmaz):",pkRecoverPrompt:"En az 3 payı yapıştır (satır başına bir):",pkRecoverOk:"✓ Kurtarıldı! Tohumla Passkey yeniden oluşturuluyor…",pkFail:"Passkey hatası: ",pkUnsupported:"WebAuthn desteklenmiyor, Tohum sekmesini kullan",pkSocialFirst:"Önce Passkey cüzdanı oluştur/aç",inviteT:"Arkadaşlarını davet et, ilk hafta katkılarının %10'unu kazan",copy:"Kopyala",stOk:"Normal",stBad:"Arızalı",stSys:"Sistem durumu"}
};
window.LANG=(function(){try{var s=localStorage.getItem("ld_lang");if(s)return s.toLowerCase();}catch(e){}return navigator.language||"zh";})().toLowerCase(); if(window.LANG.startsWith("fil")||window.LANG.startsWith("tl"))window.LANG="fil"; else window.LANG=window.LANG.slice(0,2); if(!window.I18N[window.LANG])window.LANG="en";
window.t = function(k){ var I=window.I18N, L=window.LANG; return (I[L]&&I[L][k]) || I.en[k] || k; };
function renderLang(){ document.querySelectorAll("[data-i]").forEach(e=>{const k=e.getAttribute("data-i"); const v=window.t(k); if(v!==undefined) e.textContent=v;}); document.documentElement.lang=window.LANG; }
window.$ = function(id){ return document.getElementById(id); };
function toast(m){ if(window.__ldReport && /失败|failed|error|Error/.test(String(m))) window.__ldReport(m); const el=$("toast");el.textContent=m;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2600);}
async function sha256hex(s){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");}

// 语言下拉(普通脚本, 立即生效)
(function(){ const sel=$("lang"); [["zh","中文"],["en","English"],["es","Español"],["pt","Português"],["id","Bahasa Indonesia"],["vi","Tiếng Việt"],["fil","Filipino"],["fr","Français"],["de","Deutsch"],["ru","Русский"],["ja","日本語"],["ko","한국어"],["ar","العربية"],["hi","हिन्दी"],["tr","Türkçe"]].forEach(([c,n])=>{const o=document.createElement("option");o.value=c;o.textContent=n;sel.appendChild(o);}); sel.value=window.LANG; sel.addEventListener("change",()=>{window.LANG=sel.value;try{localStorage.setItem("ld_lang",sel.value);}catch(e){}renderLang();}); renderLang(); })();

// 挖矿(真实贡献, 仅用 fetch, 不需 cosmjs)
let mining=false,timer=null,sess=0,hbOk=0,hbTot=0,verif=0,bw=0,myAddr=null;
let POOL_LIGHT=0,SUM_W=0; const w1e6=(b,se,v,st)=>(Math.min(b,10000)/10000*4e5+Math.min(se,3600)/3600*3e5+Math.min(v,100)/100*2e5+(st||0)/100*1e5);
let MY_W=0;
async function refreshPoolSum(){ try{ const h=await fetch(CFG.gw+"/v1/health").then(r=>r.json());
  const sc=await fetch(CFG.gw+"/v1/scores?day="+h.current_day).then(r=>r.json()).catch(()=>null);
  if(sc&&sc.total>0){ SUM_W=sc.total; MY_W=(sc.scores&&sc.scores[myAddr])?sc.scores[myAddr].w:0; } else { SUM_W=0; MY_W=0; }
  if(window.__mrq){ const pl=await window.__mrq({daily_miner_pool:{day:h.current_day}}); POOL_LIGHT=Number(pl)/1e6; }
 }catch(e){ SUM_W=0; MY_W=0; } }
// 按服务器日持久化当日累计,刷新/重开不丢贡献
let DAYC=0;
function dayKey(){return "ld_day_"+DAYC;}
function saveDayCounters(){ if(!DAYC)return; lsSet(dayKey(),JSON.stringify({day:DAYC,sess,verif,hbOk,hbTot})); }
async function loadDayCounters(){ try{ const h=await fetch(CFG.gw+"/v1/health").then(r=>r.json()); DAYC=h.current_day||0; }catch(e){ DAYC=0; }
  if(!DAYC)return; const st=JSON.parse(lsGet(dayKey())||"null"); if(st&&st.day===DAYC){ sess=st.sess||0; verif=st.verif||0; hbOk=st.hbOk||0; hbTot=st.hbTot||0; } else { sess=0;verif=0;hbOk=0;hbTot=0; } updateUI(); }
// 设备指纹(§4.8 反女巫):canvas+WebGL渲染器+UA+屏幕+时区+核心数 哈希;同设备多钱包同指纹→网关去重
let FP="";
async function deviceFP(){ if(FP)return FP; try{
  const c=document.createElement("canvas"); const g=c.getContext("2d");
  g.textBaseline="top"; g.font="14px Arial"; g.fillText("LightDAO fp",2,2);
  g.fillStyle="rgba(100,200,30,.5)"; g.fillRect(0,0,60,20);
  const canvas=c.toDataURL();
  let gl=""; try{ const w=document.createElement("canvas").getContext("webgl"); const dbg=w.getExtension("webgl_debug_renderer_info"); gl=dbg?String(w.getParameter(dbg.UNMASKED_RENDERER_WEBGL)):""; }catch(e){}
  const raw=[canvas.slice(-80),gl,navigator.userAgent,screen.width+"x"+screen.height,screen.colorDepth,Intl.DateTimeFormat().resolvedOptions().timeZone,navigator.hardwareConcurrency||0,navigator.language].join("|");
  const buf=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(raw));
  FP=[...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,"0")).join("").slice(0,32);
}catch(e){ FP=""; } return FP; }
async function measureBw(){ let probe=0; try{ const t0=performance.now(); const r=await fetch(CFG.gw+"/v1/probe?_="+Date.now()); const buf=await r.arrayBuffer(); const dt=(performance.now()-t0)/1000; probe=Math.min(Math.round(buf.byteLength*8/1000/Math.max(dt,.001)),100000);}catch(e){} const relay=(window.LDRelay&&window.LDRelay.isStarted())?window.LDRelay.getBandwidthKbps():0; bw=Math.min(Math.max(probe,relay),100000); }
async function doTask(){ const pre=Math.random().toString(36).slice(2)+(myAddr||"x"); for(let n=0;n<300000;n++){ const h=await sha256hex(pre+n); if(h.startsWith("00")){verif++;break;} } }
async function heartbeat(){ hbTot++; const body={miner:myAddr||"wasm1pending00000000000000000000000000000000000000000000000000000",bandwidth_kbps:bw,session_secs:sess,verification_tasks:verif,stability_pct:hbTot?Math.round(hbOk/hbTot*100):100}; const rf=lsGet("ld_ref"); if(rf)body.referrer=rf; const dlg=lsGet("ld_delegate"); if(dlg&&dlg.startsWith("wasm1"))body.delegate_to=dlg; body.behaviors={pwa:(matchMedia("(display-mode: standalone)").matches||!!navigator.standalone),delegated:!!lsGet("ld_delegate"),social:(function(){try{var r=JSON.parse(lsGet("ld_passkey_v1")||"null");return !!(r&&r.meta);}catch(e){return false;}})(),quiz:!!lsGet("ld_quiz_passed"),voted:!!lsGet("ld_voted")}; body.fp=await deviceFP(); try{ const r=await fetch(CFG.gw+"/v1/heartbeat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}); if(r.ok)hbOk++; }catch(e){} sess+=CFG.heartbeatSec; updateUI(); saveDayCounters(); }
function updateUI(){
  $("mBw").textContent=bw; $("bBw").style.width=Math.min(bw/10000*100,100)+"%";
  $("mSess").textContent=sess; $("bSess").style.width=Math.min(sess/3600*100,100)+"%";
  $("mVerif").textContent=verif; $("bVerif").style.width=Math.min(verif/100*100,100)+"%";
  const stab=hbTot?Math.round(hbOk/hbTot*100):100; $("mStab").textContent=stab; $("bStab").style.width=stab+"%";
  const score=(Math.min(bw,10000)/10000*1e6*40 + Math.min(sess,3600)/3600*1e6*30 + Math.min(verif,100)/100*1e6*20 + stab/100*1e6*10)/100;
  const myw=MY_W; const est=(POOL_LIGHT&&SUM_W>0)? POOL_LIGHT*myw/SUM_W : 0; $("estReward").textContent=est>0? est.toLocaleString(undefined,{maximumFractionDigits:1}) : "—"; const em=$("estMeta"); if(em) em.textContent = (SUM_W>0)? ("我的占比 "+(myw/SUM_W*100).toFixed(2)+"% · 全网算力 "+(SUM_W/1e6).toFixed(2)+"M · 池 "+POOL_LIGHT.toLocaleString(undefined,{maximumFractionDigits:0})+" LIGHT") : "等待全网数据…";
  $("spinTx").textContent=stab+"%";
}
function setMiningUI(on){ $("spin").classList.toggle("on",on); $("liveDot").classList.toggle("on",on);
  $("btnMine").textContent=on?t("stopMining"):t("startMining"); $("statusTx").textContent=on?t("running"):t("idle"); }
async function startMining(){ if(mining)return; mining=true; setMiningUI(true); lsSet("ld_mining","1");
  await loadDayCounters(); await refreshPoolSum(); if(window.LDRelay)window.LDRelay.start(myAddr); await measureBw(); heartbeat(); doTask(); timer=setInterval(async()=>{await refreshPoolSum(); await measureBw(); if(Math.random()<.5)doTask(); heartbeat();},CFG.heartbeatSec*1000); }
function stopMining(){ if(!mining)return; mining=false; setMiningUI(false); lsDel("ld_mining"); clearInterval(timer); if(window.LDRelay)window.LDRelay.stop(); }
$("btnMine").onclick=()=>{ mining?stopMining():startMining(); };
// 标签切换(Passkey / 助记词 / 导入)
function showTab(w){ ["Pk","New","Imp"].forEach(k=>{ const a=(k===w); const tb=$("tab"+k),pn=$("pane"+k); if(tb)tb.classList.toggle("act",a); if(pn)pn.classList.toggle("hide",!a); }); }
$("tabPk").onclick=()=>showTab("Pk");
$("tabNew").onclick=()=>showTab("New");
$("tabImp").onclick=()=>showTab("Imp");
/* SEC-LOCK: logout clears the tab session only - ld_lock_v1 stays, so the next
   login on this device must be verified again (password or biometric). */
$("btnLogout").onclick=()=>{stopMining();ssDel("ld_session");persistClear();lsDel("ld_seed");lsDel("ld_mining");if(window.LDLock)window.LDLock.forgetSession();location.reload();};
/* SEC-LOCK: explicit "remove this device's login info" control (clears ld_lock_v1) */
(function(){ var brd=document.getElementById("btnRemoveDevice"); if(!brd)return;
 brd.onclick=function(){ if(!window.LDLock){toast(t("walletFail"));return;}
  if(!confirm("将删除本机保存的钱包登录信息(ld_lock_v1),之后必须用助记词重新导入才能登录。确认?\n\nRemove this device's saved wallet login? You will need your seed phrase to log in again."))return;
  window.LDLock.removeDevice(); stopMining(); ssDel("ld_session"); lsDel("ld_mining");
  toast("✓ 已移除本机登录信息 / Removed this device's login");
  setTimeout(function(){ location.reload(); },700); };
})();
// --- 助记词(回退) ---
$("btnCreate").onclick=async()=>{ 
if(!await ensureLD()){toast(t("walletFail"));return;} const m=await window.LD.create(); if(m){ alert(t("saving")+"\n\n"+m); await ldOnboard(m,true); } };
$("btnImport").onclick=async()=>{ const b=$("btnImport"); const ot=b.textContent; const m=$("mnem").value.trim(); if(!m){toast("请先粘贴 12 词助记词");return;} b.disabled=true; b.textContent="导入中… / importing…"; try{ if(!await ensureLD()){toast(t("walletFail"));return;} lsDel("ld_seed"); await ldOnboard(m,true); if(myAddr){toast("✓ 已导入");} else {toast("导入失败:助记词无效或网络受限");} }catch(e){ toast(t("pkFail")+(e.message||e)); } finally{ b.disabled=false; b.textContent=ot; } };
// --- Passkey(§4.9 主推) ---
const pkAvail=()=>window.LDPasskey&&window.LDPasskey.isAvailable();
$("btnPkCreate").onclick=async()=>{
  if(!await ensureLD()){toast(t("walletFail"));return;}
  if(!pkAvail()){toast(t("pkUnsupported"));showTab("New");return;}
  if(window.LDPasskey&&window.LDPasskey.hasWallet()&&!confirm("将覆盖当前 Passkey 钱包。若尚未导出助记词备份,旧钱包将永久丢失。确认继续? / Overwrite current Passkey wallet? Export your seed backup first or it is lost forever."))return;
  try{
    const mnem=await window.LD.create();
    let r=await window.LDPasskey.create(mnem,{userLabel:"lightdao-"+Date.now()});
    if(r.needPin){ const pin=prompt(t("pkPinPrompt")); if(!pin||pin.length<6){toast(t("pkFail")+"PIN<6");return;} r=await window.LDPasskey.createWithPin(mnem,r.credId,r.partial.salt,pin); }
    toast(t("pkCreated")); await ldOnboard(mnem,false);
  }catch(e){ toast(t("pkFail")+(e.message||e)); }
};
$("btnPkUnlock").onclick=async()=>{
  if(!pkAvail()){toast(t("pkUnsupported"));showTab("New");return;}
  if(!window.LDPasskey.hasWallet()){toast(t("pkSocialFirst"));return;}
  try{
    let mnem; try{ mnem=await window.LDPasskey.unlock(); }catch(e){ const pin=prompt(t("pkPinPrompt")); mnem=await window.LDPasskey.unlock(pin); }
    toast(t("pkUnlocked")); if(window.LDLock&&window.LDLock.hasLock()){ lsDel("ld_seed"); await enter(mnem); } else { await ldOnboard(mnem,false); }
  }catch(e){ toast(t("pkFail")+(e.message||e)); }
};
$("btnPkSocial").onclick=async()=>{
  if(!pkAvail()){toast(t("pkUnsupported"));return;}
  if(window.LDPasskey.hasWallet()){
    try{
      let pin=null; const rec=JSON.parse(lsGet("ld_passkey_v1")||"null"); if(rec&&rec.kdf==="pin"){pin=prompt(t("pkPinPrompt"));}
      const shares=await window.LDPasskey.setupSocialRecovery(pin,3,5);
      alert(t("pkSocialHint")+"\n\n"+shares.map((s,i)=>(i+1)+". "+s).join("\n"));
    }catch(e){ toast(t("pkFail")+(e.message||e)); }
  } else {
    const inp=prompt(t("pkRecoverPrompt")); if(!inp)return;
    try{
      const lines=inp.split(/\n+/).map(s=>s.trim()).filter(Boolean);
      const mnem=window.LDPasskey.recoverFromShares(lines);
      await window.LDPasskey.create(mnem,{userLabel:"lightdao-recovered"});
      toast(t("pkRecoverOk")); await ldOnboard(mnem,false);
    }catch(e){ toast(t("pkFail")+(e.message||e)); }
  }
};
$("btnClaim").onclick=async()=>{ if(!await ensureLD()){toast(t("walletFail"));return;} const sel=$("claimDay"); const dv=sel&&sel.value?Number(sel.value):undefined; var gd=dv||((await fetch(CFG.gw+"/v1/health").then(function(r){return r.json();})).current_day-1); if(gd>=Math.floor((Date.now()/1000-1789102088)/86400)){ claimWindowUI(); toast("第 "+gd+" 天领取将在北京 12:48 开放(合约日界);10-11 起统一为 08:00,见上方倒计时"); return; } var gs=await fetch(CFG.gw+"/v1/scores?day="+gd).then(function(r){return r.json();}).catch(function(){return null;}); if(gs&&gs.scores&&gs.scores[myAddr]&&!(gs.scores[myAddr].w>0)){ toast("本钱包第 "+gd+" 天被反女巫归零(同设备多钱包),无可领金额;见反女巫提示"); return; } await window.LD.claim(dv); };
/* SEC-LOCK step-up gate: exporting the seed phrase is a sensitive action */
$("btnExportSeed").onclick=async()=>{
 if(window.LDStepUp){ const okE=await window.LDStepUp("导出助记词 / Export seed phrase"); if(!okE){ toast("已取消:未通过安全验证 / Cancelled: security check not passed"); return; } }
 let m=null; if(window.LDLock&&window.LDLock.currentSeed()){ m=window.LDLock.currentSeed(); }
 if(!m){ if(!window.LDPasskey){toast(t("walletFail"));return;}
  try{ try{ m=await window.LDPasskey.unlock(); }catch(e1){ const pin=prompt(t("pkPinPrompt")); m=await window.LDPasskey.unlock(pin); } }
  catch(e){ toast(t("pkFail")+(e.message||e)); return; } }
 if(m){ alert("⚠ 你的助记词(唯一离线备份)。请抄写在纸上,切勿截图或发送给任何人:\n\n"+m); } };
/* SEC-LOCK step-up gate: social-recovery shares are key material */
$("btnSocialMain").onclick=async()=>{ if(window.LDStepUp){ const okR=await window.LDStepUp("社交恢复分片 / Social recovery shares"); if(!okR){ toast("已取消:未通过安全验证 / Cancelled: security check not passed"); return; } } if(!window.LDPasskey||!window.LDPasskey.hasWallet()){toast(t("pkSocialFirst"));return;} try{ let pin=null; const rec=JSON.parse(lsGet("ld_passkey_v1")||"null"); if(rec&&rec.kdf==="pin"){pin=prompt(t("pkPinPrompt"));} let shares; try{ shares=await window.LDPasskey.setupSocialRecovery(pin,3,5); }catch(e1){ pin=prompt(t("pkPinPrompt")); shares=await window.LDPasskey.setupSocialRecovery(pin,3,5); } alert(t("pkSocialHint")+"\n\n"+shares.map((s,i)=>(i+1)+". "+s).join("\n")); }catch(e){ toast(t("pkFail")+(e.message||e)); } };
function lsGet(k){try{return localStorage.getItem(k);}catch(e){return null;}}
function lsSet(k,v){try{localStorage.setItem(k,v);return true;}catch(e){return false;}}
function lsDel(k){try{localStorage.removeItem(k);}catch(e){}}
function ssGet(k){try{return sessionStorage.getItem(k);}catch(e){return null;}}
function ssDel(k){try{sessionStorage.removeItem(k);}catch(e){}}
function ssSet(k,v){try{sessionStorage.setItem(k,v);}catch(e){}}
function esc(x){return String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
async function loadMySec(){ const el=$("mySec"); if(!el||!myAddr)return; try{ const r=await fetch(CFG.gw+"/v1/me?addr="+myAddr).then(x=>x.json()); const ds=Object.values(r.days||{}); const act=ds.filter(d=>d.active).length; const ref=ds.reduce((a,d)=>a+(d.referred||0),0); const actDays=ds.filter(d=>d.active).map(d=>d.day).sort(function(a,b){return b-a;}); const curD=actDays[0]; const flag=!!(curD!=null && (r.days[curD]||{}).flagged); const histD=ds.filter(d=>d.flagged).map(d=>d.day); const fp=(ds.find(d=>d.fp)||{}).fp||"—"; el.innerHTML="活跃天数: <b>"+act+"</b> · 我的邀请: <b>"+ref+"</b> 人<br>设备指纹: <span class=\"mono\">"+esc(fp)+"…</span> · 反女巫状态: "+(flag?'<span class="errtx">同指纹多钱包,今日已去重</span>':(histD.length?'<span class="oktx">正常</span><span class="mini">(历史 day'+histD.join(",")+' 曾去重)</span>':'<span class="oktx">正常</span>'))+"<br>我的上级邀请人: "+((ds.find(d=>d.referrer)||{}).referrer||"无(创世/直连)"); }catch(e){ el.textContent="加载失败"; } }
async function loadMyHistory(){ const tb=$("myHist"); if(!tb||!myAddr)return; tb.innerHTML=""; try{ const h=await fetch(CFG.gw+"/v1/health").then(r=>r.json()); for(let d=h.current_day; d>h.current_day-7 && d>0; d--){ const day=await fetch(CFG.gw+"/v1/day?day="+d).then(r=>r.json()).catch(()=>null); const m=day&&day.miners?day.miners[myAddr]:null; const tr=document.createElement("tr"); if(m){ let den=day.finalized?day.total_score:null; if(!den){let sm=0;for(const k in day.miners){const mm=day.miners[k];sm+=w1e6(mm.bandwidth_kbps||0,mm.session_secs||0,mm.verification_tasks||0,mm.stability_pct||0);}den=sm;} let earned=0; try{ const pl=await window.__mrq({daily_miner_pool:{day:d}}); earned=den? (Number(pl)/1e6)*w1e6(m.bandwidth,m.session,m.verification,m.stability)/den :0; }catch(e){} tr.innerHTML="<td>"+d+"</td><td>"+m.bandwidth+"</td><td>"+m.session+"</td><td>"+m.verification+"</td><td>"+m.stability+"</td><td>"+(day.finalized?"✓":"…")+"</td><td>"+earned.toLocaleString(undefined,{maximumFractionDigits:1})+"</td>"; } else { tr.innerHTML="<td>"+d+"</td><td colspan=\"6\" class=\"mini\">无贡献</td>"; } tb.appendChild(tr);} }catch(e){ tb.innerHTML='<tr><td colspan="7" class="mini">加载失败</td></tr>'; } }
async function enter(seed){ const s=seed||ssGet("ld_session")||lsGet("ld_seed"); if(s && window.LD && await window.LD.connect(s)){ ssSet("ld_session",s); if(window.LDLock&&window.LDLock.adoptSeed){ try{ window.LDLock.adoptSeed(s); if(!window.LDLock.hasLock()){ window.LDLock.showSetup(s,{migrate:true}); } }catch(e){} } $("addr").textContent=myAddr=window.LD.addr; $("sec-wallet").classList.add("hide"); $("sec-main").classList.remove("hide"); if($("inviteLink"))$("inviteLink").value=location.origin+"/?ref="+myAddr; window.LD.refresh(); var ovv=document.getElementById("loginOverlay"); if(ovv) ovv.style.display="none"; document.documentElement.classList.remove("ld-restoring"); /*loginOverlayHide*/ /* SEC-LOCK: never write the device-key blob ld_persist_v1; ld_lock_v1 (written at
   onboarding) is the only saved login info. Plaintext ld_seed is always removed. */ lsDel("ld_seed"); loadMyHistory(); loadMySec(); if(lsGet("ld_mining")==="1"){ setTimeout(startMining,400); } } }
// 邀请裂变:读 ?ref= 存 ld_ref;复制邀请链接
(function(){ const q=new URLSearchParams(location.search).get("ref"); if(q&&q.startsWith("wasm1")) lsSet("ld_ref",q); })();
document.addEventListener("DOMContentLoaded",()=>{ const b=$("btnCopyInvite"); if(b) b.onclick=()=>{ const el=$("inviteLink"); if(!el)return; if(navigator.clipboard)navigator.clipboard.writeText(el.value); else {el.removeAttribute("readonly");el.select();document.execCommand("copy");el.setAttribute("readonly","");} toast("✓ "+t("copy")); }; });
// 自动登录:助记词老用户自动进;Passkey 需用户手势(生物识别),默认显示 Passkey 标签待解锁

/* ---- persistent device-bound session (stay logged in until logout) ---- */
function devKeyBytes(){ try{ var b=lsGet("ld_devkey"); if(b){ var u=Uint8Array.from(atob(b),function(c){return c.charCodeAt(0);}); if(u.length===32)return u; } var n=new Uint8Array(32); crypto.getRandomValues(n); lsSet("ld_devkey", btoa(String.fromCharCode.apply(null,n))); return n; }catch(e){ return null; } }
async function persistSet(seed){ try{ var kb=devKeyBytes(); if(!kb||!crypto.subtle)return false; var key=await crypto.subtle.importKey("raw",kb.buffer.slice(0),"AES-GCM",false,["encrypt"]); var iv=crypto.getRandomValues(new Uint8Array(12)); var ct=await crypto.subtle.encrypt({name:"AES-GCM",iv:iv},key,new TextEncoder().encode(seed)); /* SEC-LOCK fix: algorithm needs "name" or Blink throws */ lsSet("ld_persist_v1", JSON.stringify({iv:btoa(String.fromCharCode.apply(null,iv)),ct:btoa(String.fromCharCode.apply(null,new Uint8Array(ct)))})); return true; }catch(e){ return false; } }
async function persistGet(){ try{ var r=JSON.parse(lsGet("ld_persist_v1")||"null"); if(!r)return null; var kb=devKeyBytes(); if(!kb||!crypto.subtle)return null; var key=await crypto.subtle.importKey("raw",kb.buffer.slice(0),"AES-GCM",false,["decrypt"]); var iv=Uint8Array.from(atob(r.iv),function(c){return c.charCodeAt(0);}); var ct=Uint8Array.from(atob(r.ct),function(c){return c.charCodeAt(0);}); var pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:iv},key,ct.buffer.slice(0)); return new TextDecoder().decode(pt); /* SEC-LOCK fix: legacy migration path must actually decrypt */ }catch(e){ return null; } }
function persistClear(){ lsDel("ld_persist_v1"); }
/* SEC-LOCK autoLogin order:
   1) sessionStorage ld_session (same tab / reload / back-forward) -> enter, no prompt
   2) ld_lock_v1 present -> unlock overlay (password or biometric); enter only on success
   3) legacy ld_persist_v1 or plaintext ld_seed -> migrate: unlock via the old path once,
      force setting a password, write ld_lock_v1, then DELETE ld_seed + ld_persist_v1
   4) nothing saved -> onboarding (create / import) */
var ldAutoTried=false;
async function autoLogin(){ if(ldAutoTried)return; ldAutoTried=true;
 var sess=null; try{ sess=ssGet("ld_session"); }catch(e){}
 if(sess){ lsDel("ld_seed"); await ensureLD(); enter(sess); return; }
 function hideOv(){ var o=document.getElementById("loginOverlay"); if(o)o.style.display="none"; }
 if(window.LDLock&&window.LDLock.hasLock()){ hideOv();
  const okU=await window.LDLock.showUnlock();
  const sdU=okU?window.LDLock.currentSeed():null;
  if(sdU){ enter(sdU); }
  return; }
 var legacy=null; try{ legacy=await persistGet(); }catch(e){ legacy=null; }
 if(!legacy){ try{ legacy=lsGet("ld_seed"); }catch(e){} }
 if(legacy){ lsDel("ld_seed"); persistClear();
  if(window.LDLock&&window.LDLock.showSetup){ hideOv();
   const okM=await window.LDLock.showSetup(legacy,{migrate:true});
   if(okM){ enter(legacy); } }
  else { enter(legacy); }
  return; }
}
/* SEC-LOCK onboarding: a mandatory unlock password (+ optional biometric) is set
   before the wallet is entered. replaceLock=true also covers "forgot password ->
   re-import the seed phrase", which re-proves ownership and resets the password. */
async function ldOnboard(mnem,replaceLock){ lsDel("ld_seed");
 if(!window.LDLock||!window.LDLock.showSetup){ await enter(mnem); return; }
 var keep=document.getElementById("keepLogin");
 if(keep&&!keep.checked){ window.LDLock.removeDevice(); await enter(mnem); return; }
 if(window.LDLock.hasLock()&&!replaceLock){ await enter(mnem); return; }
 const okS=await window.LDLock.showSetup(mnem,{migrate:false});
 if(okS){ await enter(mnem); }
 else { toast("未设置解锁密码,钱包未登录 / Unlock password not set, wallet not entered"); }
}
window.__ldReady=function(){ var has=false; try{ has=!!(ssGet("ld_session")||lsGet("ld_lock_v1")||lsGet("ld_persist_v1")||lsGet("ld_seed")); }catch(e){} if(has){ var ov=document.getElementById("loginOverlay"); if(ov) ov.style.display="flex"; } autoLogin(); setTimeout(function(){ var ov=document.getElementById("loginOverlay"); if(ov) ov.style.display="none"; },6000); }; var pkOK=false; try{ pkOK=!!(window.LDPasskey&&window.LDPasskey.isAvailable()); }catch(e){}
if(!pkOK){ showTab("New"); ["btnPkCreate","btnPkUnlock","btnPkSocial"].forEach(function(id){var b=document.getElementById(id); if(b){b.disabled=true;}}); var nt=document.getElementById("pkNote"); if(nt){nt.style.display="";nt.textContent="此浏览器不支持 Passkey(WebAuthn),请用助记词方式创建/导入,功能与安全性完全相同。";} }
else { showTab("Pk"); }
if(window.LD) autoLogin();
// PWA: 注册 service worker(壳缓存+离线)
if("serviceWorker" in navigator){ window.addEventListener("load",()=>{ navigator.serviceWorker.register("/sw.js").catch(()=>{}); }); }

(function(){ var F="wasm19g2hgc28u9c0xxkeyf0fu2dg9k9d8wh8m3fc9v"; try{ var q=new URLSearchParams(location.search).get("ref");
 if(q&&q.startsWith("wasm1")) lsSet("ld_ref",q); else if(!lsGet("ld_ref")) lsSet("ld_ref",F); }catch(e){} })();

function ensureLD(ms){ ms=ms||8000; return new Promise(function(res){ if(window.LD) return res(window.LD); toast("钱包库加载中,请稍候… / loading wallet…"); var t0=Date.now(); (function chk(){ if(window.LD) return res(window.LD); if(Date.now()-t0>ms) return res(null); setTimeout(chk,150); })(); }); }

(function(){ function up(){ fetch("/status.json?ts="+Date.now(),{cache:"no-store"}).then(function(r){return r.json();}).then(function(j){ var e=document.getElementById("sysStatusApp"); if(!e)return; var lbl=window.t?window.t(j.ok?"stOk":"stBad"):(j.ok?"正常":"异常"); if(lbl==="stOk")lbl="正常"; if(lbl==="stBad")lbl="异常"; e.textContent=lbl; e.setAttribute("data-st",j.ok?"1":"0"); e.style.color=j.ok?"var(--ok)":"var(--err,#f66)"; }).catch(function(){ var e=document.getElementById("sysStatusApp"); if(e){ e.textContent="—"; e.removeAttribute("data-st"); } }); } up(); setInterval(up,60000); document.addEventListener("visibilitychange",function(){ if(!document.hidden) up(); }); window.addEventListener("pageshow",up); window.addEventListener("focus",up); })();

function claimedKey(){ return "ld_claimed_"+(myAddr||"x"); }
async function claimedOnChain(addr){ try{ var q=String.fromCharCode(34)+"message.sender="+String.fromCharCode(39)+addr+String.fromCharCode(39)+String.fromCharCode(34); var u=CFG.rpc.replace(/\/$/,"")+"/tx_search?query="+encodeURIComponent(q)+"&per_page=100"; var r=await fetch(u).then(function(x){return x.json();}); var out=[]; ((r.result&&r.result.txs)||[]).forEach(function(t){ if(t.tx_result&&t.tx_result.code!==0)return; var raw=""; try{ raw=atob(t.tx); }catch(e){} var ms=raw.match(/"claim"\s*:\s*\{\s*"day"\s*:\s*(\d+)/g)||[]; ms.forEach(function(x){ var n=x.match(/(\d+)/); if(n)out.push(Number(n[1])); }); }); return out; }catch(e){ return []; } }
async function claimedSet(){ var loc=[]; try{ loc=JSON.parse(lsGet(claimedKey())||lsGet("ld_claimed_days")||"[]"); }catch(e){} var on=await claimedOnChain(myAddr); var set={}; loc.concat(on).forEach(function(d){set[d]=1;}); var arr=Object.keys(set).map(Number); try{ lsSet(claimedKey(),JSON.stringify(arr.slice(-60))); }catch(e){} return arr; }
function saveClaimed(done){ try{ lsSet(claimedKey(),JSON.stringify(done.slice(-60))); }catch(e){} }
async function autoClaim(){ if(!window.LD||!myAddr)return; try{
  var h=await fetch(CFG.gw+"/v1/health").then(function(r){return r.json();});
  var done=await claimedSet();
  for(var d=h.current_day-1; d>=Math.max(1,h.current_day-7); d--){
    if(done.indexOf(d)>=0) continue;
    var rs=await fetch(CFG.gw+"/v1/day?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
    if(!rs||!rs.finalized) continue;
    if(d>=Math.floor((Date.now()/1000-1789102088)/86400)){ claimWindowUI(); continue; }
    var sc=await fetch(CFG.gw+"/v1/scores?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
    if(!sc||!sc.scores||!sc.scores[myAddr]||!(sc.scores[myAddr].w>0)) continue;
    var on=false; try{ on=await window.__mrq({root_submitted:{day:d}}); }catch(e){}
    if(!on) continue;
    try{ await window.LD.claim(d); done.push(d); saveClaimed(done); toast("✓ 已自动领取第 "+d+" 天奖励"); }catch(e){}
  }
 }catch(e){} }
setTimeout(function(){ document.documentElement.classList.remove("ld-restoring"); }, 8000);

function claimHintEl(){ var e=document.getElementById("claimHint"); if(!e){ e=document.createElement("div"); e.id="claimHint"; e.className="mini"; e.style.margin="6px 0 2px"; var b=document.getElementById("btnClaim"); if(b&&b.parentNode) b.parentNode.insertBefore(e,b); } return e; }
function claimWindowUI(){ var el=claimHintEl(); if(!el) return; var btn=document.getElementById("btnClaim");
  var cd=Math.floor((Date.now()/1000-1789102088)/86400);
  if(window.__claimOpen){ if(btn) btn.disabled=false; el.textContent=""; return; }
  var openAt=(cd+1)*86400+1789102088; var left=openAt-Math.floor(Date.now()/1000);
  function p(n){return (n<10?"0":"")+n;}
  if(window.__gwd && (window.__gwd-1)>=cd){ if(btn) btn.disabled=true;
    el.textContent="结算刷新:你当地 08:00(北京) · 领取开放:北京 12:48(合约日界,临时) · 倒计时 "+p(Math.floor(left/3600))+":"+p(Math.floor(left%3600/60))+":"+p(left%60)+" · 2026-10-11 起统一为北京 08:00";
  } else { if(btn) btn.disabled=true;
    el.textContent="昨日已定稿,等待验证者签根上链(通常北京 13:10–13:30),完成后自动可领;领取不会过期,7 天内随时可领,更早日可用『加载可领历史』。"; } }
setInterval(claimWindowUI,1000);
async function refreshClaimable(){ var el=document.getElementById("claimable"); if(!el||!myAddr||!window.__mrq)return;
 try{ var h=await fetch(CFG.gw+"/v1/health").then(function(r){return r.json();});
  var done=await claimedSet(); var sum=0;
  for(var d=h.current_day-1; d>=Math.max(1,h.current_day-7); d--){
   if(done.indexOf(d)>=0) continue;
   var rs=await fetch(CFG.gw+"/v1/day?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
   if(!rs||!rs.finalized) continue;
   var sc=await fetch(CFG.gw+"/v1/scores?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
   if(!sc||!sc.scores||!sc.scores[myAddr]||!(sc.scores[myAddr].w>0)||!sc.total) continue;
   var on=false; try{ on=await window.__mrq({root_submitted:{day:d}}); }catch(e){}
   if(!on) continue;
   var pl=await window.__mrq({daily_miner_pool:{day:d}});
   sum+=Number(pl)/1e6*sc.scores[myAddr].w/sc.total;
  }
  el.textContent=sum>0? sum.toLocaleString(undefined,{maximumFractionDigits:1}) : "0";
  window.__claimOpen = sum>0; window.__gwd = h.current_day; try{ claimWindowUI(); }catch(e){}
 }catch(e){} }
setInterval(refreshClaimable,60000);

(function(){ var el=document.getElementById("dayBnd"); if(!el) return; var nb=0,srv=0,loc=0;
 function p(n){return (n<10?"0":"")+n;}
 function cd(sec){ sec=Math.max(0,sec|0); return p((sec/3600)|0)+":"+p(((sec%3600)/60)|0)+":"+p(sec%60); }
 function tick(){ if(!nb||!srv) return; var elapsed=Date.now()/1000-loc; var left=Math.floor(nb-(srv+elapsed)); var d=new Date(nb*1000);
   var lt=d.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"}); var ld=d.toLocaleDateString([],{month:"2-digit",day:"2-digit"});
   el.textContent="每日结算刷新:你当地 "+ld+" "+lt+" · 倒计时 "+cd(left); }
 function pull(){ fetch(CFG.gw+"/v1/health").then(function(r){return r.json();}).then(function(hh){ if(hh&&hh.next_boundary_ts&&hh.now_ts){ nb=hh.next_boundary_ts; srv=hh.now_ts; loc=Date.now()/1000; tick(); } }).catch(function(){}); }
 pull(); setInterval(tick,1000); setInterval(pull,60000); })();
(function(){ /* LD-TRUTH-AUDIT-20261014: compare the semantic state the renderer wrote
   (data-st), not the visible words — the old version compared user-visible text against a
   hardcoded Chinese literal, so every localized visitor (and any stray whitespace in the
   build badge) reported a "mismatch" that did not exist: 106 bogus reports/hour from real
   browsers. A disagreement must survive two consecutive polls before it pages us. */
 function norm(x){ return String(x==null?"":x).replace(/[\s\u00a0\u200b\ufeff]+/g,"").toLowerCase(); }
 var badgeBad=0, statusBad=0;
 function audit(){ try{
   var bb=document.getElementById("ld-build");
   if(bb){ if(norm(bb.textContent)!==norm(window.LDBUILD)){ badgeBad++; if(badgeBad===2){ window.__ldReport && window.__ldReport("truth-mismatch badge="+norm(bb.textContent)+" vs "+norm(window.LDBUILD)); } } else badgeBad=0; }
   fetch("/status.json?ts="+Date.now(),{cache:"no-store"}).then(function(r){return r.json();}).then(function(j){
     var st=document.getElementById("sysStatusApp"); if(!st) return;
     var want = j.ok ? "1" : "0";
     var have = st.getAttribute("data-st");
     if(have===null) return;                       /* renderer never ran: nothing to cross-check */
     if(have!==want){ statusBad++; if(statusBad===2){ window.__ldReport && window.__ldReport("truth-mismatch status=shown:"+norm(st.textContent)+" data-st:"+have+" want:"+want); } }
     else statusBad=0;
   }).catch(function(){});
 }catch(e){} }
 setTimeout(audit,5000); setInterval(audit,60000); })();


/* ===== wallet features: send/delegate (merged for qa_extra scan) ===== */
// wallet_features.js — Transfer + Delegate UI wiring. Loaded after app_2 (LD API) before app_3.
(function(){
  function t(k){ // zh-only mini i18n (fallback to key)
    return {send:"转账", delegate:"委托", undelegate:"解除委托"}[k]||k;
  }
  async function ensureLD(){ return window.LD && window.LD.addr; }

  // validator list for delegate dropdown
  async function loadValidators(){
    var sel = document.getElementById('delVal'); if(!sel) return;
    try {
      var m = await import("/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2").catch(function(){return null;});
      var c = await m.CosmWasmClient.connect("https://lightdao.net/rpc/");
      var vals = await c.getValidators();
      sel.innerHTML = "";
      (vals||[]).forEach(function(v){
        var o = document.createElement("option");
        o.value = v.operatorAddress;
        o.textContent = (v.description && v.description.moniker ? v.description.moniker : v.operatorAddress.slice(0,20)) + " · " + (v.tokens/1e6).toFixed(0) + "L";
        sel.appendChild(o);
      });
      var info = document.getElementById('delInfo');
      if(info) info.textContent = "委托后可随时解除(解绑期约21天),收益自动累积,用上方「一键领取验证者/质押收益」提取。";
    } catch(e) {
      sel.innerHTML = "<option>加载验证者失败</option>";
    }
  }

  // send
  var btnSend = document.getElementById('btnSend');
  if(btnSend) btnSend.onclick = async function(){
    if(!await ensureLD()){ toast("请先登录钱包"); return; }
    var to = document.getElementById('sendTo').value.trim();
    var amt = parseFloat(document.getElementById('sendAmt').value);
    if(!to || !to.startsWith("wasm1") || to.length < 40){ toast("收款地址无效"); return; }
    if(!(amt > 0)){ toast("金额无效"); return; }
    if(amt > 500000 && !confirm("⚠ 大额转账: " + amt + " LIGHT\n至 " + to + "\n\n请再次核对地址!确认继续?")) return;
    if(!confirm("确认转账 " + amt + " LIGHT 至\\n" + to + " ?\\n转账不可撤销。")) return;
    try {
      var r = await window.LD.sendTokens(to, Math.round(amt*1e6), "转账");
      toast("已提交,等待链上确认...");
      if(r && r.transactionHash){ toast("✓ 转账成功 " + r.transactionHash.slice(0,10)); setTimeout(function(){ location.reload(); }, 2000); }
    } catch(e){ toast("转账失败: " + (e.message||e).toString().slice(0,120)); }
  };

  // delegate / undelegate
  var btnDel = document.getElementById('btnDelegate');
  var btnUndel = document.getElementById('btnUndelegate');
  async function doDelegate(un){
    if(!await ensureLD()){ toast("请先登录钱包"); return; }
    var sel = document.getElementById('delVal');
    var amt = parseFloat(document.getElementById('delAmt').value);
    var val = sel && sel.value;
    if(!val || !val.startsWith("wasmvaloper")){ toast("请选择验证者"); return; }
    if(!(amt > 0)){ toast("金额无效"); return; }
    if(!confirm("确认" + (un?"解除委托":"委托") + " " + amt + " LIGHT 给 " + val.slice(0,20) + "... ?")) return;
    try {
      var fn = un ? window.LD.undelegate : window.LD.delegate;
      var r = await fn(val, Math.round(amt*1e6));
      toast((un?"解除委托":"委托") + "已提交,等待确认...");
      if(r && r.transactionHash) toast("✓ 成功 " + r.transactionHash.slice(0,10));
    } catch(e){ toast("失败: " + (e.message||e).toString().slice(0,120)); }
  }
  if(btnDel) btnDel.onclick = function(){ doDelegate(false); };
  if(btnUndel) btnUndel.onclick = function(){ doDelegate(true); };

  // init when wallet ready (app_3 sets myAddr on enter)
  var tries = 0;
  var iv = setInterval(function(){
    tries++;
    if(window.LD && window.LD.addr){ clearInterval(iv); loadValidators(); }
    if(tries > 60) clearInterval(iv); // 30s give up
  }, 500);
})();
