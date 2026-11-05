> Otomatik çeviri, insan tarafından gözden geçirilmedi. Anlaşmazlık durumunda Çinçe orijinal metin esas alınır.
[中文原文 / Chinese original](/whitepaper.md)

# LightDAO Teknik İncelemesi V2.4 (2026-09-26 Mainnet Canlı Sürümü)

> Bu sürüm, önde "ana ağ dağıtımı canlı" ve "sürüm değişiklikleri" bulunan V2.0 tasarım taslağını temel alır ve doğrulanmış zincir içi parametrelerle eklenir. Ana metin (Bölüm 1~12) V2.0 tasarımına göre değişmeden kalır; Fiili durumdan herhangi bir sapma durumunda, bu bölümün önceki notları ve ekleri geçerli olacaktır.

## 版本变更(V2.0 → V2.4)
- 2026-11-04 勘误（不改版本号，仍为 V2.4）：附录《主网已验证参数与地址》原写金库 `treasury_multisig` 为 5/7 多签，与正文 §7.2/§7.3/§8.1 的 3/5 冲突，也与链上实测冲突（`{"signers":{}}` 返回 5 个地址，不存在 7 名签名人）；已按正文统一为 3/5，并标明阈值本身不在合约查询接口内、只能由部署记录佐证。同节原写挖矿根为「5/7 验证者多签」，实测可证的只有阈值 5（115 笔 `submit_root` 事件 threshold 全部为 5，实际签名账户恰好 5 个），7 席授权是设计目标、当前无链上证据，已改为相应措辞。

1. **§4.5 Gas 经济:已主网部署并验证**。USD 锚定动态 min-gas-price 与 50% 销毁 / 30% 验证者 / 20% 金库分配于 2026-09-24 经治理提案(v2-lightfee)在高度 58627 上线,7 验证者协调切换、测试网端到端彩排后执行。主网实测:不足额 fee 被拒、足额 fee 按 50/30/20 精确分配。
2. **原生 denom 厘清**:质押/治理/Gas 均为 `ulight`(LIGHT,6 位小数,总供应 25 亿)。genesis 误配的 `stake` 通胀已于 2026-09-24 经治理提案归零(mint inflation=0),LIGHT 发行完全由 mining_reward 合约承担,杜绝双重发行;存量 stake 为待处置的遗留 denom(见附录 C)。
3. **§4.7 WebRTC 中继:已部署**。8 节点 coturn(TURN/STUN,TLS 证书 turn-*.lightdao.net)+ WSS 信令 + REST 临时凭证(HMAC-SHA1);客户端 P2P 数据通道互中继,中继字节计入 40% 带宽贡献;端到端实测经 TURN 中继传输成功。对称 NAT 走 TURN 兜底,失败降级纯验证模式(与 §4.7 一致)。
4. **§4.9 智能钱包:已上线**。Passkey/WebAuthn 无种子登录(PRF 派生密钥 + AES-GCM 密文存储,明文不落地)+ Shamir 3-of-5 社交恢复;助记词作为回退选项保留。
5. **§4.10 价格预言机:喂价已运行**。7 验证者 cron 轮值向 oracle_twap 提交 external_median(当前参考价 50000 = $0.05);链上 TWAP 待 LIGHT/USDC 流动性池建立后启用。v3 升级后 lightfee 直接读 external_median 转动态 min-gas。
6. **参数治理**:v3 升级将 lightfee 的 BurnPct/TreasuryPct/TransferUsd/StaticPrice/OracleContract 迁入链上 paramstore,治理参数提案可运行时调整,无需再协调升级。

## Ana ağ dağıtımı yayında (2026-09-26)

- 链 `lightdao-mainnet-1`,7 验证者(JP/KR/SG/US/HK/FR/UK)全部 BONDED、无 jailed;满足 §4.7「验证者<7 不得 TGE」的硬性底线
- 客户端 https://lightdao.net(PWA):Passkey 钱包 + 挖矿 + WebRTC 中继 + 领取,多语言(中/英/西)
- 挖矿闭环:浏览器贡献 → 网关每日定稿 → Merkle 根 5 签上链(阈值 5,链上可查) → 矿工凭 proof 领取;每日根持续提交
- 升级治理:v2-lightfee(已应用 @58627)、mint 归零(已应用)、v3-lightfee(全票通过,高度 118055 自动切换)
- 完整端点/合约地址/升级历史见仓库 `docs/MAINNET_STATUS.md`

---

#LightDAO Teknik Raporu V2.0

**Tam metin doğrulama ve redaksiyon için optimize edilmiş sürüm (uluslararası web istemcisi · sayısal denetim · üçüncü taraf denetimi · ekonomik model için optimize edilmiş sürüm) **

Yayın tarihi: 4 Ağustos 2026

Temel prensip: Tarayıcılar düğümlerdir, herkes katılabilir ve kar kurallara göre paylaşılır

Yasal konumlandırma: LIGHT ve alt tokenler, ekolojik katkı noktaları ve SPV gelir dağılımı talep hakları sertifikaları olarak konumlandırılmıştır ve menkul kıymet veya finansal ürün değildir; Belirli yasal nitelikler, ilgili yargı bölgelerindeki geçerli yasal görüşlere tabidir.

> Bu belge, teknik incelemenin tam metninin doğrulanmış ve optimize edilmiş bir versiyonudur ve yatırım tavsiyesi, menkul kıymet ihraç belgeleri, finansal ürün açıklamaları veya herhangi bir tür sermaye garantisi taahhüdü teşkil etmez. Lütfen katılmadan önce hukuk, vergi ve finans uzmanlarına danışın.

---

## İçindekiler

- Ön beyan
- Giriş: Üç kişinin hikayesi
- Bölüm 1: Gördüğümüz gerçek
- Bölüm 2: LightDAO'nun yanıtı
- Bölüm 3: Uyumluluk ve yasal izolasyon
- Bölüm 4: Teknik Mimari
- Bölüm 5: Token Ekonomik Modeli
- Bölüm 6: Yönetişim Mekanizması
- Bölüm 7: Güç kontrolleri ve dengeleri ve rol tanımı
- Bölüm 8: Güven ve Güvenlik Mekanizması
- Bölüm 9: Yatırım operasyonları ve çıkış stratejileri
- Bölüm 10: Yol Haritası
- Bölüm 11: Topluluk kültürü ve geliştirici ekolojisi
- Bölüm 12: Ekip ve Danışmanlar
- Bölüm 13: Risk Uyarısı ve Sorumluluk Reddi
- Ek A: Temel parametrelerin özet tablosu
- Ek B: Sayısal türetme ve doğrulama
- Ek C: Denetim Düzeltme Günlüğü
- Ek D: Hızlı Referans Terimler Dizini

---

## Yönetici Özeti

**LightDAO nedir:** Dünyanın her yerindeki sıradan insanların bir tarayıcı aracılığıyla gerçek ticari yatırımlara katılmasına ve karları paylaşmasına olanak tanıyan, merkezi olmayan, özerk bir kuruluş. Kullanıcıların bir madencilik makinesi satın almasına, teknik bir altyapıya sahip olmasına veya nitelikli yatırımcı eşiğini karşılamasına gerek yok; yalnızca bir tarayıcı ve az bir süre ile kullanıcılar, LIGHT token ödülleri almak için ağ kaynaklarına katkıda bulunabilir ve yönetişim oylaması yoluyla yatırım kararlarına katılabilir.

**Hangi sorun çözüldü:** Küresel nüfusun en alttaki %50'si (yaklaşık 4 milyar insan) toplam servetin yalnızca %2'sine sahip (World Inequality Lab, 2026). Yüksek kaliteli varlıklar (özel sermaye, risk sermayesi) nitelikli yatırımcı eşiğinin (200.000 $ yıllık gelir/1 milyon $ net değer) kapsamı dışındadır. Kripto para alanında bir "evrensel katılım" anlatısı olsa da tokenların büyük çoğunluğu sonunda sıfıra dönüyor (CoinGecko 2025: 11,56 milyon token öldü) ve DAO yönetişim katılım oranı yalnızca %3-12 civarında.

**Nasıl çözülür:** Çift motorlu model - Fonların %70'i topluluk düzeyindeki katı tüketici varlıklarına (nakit akışı motoru) ve %30'u son teknolojiye (büyüme motoru) yatırılır. Yatırımlar Cayman SPV aracılığıyla gerçekleştirilir ve karlar zincir içi kurallara göre dağıtılır: %40'ı alt token sahiplerine, %30'u yeniden yatırım için kasaya geri döner, %20'si imha için LIGHT geri satın alınır ve %10'u sigorta fonlarına tahakkuk ettirilir.

**Temel Veriler:**

| Göstergeler | Değerler |
|------|------|
| Toplam LIGHT miktarı | 2,5 milyar asla verilmeyecek |
| Yatırım Kasası | 850 milyon (temel konuşlandırılabilirlik ≈ 100 milyon dolar) |
| Madencilik çıktısı | 1 milyar, her 2 yılda bir yarıya indi |
| İlk Çağ Gününde Yayınlandı | ≈684.900 parça (100.000 madenci çalışırken ortalama 6,51/gün) |
| Deflasyon için sonuç | Dolaşım ≤ 1 milyar olduğunda yanmayı kalıcı olarak durdurun (temel senaryonun 11-12 yılları) |
| Yönetişim Eşiği | Teklif ≥ 5.000 IŞIK; Komite ≥ 50.000 IŞIK |
| Teknoloji Yığını | Cosmos SDK + Tendermint PoS + CosmWasm + PWA |
| Doğrulayıcılar | Başlangıç ​​21 (minimum 10), üst sınır 100 |
| İlk finansman | Hollanda açık artırması 15 milyon $ + TGE öncesi stratejik finansman 2,25-3,75 milyon $ |

**Farklılaşma:** Şu ​​anda "sıfır eşikli web madenciliği"ni "uyumlu SPV varlık yatırımı" ile birleştiren tek proje. Pi Network'ten (pratik bir yardımcı program yok), Helium'dan (200 $'dan fazla donanım gerektirir) ve geleneksel DAO'dan (yüksek eşikli elit yönetişim) farklıdır.

**Yol haritası:** 2026 4. Çeyrek hazırlığı → 2027 1. Çeyrek-2. Çeyrek geliştirme → 3. Çeyrek denetim testi → 4. Çeyrek TGE çevrimiçi → 2028 1. Çeyrek tohum kullanıcıları → 2. Çeyrek-3. Çeyrek ilk yatırım → 4. Çeyrek sonrası ölçek.

---

## Ön beyan

**Bu bir yatırım teklifi değildir**

Bu teknik incelemede açıklanan "ekolojik ödüller" ve "anlaşma gelir dağılımı", anlaşmanın içsel mekanizması tarafından oluşturulan teşvik düzenlemeleridir ve herhangi bir menkul kıymet ihracı, finansal ürün satışı, sermaye garantisi taahhüdü veya yatırım tavsiyesi teşkil etmez.

LIGHT ve alt tokenlerin hiçbir içsel değeri yoktur ve fiyat sıfıra dönebilir. Katılmadan önce lütfen kendi hukuk, vergi ve finans uzmanlarınıza danışın ve özel anahtar saklama, vergi beyanı ve katılım konusunda tüm sorumluluğu üstlenin.

---

## Giriş: Üç kişinin hikayesi

Maria, Manila'da yemek dağıtım görevlisi olarak çalışıyor, günde 12 saat çalışıyor ve ayda yaklaşık 15.000 Filipin Pesosu (yaklaşık 270 ABD Doları) kazanıyor. Yan taraftaki popüler sütlü çay zinciri markasına yatırım yapmak istedi ancak karşı taraf ona şunu söyledi: "Minimum yatırım 25.000 ABD Dolarından başlıyor." Maria 25.000 ABD dolarını bulamadı.

Kwame, Lagos'ta araç çağırma hizmeti veriyor. Yapay zeka konusunda iyimser ve küçük bir finansal teknoloji şirketine yatırım yapmak istiyor. Kurum ona şunları söyledi: "Minimum abonelik tutarı 100.000 ABD Doları ve kilitlenme süresi 5 yıldır." Kwame 100.000 ABD dolarını bulamadı.

Elena, São Paulo'da emekli bir öğretmendir ve aylık maaşı yaklaşık 3.000 Brezilya realidir (yaklaşık 550 ABD Doları). Komşusunun çocuklarının blockchain şirketlerinde çalışarak para kazandığını duymuştu ancak teknik incelemeyi okuyamıyordu ve profesyonel madencilik ekipmanlarını nasıl satın alıp yapılandıracağını bilmiyordu.

Üçü dünya çapındaki sıradan insanların büyük çoğunluğunu temsil ediyor: Katılma kararları ve istekleri var ancak düşük eşikli, şeffaf ve uygun maliyetli katılım kanallarından yoksunlar.

LightDAO bu insanlar için tasarlanmıştır. İnternet özellikli bir cihaz, bir tarayıcı ve küçük bir miktar parayla ekolojik inşaata katılabilirsiniz; Uyumlu bir SPV yapısı aracılığıyla kullanıcılar aynı zamanda yüksek kaliteli şirketlerin nakit akışı dağılımına ve ileri teknoloji projelerinin erken büyümesine dolaylı olarak erişme fırsatına da sahip oluyor.

---

## Bölüm 1: Gördüğümüz gerçek

### 1.1 Küresel zenginliğin dengesiz dağılımı

Dünya Eşitsizlik Laboratuvarı'nın 2026 Dünya Eşitsizlik Raporu'na (bundan böyle "Rapor" olarak anılacaktır) göre:

| Veri | Kaynak |
|------|------|
| Dünya nüfusunun en zengin %0,001'inin (yaklaşık 60.000 kişi) sahip olduğu servet, nüfusun en alttaki %50'sinin (yaklaşık 4 milyar kişi) toplam servetinin yaklaşık üç katıdır | Dünya Eşitsizlik Laboratuvarı, 2026 |
| Dünya nüfusunun en tepedeki %1'i toplam gelirin %23'ünü ve toplam servetin %38'ini kontrol ediyor | Dünya Eşitsizlik Laboratuvarı, 2026 |
| Dünya nüfusunun en tepedeki %10'u toplam gelirin %53'ünü ve toplam servetin %75'ini kontrol ediyor | Dünya Eşitsizlik Laboratuvarı, 2026 |
| Küresel nüfusun en alttaki %50'si toplam gelirin yalnızca %8'ini ve toplam servetin %2'sini alıyor | Dünya Eşitsizlik Laboratuvarı, 2026 |

"Rapor" şunu belirtiyor: "Küresel eşitsizlik tarihsel olarak aşırı düzeylerde kalıyor. Eşitsizlik sadece piyasanın doğal işleyişinden kaynaklanmıyor, aynı zamanda politika tercihlerini, kurumsal yapıları ve ekonomik ve politik gücün eşitsiz dağılımını da yansıtıyor."

**Kaynak Notu:** Yukarıdaki veriler Dünya Eşitsizlik Laboratuvarı'nın 2026 Dünya Eşitsizlik Raporu'ndan alıntıdır. Rapor Lucas Chancel, Ricardo Gómez-Carrera, Rowaida Moshrif ve Thomas Piketty tarafından yönetildi (wid.world resmi web sitesi tarafından onaylandı). Resmi yayınlanmadan önce, ikincil çevirideki olası hataları azaltmak için rapordaki belirli grafik numaralarının ayrıca işaretlenmesi önerilir.

**Veri tutarlılığı kontrolü:** Yukarıdaki oranlar, 2022 Dünya Eşitsizlik Raporu'nun (en üstteki %10'un toplam servetin %76'sına, en alttaki %50'nin toplam servetin %2'sine sahip olması) sonucuna göre makul bir trendde devam ettiğini ve sapmanın istatistiksel olarak kabul edilebilir aralıkta olduğunu görüyoruz.

### 1.2 Sıradan insanlar yüksek kaliteli varlıklardan dışlanır

Büyük küresel yargı bölgelerinde özel sermaye ve risk sermayesi için katı nitelikli yatırımcı eşikleri vardır:

**Amerika Birleşik Devletleri (SEC Düzenlemesi D, Kural 501, 17 CFR §230.501):** Nitelikli yatırımcılar (Akredite Yatırımcılar) aşağıdaki koşullardan birini karşılamalıdır - bireyin yıllık geliri 200.000 ABD Dolarından az olmamalıdır (veya eşiyle birlikte toplam 300.000 ABD Dolarından az olmamalıdır) ve art arda iki yıl boyunca standardı karşılamış olmalıdır; veya net servetin (birincil ikamet yeri hariç) 1.000.000 ABD Dolarından az olmaması.

**AB (MiFID II, 2014/65/AB, Ek II):** Profesyonel yatırımcılar (Profesyonel Yatırımcılar) aşağıdaki koşullardan en az ikisini karşılamalıdır: 500.000 Euro'dan az olmayan bir finansal araç yatırım portföyü; finans sektöründe en az bir yıl süreyle profesyonel bir pozisyonda bulunmak; üç ayda bir 10'dan az olmamak üzere büyük ölçekli işlemlerin gerçekleştirilmesi.

**Küresel Özel Sermaye Fonu Uygulaması:** Tek bir fon için minimum abonelik tutarı genellikle 250.000 ABD Doları ile 1.000.000 ABD Doları arasındadır; Düzenleyici kurallar genellikle "hisseleri bölmek, eşikleri düşürmek ve başkaları adına emir tutmak" gibi kaçamak davranışları yasaklar.

| Varlık türleri | Sıradan insanlar katılabilir mi | Ana nedenler |
|----------|---------------|----------|
| Borsada işlem görmeyen yüksek kaliteli şirketlerde özsermaye | Genellikle yapılamaz | Nitelikli yatırımcılar için eşik daha yüksektir; örneğin, Amerika Birleşik Devletleri'nde net değerin 1 milyon ABD Dolarından az olmaması veya yıllık gelirin 200.000 ABD Dolarından az olmaması gerekmektedir |
| Risk sermayesi (erken aşama teknoloji şirketleri) | Genellikle hayır | Çoğunlukla nitelikli yatırımcılara açık olan tek bir fonun yatırım tutarı genellikle 250.000 ABD Dolarından az değildir |
| Listelenen şirket hisseleri | Evet, ancak erken karlar genellikle birincil piyasa katılımcıları tarafından elde ediliyor | İkincil piyasa fiyatlandırması genellikle geleceğe yönelik beklentileri içerir ve yatırımcılar şirketin erken kar dağıtımına doğrudan katılmaz |

### 1.3 Kripto para birimi alanındaki üç büyük kusur

**Kusur 1: Son derece yüksek başarısızlık oranı**

CoinGecko'nun 2025 yıllık istatistik raporuna göre, yaklaşık **11,56 milyon token** yalnızca 2025'te sıfıra dönecek veya ticareti duracak (her zincirdeki uzun kuyruklu tokenlar dahil). CoinGecko'nun tarihsel olarak takip ettiği 20 milyondan fazla tokenin büyük çoğunluğu "ölü" durumda (ticaret hacmi yok, geliştirme faaliyeti yok ve fiyatlar tarihi en yüksek seviyelere göre %99'dan fazla düştü).

Aynı zamanda geleneksel borsaların başarısızlık oranı kripto para birimlerine göre çok daha düşüktür. Bessembinder'in (2018) "Hisse Senetleri Hazine Bonosundan Daha İyi Performans Gösteriyor mu?" başlıklı makalesine göre. 1926'dan 2016'ya kadar tüm ABD hisse senetlerini kapsayan bir çalışma olan "Journal of Financial Economics"te yayınlandı:

| Metrikler | Veri | Kaynaklar |
|------|------|------|
| Toplam net zenginlik yaratan hisse senetlerinin oranı | Sadece yaklaşık %4 (1.092 hisse senedi) | Bessembinder (2018), JFE 129(3):440-475 |
| Ortalama hisse senedinin ömür boyu getirisi | Negatif (Hazine bonolarının performansı düşük) | Bessembinder (2018), JFE |
| ABD hisse senetlerinin ömür boyu performansının yaklaşık %58'i | Aynı dönemde düşük performans gösteren Hazine bonoları | Bessembinder (2018), JFE |
| 2025'te sıfırlanacak/ticareti durduracak token sayısı | ≈11,56 milyon | CoinGecko 2025 Yıllık Raporu |

**Karşılaştırmalı Sonuç:** Kripto para alanındaki kalıcı sermaye kaybı oranı, geleneksel borsaya göre çok daha yüksektir. ABD borsasındaki bireysel hisse senetlerinin yaklaşık %58'i Hazine bonolarının altında performans gösterse de, yatırımcılar yine de endeks fonları aracılığıyla ortalama piyasa getirisi elde edebiliyor; Kripto para piyasasında, tokenlerin büyük çoğunluğu sıfıra dönüyor ve "indekslere" benzer etkili çeşitlendirme araçlarının eksikliği var.

**Kaynak beyanı:** Bessembinder, H. (2018). "Hisse Senetleri Hazine Bonosundan Daha İyi Performans Gösteriyor mu?" *Finansal Ekonomi Dergisi*, 129(3), 440-475. Arizona Eyalet Üniversitesi. Bu makale, finans alanında oldukça fazla alıntı yapılan bir belgedir (alıntı >2.000) ve veriler, CRSP veritabanındaki 1926'dan 2016'ya kadar tüm ABD hisse senetlerini kapsamaktadır. CoinGecko'nun verileri, birçok finansal medya (Sina Finance, Phemex, RBC Crypto) tarafından rapor edilen 2025 Token Hayatta Kalma Durumu İstatistik Raporundan (Ocak 2026'da yayınlandı) gelmektedir.

**Kusur 2: Madencilik oldukça merkezileştirilmiştir**

Bitcoin madenciliği yüksek derecede konsantrasyon göstermiştir:

| Madencilik havuzu | Karma oranı oranı |
|------|---------|
| Dökümhane ABD | Yaklaşık %30 |
| Karınca Havuzu | Yaklaşık %19 |
| BTC aracılığıyla | Yaklaşık %14,5 |
| F2Havuzu | Yaklaşık %10 |
| MARA Havuzu | Yaklaşık %5 |
| En iyi iki madencilik havuzu birleştirildi | %50'den fazlası |
| En iyi dört madencilik havuzu birleştirildi | Yaklaşık %75 |

**Kaynak Notu:** Yukarıdaki veriler 2025 yılının aylık hashrate dağıtım raporundan derlenmiştir (CoinGradient 2025.3 "Foundry, Antpool ve Viabtc Dominate Bitcoin Mining"; HashrateIndex "2025'in En İyi 10 Bitcoin Madencilik Havuzu"). Farklı veri kaynaklarından alınan spesifik değerler biraz farklılık gösterebilir (genellikle ±%2 dahilinde), ancak "en büyük dört madencilik havuzunun bilgi işlem gücünün yaklaşık %75'ini kontrol ettiği" sonucu, birden fazla ana akım izleme platformuna yansıtılmaktadır.

**Kusur 3: DAO yönetişimine katılım oranı son derece düşük**

| Veri | Kaynak |
|------|------|
| Çoğu DAO'nun oylamaya katılım oranı yalnızca %3-%12 civarındadır (ortalama %6 civarındadır) | DeepDAO (2025) Zincir içi yönetişim veri toplama; Toplantı Odası DAO Yönetişim Raporu (2024) |
| Az sayıda para sahibi, oy haklarının büyük çoğunluğunu kontrol ediyor (yönetişim gücünün yüksek yoğunlaşması) | ACM (2024) "DAO Yönetişimi: Oylama Gücü, Katılım ve Tartışma" DOI:10.1145/3777416 |

### 1.4 Temel Bilgiler

Yargım var ama giriş biletim yok; Vizyonum var ama konuşmaya hakkım yok; Katılmak istiyorum ama yüksek eşikler beni engelliyor.

---

## Bölüm 2: LightDAO'nun yanıtı

### 2.1 Çekirdek konumlandırma

LightDAO, zincir üstü yönetime ve yatırım yürütme taşıyıcısı olarak uyumluluk SPV'sine sahip ulusal bir yatırım özerk kuruluşudur. Hafif web düğümleri için özel olarak tasarlanmış halka açık bir zincir aracılığıyla, küresel kullanıcılar tek bir tarayıcıyla ağ bakımına, yönetişim oylamasına katılabilir ve kurallara göre ekolojik faydaları paylaşabilir.

### 2.2 Çift motorlu model

| Motor | Yatırım Yönü | Hedef | Gelir Özellikleri |
|------|---------|------|---------|
| Birinci Motor: Nakit Akışı Motoru (Shou) | Topluluk düzeyinde katı tüketim hizmeti varlıkları | Sürekli nakit akışı oluşturun ve kârı kurallara göre dağıtın | Göreceli istikrarın peşinde olun ancak sabit gelir sözü vermeyin |
| Motor 2: Büyüme motoru (saldırı) | Son teknoloji şirketleri | Özsermaye değer artışı ve çıkış getirileri elde edin | Esneklik potansiyeli yüksek ancak aynı zamanda kayıplarla veya çıkış başarısızlığıyla da karşılaşılabilir |

**Tahsis disiplini:** Prensip olarak fonların %70'ini istikrarlı nakit akışına sahip varlıklara, %30'unu ise yüksek büyüme hedeflerine ayırmak.

**Yatırım ölçeği büyüme yolu:** Tek bir yatırımın boyutu, LIGHT fiyatı ve kasa kapasitesiyle dinamik olarak büyür - başlangıç ​​dönemi (LIGHT 0,02 - 0,05 ABD Doları), topluluk düzeyinde 2,55 milyon ABD Doları - 6,37 milyon ABD Doları arasındaki küçük varlıklar için uygundur; büyüme aşaması (0,05-0,30 dolar) bölgesel zincirlere ve 6,37 milyon dolar-38,25 milyon dolarlık (Aşağı Orta Pazar kıyaslaması) PE'deki Tohum-A turlarına giriyor; olgun aşamada (0,30$-1,00$), 38,25 milyon $ ile 127,5 milyon $ arasındaki orta piyasa PE seviyesine ulaşır; ölçek aşamasında (1,00 $+), büyük ölçekli satın almalar ve 127,5 milyon $'ın üzerinde halka arz öncesi yatırımlar gerçekleştirebilir. Katı kısıtlamalar: tek bir işlem, yatırım hazinesinin kalan miktarının %15'ini geçmeyecektir (ayrıntılar için Bölüm 9'a bakınız).

**İlk hedef konumlandırma ilkesi:** Belirli bir şirket adını varsaymak yerine, öncelikle bir tarama çerçevesi oluşturun - kanıtlanmış bir tek mağazalı ekonomik model, istikrarlı nakit akışı kayıtları (son üç yıldaki FAVÖK marjı %10'dan az değildir ve yıllar arası oynaklık %15'ten yüksek değildir) ve net bir bölgesel genişleme yolu gerektiren topluluk düzeyinde katı tüketici hizmetleri varlıklarına öncelik verin. Spesifik hedef topluluk önerileriyle belirlenir.

### 2.3 Temel değer önerisi

**Tarayıcı düğümdür** - Bir madencilik makinesi satın almanıza veya profesyonel bir teknik altyapıya sahip olmanıza gerek yoktur. Resmi web platformunu ziyaret ederek ağ katkılarına katılabilirsiniz.

**Herkes katılabilir** - Yönetişim eşiğine ulaştıktan sonra, küçük miktarda LIGHT sahipleri de fon tahsisinin yönüne ortaklaşa karar vermek için oylamaya katılabilir.

**Kurallara uygun kar paylaşımı** - Yatırım yapılan şirketlerin faaliyet karları ve teknoloji projelerinin çıkış getirileri, zincir içi kurallara ve SPV düzenlemelerine uygun olarak dağıtılacaktır.

### 2.4 Slogan

"Tarayıcınız aynı zamanda yüksek kaliteli varlıklara giriş de olabilir."

### 2.5 Rekabetçi ürün farklılaştırma analizi

| Boyut | Pi Ağı | Helyum | Geleneksel DAO (MakerDAO vb.) | IşıkDAO |
|------|-----------|----------|----------|----------|
| Katılım yöntemi | Mobil uygulamaya tıklayın | Donanım erişim noktası satın alın (200-1000$) | Token satın alma + zincir üstü işlem | Tarayıcı erişimi, sıfır donanım maliyeti |
| Giriş maliyeti | Sıfır (ancak pratik bir faydası yok) | Yüksek (donanım + kurulum) | Orta ila yüksek (yönetim tokenleri satın alınması gerekiyor) | Sıfır (yalnızca bir tarayıcı) |
| Toplam jeton miktarı | 100 milyar | 223 milyon | Değişir | 2,5 milyar |
| Gerçek yatırım fonksiyonu | Yok | Yok (yalnızca ağ kapsama alanı) | Evet (ancak eşik son derece yüksektir) | Evet (SPV yapısı, herkes katılabilir) |
| Gelir kaynağı | Belirsiz | Ağ kullanım ücreti | Sözleşme ücreti | Kurumsal kâr + çıkış getirisi + Gaz ücreti |
| Yasal izolasyon | Yok | Yok | Bazıları evet | Cayman SPV+ZK-KYC |
| Yönetişim katılım oranı | Son derece düşük (önemli bir yönetim yok) | Düşük | Yaklaşık %6 | Hedef >%15 (çift boyutlu oylama + teşvikler) |

**LightDAO'nun temel farkı:** Şu ​​anda "sıfır eşikli web madenciliği" ile "uyumlu SPV varlık yatırımı"nı birleştiren tek projedir. Kullanıcılar yalnızca token ödülleri elde etmek için ağ kaynaklarına katkıda bulunmakla kalmıyor, aynı zamanda yönetişim oylaması yoluyla gerçek kurumsal yatırım kararlarına doğrudan katılıyor ve işletme karlarını paylaşıyor.

> **[Bu bölümdeki terminoloji]**
> **DAO** (Merkezi Olmayan Özerk Organizasyon): Yönetişim kurallarının akıllı sözleşmeler yoluyla kodlandığı ve kolektif kararların token sahipleri tarafından alındığı organizasyonel bir form. Geleneksel bir şirket hiyerarşisi yoktur.
> **SPV** (Özel Amaçlı Araç): Risk izolasyonunu sağlamak amacıyla belirli işlemler veya yatırımlar için kurulmuş bağımsız bir tüzel kişilik (genellikle Cayman Adaları'nda kayıtlıdır). SPV'nin borçları ve yasal yükümlülükleri DAO'nun kendisine aktarılmaz.
> **DePIN** (Merkezi Olmayan Fiziksel Altyapı Ağı, merkezi olmayan fiziksel altyapı ağı): Kullanıcıları altyapı oluşturmak için fiziksel kaynaklara (bant genişliği, depolama, bilgi işlem gücü, kablosuz kapsama alanı vb.) katkıda bulunmaya teşvik etmek için belirteçleri kullanan bir ağ modeli.
> **Aşağı Orta Piyasa PE** (alt orta sınıf özel sermaye): küresel özel sermaye sektörünün bir pazar segmenti. Tek bir işlemin boyutu genellikle 10 milyon ila 100 milyon dolar arasındadır ve hedef şirketin FAVÖK'ü 2 milyon ila 15 milyon dolar arasındadır.

---

## Bölüm 3: Uyumluluk ve yasal izolasyon

### 3.1 SPV yasal izolasyon katmanı

DAO herhangi bir fiziksel kuruluşta doğrudan öz sermayeye sahip değildir. Tüm dış yatırımlar Cayman Adaları'nda kurulan özel amaçlı araçlar (SPV'ler) aracılığıyla gerçekleştirilmektedir.

| Tasarım Noktaları | Açıklama |
|-----------|------|
| SPV Şartı | SPV'nin operasyonunun DAO'nun etkin çözümüne uygun olacağı açıkça kabul edilmiştir |
| Alt belirteçlerin yasal tanımı | Alt tokenler, yalnızca gelecekteki nakit akışına ilişkin dağıtım niteliklerini temsil eden "SPV gelir dağıtımı talep hakları sertifikalarıdır" |
| Hissedar hakları taşımamaktadır | Kurumsal yönetim hakları, tasfiye imtiyazları veya herhangi bir hissedar hakkı taşımamaktadır |
| SPV yöneticileri | bağımsız üçüncü şahıslar tarafından hizmet verilmektedir; DAO geçerli bir karar alarak yöneticileri değiştirebilir |
| Fon denetimi | Banka hesapları lisanslı saklama kurumları tarafından denetlenmektedir ve fon transferlerinin çoklu imza ve uyumluluk doğrulamasından geçmesi gerekmektedir |
| SPV anlaşmazlık çözümü | SPV tüzüğü bir tahkim şartı (SIAC veya ICC) şart koşar ve DAO, bir yönetim kararı aracılığıyla tahkim işlemlerini başlatabilir |

### 3.2 İsteğe bağlı doğrulama ve gizlilik koruması

**Protokole katılmak için herhangi bir kimlik gerekmemektedir. ** Web sayfalarını ziyaret edin, cüzdanlar oluşturun, kaynaklara katkıda bulunun, LIGHT alın, yönetim oylamasını başlatın ve oylamaya katılın - tüm süreç boyunca belge yüklemeye gerek yoktur ve zincirde hiçbir kişisel tanımlayıcı bilgi (PII) saklanmaz.

Yalnızca bir kullanıcı, düzenlemeye tabi bir üçüncü taraf hizmetini aktif olarak kullandığında, hizmetin kendisinin yasalara uygun olarak çalışması gerektiğinin doğrulanması söz konusu olacaktır. Bu doğrulama hizmet tarafı tarafından toplanır, üstlenir ve saklanır. LightDAO hiçbir veriyi toplamaz, aktarmaz veya saklamaz:

| Senaryo | Doğrulamayı kim gerçekleştirir | Kullanıcının yapması gerekenler |
|---|---|---|
| Fiat kanalları üzerinden alım/satım | Lisanslı üçüncü taraflar (MoonPay, Ramp Network, Transak gibi) | Uyumluluk sürecini hizmet sağlayıcının kendi gereksinimlerine göre tamamlayın |
| Değişim alt belirteçleri (yatırım hisse sertifikaları) | Belirli ürünün ve hizmet sağlayıcısının gereksinimlerine bağlı olarak | Hiçbir doğrulamaya gerek kalmadan yalnızca madencilik ve yönetişim yapabilirsiniz |
| Banka kartına para çekme/yerel ödeme | Para çekme ve ödeme hizmet sağlayıcısı | Uyumluluk sürecini servis sağlayıcının gerektirdiği şekilde tamamlayın |

Temel ilkeler: **Varsayılan olarak sıfır doğrulama; doğrulama yalnızca kullanıcının düzenlenmiş hizmete aktif olarak girdiği anda gerçekleşir ve hizmet sağlayıcı tarafından karşılanır. **"Doğrulama yapılmaması" nedeniyle hiç kimse madencilik, elde tutma, devretme veya oy kullanma hakkını kaybetmeyecektir.

> Teknoloji saklıdır: Gelecekte belirli bir varlık türü yeterlilik eşikleri gerektirirse, kullanıcılar kendi kimlik bilgilerini sıfır bilgi kanıtı (ZK) biçiminde tutacak ve zincir herhangi bir kimlik bilgisi olmadan yalnızca "karşılanıp karşılanmadığını" doğrulayacaktır - bu yol haritasının bir parçasıdır ve mevcut bir gereklilik değildir.

### 3.3 Vergi Sorumluluğu Beyanı

Anlaşma vergi beyanı hizmeti sağlamamaktadır ve tüm ekolojik ödüller ve ilgili gelirlere ilişkin vergi yükümlülükleri kullanıcılar tarafından karşılanmaktadır. Kullanıcılar vergi ikamet yerlerinin ilgili yasa ve düzenlemelerine uymalıdır.

### 3.4 Kullanıcı erişimi: herkese açık

**Kayıt ve katılım için herhangi bir eşik yok**: E-posta, cep telefonu numarası, sosyal hesap veya kimlik kanıtı gerekli değildir; İhtiyacınız olan tek şey web sayfası açabilen bir cihazdır. LightDAO ** herhangi bir ülke veya bölgede kullanıcı katılımını aktif olarak kısıtlamaz veya coğrafi sınırlama uygulamaz. **

Tek dış kısıtlama üçüncü taraf hizmetlerinden kaynaklanmaktadır: Belirli bir yerin yasalarının belirli hizmetler (fiat para yatırma ve çekme gibi) için başka gereklilikleri varsa, bu hizmetler yerel lisanslı kurumlar tarafından kendi taraflarındaki yasaya uygun olarak gerçekleştirilecek ve kimsenin zincir içi işlevleri (madencilik, tutma, transferler, oylama, teklifler) kullanımını etkilemeyecektir.

Belirli bir yargı bölgesinin gelecekte açık yasaklayıcı düzenlemeler yayınlaması durumunda protokolün yanıt sırası şu şekildedir:

1. Öncelikle mevcut kullanıcıların varlık elden çıkarma haklarının etkilenmediğinden emin olun; zincirdeki varlıklar dondurulamaz ve herkes LIGHT ve alt tokenlerini istediği zaman aktarabilir;
2. Birden fazla ön uç portalı (IPFS aynaları ve topluluk aynaları dahil) aracılığıyla erişilebilir olmaya devam edin;
3. Son adım, yasal yaptırım kapsamında **üçüncü taraf hizmetlerinin** mevcut kapsamını ayarlamaktır.

Kısacası: *** Kısıtlamalar yalnızca hizmetlere yönelik olabilir, kişilere değil. **

### 3.5 Yasal para yatırma ve çekme işlemleri ve zincirler arası kanallar

**Fiat para birimi kanalı (üçüncü taraf hizmet toplama):** Protokolün kendisi yasal para yatırma ve çekme hizmetlerini yürütmez ancak web platformu, Kuzey Amerika, Avrupa, Güneydoğu Asya ve Latin Amerika'daki büyük pazarları kapsayan uyumlu üçüncü taraf kanallarını (MoonPay, Ramp Network, Transak vb.) entegre eder; yerel P2P pazarının toplamı Afrika ve Güney Asya'yı kapsamaktadır; para çekme işlemleri GCash, M-Pesa, Pix ve GrabPay gibi yerel ödeme yöntemlerini destekler.

**Zincirler arası köprü ve LIGHT edinme kanalları:** TGE'den sonra LightDAO zincirinde yerleşik AMM işlemleri; IBC aracılığıyla Cosmos ekosistemiyle birlikte çalışabilirlik; 6. aydan itibaren wLIGHT (Ethereum/Solana) planlaması; Uygunluğa bağlı olarak 6. aydan itibaren CEX listeleme başvurusu. Zincirler arası köprü, bağımsız bir üçüncü taraf tarafından işletilmektedir ve köprünün çevrimiçi hale gelmesinden önce bağımsız bir denetim raporu gereklidir.

### 3.6 Davet Mekanizması Uyumluluk Beyanı (Anti-MLM Analizi)

LightDAO'nun davet teşviki **tek katmanlı paylaşımdır** (yalnızca doğrudan davet edenler, davetlinin madencilik ödüllerinin sabit bir kısmını alır) ve çok düzeyli pazarlamanın (MLM) temel özelliklerine sahip değildir: çok düzeyli yinelemeli komisyon yoktur; gelir, yeni gelenin asıl parası yerine protokoldeki önceden belirlenmiş tokenlerin serbest bırakılmasından gelir; Madenciliğe katılmak için sıfır maliyet ve giriş ücreti yoktur. Bu yapı "açık kaynak proje katılımcısı öneri ödüllerine" daha yakındır. Resmi operasyondan önce, özel uyum görüşleri vermek üzere hedef pazarda lisanslı bir avukat tutulacaktır.

> **[Bu bölümdeki terminoloji]**
> **KYC** (Müşterinizi Tanıyın, Müşterinizi Tanıyın): Finansal kuruluşların kullanıcı kimliğini doğrulamaya yönelik, genellikle kimlik belgelerinin, adres kanıtının vb. ibraz edilmesini gerektiren bir uyumluluk süreci.
> **ZK-KYC** (Sıfır Bilgi KYC, sıfır bilgi kanıtı KYC): Kullanıcıların sözleşmeye ilişkin belirli kişisel bilgileri açıklamasına gerek yoktur ve yalnızca "belirli koşulları karşıladığımı" (18 yaş ve üzeri, yaptırım uygulanmayan uyruk gibi) uyumluluk doğrulama yöntemini kanıtlamak için kriptografi kullanırlar. Zincirde hiçbir orijinal belge verisi saklanmaz.
> **PII** (Kişisel Olarak Tanımlanabilir Bilgiler, Kişisel Olarak Tanımlanabilir Bilgiler): Belirli bir gerçek kişiyi tek başına veya birlikte tanımlayabilen ad, kimlik numarası, adres, biyometrik özellikler vb. veriler.
> **Reg D / Reg S** (ABD Menkul Kıymetler Kanununun Düzenleme D/Yönetmelik S): Reg D, Amerika Birleşik Devletleri'nde kamu kaydı olmaksızın "nitelikli yatırımcılara" özel yerleşimlere izin verir (Kural 501 tanım standardı); Reg S, ABD kayıt gerekliliklerini tetiklemeden menkul kıymetlerin ABD dışındaki kişilere satışına izin verir.
> **MiFID II** (Finansal Araçlarda AB Piyasaları Direktifi II, 2014/65/AB): AB finansal düzenleyici çerçevesi, Ek II, "profesyonel yatırımcılar" için tanımlama kriterlerini tanımlar (500 bin Euro'luk finansal araç portföyü, 1 yıllık finans sektörü deneyimi, üç ayda bir 10 büyük ölçekli işlem, ikinci gerekliliği karşılar).
> **MLM** (Çok Düzeyli Pazarlama, çok düzeyli pazarlama): çok düzeyli yinelenen komisyonlar (alt ekip geliştirme, alt ekip geliştirme ve üst ekip katman katman komisyonlar) yoluyla bir iş modeli. Temelde tek katmanlı öneri ödüllerinden farklıdır - LightDAO yalnızca tek katmanlıdır (A, B'yi davet eder, A, B'den pay alır; B, C'yi davet eder, A, C'den herhangi bir pay almaz).
> **IBC** (Blok Zincirleri Arası İletişim, zincirler arası iletişim protokolü): Cosmos ekosisteminin yerel çapraz zincir standardı olup, merkezi bir aracıya ihtiyaç duymadan varlıkların ve mesajların farklı blok zincirleri arasında güvenli bir şekilde aktarılmasına olanak tanır.

---

## Bölüm 4: Teknik Mimari

### 4.1 Halka açık zincir nedir?

LightDAO'nun halka açık zinciri, "şeffaf kuralları olan ve istenildiği zaman değiştirilemeyen bir kamu hesap defteri" olarak anlaşılabilir: yönetişim kuralları koda yazılır ve herkesin oylama kayıtları, sermaye akışları ve kar dağıtımı zincir üzerinde sorgulanabilir ve doğrulanabilir.

### 4.2 Teknik parametreler ve seçim gösterimi

| Teknik ürünler | Seçim | Seçim esası |
|----------|------|------------|
| Temel çerçeve | Kozmos SDK'sı | Modüler mimari, çoklu üretim zinciri doğrulaması |
| Uzlaşma mekanizması | Tendermint PoS | Anında kesinlik; blok oluşturma 1,5-2 saniye sürer; BFT hata toleransı ≤ 1/3 kötülük |
| Akıllı Sözleşmeler | KozmWasm | WebAssembly + Rust, derleme zamanı bellek güvenliği |
| Çapraz zincir yetenekleri | IBC protokolü | Cosmos yerel çapraz zincir standardı |
| Ön uç etkileşimi | Aşamalı Web Uygulaması (PWA) | Tarayıcı çalışıyor, masaüstü/mobil cihazlara uyarlanabilir, kurulum gerektirmez |

### 4.3 Hafif düğüm madenciliği mekanizması ve teşvik modeli

#### 4.3.1 Madencilik yöntemi

Kullanıcılar resmi web platformuna bir tarayıcı aracılığıyla erişir, bir cüzdan oluşturur ve "Madenciliği Başlat"ı tıklar. Madencilik süreci sırasında kullanıcılar, tarayıcı aracılığıyla ağ bant genişliğine (veri aktarımı ve doğrulama) ve yerel bilgi işlem kaynaklarına (hafif blok başlığı doğrulaması) katkıda bulunur ve yüksek enerjili bilgi işlem gücüne güvenmezler.

**Web tarafı teknolojisi uygulaması:** WebRTC veri kanalı P2P aktarımı; Web Worker arka plan blok başlığı doğrulaması; Service Worker'ın çevrimdışı önbelleği ve kalp atışı; WebSocket uzun bağlantı.

**Mobil tarayıcı uyarlaması:** Kümülatif geçerli bir oturum sistemi benimseyin (günde 4 saat = %100 puan); bağlantı kesildikten sonra 5 dakika içinde yeniden bağlanmak için puan düşülmeyecektir; PWA'yı kuran kullanıcılar ek olarak %10 çevrimiçi süre bonusu alacaklardır; yetkilendirilmiş çevrimiçi mekanizma (delege için %70/aktarma düğümü için %30).

#### 4.3.2—4.3.3 Teşvik planı ve üç motorlu model

"PoC katkısı kanıtı + davet fisyon teşviki + davranışsal bonus teşviki" şeklindeki üç motorlu modeli benimser.

#### 4.3.4 Katkı boyutları ve ağırlığı

| Katkı boyutu | Ağırlık | Ölçüm yöntemi |
|---------|------|---------|
| Bant genişliği aktarımı katkısı | %40 | Yükleme geçiş trafiğinin doğrulama veri hacmine oranı |
| Etkili oturum süresi | %30 | Günlük kümülatif etkili oturumlar (4 saat = %100) |
| Doğrulama katkısını engelle | %20 | Etkili bir şekilde doğrulanmış blok başlıklarının sayısı ve doğruluğu |
| Ağ kararlılığı | %10 | Bağlantı gecikmesi, paket kaybı oranı, yanıt süresi |

#### 4.3.5 Ödül hesaplama formülü

**Günlük Madencilik Ödülü = Temel Ödül × Katkı Ağırlığı Puanı × (1 + Davet Bonusu) × (1 + Davranış Bonusu)**

- BaseReward = Tüm ağ tarafından gün içinde yayımlanan toplam miktar ÷ Gün içindeki aktif madencilerin toplam sayısı
- Davet bonusu = etkin davetli sayısı × %1 (üst sınır %20)
- Davranış bonusu = %5 oy katılımı + %5 içerik katkısı + %5 topluluk etkinliği + %5 düğüm doğrulama kalitesi (üst sınır %20)
- Tam bonus katsayısı = (1+%20) × (1+%20) = 1,44 kat

#### 4.3.6 Fisyon teşviklerini davet edin

| Seviye | Geçerli davetiye sayısı | Davet payı oranı | Tek seferlik ek ödül | Yönetişim ağırlık bonusu |
|------|---------------|---------------|-------------|----------------|
| Madenciler | 0 kişi | — | Temel madencilik ödülleri | Yok |
| Vaiz | En az 3 kişi | %10 | 100 IŞIK | Yok |
| Büyükelçi | En az 10 kişi | %15 | 500 LIGHT + zincir üstü rozet | Oy ağırlığı +%5 |
| Ortaklar | En az 50 kişi | %20 | 2.500 LIGHT + zincir üstü rozet | Oy ağırlığı +%10 |

Yönetişim ağırlığı bonusu ve itibar bonusu (+%30'a kadar) bağımsız olarak biriktirilir ve toplam üst limit +%40'tır. Davet bonusu 20 kişi olduğunda zirveye ulaşır (20×1%=%20).

#### 4.3.7 Hile karşıtı mekanizma

Tarayıcı ortamı bütünlüğü tespiti (Canvas/WebGL/WebRTC parmak izi), paket derinliği tespiti, IP kümeleme ve davranış modeli analizi, çok boyutlu davranışsal parmak izi (fare yörüngesi/klavye ritmi/kaydırma davranışı), davet adresi özgünlük doğrulaması. Anti-Sybil saldırısının maliyeti: 10.000 bağımsız parmak izi oluşturmak için 50.000 ila 200.000 ABD Doları; tespit oranı hedefi >%90-95.

### 4.4 LIGHT Token Fonksiyon Matrisi

Ağ yakıtı (Gaz ücreti), yönetim hakları (oylama/teklif/kampanya), taahhüt bağlama (marj/kampanya/doğrulayıcı), yatırım değişimi (alt tokenlar), ekolojik teşvikler (madencilik/davet/davranış), gelecekteki genişleme (dApp/NFT/zincirler arası).

### 4.5 Gaz ücreti ve işlem ücreti mekanizması

**Tasarım Prensibi:** Gaz ücreti ABD Doları eşdeğerine sabitlenir ve yüklenen gerçek LIGHT miktarı, zincir üzerindeki oracle tarafından her 24 saatte bir otomatik olarak dönüştürülür (Bölüm 4.10). Bu, LIGHT'ın fiyatı ister yükselsin ister düşsün, kullanıcının gerçek ödeme maliyetinin (ABD doları cinsinden) sabit kalmasını sağlar ve "para birimi fiyatı 100 kat artar → transfer ücreti 10 $ olur" veya "para birimi fiyatı %90 düşer → sıfır maliyetli bilet kullanımı" sorununu ortadan kaldırır.

**USD çıpalı gaz ücreti hedefi:**

| İşlem türü | USD eşdeğeri hedefi | IŞIK=0,05$ olduğunda gerçek koleksiyon | IŞIK=0,50$ olduğunda gerçek koleksiyon | Tasarım amacı |
|---------|------------|------------------|------------------|----------|
| Olağan transfer | 0,001$ | 0,02 IŞIK | 0,002 IŞIK | Küçük miktarlardaki kullanıcıların serbestçe para aktarabilmesini sağlamak için son derece düşük eşik |
| Yönetim Oylaması | 0,005$ | 0,10 IŞIK | 0,01 IŞIK | Maliyetsiz oy fırçalamayı önlemek için transferden biraz daha yüksek |
| Bir teklif gönderin | 0,10$ | 2.0 IŞIK | 0,2 IŞIK | Teklifin ciddiyetini artırmak için mevduat sistemiyle işbirliği yapın |
| Alt token değişimi | 0,50$ | 10,0 IŞIK | 1.0 IŞIK | Büyük ölçekli operasyonların ciddiyetine uygun olarak daha yüksek ücretler |
| Madencilik kalp atışı raporlaması | 0$ (ücretsiz) | 0 | 0 | Madencilik katkıları için Gaz alınmaması, sıfır maliyetli katılımın sağlanması |

**Dinamik dönüşüm kuralları:**

- 实际Gas费（LIGHT）= USD目标 ÷ 预言机24h TWAP价格
- 每24小时（UTC 00:00区块）由oracle_twap合约自动更新换算比率
- 设置下限：任何交易类型的Gas费不低于0.001 LIGHT（防止价格为零时Gas归零）
- 设置上限：任何交易类型的Gas费不高于100 LIGHT（防止价格极低时Gas过高阻碍使用）
- USD目标值本身可通过微型提案（$100保证金）由治理调整

**Gaz ücreti tahsis kuralları:**

| Hedef | Oran | İşlev |
|------|------|------|
| Kalıcı imha | %50 | Deflasyonun devam etmesi dolaşım arzını azaltıyor |
| Doğrulayıcı ödülleri | %30 | Doğrulayıcıları ağ güvenliğini sürdürmeye ve bloklar oluşturmaya teşvik edin |
| Ekolojik Hazine | %20 | Tamamlayıcı geliştirici finansmanı ve topluluk işletme fonları |

**Gaz ücreti deflasyonu tahmini:** Günlük ortalama 100.000 aktif işlem ve ortalama gas ücretinin 0,005 ABD Doları (esas olarak oylama ve transferler) olduğunu varsayarsak, günde yok edilen ABD Doları'nın eşdeğeri = 100.000 × 0,005 ABD Doları × %50 = 250 ABD Doları/gün. LIGHT=0,05$ olduğunda, 5.000 IŞIK/gün≈1,825 milyon/yıl'a eşdeğerdir; LIGHT=0,50$ olduğunda, 500 IŞIK/gün≈182.500/yıl'a eşdeğerdir. Gas ücreti deflasyonlu LIGHT miktarı, fiyat arttıkça azalır (ABD doları eşdeğeri sabittir), ancak fiyata olan desteği "eşdeğerinin sürekli satın alınması" ile yansıtılır - her işlem, sabit bir ABD doları oranında tokenları yok eder.

### 4.6 Doğrulayıcı sistem

| Boyutlar | Doğrulayıcılar | Işık düğümleri (tarayıcı madencileri) |
|------|---------|-------------------|
| Sorumluluklar | Blok oluşturma, fikir birliği, tam düğüm | Blok başlığı doğrulaması, veri aktarımı |
| Bahis | Minimum 500.000 IŞIK | Yok |
| Gelir | Gaz ücreti %30 + günlük salınım havuzu %5 | PoC madenciliği ödülleri (günlük yayın havuzu %95) |
| Miktar | Başlangıç ​​21, üst sınır 100 | Üst sınır yok |
| Kesme | Çift imza için %5 ceza + 180 günlük yasak | Yok |

**Aşamalı başlatma (BFT hata toleransı: N≥3f+1):**

| Aşama | Doğrulayıcı sayısı | Hata toleransı f | Zincir durma koşulları | Kullanıcı deneyimi |
|------|-----------|----------|---------------|----------|
| Testnet (TGE'den 3 ay önce) | 7 | 2 | 3 kişi aynı anda çevrimdışı | Dahili testler kısa kesintileri tolere edebilir |
| Ana Ağ TGE | Minimum 10, hedef 21 | 3-6 | 4-7 aynı anda çevrimdışı | Sorunu düzeltmek için ara sıra kesintiler (üç ayda bir <1 kez) |
| 7. aydan itibaren seçime açık | 21-100 | 6-33 | 7-34 aynı anda çevrimdışı | Kullanıcı farkında değil |

**Kesin sonuç: Doğrulayıcı sayısı 7'den az olduğunda TGE yürütülmeyecektir. ** 7'den küçük olması f ≤ 1 anlamına gelir. Herhangi bir tek nokta arızası, tüm zincirin kapanmasına neden olur; bu, teknik bilgisi olmayan kullanıcılar için "ürün bulunamaması" anlamına gelir.

### 4.7 Ağ altyapı katmanı

Doğrulayıcı düğümler, WebSocket erişim ağ geçitlerini dağıtılmış bir şekilde taşır (her doğrulayıcının üst sınırı 50.000 bağlantıdır); P2P sinyali, doğrulayıcı + topluluk aktarma düğümü tarafından sağlanır; kalp atışı Merkle toplaması yalnızca blok başına Kök karmasını (zincir üzerindeki yük O(1)) gönderir; ön uç IPFS+CDN aracılığıyla dağıtılır.

P2P ağı: WebRTC ICE çerçevesi (STUN önceliği/TURN geri dönüşü); kullanıcıların yaklaşık %70-80'i doğrudan bağlanabiliyor, simetrik NAT kullanıcılarının %20-30'u TURN geçişini geçiyor; P2P başarısız olduğunda "saf kimlik doğrulama moduna" düşürülür.

Performans özellikleri: Teorik TPS 1.000-3.000; blok boyutu 2 MB (yönetim ayarlanabilir); ışık düğümü senkronizasyonu <30 saniye; milyon düğüm kalp atışı Merkle toplanması <500 ms.

### 4.8 Katkı kanıtı doğrulama mekanizması

Üç katmanlı doğrulama mimarisi: (1) Doğrulayıcı rastgele çapraz örnekleme testi (her 10 dakikada bir %5 düğüm, 30 saniye yanıt süresi); (2) P2P eşdüzey karşılıklı doğrulama (8-16 eş bağımsız olarak veri alışverişi hacmini kaydeder, medyanı alır); (3) Zincir üzerinde Merkle toplanması (her blok katkı puanı Kökünü gönderir, kullanıcılar Merkle Kanıtı aracılığıyla kendi kendine kontrol edebilir). Art arda 3 kez mücadele edilmemesi → günün puanı sıfırlanacaktır; 7 gün içinde toplam 5 kez → hile karşıtı bir inceleme tetiklenecektir.

### 4.9 Cüzdan ve Anahtar Yönetimi

Üç katmanlı mimari: (1) Gömülü akıllı cüzdan (Passkey/WebAuthn, anımsatıcı ifade gerekmez, %80'den fazla kullanıcıyı hedefler); (2) Sosyal kurtarma cüzdanı (3-5 onarıcı, Shamir parçalaması, 2/3 çoğunluk onayı); (3) Kendi kendine barındırılan cüzdan (BIP-39 anımsatıcı ifade + donanım cüzdanı uyumlu). Yeni kullanıcıların ilk 100 işlemine ait gas ücretleri ekolojik fon (Paymaster modeli) tarafından ödenecek.

### 4.10 Fiyat Oracle

Zincir içi TWAP (LIGHT/USDC havuzunun 30 günlük zaman ağırlıklı ortalama fiyatı) ana fiyat kaynağıdır; 3+ harici DEX/CEX toplaması eklenmiştir (doğrulayıcılar dönüşümlü olarak gönderir, medyanı alır); >±%15 sapmalar istisna işaretlerini tetikler; >%5'ten fazla tek blok sapmaları TWAP'a (flash kredi manipülasyonuna karşı) dahil edilmez; Tüm harici oracle'lar başarısız olduğunda saf zincir üstü TWAP'ye geri dönüş.

### 4.11 Akıllı Sözleşme Modülü Mimarisi

10 temel sözleşme: light_token, mining_reward, yönetişim, treasury_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, Insurance_fund. Temel sözleşmenin TGE'den önce resmi doğrulamayı tamamlaması gerekir.

### 4.12 Protokol Yükseltme ve Zincir Yönetişim

Seviye 4 yükseltmesi: L1 parametre ayarlaması (yönetim oylaması 24-72 saat) → L2 sözleşme geçişi (büyük teklif + denetim + 72 saat gecikme) → L3 fikir birliği değişikliği (%66 kabul edildi + 2/3 doğrulayıcı sinyaller + 7 günlük çatal koruma süresi) → L4 acil durum onarımı (gölge komitenin askıya alınması + çoklu imza düzeltme + 72 saat onay).

> **[Bu bölümdeki terminoloji]**
> **Cosmos SDK**: Geliştiricilerin yapı taşları gibi özel halka açık zincirleri birleştirmesine olanak tanıyan modüler bir blockchain geliştirme çerçevesi. Çeşitli üretim zincirleri (Cosmos Hub ve Osmosis gibi) olgunluğunu doğruladı.
> **Tendermint PoS** (Proof of Stake, Proof of Stake): Doğrulayıcıların (bilgi işlem gücü için rekabet etmek yerine) token taahhüt ederek blok üretme hakkını elde ettiği bir fikir birliği mekanizması. "Anında kesinlik" sağlar; bir blok işlendikten sonra geri alınamaz.
> **BFT** (Bizans Hata Toleransı, Bizans Hata Toleransı): Dağıtılmış bir sistemde, bazı düğümlerin kötülük yapmasını veya hatalı çalışmasını tolere edebilen ve yine de doğru şekilde fikir birliğine varabilen bir mekanizma. Tendermint BFT, doğrulayıcıların 1/3'ünden fazlasının aynı anda kötü davranmasına veya çevrimdışı olmasına tolerans gösteremez.
> **CosmWasm**: Cosmos ekosisteminin WebAssembly teknolojisine dayalı akıllı sözleşme motoru, sözleşme yazmak için Rust dilinin kullanımını destekler ve derleme zamanı belleği güvenliği özelliklerine sahiptir (arabellek taşmaları gibi yaygın güvenlik açıklarını önler).
> **PWA** (Progressive Web App, Progressive Web App): Tarayıcı üzerinde çalışan ancak yerel benzeri uygulama deneyimine sahip bir web teknolojisi. Çevrimdışı önbelleğe almayı, anında bildirimleri ve uygulama mağazası aracılığıyla indirip yüklemeye gerek kalmadan ana ekrana eklemeyi destekler.
> **WebRTC/WebSocket**: İki tarayıcı gerçek zamanlı iletişim teknolojisi. WebRTC, P2P veri aktarımı (düğümler arasında doğrudan iletim) için kullanılır; WebSocket, istemci ile doğrulayıcı arasında uzun bir bağlantıyı (kalp atışı, ödül bildirimi) sürdürmek için kullanılır.
> **PoC** (Katkı Kanıtı): LightDAO tarafından benimsenen teşvik mekanizması, bilgi işlem gücü rekabetine veya sermaye taahhüdüne güvenmek yerine, kullanıcılar tarafından gerçekten katkıda bulunulan ağ kaynaklarını (bant genişliği aktarımı, blok doğrulama, çevrimiçi zaman) doğrulayarak ödüller verir.
> **Merkle Ağacı** (Merkle Ağacı): Büyük miktarda verideki belirli bir girişin bütünlüğünün etkili bir şekilde doğrulanmasına olanak tanıyan karma ağaç veri yapısı. Bu teknik inceleme, milyonlarca ışık düğümü kalp atışını tek bir Kök karmasında toplamak ve bunu zincire (O(1) depolama ek yükü) yüklemek için kullanılır.
> **Gas ücreti**: Blockchain üzerinde işlemleri yürütmek veya sözleşme işlemlerini gerçekleştirmek için gerekli olan ve bilgi işlem ve depolama kaynakları için doğrulayıcıyı telafi etmek amacıyla kullanılan işlem ücreti. LightDAO'nun Gaz ücreti USD eşdeğeri cinsinden sabitlenir ve her 24 saatte bir kahin tarafından otomatik olarak LIGHT miktarına dönüştürülür.
> **Kesme** (ceza): Doğrulayıcının kötülük yapması (çift imzalama gibi) veya uzun süre çevrimdışı kalması nedeniyle taahhüt edilen tokenların bir kısmını kesintiye uğratmak zorunda kaldığı bir ceza mekanizması. PoS ağının güvenliği için ekonomik bir garantidir.
> **Oracle** (Oracle): Zincir dışı verileri (piyasa fiyatları, hava durumu, spor skorları gibi) zincir içi akıllı sözleşmelere güvenli bir şekilde aktaran bir altyapı bileşeni. LightDAO, zincir üstü TWAP + çoklu kaynak toplamanın hibrit oracle mimarisini kullanır.
> **TWAP** (Zaman Ağırlıklı Ortalama Fiyat): Anlık büyük tutardaki işlemlerin fiyat referansı üzerindeki manipülasyon etkisini azaltmak için belirli bir süre içindeki her bloğun fiyatı zamana göre eşit şekilde ağırlıklandırılır.
> **AMM** (Otomatik Piyasa Yapıcı): Bir likidite havuzu (sipariş defteri yerine) aracılığıyla token değişimini gerçekleştiren merkezi olmayan bir ticaret protokolü. Fiyat, havuzdaki varlıkların oranına göre bir formüle göre otomatik olarak belirlenir.
> **DEX / CEX**: DEX (Merkezi Olmayan Borsa, merkezi olmayan borsa) kullanıcı varlıklarını barındırmaya ihtiyaç duymaz ve akıllı sözleşmeler yoluyla eşler arası ticaret yapar; CEX (Merkezi Borsa, merkezi borsa), operatörün varlıkları saklamasını ve işlemleri eşleştirmesini gerektirir.
> **IPFS** (InterPlanetary Dosya Sistemi, InterPlanetary Dosya Sistemi): Bu teknik incelemede ön uç uygulamaların sansüre dayanıklı olarak barındırılması için kullanılan merkezi olmayan dosya depolama ve dağıtım protokolü (etki alanı adı engellenmiş olsa bile kullanıcılar IPFS aracılığıyla platforma erişmeye devam edebilir).

---

## Bölüm 5: Token Ekonomik Modeli

### 5.1 Toplam tasarım esası

**LIGHT toplam arzı: 2,5 milyar (2.500.000.000) ve asla ek olarak verilmeyecektir. **

| Karşılaştırma projeleri | Toplam tutar | Katılım yöntemleri | LightDAO ile Karşılaştırılabilirlik |
|---------|------|---------|------------------|
| Bitcoin | 21 milyon | PoW madencilik makinesi | Anlatı referansı, eşik çok yüksek |
| Helyum (HNT) | 223 milyon | Donanım erişim noktası 200$+ | DePIN karşılaştırması, donanımla sınırlı ölçek |
| Filecoin (FIL) | 2 milyar | Depolama donanımı | Büyüklük olarak birbirine en yakın olan her ikisi de "jeton karşılığında kaynaklara katkıda bulunuyor" |
| Kaspa (KAS) | 28,7 milyar | PoW grafik kartı | Çok büyük, yumuşak düşüşün referans değeri var |
| Pi Ağı | 100 milyar | Mobil tıklamalar | Olumsuz öğretim materyali: Toplam miktar çok büyük → değer algısı son derece düşük |

**2,5 milyar coinin seçilmesinin temel nedeni:**

1. **Yatırım kapasitesi (birincil kısıtlama):** Kasadaki 850 milyon jeton × taban fiyat 0,15 $ × %75 kullanım oranı = **95,63 milyon $ ≈ 100 milyon $** dağıtılabilir sermaye, Aşağı Orta Piyasa PE'nin minimum güvenilir eşiğine ulaşıyor. Akademik temel: Cong, Li ve Wang (2021) "Tokenomics: Dynamic Adoption and Valuation" (*Review of Financial Studies* 34(3):1105-1155, NBER w27222), platform faydasının (yatırım getirisi → geri satın alma → fiyat desteği) dağıtım genişliğinin değil, token değerinin temel itici gücü olduğunu kanıtlıyor.
2. **Ağ rehberliği:** Çağın ilk gününde 1 milyar madeni para çıkarıldı ve 684.900 madeni para piyasaya sürüldü. 100.000 aktif madenci olduğunda kişi başına düşen ortalama 6,51 IŞIK/gün oluyor ve "tamsayı algısı" korunuyor.
3. **Operasyonel fizibilite:** TGE öncesi geliştirme/denetim/yasal finansman açığını (1,10-2,85 milyon $) çözmek için %10 stratejik işletme fonu (250 milyon jeton). Saf topluluk modeli bu maliyeti karşılayamaz.
4. **Deflasyon fizibilitesi:** Temel senaryoya göre 1 milyar koinin alt sınırına 11. ila 12. yıllarda ulaşılır (21 milyarlık planın 15 yıl+ süresinden %25-30 daha kısa).
5. **Makul kıyaslama:** DePIN alanında piyasa değerine göre ilk beş proje arasında yer alan Filecoin (2 milyar) ile aynı seviye.

### 5.2 Token dağıtım planı

| Tahsis Kategorisi | Oran | Miktar | Amaç | Yayın Yöntemi |
|---------|------|------|------|---------|
| Hafif düğüm madenciliği | %40 | 1 milyar | Ağa katkıda bulunanları ödüllendirin | Her 2 yılda bir yarıya indirilir, katkıya göre gerçek zamanlı olarak yayınlanır |
| Kurumsal Yatırım Kasası | %34 | 850 milyon adet | DAO yönetimi altında yatırım gerçekleştirme (yatırım sırasında yok edilir) | Çoklu imza kilitleme, yalnızca geçerli kararlarla serbest bırakılır ve yok edilir |
| Ekolojik Kalkınma Fonu | %16 | 400 milyon | Likidite, airdroplar, geliştirici finansmanı, topluluk operasyonları | Aşamalı sürüm (bkz. Bölüm 5.3) |
| Stratejik işletme fonu | %10 | 250 milyon madeni para | Ekip, denetim, hukuk, altyapı, stratejik yatırımcılar | 12 aylık uçurum + 36 aylık doğrusal (bkz. bölüm 5.X) |

**Endüstri Karşılaştırması (Tokenomics.net 2024-2025 kohort karşılaştırması):** Topluluk/kullanıcı ödülleri %20-35 (LightDAO: %40 madencilik + %16 ekoloji = %56, VC turu olmaması nedeniyle daha yüksek); hazine/rezervler %15-25 (LightDAO: %34, yatırım fonksiyonu nedeniyle); ekip/yatırımcılar %15-45 (LightDAO: %10, sektörden çok daha düşük, "Ulusal DAO" anlatısını sürdürüyor).

### 5.3 Ekolojik Kalkınma Fonu Yayın Planı

| Sahne | Zaman | Oran | Miktar | Amaç |
|------|------|------|------|------|
| TGE | 0. Gün | %30 | 120 milyon adet | DEX likiditesi (%60=72 milyon) + tohum airdropu (%40=48 milyon) |
| Doğrusal sürüm periyodu 1 | 1. ila 12. ay | %40 | 160 milyon jeton | Ayda 13,33 milyon jeton: topluluk teşvikleri, pazarlama, airdrop planı |
| Doğrusal sürüm periyodu 2 | 13'ten 24'e | %30 | 120 milyon jeton | Ayda 10 milyon jeton: geliştirici finansmanı, ekolojik inşaat, rezervler |

### 5.4 Stratejik Operasyon Fonu (250 milyon jeton)

| Alt Kategori | Oran | Miktar | Nesne | Yayın Kuralı |
|----------|------|------|------|------------|
| Jetonlar için hizmet alışverişi | %50 | 125 milyon jeton | Geliştirme şirketleri, denetim kurumları, hukuk firmaları, doğrulama operatörleri | 12 ay uçurum + 36 ay doğrusal; LIGHT olarak ödenen hizmet ücretlerinin %30-50'si |
| Stratejik finansman | %30 | 75 milyon adet | 2-3 DePIN/Cosmos ekolojik fonları veya tüketici endüstrisi stratejik partileri | Ön TGE 0,03-0,05 $'a satıldı (2,25-3,75 milyon $ artış); 12 ay uçurum + 24 ay doğrusal; tek yatırımcı ≤ toplamın %2'si |
| Temel katkıda bulunanlar | %20 | 50 milyon jeton | 3-5 sponsor/temel oluşturucular | 12 ay uçurum + 36 ay doğrusal; üç aylık dönüm noktası değerlendirmesine dayanarak yayınlandı; dönem boyunca satış yok |

**Stratejik yatırımcı gereksinimleri:** Finansal olmayan katkılar (anlaşma akışı, doğrulama hizmetleri, uyumluluk kaynaklarından biri) sağlanmalıdır ve yalnızca finansal yatırımcılar kabul edilmez.

**Mevzuata Uygunluk:** TGE öncesi satış, Reg S (ABD dışındaki yatırımcılar) + Reg D Kural 506(c) (ABD nitelikli yatırımcılar) ikili yol muafiyetini benimser.

**Temel katkıda bulunanların açıklama kuralları:** Yalnızca toplam tutar (50 milyon = toplam tutarın %2'si) ve yayın kuralları açıklanır, kişisel isimler ve bireysel kotalar açıklanmaz. Açıklanan rol kategorileri: Teknoloji/Yatırım/Uyum/Topluluk.

### 5.5 Madencilik çıktısı ve yarıya indirme planı

**Türetim:** 2A = 1 milyar → A = 500 milyon (İlk Çağ). Günlük sürüm = 500 milyon ÷ 730 = 684.932 parça ≈ 684.900/gün. Her blok = 684,932÷49,371 ≈ 13,87 IŞIK.

**Not:** Her bloğun ödül havuzu tüm ağ tarafından paylaşılır; bunun %5'i doğrulayıcılara (34.200/gün) ve %95'i hafif düğüm madencilerine (650.700/gün) tahsis edilir.

| Çağ | Zaman | Toplam çıktı | Günlük yayın | Blok başına ödül havuzu |
|------|------|---------|---------|------------|
| 1. Çağ | 0-24 ay | 500 milyon | ≈684,900 | ≈13,87 IŞIK |
| 2. Çağ | 25-48 ay | 250 milyon adet | ≈342,500 | ≈6,93 IŞIK |
| 3. Çağ | 49-72 ay | 125 milyon adet | ≈171,200 | ≈3,47 IŞIK |
| 4. Çağ | 73-96 ay | 62,5 milyon adet | ≈85,600 | ≈1,73 IŞIK |
| 5. Çağ | 97-120 ay | 31,25 milyon adet | ≈42,800 | ≈0,87 IŞIK |

**Kontrol edin:** 5+2,5+1,25+0,625+0,3125+… = 5×2 = 1 milyar ✓. İlk 10 yılda %97'si tamamlandı.

### 5.6 Kullanıcı geliri referans modeli

| Ağ boyutu | Kişi başına günlük gelir | Aylık gelir | Yıllık gelir | Tam kar marjı (1,44x) aylık gelir |
|---------|-----------|--------|--------|---------|
| 10.000 madenci (tohum aşaması) | ≈65.07 | ≈1,952 | ≈23,751 | ≈2,811 |
| 100.000 madenci (büyüme aşaması) | ≈6,51 | ≈195,2 | ≈2,375 | ≈281.1 |
| 1 milyon madenci (ölçek dönemi) | ≈0,65 | ≈19,5 | ≈237,5 | ≈28,1 |

**İş ortağı düzeyi (50 davetiye, %20 pay, tam bonus):**

| Ağ ölçeği | Kendisi (bonus dahil) | Davet paylaşımı | Günlük kapsamlı | Aylık kapsamlı |
|---------|------------|---------|--------|------------|
| 10.000 madenci | ≈93.7 | ≈650.7 | ≈744.4 | ≈22,332 |
| 100.000 madenci | ≈9.37 | ≈65.07 | ≈74.44 | ≈2,233 |
| 1 milyon madenci | ≈0,94 | ≈6,51 | ≈7.45 | ≈223.4 |

### 5.7 Airdrop Büyüme Planı

**Ekonomik model:** Toplam airdrop bütçesi = ulaşılan kullanıcı sayısı × kişi başına airdrop × (1+atık oranı) = 100.000 × 150 LIGHT × 1,3 ≈ 19,5 milyon (satın alma türü) + 35,5 milyon (ekolojik tür) = **55 milyon** (400 milyonluk ekolojik fonun %13,75'ini oluşturur).

| Airdrop türü | Tetikleme koşulları | Tek kota | Bütçe |
|---------|---------|---------|------|
| İlk Madencilik Airdrop'u | İlk kez 4 saatlik etkili madencilik tamamlandı | 50 IŞIK | 15 milyon adet |
| Coğrafi genişleme | Hedef pazar kullanıcıları ZK-KYC'yi tamamlıyor | 100 IŞIK | 10 milyon adet |
| Kazanmayı Öğrenin | Eğitim Modülünü Tamamla + Sınav | 30 IŞIK | 6 Milyon Para |
| İlk Yönetişim Oyu | Oylamaya İlk Katılım | 20 IŞIK | 3 milyon jeton |
| Likidite sağlanması | LP enjeksiyonu 30 gün boyunca ≥50$ kilitlenme | 200 IŞIK | 10 milyon adet |
| İçerik oluşturma | Topluluk tarafından doğrulanmış eğitimler/çeviriler | 50-200 IŞIK | 6 milyon adet |
| İşbirliği kanalları | Kayıt + ortaklar aracılığıyla ilk madencilik | 80 IŞIK | 5 milyon adet |

**CAC doğrulaması:** 55 milyon jeton × 0,03 ABD doları = 1,65 milyon ABD doları ÷ 30.000 tutulan aktif madenci = **55 ABD doları/kişi** (endüstri aralığı 50-200 ABD doları, alt uçta). Akademik temel: Zheng (2023) "Dumbo Drop Operasyonu: İlk Para Teklifinde Başarı için Airdrop Yapılmalı mı, Yapılmamalı mı?" olaya bağlı airdropların tutulma oranının saf airdropların 3-5 katı olduğunu kanıtlıyor.

**Kötüye kullanıma karşı koruma:** Benzersiz tarayıcı parmak izi + ZK-KYC; adres başına kategori başına 1 taleple sınırlıdır; 30 günlük kilitlenme süresi; Talepten sonraki 30 gün içinde zincir içi aktivite olmadan otomatik geri dönüşüm.

### 5.8 Çift Motorlu Volan ve Sermaye Havuzu

Volan: Oylama → Vault LIGHT imhası → USDC ödemesi → Kârın yeniden akışı → Geri satın alma ve imha → Fiyat desteği → Daha fazla kullanıcı.

Çift yollu sistem: istikrarlı hazine (USDC, kar tutma) + esnek hazine (HAFİF katman, yatırım yaparken yok edilir ve piyasaya akmaz). Geri alımlar, ortalama günlük işlem hacminin %5'i kadar tek bir emirle TWAP kullanılarak bölünür.

### 5.9 Alt token ihracı ve ticareti

Toplam ihraç tutarı = yatırım tutarı ÷ 1 $; döviz fiyatı 30 günlük VWAP'ye dayanmaktadır; takastan elde edilen tüm IŞIK yok edilecek; Destekçilerin %50'si/%30 airdrop/%20 işletme rezervi dağıtılacaktır (6 ay boyunca kilitli). Tek adres için temettü limiti %15'tir. Alt tokenler, zincir üzerinde AMM'de, ihraç edildikten sonra 30 günlük bir kilitlenme süresiyle alınıp satılıyor ve çekildikten sonra "tasfiye edilmiş" olarak işaretlenecek.

### 5.10 İlk Likidite ve Fiyat Keşfi

**TGE (Token Oluşturma Etkinliği, belirteç oluşturma etkinliği) düzenlemesi: **

| Proje | Planı |
|------|------|
| Başlangıç ​​likidite havuzu | Ekolojik kalkınma fonu TGE tarafından piyasaya sürülen 120 milyon parçadan 72 milyon parça (%60) tahsis edilerek DEX likidite havuzuna enjekte edildi |
| Eşleşen varlıklar | USDC (ana havuz), USDT (yardımcı havuz) |
| Airdrop | Geriye kalan 48 milyon (%40) ise başlangıç ​​kullanıcılarına yapılacak airdroplar için kullanılacak (bkz. Bölüm 5.7 Airdrop Planı) |
| Borsalarda listeleniyor | TGE'den sonra ilk olarak merkezi olmayan borsalarda (Osmosis, JunoSwap gibi) listelendi; uyum koşullarına bağlı olarak 6. aydan itibaren merkezi borsalarda kote olmak için başvuruda bulunun |

**Hollanda Açık Artırmasının ayrıntılı mekanizması:**

Hollanda açık artırması, fiyatların yüksekten düşüğe doğru indiği bir fiyatlandırma yöntemidir. İngiltere'deki açık artırmaların (fiyatların düşükten yükseğe doğru teklif edildiği) aksine, Hollanda açık artırmasında satıcı yüksek bir başlangıç ​​fiyatı belirler ve alıcı belirli bir fiyat noktasında bir abonelik sunana kadar fiyat zaman içinde otomatik olarak düşer. Toplam abonelik tutarının hedefe ulaştığı ilk fiyat son açılış fiyatıdır.

**Neden sabit fiyatlı veya İngilizce açık artırma yerine Hollanda açık artırmasını seçmelisiniz:**

| Fiyatlandırma | Avantajları | Dezavantajları | Uygulanabilirlik |
|---------|------|------|--------|
| Sabit fiyatlı ön satış | Basit | Fiyatlandırma subjektiftir, çok yüksek olursa satmaz, çok düşük olursa robotlar kapar | Uygun değil (fiyat bulma işlevi yok) |
| İngiliz açık artırması (teklif verme) | Tam fiyat keşfi | Büyük alıcılar stratejik olarak bekleyip fiyatları artırabilir; gaz savaşı | Uygun değil (zincir içi gaz savaşı küçük kullanıcıları hariç tutar) |
| **Hollanda Açık Artırma** | **Otomatik fiyat keşfi; ihaleye gerek yok (gaz savaşı yok); büyük ve küçük alıcıların eşit katılımı; anti-bot (fiyat düşürme mekanizması doğal olarak önden çalışmayı engeller)** | Başlangıç ​​fiyatı ve yavaşlama oranının makul bir şekilde ayarlanması gerekiyor | **En uygun (adil + verimli + manipülasyona karşı)** |

**LightDAO Hollanda müzayedesine özel parametreler:**

| Parametreler | Ayarlar | Açıklama |
|------|------|------|
| Açık artırma hedefi | LIGHT tokenleri (ekoloji fonu TGE tarafından serbest bırakılan 72 milyondan tahsis edilmiştir) | Açık artırmadan elde edilen USDC, istikrarlı kasaya aktarılacak |
| Hedef bağış toplama tutarı | **15 milyon ABD Doları** | 5 milyon $ → istikrarlı hazinenin asgari rezervi; 10 milyon $ → ilk yatırım sermayesi |
| Başlangıç ​​fiyatı | 0,20$/IŞIK | Beklenen denge fiyatının üzerinde, saniyeler içinde kaybolmamasını sağlıyor |
| Yavaşlama oranı | Her saat %5 oranında azaltın | 0,20$'dan başlayıp yaklaşık 48 saat sonra 0,017$'a düşüyor (eğer kimse abone olmazsa) |
| Minimum rezerv fiyatı | 0,01$/IŞIK | Rezerv fiyatının düşürülmesine rağmen hedefe hala ulaşılamaması durumunda açık artırma 24 saat ertelenecek veya nesne sayısı ayarlanacak |
| Abonelik yöntemi | Kullanıcı "Geçerli fiyattan X USDC eşdeğeri LIGHT satın almak istiyorum" ifadesini gönderir | Teklif verilmesine gerek yoktur, sistem nihai birleştirilmiş fiyata göre çözümlenecektir (her türlü fazlalık tazminatsız olarak iade edilecektir) |
| Tek kullanıcı üst sınırı | Hedef bağış toplama tutarının %5'inden fazlası (yani 750.000 $) | Tek bir alıcının ilk çipleri tekeline almasını önleyin |
| KYC Gereksinimleri | Gelişmiş Doğrulama (Vergi Mukimliği) | Uyumluluk Gereksinimleri |

**Açık artırma sonuçlarından elde edilen fonların hedefi:**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**Fiyat keşfi koruma süresi:** TGE'den sonraki ilk 72 saat içinde bir fiyat dalgalanma devre kesicisi kurulur - DEX işlem fiyatı açık artırma açılış fiyatından ±%50'den fazla saparsa, aşırı spekülasyonun ekolojik girişime müdahale etmesini önlemek için alt token değişim işlevi askıya alınacaktır (madencilik ve transferler etkilenmeyecektir). Sigorta 72 saat sonra otomatik olarak serbest kalacaktır.

**Neden daha düşük yerine 15 milyon dolar:** 10 milyon dolarlık başlangıç ​​yatırım sermayesinin ilk yılda 3-5 yatırımı desteklemesi gerekiyor (tek bir yatırım 2-5 milyon dolar, Bölüm 9.1'deki başlangıç ​​döneminin ölçeğine bakın). Yalnızca 5 milyon dolar toplanırsa (tümü rezerv olarak), ilk yılda dağıtılabilir yatırım sermayesi olmayacak ve volan çalışmayacaktır. 15 milyon $ = 5 milyon $ rezerv + 10 milyon $ yatırım; bu, "güvenlik alt çizgisi" ile "volan başlangıcı" arasındaki mümkün olan minimum dengedir.

### 5.11 Deflasyon mekanizması ve sonuç

**Dolaşım hacmi = madencilik salınımı + ekolojik salınım + serbest bırakılan stratejik fon − takas ve imha − gaz imhası – geri satın alma ve imha. **Yatırım kasasından çıkan 850 milyon coin hiç dolaşıma girmedi. Teorik dolaşım üst sınırı = 10+4+2,5 = **1,65 milyar**.

| Tetikleme koşulları | Sistem davranışı |
|---------|---------|
| Tiraj ≤ 1,5 milyar adet | Yavaşlama sinyali (son derece düşük imha senaryosu) |
| Dolaşım hacmi ≤ 1,2 milyar adet | Erken uyarı duyurusu, aktif imhanın askıya alınması (baz senaryonun yaklaşık 8. yılı) |
| Dolaşım hacmi ≤ 1 milyar | Kesin durdurma, tüm yıkımlar kalıcı olarak kapatıldı (temel senaryo yaklaşık 11-12 yıldır) |

### 5.12 Fiyat istikrarı mekanizması (ölüm karşıtı sarmal)

**Temel Prensip:** LightDAO günlük piyasa fiyatı keşfine müdahale etmez. Protokol, "ölüm sarmalına" düşme riskini azaltmak için yalnızca aşırı aşağı yönlü senaryolarda parametrelerini ayarlıyor.

**Derecelendirme mantığı:** Farklı değişken ortamlarda, aynı düşüş farklı anormallik derecelerini temsil eder. Volatilitenin düşük olduğu bir piyasada keskin bir düşüş, daha güçlü bir anormal sinyaldir ve daha yüksek yoğunlukta müdahale gerektirir; Volatilitenin yüksek olduğu bir piyasada keskin bir düşüş nispeten yaygındır ve daha hafif müdahaleler yapılabilir. Bu nedenle müdahalenin yoğunluğu, yalnızca düşüşün mutlak değerine bağlı olmaktan ziyade, sinyalin anormalliğiyle pozitif yönde ilişkilidir.

**Mekanizmanın tam akış şeması:**

| Piyasa durumu | 30 günlük tarihsel volatilite | Tetikleme koşulları | Sinyal seviyesi | Tetikleyiciden sonra yürütme | Kurtarma koşulları |
|---------|--------------|---------|---------|----------|---------|
| Düşük oynaklık | ≤%30 | Art arda 5 gün boyunca kümülatif düşüş ≥%40 | Seviye I | Madencilik çıktısı %50'ye düştü; imha oranı %20'den %35'e çıktı; risk parametresi ayarlaması tanıtım süresi 72 saatten 12 saate kısaltıldı; gölge komite aktif duruma geçti (kanun uyarınca yalnızca geçici uzaklaştırma hakkı kullanılabilir) | Fiyat 30 günlük hareketli ortalamanın üzerinde yer aldı ve tetik fiyatından %80'den fazla toparlandı ve art arda 10 gün boyunca bu şekilde kaldı |
| Orta dalgalanma | %30-%60 | Art arda 7 gün boyunca kümülatif düşüş ≥ %50 | Seviye II | Madencilik çıktısı %50'ye düştü; imha oranı %20'den %30'a çıktı; tanıtım süresi 24 saate kısaltıldı; gölge komitesi aktif duruma geçti | Fiyat 30 günlük hareketli ortalamanın üzerinde yer aldı ve tetik fiyatından %60'ın üzerinde toparlanma gösterdi ve art arda 7 gün boyunca bu şekilde kaldı |
| Yüksek oynaklık | %60-%100 | 10 gün üst üste kümülatif düşüş ≥%55 | Seviye III | Madencilik üretimi %75'e düştü; imha oranı %20'den %25'e çıktı; tanıtım süresi 48 saate kısaltıldı; gölge komitesi bekleme moduna girdi | Fiyat 30 günlük hareketli ortalamanın üzerinde yer aldı ve tetik fiyatından %40'ın üzerinde toparlanma gösterdi ve art arda 5 gün boyunca bu şekilde kaldı |
| Aşırı oynaklık | >%100 | Art arda 10 gün boyunca kümülatif düşüş ≥ %65 | Seviye III | Yüksek volatiliteye yönelik Seviye III önlemlerine göre uygulanmıştır | Yüksek volatilite için Seviye III toparlanma koşullarına göre uygulandı |

**Hariç tutma koşulları:** Yalnızca Bitcoin'in aynı dönemdeki düşüşü LIGHT'ın düşüşünün %50'sinden az olduğunda, yukarıdaki mekanizma sistemik bir piyasa çöküşünü dışlamak için tetiklenebilir (yani, BTC de aynı dönemde düşerse bu genel bir piyasa olayıdır ve LIGHT için ayrı bir müdahale başlatılmaz).

**Kurtarma mantığı açıklaması:** Geri tepme gereksinimleri ve süresi anormallik seviyesiyle birlikte azalır: Seviye I, en yüksek geri tepme genliğini (%80) ve en uzun onay süresini (10 gün) gerektirirken Seviye III nispeten daha düşük gereksinimler gerektirir (%40/5 gün). Bu düzenleme, "anormal sinyal ne kadar güçlü olursa, müdahale o kadar güçlü ve iyileşme onayı da o kadar sıkı olur" şeklindeki ilerici mantıkla uyumludur.

**Volatilite ve fiyat veri kaynağı:** 30 günlük tarihsel dalgalanma ve kümülatif düşüş, günlük UTC 00:00 bloğunun TWAP anlık görüntüsüne dayalı olarak zincir üstü fiyat oracle'ı (bkz. Bölüm 4.10) tarafından sağlanır ve herhangi bir harici veri kaynağına dayanmaz.

### 5.13 Kazanç Sürdürülebilirliği Stres Testi

| Stres senaryoları | Ne Olursa | Protokol yanıtları | En kötü durum sonuçları |
|---------|---------|---------|---------|
| Tüm yatırımlar başarısız oldu | Yatırım yapılan tüm şirketler zarar etti veya çıkamadı | Sigorta fonu (tahakkuk eden kârın %10'u) zararların bir kısmını karşılar; operasyonları sürdürmek için istikrarlı hazine rezervleri (≥8 milyon$); toplum yeniden değerlendirinceye kadar yeni yatırımlar askıya alındı ​​| Alt token sahipleri temettü alamazlar; LIGHT fiyatı baskı altında ancak sıfıra dönmüyor (madencilik ve yönetim fonksiyonları çalışmaya devam ediyor) |
| Piyasa %80 düştü | LIGHT fiyatı zirveden %80 düştü | Ölüm karşıtı sarmal mekanizmayı tetikleyin (seviye II veya seviye III); madencilik çıktısı %50-75 oranında azaldı; imha oranı arttırıldı; gölge komite yüksek riskli operasyonları askıya alabilir | Kullanıcı geliri azalıyor ancak ağ çalışmaya devam ediyor; kurtarma koşulları karşılandığında mekanizma otomatik olarak kaldırılır |
| Başlıca piyasa düzenleme yasakları | Büyük bir ülke kripto varlıklarını tamamen yasakladı | Ön uç anahtarlamalı IPFS aynası erişilebilir olmaya devam eder; zincir üstü varlıklar ve mevcut kullanıcı hakları ve çıkarları etkilenmez; üçüncü taraf hizmetlerinin kullanılabilirliği yalnızca yasal yaptırım kapsamında ayarlanır; Cayman Adaları'ndaki SPV operasyonları tek bir ülkenin yargı yetkisine tabi değildir | Bölgedeki kullanıcı artışı durağanlaştı; dünyadaki diğer bölgeler etkilenmemektedir |
| Büyük ölçekli kullanıcı kaybı | Aktif madenciler %70'ten fazla düştü | BaseReward otomatik olarak yeniden dağıtılır (payda küçülür → elde tutulan kullanıcıların kişi başına geliri artar); davet teşvikleri, geri dönüş akışlarını çekecek şekilde ağırlıklandırılıyor; yönetişim eşikleri geçici olarak düşürüldü (Bölüm 5.14'teki dinamik mekanizma) | Ağ güvenliği azaltıldı ancak zincir durdurulmayacak (Tendermint BFT, doğrulayıcıların <1/3'ünün çevrimdışı olmasını tolere ediyor) |
| Başlıca akıllı sözleşme güvenlik açıkları | Temel sözleşmelerde bulunan istismar edilebilir güvenlik açıkları | Fon çıkışlarının çoklu imzayla acil olarak askıya alınması (72 saatlik zaman kilidi yanıt penceresi sağlar); Yedek sözleşme geçiş oylamasını başlatın (L4 düzeyinde acil durum onarımı, bkz. Bölüm 4.12); Sigorta fonu kullanıcı kayıplarını karşılıyor | Bazı fonlar zarar görebilir; Geçiş tamamlandıktan sonra normal işlemler devam ediyor |

### 5.14 Nesiller arası dengeleme mekanizması

Yönetişim eşiğinin dinamik olarak ayarlanması: her 1 milyon yeni kümülatif aktif madenci için teklif eşiği otomatik olarak %5 düşürülür (alt sınır 2.500 LIGHT).

> **[Bu bölümdeki terminoloji]**
> **TGE** (Token Oluşturma Etkinliği): Bir tokenın akıllı bir sözleşme yoluyla ilk oluşturulduğu ve dağıtıldığı nokta; buna genellikle bir başlangıç likidite havuzunun oluşturulması, Hollanda açık artırma fiyatlandırması ve ilk halka açık işlem eşlik eder. Geleneksel finanstaki halka arza benzer, ancak borsada listelenmeyi içermez.
> **Halving** (Halving): Madencilik çıktısının her sabit dönemde (LightDAO için 2 yıl/730 gün) otomatik olarak %50 oranında azaltıldığı bir mekanizma. Amaç kademeli kıtlık yaratmaktır; zaman geçtikçe daha az yeni arz eklenir ve talep azalmazsa fiyatlar desteklenecektir. Bitcoin her 4 yılda bir yarılanmayı benimser.
> **Hazine** (Hazine): Çoklu imza sözleşmeleriyle kilitlenen ve yalnızca yönetim kararları yoluyla serbest bırakılabilen jeton rezervleri. LightDAO'nun iki tür kasası vardır: yatırım kasaları (LIGHT'ı tutan ve yatırımlar yürütüldüğünde yok edilen) ve istikrarlı kasalar (USDC'yi tutan ve yatırım bedelini ve işletme giderlerini ödemek için kullanılanlar).
> **Deflasyon** (Deflasyon): Tokenların toplam arzının veya dolaşımının azalmaya devam ettiği süreç. LightDAO deflasyonu dört mekanizma aracılığıyla başarır: yatırımın gerçekleştirilmesi ve imhası, alt token değişimi ve imhası, gas ücretinin imhası (%50) ve kârın yeniden satın alınması ve imhası.
> **Ölüm Spirali** (Ölüm Spirali): Token fiyatları düşer → madencilerin geliri azalır → madenciler ayrılır → ağ güvenliği/katkısı azalır → daha fazla güven kaybı → fiyatların düşmeye devam ettiği bir kısır döngü. Bölüm 5.12'deki kademeli müdahale mekanizması bu döngüyü kesintiye uğratmak için tasarlanmıştır.
> **Alt token** (Alt token): Her kurumsal yatırım tamamlandıktan sonra kurallara uygun olarak verilen SPV gelir dağıtım talep belgesi (bir kahve markası → CAFE tokeninin alınması gibi). Alt tokenleri tutmak = gelecekteki karların dağıtımına ilişkin nitelikleri elinde tutmak ve hissedar haklarını veya kurumsal yönetim haklarını temsil etmez.
> **LP** (Likidite Sağlayıcı): DEX likidite havuzuna eşit değerde iki varlık (LIGHT+USDC gibi) enjekte eden katılımcılar bunun karşılığında işlem ücreti kazanırlar. LP, DEX'in normal işleyişinin temelidir.
> **VWAP** (Hacim Ağırlıklı Ortalama Fiyat): Belirli bir süre içindeki fiyat, her işlemin hacmine göre ağırlıklandırılır ve gerçek piyasa işlem maliyetini yansıtır. LightDAO, alt token değişimi için fiyatlandırma kriteri olarak 30 günlük VWAP'yi kullanıyor.
> **CAC** (Müşteri Edinme Maliyeti, kullanıcı edinme maliyeti): Etkin bir aktif kullanıcı edinmenin ortalama maliyeti. LightDAO airdrop programının hedef CAC'si 55 ABD Doları/elde tutulan aktif madencilerdir (sektör aralığı 50-200 ABD Doları).
> **wLIGHT** (Sarılı LIGHT, kapsüllenmiş LIGHT): Zincirler arası köprüler aracılığıyla Ethereum veya Solana'da yayınlanan LIGHT eşdeğeri tokenlar ve eşit miktarda yerel LIGHT, köprü sözleşmesi tarafından 1:1 rezerv olarak kilitlenir. Amaç, Cosmos dışındaki ekosistem kullanıcılarının IŞIK elde etmelerine ve tutmalarına olanak sağlamaktır.
> **Hollanda Müzayedesi** (Hollanda Müzayedesi): Fiyatın yüksekten düşüğe doğru indiği fiyatlandırma yöntemidir. Satıcı, başlangıç ​​için yüksek bir fiyat belirler ve alıcı belirli bir fiyat noktasında abonelik gönderene kadar fiyat zaman içinde otomatik olarak düşer. Toplam abonelik tutarının hedefe ulaştığı ilk fiyat, nihai işlem fiyatıdır. Avantajı, hiçbir teklife gerek olmaması (gaz savaşı olmaması), her boyuttaki alıcının eşit olmasıdır ve doğal olarak robot ön alımlarına karşı dirençli olmasıdır.

---

## Bölüm 6: Yönetişim Mekanizması

### 6.1 İki boyutlu oylama modeli

Para birimi ağırlığı (itibar + seviye bonusu, toplam üst limit +%40 dahil) + adres sayısı (1 adres = 1 oy, ilgili adresler birleştirilir). Oy hakları 90 gün geçerlidir ve 5 LIGHT aktarılarak aktif hale getirilebilir. İtibar bonusu: Para birimini 1 yıl boyunca tutmak + 15 geçerli oy → +%30'a kadar.

### 6.2 Dinamik geçiş hızı

Minimum geçiş oranı = %50 + (%50 - gerçek oy oranı). Oy oranı ≥%50 olduğunda basit çoğunluk.

### 6.3 Teklif parametreleri

| Tür | Marj | Jeton oylama oranı | Adres oy oranı | Geçiş oranı | Yürütme gecikmesi |
|------|--------|-----------|-----------|--------|------------|
| Mikro | 100$ | ≥%15 | ≥%20 | Dinamik ≥%55 | 24 saat |
| Edinme türü | 500 $ | ≥%25 | ≥%30 | Dinamik ≥%60 | 72 saat |
| Risk sermayesi türü | 500 $ | ≥%35 | ≥%40 | Dinamik ≥%60 | 72 saat |
| Binbaşı | 1.000$ | ≥%45 | ≥%50 | Dinamik ≥%66 | 72 saat |
| Acil Durum | 2.000$ | ≥%50 | ≥%60 | ≥%75 | Finansmansız 6 saat/yüksek riskli 1 saat; sermaye işlemleri hâlâ 72 saatlik zaman kilidine tabidir |

### 6.4 Teklif yaşam döngüsü

Başvuru yeterliliği: ≥5.000 LIGHT + 30 ardışık gün rehin + depozito. Kamu duyurusu 72 saat (≤ 2 kez revize edilmiştir). Oylama 7 gün içinde gerçekleşir (hızlı geçiş için 48 saat, ≤500.000 USDC). Veto 90 gün boyunca soğuyor. Etkinliği 24 saat gecikir.

**Eşik açıklaması:** Başlangıç ​​aşamasında 5.000 jeton (10.000 madenci) ≈ 77 günlük temel çıktı; partner düzeyi ≈ 7 gün. Yönetişim yedinci ayda etkinleştirilecek ve ilk kullanıcılar yeterli birikim süresine sahip olacak.

### 6.5 Oy verme teşvikleri

Katılım (hatta paylaşım) için temel bir teşvik vardır ve doğru karar için ek bir bonus vardır (bahis havuzunun %50'si). 5-500 LIGHT aralığında bahis yapın. Sürü etkisini bastırın: Rakipler "yanlış takımda" olsalar bile yine de temel teşvikler alıyorlar.

### 6.6 Başarı veya başarısızlık için ödüller ve cezalar

İyi niyetle başarısızlık: %50 depozito iadesi + 30 günlük bekleme süresi. Kötü niyetli başarısızlık (sahtecilik/tekrarlama): El konulan tutarın tamamı + kalıcı yasak. Dolandırıcılık kanıtı: 5.000 LIGHT ile sınırlıdır, %40 kuruluş cezası bonusu + 500 LIGHT.

### 6.7 Mali Şeffaflık

Zincirdeki gerçek zamanlı kontrol paneli + üç aylık mali rapor + yıllık bağımsız denetim (ilk denetim TGE'den önce tamamlanmalıdır) + yatırım hedeflerinin gerçek zamanlı açıklanması.

---

## Bölüm 7: Güç kontrolleri ve dengeleri ve rol tanımı

### 7.1 İlk Muhafız

İzinler belge/format/resmi web sitesi bilgileriyle sınırlıdır. Vade ≤ 24 ay. Alternatif bir vasi belirlenmelidir (art arda 30 gün boyunca imza atılamaz → otomatik olarak devralınır). Eş zamanlı sakatlık → Geçici bir yönetici atamak için 48 saatlik acil oylama.

### 7.2 Güç Aktarımı Yol Haritası

| Sahne | Zaman | İzinler | Yatırım Onayı |
|------|------|------|--------|
| Yaratılış dönemi | 0-6 ay | Guardian (finansal olmayan) | Guardian + topluluk çoklu imzası 3/5 |
| Geçiş dönemi | Temmuz-Aralık | Guardian + çekirdek katılımcı ortak imza attı | Yukarıdakiyle aynı + çekirdek katılımcı |
| Vade süresi | 13-24 ay | Yönetişim Komitesi 3/5 | Düzenli iki boyutlu oylama |
| Özerklik dönemi | 25 ay + | Tüm sahipler | Aynı vade dönemi |

### 7.3 Yönetişim Komitesi

Güç beş kişi arasında paylaştırılır (dönüşümlü başkan/finans/teknoloji/topluluk/anahtar), üç ayda bir rotasyon yapılır ve görev süresi altı aydır ve bir kez yeniden seçilebilir. Kampanyada 50.000 LIGHT + 100 adres ortak imzası taahhüt ediliyor. Karar alma ≥3 kişiyi içerir ve ≥3 pozisyonu kapsar.

**Eşik açıklaması:** Başlangıç ​​aşamasında 50.000 jeton ≈ ortaklar için 67 gün (2,2 ay); büyüme aşamasında ≈ 672 gün (22 ay). Komitenin 13. aydaki ilk seçimi erken ortaklara açıktır.

### 7.4 Gölge Komitesi

Yalnızca "ihlaller/yaptırımlar/büyük dolandırıcılık" nedeniyle geçici uzaklaştırma. Tüm oyların 72 saat içinde onaylanması gerekiyor (muhalefet >%60→reddedildi). Art arda iki kez reddedildi → otomatik olarak suçlandı ve dağıtıldı.

### 7.5—7.6 Kampanya doğrulaması ve temel plan

SimHash>%80 diskalifiye; Yapay zeka içeriği açıklamalarla desteklenmelidir; Eksik sorular için oyların %20'si düşülecektir. Anahtar parça yedekleme + üç aylık durum kontrolü + 7 günlük genel duyuru + oylama değişimi.

---

## Bölüm 8: Güven ve Güvenlik Mekanizması

### 8.1 Beş ana güvenlik mekanizması

Zaman kilidi 72 saat (acil durum teklifleri sermaye operasyonlarından muaf değildir); çoklu imza 3/5; üç aylık rotasyon ≤ 2 oturum; Dolandırıcılık için %100 ceza; tüm işlemler zincirdedir.

### 8.2 Sigorta Fonu

Başarılı yatırım kârının **%10'u** tahakkuk ettirilir. Talepler bağımsız olarak bildirilmelidir + DAO lehinde %66 + tek ≤ havuz %20. Ek kaynak: Sahtecilik cezasının %30'u. "Kısmi tampon" konumlandırması tam koruma değildir.

### 8.3 Ekstrem plan

Denetim siyah kuğu → IPFS + yönetici haklarının kaldırılması; dolandırıcılık → gölge komitenin askıya alınması (72 saat onay) + sigorta fonu + SPV tahkimi; ölüm sarmalı → Bölüm 5.12 mekanizması; sözleşme güvenlik açığı → çoklu imzanın askıya alınması + geçiş oylaması; doğrulayıcılar kolektif olarak kötülük yapıyor → BFT toleransı <1/3, aşılması durumunda zincir askıya alınacak + acil oylama geçişi.

---

## Bölüm 9: Yatırım Operasyonları ve Çıkış Stratejileri

### 9.1 Yatırım hedeflerinin taranması ve ölçeği

**Yatırım ölçeğinin aşamalı büyüme yörüngesi (formül: hazine fazlası × %15 × LIGHT fiyatı): **

| Sahne | IŞIK fiyatı | Kasanın ilk döneminde tek işlem limiti | Uyum hedefleri | Endüstri kıyaslaması |
|------|----------|----------|----------|----------|
| Başlangıç ​​dönemi (Y1-2) | 0,02$—0,05$ | 2,55 milyon dolar — 6,37 milyon dolar | Tek mağaza/küçük zincir, melek yuvarlak | Mikro PE |
| Büyüme aşaması (Y3-5) | 0,05$—0,30$ | 6,37 milyon dolar — 38,25 milyon dolar | Bölgesel zincir 30-200 mağaza, Seed-A turu | Alt Orta Piyasa PE |
| Olgunluk aşaması (Y5-8) | 0,30$—1,00$ | 38,25 milyon $—127,5 milyon $ | Çok uluslu zincir/orta ölçekli teknoloji, yuvarlak B-C | Orta Piyasa PE |
| Ölçek dönemi (Y8+) | 1,00$+ | 127,5 milyon $+ | Büyük ölçekli satın almalar, Halka Arz Öncesi | Büyük ölçekli PE/Büyüme aşaması VC |

### 9.2 Yatırım karar verme süreci

Proje keşfi (≥5.000 LIGHT) → bağımsız durum tespiti → 72 saat kamu duyurusu → iki boyutlu oylama → 24/72 saat uygulama.

### 9.3 Çıkış ve kar dağıtımı

Yıllık temettü: **%40** alt token sahipleri / **%30** sabit kasa / **%20** imha için LIGHT geri satın alma / **%10** sigorta fonu.
Çıkış geliri: **%70** Stabil Kasa / **%30** Yeniden Satın Alma ve Yakma.

### 9.4 Yatırım Disiplini

| Kurallar | İçerik |
|------|------|
| Tek imha sınırı | Kalan kasa × %15 (başlangıçta 850 milyon × %15 = 127,5 milyon jeton) |
| Tek hedef | Kasanın toplam değerinin ≤%25'i |
| Sanayi yoğunlaşması | Portföyün ≤%40'ı |
| Coğrafi konsantrasyon | Portföyün ≤%30'u |
| İstikrarlı hazine rezervleri | TGE'de (açık artırmada) 5 milyon dolar, 24. ayda 8 milyon dolara ulaştı |
| Bekleme süresi | 2 ardışık arıza → 180 gün |

**Kasa kapasitesi:** 850 milyon parça × 0,10 ABD doları = 85 milyon ABD doları (başlangıçtaki toplam kapasite); × 0,30 ABD Doları = 255 milyon ABD Doları; × 1,00 ABD Doları = 850 milyon ABD Doları. %15 tek işlem limiti, yatırım temposunun fiyatla pozitif ilişkisini sağlıyor.

> **[Bu bölümdeki terminoloji]**
> **FAVÖK** (Faiz, Vergi, Amortisman ve Amortisman Öncesi Kazanç): Bir şirketin temel operasyonlarının karlılığını ölçen, mali yapının (faiz), vergi politikasının (vergi) ve muhasebe tercihlerinin (amortisman/amortisman) müdahalesini ortadan kaldıran, işletmeler arası ve sektörler arası karşılaştırmaları kolaylaştıran bir gösterge. FAVÖK marjı = FAVÖK ÷ faaliyet geliri.
> **DCF** (İndirgenmiş Nakit Akışı, indirgenmiş nakit akışı yöntemi): Şirketin gelecekteki beklenen nakit akışlarını belirli bir iskonto oranıyla bugünkü değere dönüştüren değerleme yöntemidir. Sabit nakit akışına sahip olgun işletmeler (tüketici zincirleri gibi) için uygundur, ancak henüz kârlı olmayan erken aşamadaki teknoloji şirketleri için uygun değildir.
> **IPO** (İlk Halka Arz): Bir şirketin ilk kez halka açık olarak borsada hisse ihraç etmesi ve işlem görmek üzere listelenmesidir. LightDAO için yatırım yapılan şirketlerin halka arzı, büyüme motorlarının ana çıkış yollarından biridir.
> **Halka arz öncesi**: Şirket resmi olarak listelenmeden önce özel sermaye finansmanının son turu. Genellikle değerleme halka arz sonrası seviyeye yakındır, risk önceki turlara göre daha düşüktür ancak getiri katsayısı da daha düşüktür.
> **TWAP Uygulaması** (Zaman Ağırlıklı Ortalama Fiyat Uygulaması): Büyük miktardaki geri alım emirlerini birden fazla küçük miktarlı emirlere bölün ve tek bir büyük emrin piyasa fiyatı üzerindeki etkisini önlemek için bunları belirli bir süre boyunca eşit şekilde uygulayın. LightDAO, tek bir geri alımın ortalama günlük işlem hacminin %5'ini aşmamasını şart koşuyor.

---

## Bölüm 10: Yol Haritası

| Aşama | Zaman | Temel Hedefler | Önemli Kilometre Taşları | Önkoşullar |
|------|------|---------|-----------|---------|
| Hazırlık dönemi | 4. Çeyrek 2026 | Tüzel kişilik + ekip + mevcut fonlar | Cayman/BVI varlık kaydı tamamlandı; teknik ortak veya geliştirme ekibi imzalandı; stratejik yatırımcı niyeti doğrulandı (2-3 şirket); başlangıç ​​sermayesi ≥ 150.000 $ | kurucu kimlik açıklama yöntemini belirler; BP ve Pitch Deck'in tamamlanması |
| Geliştirme dönemi | 2027 1. Çeyrek-2. Çeyrek | Çekirdek sistem geliştirme | 10 akıllı sözleşme modülü geliştirildi; PWA ön uç geliştirmesi tamamlandı; 7 doğrulayıcı test ağı devreye alındı; dahili Alfa testi geçti | Geliştirme ekibi mevcut; gereksinimler belgesi (teknik özellikler) sonuçlandırıldı |
| Denetim ve test dönemi | 3. Çeyrek 2027 | Güvenlik ve uyumluluk doğrulaması | Bağımsız güvenlik denetim raporunun yayınlanması (≥1 üst kurum); yasal uyumluluk görüş mektubunun yayınlanması (MLM + menkul kıymetler kanunu); 50.000 eş zamanlı stres testi geçildi; hile karşıtı sistem yanlış pozitif oranı <%2; yönetim oylaması çalışması tamamlandı | Sözleşme geliştirmenin dondurulması (Kod Dondurma); denetim ücretleri uygulanıyor |
| TGE ve ana ağ çevrimiçi | 4. Çeyrek 2027 | Token ihracı + ağ lansmanı | Hollanda açık artırması tamamlandı (hedef 15 milyon dolar); ana ağ çevrimiçi (≥10 doğrulayıcı); halka açık madencilik platformu; DEX likidite havuzu kuruldu; tohum airdrop'u düzenlendi | Denetim geçti; doğrulayıcılar ≥7 (kesin sonuç); açık artırma sözleşmesi dağıtımı |
| İnanç oluşturma dönemi | 2028 1. Çeyreği (TGE'den sonraki 1. ila 3. ay) | 30.000-50.000 tohum kullanıcısı | Aktif madenciler 30.000'i aştı; ilk yönetişim oylama uygulaması; çok dilli topluluk kanalı kuruldu (İngilizce/Çince/İspanyolca/Portekizce/Filipinler); ilk aylık topluluk raporu yayınlandı | TGE tamamlandı; topluluk operasyonları ekibi hazır |
| Değer sabitleme dönemi | 2028'in 2. Çeyreği - 3. Çeyreği (TGE'den sonraki 4. ila 9. aylar) | İlk yatırım + geçiş dönemi yönetimi | İlk yatırım teklifi kabul edildi (oluşturma döneminde çoklu imza onayı 4. ila 6. ay arasında geçerlidir; geçiş döneminde ortak onay 7. aydan itibaren geçerlidir); ilk SPV teslimatı tamamlandı; doğrulayıcılar seçime açıktır (7. aydan itibaren); ilk üç aylık mali rapor yayınlandı | istikrarlı hazine USDC≥5 milyon$; yatırım hedefi durum tespiti tamamlandı |
| Yönetişim olgunluk dönemi | 2028 4. Çeyrek-2029 1. Çeyrek (TGE'den sonraki 10. ila 15. ay) | Komite seçimi + merkezi olmayan yönetime geçiş | Yönetim komitesinin ilk seçimi (13. ay); Vade dönemine girilmesi (Komitenin 3/5 kararı); wLIGHT çapraz zincir köprüsü çevrimiçi oluyor; CEX listeleme başvurusu gönderildi; Geliştirici finansman planı başlıyor | Aktif madenciler ≥ 100.000; ≥ 100 ortak adaylara hitap ediyor |
| Ekolojik genişleme dönemi | 2029'un 2. çeyreğinden itibaren (16. ay + TGE'den sonra) | Büyük ölçekli çoğaltma | Aktif madenciler 200.000-500.000'i aştı; 2-3 yatırım tamamlandı; ilk kârın ülkesine geri gönderilmesinin doğrulanması; LIGHT'ın geri alımı ve imhası başladı | Yönetişim komitesi normal şekilde çalışıyor; yatırım modeli doğrulandı |
| Olgun operasyon dönemi | 2029'un 4. çeyreğinden itibaren (25. ay + TGE'den sonra) | Volanın dönüşü + tam özerklik | Özerklik dönemine girilmesi (tüm sahiplerden gelen önemli teklifler); kümülatif yatırım portföyü dağıtımı ≥ 30 milyon $; deflasyon verileri kamuya açık olarak doğrulanabilir | Yönetişim tamamen merkezi değildir |

**Yol haritası tasarım ilkeleri:**

- **TGE öncesi denetim:** Tokenlar asla bağımsız bir güvenlik denetimi tamamlanmadan verilmeyecektir. Bu, kullanıcı fonlarının güvenliğinin temel garantisidir.
- **Doğrulayıcılar kullanıcılardan önce gelir:** Ana ağ çevrimiçi olduğunda, 10'dan fazla doğrulayıcı (BFT hata toleransı f≥3) bulunarak ağın tek bir arıza noktası nedeniyle kapanmamasını sağlar.
- **Yatırım genişlemeden önce gelir:** Ancak ilk yatırım başarılı olduktan ve doğrulanabilir kâr getirisi sağladıktan sonra büyük ölçekli genişlemeye girebiliriz. "Önce insanları dolaştırıp sonra projeleri bularak" arabayı atın önüne koymaktan kaçının.
- **Zaman Arabelleği:** Her aşama için %20-30 zaman arabelleği ayırın. Teknoloji geliştirme, denetim onarımları ve yasal süreçlerin tümü beklentileri aşabilir ve yol haritası "en iyimser senaryo" olmamalıdır.

**Beyaz Kitap ile İlişki Yayın Tarihi (4 Ağustos 2026):** Beyaz Kitap, projenin vizyonunu ve teknik tasarımını açıklayan bir kamu açıklaması olarak Ağustos 2026'da yayınlandı. Fiili uygulama 2026 yılının 4. çeyreğinde (hazırlık dönemi) başlayacak ve TGE hedefi 2027 yılının 4. çeyreğidir. Teknik incelemenin yayınlanması ile TGE arasındaki yaklaşık 14 aylık boşluk, ekip oluşturma, geliştirme, denetim ve uyumluluk hazırlığı için kullanıldı.

---

## Bölüm 11: Topluluk Kültürü ve Geliştirici Ekolojisi

### 11.1 Dört Değer

- **Şeffaflık mükemmellikten iyidir** - Kusurları ortaya çıkarmak, mükemmelliği gizlemekten daha iyidir. Tüm hazine akışları, yatırım kararları ve yönetişim oyları zincirde kalıcı olarak mevcuttur.
- **Kademeli olarak radikal olmaktan iyidir** - Küçük adımlar atın ve yinelemeye devam edin. İlk yatırım 2-5 milyon dolardan başlayacak, model doğrulandıktan sonra ölçek genişletilecek.
- **Sorumluluklar haklardan daha iyidir** - Haklar ve yükümlülükler eşittir. Yönetim komitesi üyeleri 50.000 LIGHT sözü vermeli ve politika gündemlerini açıklamalıdır. Görevlerini yerine getirmemeleri durumunda para cezasına çarptırılacaklar.
- **Çeşitlilik homojenlikten iyidir** - Farklı sesler sistemin bağışıklığıdır. İki boyutlu oylama (coin + adres), hem balinaların hem de perakende yatırımcıların söz sahibi olmasını sağlar.

### 11.2 Jüri sistemi

| Boyutlar | Kurallar |
|------|------|
| Kompozisyon | 10.000'den fazla LIGHT'a sahip olan ve herhangi bir ihlal kaydı olmayan 12 kullanıcıyı rastgele seçin |
| Dönem | 30 gün, süre dolduktan sonra tekrar rastgele çekilecek |
| Sorumluluklar | Hile karşıtı ceza şikayetlerini, teklif dolandırıcılığı suçlamalarını ve topluluk anlaşmazlıklarını dinleyin |
| Süreç | Cezalandırılan kullanıcılar 72 saat içinde kanıt sunabilir; jüri 48 saat içinde karar vermeli |
| Yargı standartları | 12 kişiden ≥8'i (2/3 çoğunluk) cezanın sürdürülmesini veya iptal edilmesini kabul etmelidir |
| Kaçınma | Taraflarla davet ilişkisi bulunan veya aynı IP aralığında yer alan jüri üyelerinin otomatik olarak değiştirilmesi |
| Ücretlendirme | Dönem boyunca günlük 5 LIGHT tutarında jüri hizmeti sübvansiyonu alın (ekolojik fondan ödenir) |

### 11.3 Geliştirici Ekolojik Planı

| Modül | İçerik | Finansman Kaynakları | Nasıl Başvurulur |
|------|------|---------|---------|
| Geliştirici Finansmanı (Hibeler) | LightDAO zincirinde dApp'ler, araçlar ve altyapı oluşturan ekipler için, LIGHT | Ekolojik Kalkınma Fonu (Doğrusal Sürüm Aşama 2) | Teklif gönderin → Teknik inceleme görevlisi değerlendirmesi → Yönetişim oylaması (mikro teklif süreci) |
| SDK ve API | Üçüncü taraf geliştirme eşiğini düşürmek için JavaScript/TypeScript SDK'sı, REST API'si ve WebSocket arayüzleri sağlayın | Teknik inceleme görevlisi gelişime öncülük ediyor | Açık kaynak, GitHub'ta herkese açık |
| Hackathon | Her üç ayda bir, LIGHT |'a eşdeğer 100.000 $ ödül havuzuyla çevrimiçi bir hackathon düzenleniyor. Ekolojik Kalkınma Fonu | Kaydı açın, eşik yok |
| Hata Ödülü | Temel sözleşme hatası ödül programı, geçerli tek bir güvenlik açığı için 1.000 ila 50.000 ABD Doları arası ödül (önem derecesine göre derecelendirilmiştir) | Sigorta Fonu + Ekolojik Kalkınma Fonu | Immunefi veya kendi oluşturduğunuz platform aracılığıyla gönderin |
| CosmWasm Sözleşme Piyasası | Üçüncü tarafları akıllı sözleşmeleri uygulamaya teşvik edin ve gaz ücreti gelirinin %20'si geliştiricileri desteklemek için ekolojik hazineye iade edilecek | Gaz ücreti dağıtımı (bkz. Bölüm 4.5) | Otomatik, başvuru gerektirmez |

### 11.4 Çoklu dil ve yerelleştirme stratejisi

| Boyutlar | Planlama |
|------|------|
| Platform dili | Başlangıçta İngilizce, Çince, İspanyolca, Portekizce ve Filipinceyi destekler; Fransızca, Arapça, Svahili ve Endonezce 6. aydan itibaren eklenecek |
| Yönetişim dili | Teklifler ve kampanya platformları her dilde kabul edilir ve sistem, makine çevirisi + topluluk kılavuzunun redaksiyonunu sağlar |
| Topluluk Operasyonları | Dile göre bağımsız topluluk kanalları (Discord/Telegram) oluşturun ve her kanal yerelleştirilmiş topluluk irtibat gönüllüleriyle donatılmıştır |
| Belge Çevirisi | Teknik incelemeler ve temel belgeler topluluk çeviri gönüllüleri tarafından doldurulur ve çeviri katkıları "İçerik Katkısı" davranış bonusuna (%5) dahil edilir |
| Yerelleştirme Finansmanı | Ekolojik kalkınma fonunun %10'u (40 milyon jeton) yerelleştirme topluluğu oluşturma ve çeviri teşviklerine ayrıldı |

---

## Bölüm 12: Ekip ve Danışmanlar

### 12.1 Temel rol tanımı

| Rol | Sorumluluklar | Arka Plan Gereksinimleri | Açıklama Yöntemleri |
|------|------|---------|---------|
| İlk Koruyucu/Proje Sponsoru | İlk sözleşmeleri dağıtın, belgeleri koruyun ve erken operasyonları koordine edin | Akıllı sözleşme dağıtımı veya DeFi protokol operasyon kayıtları ile blockchain sektöründe ≥ 3 yıllık deneyim | TGE'den önce gerçek kimliğinizi açıklayın veya üçüncü taraf kimlik doğrulama raporu sağlayın (noter imzası + zincir üstü mesaj doğrulaması gibi) |
| Teknik lider | Sözleşme mimarisi tasarımı, geliştirme ekibi yönetimi, denetim yerleştirme | Cosmos SDK/CosmWasm geliştirme deneyimi, üretim zinciri dağıtım kaydı | Yukarıdakinin aynısı |
| Sorumlu yatırım sorumlusu | Hedef taraması, durum tespiti koordinasyonu, SPV kurulumu, çıkış yönetimi | Özel sermaye/risk sermayesi sektöründe tamamlanmış çıkış senaryolarıyla deneyim | Yukarıdakinin aynısı |
| Uyumluluk danışmanı | Yasal yapı tasarımı, düzenleyici yerleştirme, MLM uyumluluk danışmanlığı | ABD/AB/Cayman niteliklerine sahip avukat | Kamu hukuku firmasının adı (kabul etmediğim sürece kişisel adım açıklanmayacaktır) |

### 12.2 Danışma Kurulu

- 3-5 bağımsız danışmandan oluşur ve şunları kapsar: DePIN teknolojisi, sınır ötesi yatırım uyumluluğu, topluluk operasyonları ve tüketici endüstrileri;
- Danışmanlar, LIGHT tokenleri (stratejik işletme fonunun "tokenlar için hizmet alışverişi" kısmından ödenir) şeklinde danışmanlık ücreti alırlar ve 12 ay boyunca kilit altında tutulurlar;
- Danışmanların listesi TGE'den önce kamuya duyurulur ve topluluk araştırmalarına açıktır (merkezi olmayan metin sorgulama toplantısı, bkz. Bölüm 7.5);
- Danışmanlar aynı anda Yönetim Komitesi üyesi olarak görev yapamazlar (çıkar çatışması ayrımı).

### 12.3 Ekip Taahhüdü ve Kısıtlamalar

| 约束 | 规则 |
|------|------|
| 代币锁仓 | 核心团队持有的LIGHT（含战略运营基金分配）须锁仓12个月，解锁后线性释放36个月 |
| 出售限制 | 初始监护人在任期内（≤24个月）不得出售通过任何渠道获得的LIGHT（含空投、奖励、薪酬） |
| 利益冲突 | 团队成员的利益冲突须在任命时完整披露（是否持有其他DAO代币、是否与潜在投资标的存在关联） |
| 未披露后果 | 未披露利益冲突一经查实，永久禁止参与治理，已解锁代币的50%罚没至保险基金 |
| 替换机制 | 核心角色离职或失能时，由治理委员会（成立前由初始监护人+备选监护人）指定继任者，须经社区公示72小时无异议 |

### 12.4 Temel katılımcı tazminatı (stratejik işletme fonunun %20'si)

- Toplam tutar: 50 milyon LIGHT (toplam tutarın %2'sine karşılık gelir)
- Kapsanan kişi sayısı: 3-5 kişi
- Sürüm kuralları: Aralık uçurumu + 36 ay doğrusal (yani 13. aydan itibaren her ay yaklaşık 1.157 milyon coin piyasaya sürülecek)
- Dönüm noktası bağlayıcılığı: Her üç ayda bir, yönetim komitesi (ilk vasi + kuruluştan önceki bağımsız üçüncü taraf), üç aylık kota kaldırılmadan önce dönüm noktasına ulaşıldığını doğrular.
- Açıklama kuralları: Sadece toplam miktar ve yayın kuralları açıklanır, kişi isimleri ve tek kişilik kotalar açıklanmaz (Gizliliğin korunması amacıyla ve aynı zamanda toplam tutarın aşılmadığı zincirdeki çoklu imza adresi üzerinden doğrulanabilir)

---

## Bölüm 13: Risk Uyarısı ve Sorumluluk Reddi

### 13.1 Risk uyarısı

| Risk türü | Açıklama | Etki azaltıcı önlemler |
|---------|------|---------|
| Piyasa Riski | LIGHT fiyatları önemli ölçüde dalgalanabilir ve geçmiş fiyatlar gelecekteki performansı temsil etmez. TGE'nin başlangıç ​​likiditesi sınırlıdır ve fiyatlar şiddetli dalgalanabilir | Hollanda müzayede fuarı fiyatlandırması; ±%50 devre kesiciler TGE'den 72 saat sonra; ölüm karşıtı sarmal dört seviyeli müdahale mekanizması |
| Proje Riski | Yatırım hedefi zarara uğrayabilir, risk sermayesi projesi başarısız olabilir ve ana paranın tamamı kaybolabilir. PE/VC endüstrisinin tarihsel ortalama başarısızlık oranı yaklaşık %50-70'tir (tek işlem) | Çift motorlu merkezi olmayan yönetim (%70 nakit akışı + %30 büyüme); tek hedef ≤ %25; endüstri ≤ %40; bölge ≤ %30; Sigorta fonları için %10 provizyon |
| Teknik riskler | Akıllı sözleşmelerin keşfedilmemiş güvenlik açıkları olabilir; tarayıcı uyumluluğu madencilik deneyimini etkileyebilir; zincirler arası köprülere saldırı yapılabilir | Bağımsız denetim + TGE nezdinde resmi doğrulama; Hata Ödülü 1.000 - 50.000 $; 72 saatlik zaman kilidi; çoklu imzalı süspansiyon mekanizması |
| Mevzuat riskleri | Çeşitli ülke ve bölgelerdeki düzenleyici politikalar değişebilir ve bu durum sınırlı işlevlere veya belirli bölgelerdeki kullanıcıların katılamamasına neden olabilir | Cayman SPV yapısı; varsayılan sıfır doğrulaması (doğrulama, hizmet tarafında lisanslı bir üçüncü taraf tarafından gerçekleştirilir); ön uç IPFS aynası sansüre dayanıklıdır; belirli ülkelere pazarlanmıyor |
| Likidite riski | Alt token erken aşamada yeterli işlem derinliğine sahip olmayabilir; LIGHT, TGE'nin erken aşamasında satış baskısıyla karşı karşıya kalabilir | Alt token AMM'nin başlangıç ​​likiditesi (ihracın %6'sı); 30 günlük transfer kilitleme süresi; Ekip/yatırımcı 12 aylık uçurum + 36 aylık doğrusal |
| Seyrelme riski | Aktif madencilerin sayısı arttıkça kişi başına düşen madencilik geliri doğal olarak azalacaktır (BaseReward paydası artar) | Tasarım amacı: İlk katılımcılar daha yüksek getiri elde etmek için daha yüksek risk alırlar; daha sonraki kullanıcılar davetiye paylaşımı yoluyla birikimi hızlandırabilir; yönetişim eşiği dinamik olarak düşürülüyor |
| Operasyonel risk | Yatırım yapılan şirketin işleyişi ve yönetimi beklentileri karşılayamayabilir; SPV operasyonları üçüncü taraf direktörlere dayanır; yatırım ekibi kaybolabilir | SPV tüzüğü kısıtlamaları + bağımsız direktörler; DAO, yöneticileri değiştirmek için oy kullanabilir; SIAC/ICC tahkim hükümleri; kilit kişi sigortası (araştırma aşamasında) |
| Zincirler arası köprü riskleri | wLIGHT çapraz zincirli köprü üçüncü bir tarafça işletilmektedir ve köprü sözleşmesindeki boşluklar varlık kayıplarına yol açabilir (geçmişte çapraz zincirli köprüler en büyük tek kayıp kaynağıdır) | Köprü çevrimiçi hale gelmeden önce bağımsız denetim; köprü varlıkları toplam arzın %5'ini geçmez; risk açıklaması; kullanıcılar yalnızca yerel zinciri kullanmayı seçebilir |
| Doğrulayıcı riski | Doğrulayıcıların toplu olarak çevrimdışı olması veya kötülük yapması, zincirin blok üretimini askıya almasına ve tüm kullanıcı işlemlerinin (madencilik, oylama, transferler) geçici olarak kullanılamamasına neden olabilir | Tendermint BFT <1/3 kötülüğü tolere eder; doğrulayıcılar ≥ 21 (f=6); Kesici ceza; acil göç oylama mekanizması |

### 13.2 Sorumluluk reddi beyanı

- LIGHT ve alt tokenler menkul kıymet değildir, gerçek değeri yoktur ve fiyatı sıfıra dönebilir. Bu tanıtım yazısı herhangi bir menkul kıymet ihraç belgesi, yatırım teklifi veya yatırım tavsiyesi niteliğinde değildir.
- Anlaşmanın gelir dağılımı, dayanak varlıkların fiili işletme performansına bağlıdır ve geçmiş veriler gelecekteki geliri temsil etmez. Yatırım getirilerine ilişkin her türlü açıklama ileriye dönük tahminlerdir ve vaat değildir.
- Kullanıcı, özel anahtarın kaybolması veya sızmasından kaynaklanan tüm zararları karşılamalıdır ve sözleşme, geri alma hizmetleri sağlamamaktadır. Tier 1 (Passkey) veya Tier 2 (Sosyal Kurtarma) cüzdanı kullanmak bu riski azaltır ancak ortadan kaldırmaz.
- Bu sözleşme dünyanın her yerindeki kullanıcılara açıktır (geçerli yasa ve düzenlemelere tabidir). Kullanıcılar, kendi yetki alanlarında şifrelenmiş varlıklara, DAO kuruluşlarına ve SPV gelir sertifikalarına yönelik yasal tutumu doğrulamalı ve katılımlarının yasal ve uyumlu olmasını sağlamalıdır.
- Bu tanıtım belgesindeki ileriye dönük beyanlar (yol haritaları, gelir modelleri, deflasyon tahminleri, yatırım ölçeği tahminleri dahil) mevcut varsayımlara dayanan tahminlerdir ve gerçek sonuçlar pazar, teknoloji, mevzuat, ekip uygulaması ve diğer faktörler nedeniyle önemli ölçüde farklılık gösterebilir.
- Davet teşvikleri tek düzeyli bir paylaşım mekanizmasıdır ve çok düzeyli pazarlama veya saadet zinciri oluşturmaz. Ancak kullanıcıların yine de kendi yetki alanlarında yönlendirme ödüllerine yönelik yasal tutumu onaylamaları gerekir.
- LightDAO ekosistemine katılmak için minimum yaş 18'dir (veya yargı alanınızdaki yasal reşit olma yaşı (hangisi daha yüksekse). Küçüklerin madencilik, yönetim veya yatırım faaliyetlerine katılmasına izin verilmez.

---

## Ek A: Temel parametrelerin özet tablosu

| Kategori | Parametre | Değer |
|------|------|------|
| Düzenleme | Toplam tutar | 2,5 milyar adet, bir daha asla ihraç edilmedi |
| Düzenleme | madencilik | %40 = 1 milyar jeton |
| Düzenleme | Yatırım Kasası | %34 = 850 milyon jeton |
| Düzenleme | Ekolojik Fon | %16 = 400 milyon adet |
| Düzenleme | Stratejik Operasyonlar | %10 = 250 milyon jeton (hizmet %50/finansman %30/katkıda bulunanlar %20) |
| Düzenleme | Yarılanma döngüsü | 2 yılda bir |
| Düzenleme | İlk Çağ Günü Yayını | ≈684.900 (madenciler %95 = 650.700, doğrulayıcılar %5 = 34.200) |
| Düzenleme | Blok başına ödül havuzu | ≈13,87 IŞIK |
| madencilik | Katkı ağırlığı | Bant genişliği %40/oturum %30/doğrulama %20/kararlılık %10 |
| madencilik | Tam bonus | 1,44 kez |
| Davetiye | Evangelist/Büyükelçi/Ortak | 3 kişi %10+100L/10 kişi %15+500L+%5/50 kişi %20+2500L+%10 |
| Davranış | Dört ürün × %5 | Üst sınır %20 |
| Gaz ücreti | Fiyatlandırma mekanizması | USD eşdeğeri demirleme, her 24 saatte bir kahin tarafından otomatik olarak LIGHT miktarına dönüştürülür |
| Gaz ücreti | Olağan transfer | 0,001 ABD Doları eşdeğeri (@0,05 ABD Doları=0,02 IŞIK) |
| Gaz ücreti | Yönetişim oylaması | 0,005 ABD Doları eşdeğeri (@0,05 ABD Doları=0,10 IŞIK) |
| Gaz ücreti | Dağıtım kuralları | %50 imha / %30 doğrulayıcılar / %20 ekolojik hazine |
| Deflasyon | Yavaşlama/erken uyarı/sonuç | ≤1,5 milyar/≤1,2 milyar/≤1 milyar (dolaşım hacmi) |
| Deflasyon | Teorik üst sınır | 1,65 milyar (10+4+2,5, hazinedeki 850 milyon hiçbir zaman dolaşıma girmeyecek) |
| Yönetişim | Teklif Eşiği | ≥5.000 LIGHT + 30 günlük stake |
| Yönetişim | Komite Staking | 50.000 IŞIK + 100 Adres |
| YÖNETİM | JÜRİ | 10.000 IŞIK |
| Yönetişim | Bahis | 5—500 IŞIK |
| Yönetişim | İtibar bonusu | 1 yıl +15 oy → +%30 (toplam sınır +%40) |
| Yatırım | Tek limit | Kasada kalan × %15 (başlangıçta 127,5 milyon jeton) |
| Yatırım | Temel konuşlandırılabilir | 850 milyon × 0,15 $ × %75 = 95,63 milyon $ ≈ 100 milyon $ |
| Yatırım | Kâr dağıtımı (yıllık) | 40/30/20/10 |
| Yatırım | Kâr dağıtımı (çıkış) | 70/30 |
| Açık artırma | Hedef | 15 milyon $ (5 milyon $ rezerv + 10 milyon $ yatırılan sermaye) |
| Rezervler | İstikrarlı Hazine | TGE 5 milyon $ → 24. Ay 8 milyon $ |
| Sigorta | Kâr | Kâr %10 |
| Airdrop | Toplam bütçe | 55 milyon (ekolojik fon %13,75), CAC≈55$/tutulan kullanıcı |
| Doğrulayıcılar | Harf/Başlık | 21 (minimum 10) / 100 |
| Doğrulayıcı | Minimum bahis | 500.000 IŞIK |
| Doğrulayıcı | TGE zor sonuç | ≥7, aksi takdirde çevrimiçi olmasına izin verilmeyecektir |

---

## Ek B: Sayısal türetme ve doğrulama

### B.1 Madencilik çıktısı

2A=1 milyar →A=500 milyon. Günlük sürüm = 500 milyon ÷ 730 = 684.932 ≈ 684.900. Madencilik havuzu=684,932×95%=650,685≈650,700. Doğrulayıcılar=684,932×%5=34,247≈34,200. Her blok=684,932÷49,371≈13,87. Doğrulama: 684,932×730=499,999,960≈500 milyon ✓

### B.2 Yönetişim eşiği erişilebilirliği

100.000 madenci karşılaştırması (6,51/gün, ortak 74,44/gün): teklif 5.000→768 gün/67 gün; komite 50.000→7.684 gün (21 yıl)/672 gün (22 ay); jüri 10.000→1.537 gün (4,2 yıl)/134 gün (4,5 ay); bahis 500→77 gün/6,7 gün.

Başlangıç ​​dönemi (10.000 madenci, 65,07/gün, ortaklar 744,4/gün): teklif → 77 gün (2,5 ay) / 6,7 gün; komite → 768 gün (25 ay) / 67 gün (2,2 ay); jüri → 154 gün (5 ay) / 13,4 gün.

### B.3 Deflasyon Zaman Çizelgesi

Dolaşım hacmi = madencilik + ekoloji + strateji (haklı) - takas - Gaz - geri satın alma. Hazinedeki 850 milyon asla dolaşıma girmeyecek.

| Yıl | Kümülatif Madencilik | Ekoloji | Strateji | Değişim | Gaz | Geri alım | Dolaşım |
|----|---------|------|------|------|-----|------|--------|
| 1 | 2.50 | 2.80 | 0 | 0 | 0.01 | 0 | ≈5,29 |
| 2 | 5.00 | 4.00 | 0.83 | 0,05 | 0.02 | 0 | ≈9,76 |
| 3 | 6.25 | 4.00 | 1.67 | 0.20 | 0.03 | 0,05 | ≈11.64 |
| 4 | 7.50 | 4.00 | 2.50 | 0,45 | 0.04 | 0.20 | ≈13,31(tepe) |
| 5 | 8.13 | 4.00 | 2.50 | 0,80 | 0,05 | 0,50 | ≈13.28 |
| 6 | 8.75 | 4.00 | 2.50 | 1.20 | 0.06 | 0,90 | ≈13.09 |
| 7 | 9.06 | 4.00 | 2.50 | 1.60 | 0.07 | 1.40 | ≈12,49 |
| 8 | 9.38 | 4.00 | 2.50 | 2.00 | 0.08 | 1.90 | ≈11.89 |
| 9 | 9.53 | 4.00 | 2.50 | 2.40 | 0.09 | 2.30 | ≈11.24 |
| 10 | 9.69 | 4.00 | 2.50 | 2.80 | 0.10 | 2.70 | ≈10.59 |
| 11 | 9.77 | 4.00 | 2.50 | 3.10 | 0.11 | 3.00 | ≈10.06 |
| 12 | 9.84 | 4.00 | 2.50 | 3.40 | 0.12 | 3.30 | ≈9.52 |

Sonuç: Zirve Y4≈1,331 milyar; Y8 1,2 milyarlık uyarı çizgisine dokundu; 1 milyarlık alt sınıra Y11-12 ulaşıyor; 1,5 milyarlık yavaşlama çizgisi yalnızca son derece düşük bir yıkım senaryosudur.

---

## Ek C: Denetim düzeltme günlüğü (toplam 36 öğe)

Bu turda 22 orijinal öğe (L1-5, A1-4, D1-4, M1-8, G1-3) + 7 teknik mimari öğesi (T1-7) + 7 ekonomik model optimizasyon öğesi içerir:

| Sayı | Düzeltme |
|------|------|
| E-1 | Toplam tutar 2,1 milyar → 2,5 milyar (yatırım kapasitesi kısıtlamalarından kaynaklanmaktadır) |
| E-2 | Tahsis 50/30/20→40/34/16/10 (yeni stratejik işletme fonlarının %10'u) |
| E-3 | Hollanda açık artırması 10 milyon $→15 milyon $ (başlangıç ​​yatırım sermayesi 5 milyon $→10 milyon $) |
| E-4 | Yeni 5,7 bölümlü airdrop büyüme planı (55 milyon parça, CAC 55 $/kişi) |
| E-5 | Doğrulayıcılar aşamalı olarak başlatılır (Testnet 7→TGE minimum 10/Target 21→Open 100) |
| E-6 | Deflasyon tetikleme hattı ayarı (14/12/10 → 15/12/10, 1,65 milyar dolaşım sınırına uyarlandı) |
| E-7 | Tüm harici alıntıları doğrulanabilir kaynaklarla değiştirin (doğrulanamayan SSRN belgelerini kaldırın) |

---

## Ek D: Hızlı Terimler Dizini

Her terimin tam açıklaması, ilk göründüğü bölümün sonundaki [Bu Bölümdeki Terimler] yorum bloğunda belirtilmiştir. Bu dizin, hızlı gezinme için tüm terimleri ve bölümlerini alfabetik sırayla listeler.

| Terminoloji | Tanım Bölüm |
|------|---------------|
| AMM (Otomatik Piyasa Yapıcı) | Bölüm 4 |
| BFT (Bizans Hata Toleransı) | Bölüm 4 |
| CAC (Müşteri Kazanma Maliyeti) | Bölüm 5 |
| CEX (Merkezi Borsa) | Bölüm 4 |
| Cosmos SDK'sı | Bölüm 4 |
| KozmWasm | Bölüm 4 |
| DAO (Merkezi Olmayan Özerk Organizasyon) | Bölüm 2 |
| DCF (İndirgenmiş Nakit Akışı Yöntemi) | Bölüm 9 |
| DePIN (Merkezi Olmayan Fiziksel Altyapı Ağı) | Bölüm 2 |
| DEX (Merkezi Olmayan Borsa) | Bölüm 4 |
| FAVÖK (faiz, vergi, amortisman ve amortisman öncesi kazanç) | Bölüm 9 |
| Gaz Ücreti | Bölüm 4 |
| IBC (Zincirler Arası İletişim Protokolü) | Bölüm 3 |
| IPFS (Gezegenlerarası Dosya Sistemi) | Bölüm 4 |
| KYC (Müşterinizi Tanıyın) | Bölüm 3 |
| LIGHT (yerel belirteç) | Bölüm 4 |
| LP (Likidite Sağlayıcı) | Bölüm 5 |
| Alt Orta Piyasa PE (Alt Orta Piyasa Özel Sermayesi) | Bölüm 2 |
| Merkle Ağacı | Bölüm 4 |
| MiFID II (Finansal Araçlar Yönergesi II'de AB Piyasaları) | Bölüm 3 |
| MLM (Çok Düzeyli Pazarlama) | Bölüm 3 |
| PII (Kişisel Tanımlayıcı Bilgiler) | Bölüm 3 |
| PoC (Katkı Kanıtı) | Bölüm 4 |
| PoS (Stake Kanıtı) | Bölüm 4 |
| PoW (İş Kanıtı) | Bölüm 4 |
| Halka Arz Öncesi | Bölüm 9 |
| PWA (Aşamalı Web Uygulaması) | Bölüm 4 |
| Reg D / Reg S (ABD Menkul Kıymetler Kanunu D/S Yönetmeliği) | Bölüm 3 |
| Kesme | Bölüm 4 |
| SPV (Özel Amaçlı Araç) | Bölüm 2 |
| TGE (Token Oluşturma Etkinliği) | Bölüm 5 |
| TWAP (Zaman Ağırlıklı Ortalama Fiyat) | Bölüm 4 |
| TWAP Gerçekleştirme (Geri Alım ve Bölünmüş Emirler) | Bölüm 9 |
| VWAP (Hacim Ağırlıklı Ortalama Fiyat) | Bölüm 5 |
| wLIGHT (kapsüllü IŞIK) | Bölüm 5 |
| ZK-KYC (Sıfır Bilgi Kanıtı KYC) | Bölüm 3 |
| Alt belirteç | Bölüm 5 |
| Ölüm Sarmalı | Bölüm 5 |
| Yarıya indirme | Bölüm 5 |
| Hazine (Hazine) | Bölüm 5 |
| Hollanda Müzayedesi | Bölüm 5 |
| Kahin | Bölüm 4 |

---

**Tam beyaz kağıt biter**

**Telif Hakkı Bildirimi:** Bu belge açık kaynaklı bir topluluk belgesidir ve serbestçe çoğaltılabilir ancak içeriğin tamamının korunması gerekir.

---

# Ek: Ana ağ tarafından doğrulanan parametreler ve adresler (V2.4 canlı)

## A. §4.5 Gas 经济实测参数
- min-gas-price 公式:`(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas`;当前 TransferUsdTarget=$0.001、UsdPerLight=$0.05、RefTransferGas=100000 → **0.2 ulight/gas**
- 分配实测(总 fee 300000 ulight):销毁 150000(50%)/ 金库 60000(20%)/ 验证者 90000(30%),精确匹配
- 销毁地址:`wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu`(确定性死地址)
- 金库:`treasury_multisig` 合约(3/5 多签;链上 `signers` 查询返回 5 名签名人,阈值本身不在查询接口内)

## B. 核心合约地址
见仓库 `docs/MAINNET_STATUS.md`(light_token / mining_reward / governance / treasury_multisig / oracle_twap / vesting 等 10 合约)。

## C. Eski değerin (hissenin) elden çıkarılması
oluşum uyumsuzluğu mint_denom=stake sıfıra sıfırlandı ve ek ihraç durduruldu; mevcut hisse (yaklaşık 2,56e11 mikro birim) amaçsız bırakılmıştır ve elden çıkarma planı (takas/yok etme) yönetim önerilerini beklemektedir ve ulight ekonomik modeli etkilemeyecektir.

## D. §4.4 canlı hak kazanma
Vault 250.000.000 IŞIK, 3 bağımsız program: 75M (uçurum 0)/ 100M (uçurum 1 yıl)/ 75M (uçurum 2 yıl), zaten zincirde.

## E. 安全实践
- 主网升级为 x/upgrade 治理 + 全节点同块高协调 + auto-swap 看门狗,测试网端到端彩排后执行
- Passkey 种子仅密文存储;Shamir 分片本地不保存
- 合约挖矿根提交阈值 5(链上每笔 `submit_root` 事件实测 threshold=5;当前 5 个授权账户在签,7 席为设计目标);反女巫/反作弊见 §4.8
