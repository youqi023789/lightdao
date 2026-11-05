> Otomatik çeviri, insan tarafından gözden geçirilmedi. Anlaşmazlık durumunda Çinçe orijinal metin esas alınır.
[中文原文 / Chinese original](/whitepaper.md)

# LightDAO Teknik İncelemesi V2.4 (2026-09-26 Mainnet Canlı Sürümü)

> Bu sürüm, önde "ana ağ dağıtımı canlı" ve "sürüm değişiklikleri" bulunan V2.0 tasarım taslağını temel alır ve doğrulanmış zincir içi parametrelerle eklenir. Ana metin (Bölüm 1~12) V2.0 tasarımına göre değişmeden kalır; Gerçek durumdan herhangi bir sapma durumunda, bu bölümün önceki notları ve ekleri geçerli olacaktır.

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

**Farklılaşma:** Şu ​​anda "sıfır eşikli web madenciliği"ni "uyumlu SPV varlık yatırımı" ile birleştiren tek proje. Pi Ağından (pratik bir yardımcı program yok), Helyumdan (200 ABD dolarının üzerinde donanım gerektirir) ve geleneksel DAO'dan (yüksek eşikli elit yönetişim) farklıdır.

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

LightDAO bu insanlar için tasarlanmıştır. İnternet özellikli bir cihaz, bir tarayıcı ve az miktarda parayla ekolojik inşaata katılabilirsiniz; Uyumlu bir SPV yapısı aracılığıyla kullanıcılar aynı zamanda yüksek kaliteli şirketlerin nakit akışı dağılımına ve ileri teknoloji projelerinin erken büyümesine dolaylı olarak erişme fırsatına da sahip oluyor.

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

**Amerika Birleşik Devletleri (SEC Düzenlemesi D, Kural 501, 17 CFR §230.501):** Nitelikli yatırımcılar (Akredite Yatırımcılar) aşağıdaki koşullardan birini karşılamalıdır - bir bireyin yıllık geliri 200.000 ABD Dolarından az olmamalıdır (veya eşiyle birlikte toplam 300.000 ABD Dolarından az olmamalıdır) ve art arda iki yıl boyunca standardı karşılamış olmalıdır; veya net servetin (birincil ikamet yeri hariç) 1.000.000 ABD Dolarından az olmaması.

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

**Karşılaştırmalı Sonuç:** Kripto para birimi alanındaki kalıcı sermaye kaybı oranı, geleneksel borsaya göre çok daha yüksektir. ABD borsasındaki bireysel hisse senetlerinin yaklaşık %58'i Hazine bonolarının altında performans gösterse de yatırımcılar yine de endeks fonları aracılığıyla ortalama piyasa getirisi elde edebilirler; Kripto para piyasasında tokenlerin büyük çoğunluğu sıfıra dönüyor ve "indekslere" benzer etkili çeşitlendirme araçlarının eksikliği var.

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

**Yatırım ölçeği büyüme yolu:** Tek bir yatırımın boyutu, LIGHT fiyatı ve kasa kapasitesiyle dinamik olarak büyür - başlangıç ​​dönemi (LIGHT 0,02 - 0,05 ABD Doları), topluluk düzeyinde 2,55 milyon ABD Doları - 6,37 milyon ABD Doları arasındaki küçük varlıklar için uygundur; büyüme aşaması (0,05-0,30 dolar) bölgesel zincirlere ve 6,37 milyon dolar-38,25 milyon dolarlık (Aşağı Orta Pazar kıyaslaması) PE'deki Tohum-A turlarına giriyor; olgun aşamada (0,30$-1,00$), 38,25 milyon $ ile 127,5 milyon $ arasındaki orta piyasa PE seviyesine ulaşır; ölçek aşamasında (1,00$+), büyük ölçekli satın almaları ve 127,5 milyon doları aşan halka arz öncesi yatırımları gerçekleştirebilir. Katı kısıtlamalar: tek bir işlem, yatırım hazinesinin kalan miktarının %15'ini geçmeyecektir (ayrıntılar için Bölüm 9'a bakınız).

**İlk hedef konumlandırma ilkesi:** Belirli bir şirket adını varsaymak yerine, öncelikle bir tarama çerçevesi oluşturun - kanıtlanmış bir tek mağazalı ekonomik model, istikrarlı nakit akışı kayıtları (son üç yıldaki FAVÖK marjı %10'dan az değildir ve yıllar arası oynaklık %15'ten yüksek değildir) ve net bir bölgesel genişleme yolu gerektiren topluluk düzeyinde katı tüketici hizmetleri varlıklarına öncelik verin. Spesifik hedef topluluk önerileriyle belirlenir.

### 2.3 Temel değer önerisi

**Tarayıcı düğümdür** - Bir madencilik makinesi satın almanıza veya profesyonel bir teknik altyapıya sahip olmanıza gerek yoktur. Resmi web platformunu ziyaret ederek ağ katkılarına katılabilirsiniz.

**Herkes katılabilir** - Yönetişim eşiğine ulaştıktan sonra, küçük miktarda LIGHT sahipleri de fon tahsisinin yönüne ortaklaşa karar vermek için oylamaya katılabilir.

**Kurallara göre kâr paylaşımı** - Yatırım yapılan şirketlerin faaliyet kârları ve teknoloji projelerinin çıkış getirileri, zincir içi kurallara ve SPV düzenlemelerine uygun olarak dağıtılacaktır.

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
| SPV Şartı | SPV'nin operasyonunun DAO |
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

> Teknoloji saklıdır: Belirli bir varlık türü gelecekte yeterlilik eşikleri gerektirirse, kullanıcılar kendi kimlik bilgilerini sıfır bilgi kanıtı (ZK) biçiminde tutacak ve zincir herhangi bir kimlik bilgisi olmadan yalnızca "karşılanıp karşılanmadığını" doğrulayacaktır - bu yol haritasının bir parçasıdır ve mevcut bir gereklilik değildir.

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
| Temel çerçeve | Cosmos SDK'sı | Modüler mimari, çoklu üretim zinciri doğrulaması |
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
> **Tendermint PoS** (Proof of Stake, Proof of Stake): Doğrulayıcıların (bilgi işlem gücü için rekabet etmek yerine) token taahhüt ederek blok üretme hakkını elde ettiği bir fikir birliği mekanizması. "Anında kesinlik" sağlar; bir blok gönderildikten sonra geri alınamaz.
> **BFT** (Bizans Hata Toleransı, Bizans Hata Toleransı): Dağıtılmış bir sistemde, bazı düğümlerin kötülük yapmasını veya hatalı çalışmasını tolere edebilen ve yine de doğru şekilde fikir birliğine varabilen bir mekanizma. Tendermint BFT, doğrulayıcıların 1/3'ünden fazlasının aynı anda kötü davranmasına veya çevrimdışı olmasına tolerans gösteremez.
> **CosmWasm**: Cosmos ekosisteminin WebAssembly teknolojisine dayalı akıllı sözleşme motoru, sözleşme yazmak için Rust dilinin kullanımını destekler ve derleme zamanı belleği güvenliği özelliklerine sahiptir (arabellek taşmaları gibi yaygın güvenlik açıklarını önler).
> **PWA** (Progressive Web App, Progressive Web App): Tarayıcı üzerinde çalışan ancak yerel benzeri bir uygulama deneyimine sahip bir web teknolojisi. Çevrimdışı önbelleğe almayı, anında bildirimleri ve uygulama mağazası aracılığıyla indirip yüklemeye gerek kalmadan ana ekrana eklemeyi destekler.
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
| Filecoin (FIL) | 2 milyar | Depolama donanımı | Büyüklük bakımından birbirine en yakın olan her ikisi de "jeton karşılığında kaynaklara katkıda bulunuyor" |
| Kaspa (KAS) | 28,7 milyar | PoW grafik kartı | Çok büyük, yumuşak düşüşün referans değeri var |
| Pi Ağı | 100 milyar | Mobil tıklamalar | Olumsuz öğretim materyali: Toplam miktar çok büyük → değer algısı son derece düşük |

**2,5 milyar coinin seçilmesinin temel nedeni:**

1. **Yatırım kapasitesi (birincil kısıtlama):** Kasadaki 850 milyon jeton × taban fiyat 0,15 $ × %75 kullanım oranı = **95,63 milyon $ ≈ 100 milyon $** dağıtılabilir sermaye, Aşağı Orta Piyasa PE'nin minimum güvenilir eşiğine ulaşıyor. Akademik temel: Cong, Li ve Wang (2021) "Tokenomics: Dynamic Adoption and Valuation" (*Review of Financial Studies* 34(3):1105-1155, NBER w27222), platform faydasının (yatırım getirisi → geri satın alma → fiyat desteği) dağıtım genişliğinin değil, token değerinin temel itici gücü olduğunu kanıtlıyor.
2. **Ağ rehberliği:** Çağın ilk gününde 1 milyar madeni para çıkarıldı ve 684.900 madeni para piyasaya sürüldü. 100.000 aktif madenci olduğunda kişi başına ortalama 6,51 IŞIK/gün olup, "tamsayı algısı" korunmaktadır.
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

**战略投资者要求：** 必须提供非资金贡献（deal flow、验证者服务、合规资源之一），纯财务投资者不接受。

**监管合规：** Pre-TGE sale采用Reg S（非美国投资者）+ Reg D Rule 506(c)（美国合格投资者）双轨豁免。

**核心贡献者披露规则：** 仅披露总额（5,000万枚=总量2%）和释放规则，不公开个人姓名和单人额度。角色类别公开：技术/投资/合规/社区。

### 5.5 挖矿产出与减半计划

**推导：** 2A = 10亿 → A = 5亿（第一纪元）。日释放 = 5亿÷730 = 684,932枚 ≈ 68.49万/天。每区块 = 684,932÷49,371 ≈ 13.87 LIGHT。

**注意：** 每区块奖励池为全网共享，其中5%划拨验证者（3.42万/天），95%分配轻节点矿工（65.07万/天）。

| 纪元 | 时间 | 产出总量 | 日释放量 | 每区块奖励池 |
|------|------|---------|---------|------------|
| 第1纪元 | 0—24月 | 5亿枚 | ≈68.49万 | ≈13.87 LIGHT |
| 第2纪元 | 25—48月 | 2.5亿枚 | ≈34.25万 | ≈6.93 LIGHT |
| 第3纪元 | 49—72月 | 1.25亿枚 | ≈17.12万 | ≈3.47 LIGHT |
| 第4纪元 | 73—96月 | 6,250万枚 | ≈8.56万 | ≈1.73 LIGHT |
| 第5纪元 | 97—120月 | 3,125万枚 | ≈4.28万 | ≈0.87 LIGHT |

**校验：** 5+2.5+1.25+0.625+0.3125+… = 5×2 = 10亿 ✓。97%在前10年完成。

### 5.6 用户收益参考模型

| 网络规模 | 人均日收益 | 月收益 | 年收益 | 满加成(1.44x)月收益 |
|---------|-----------|--------|--------|-------------------|
| 1万矿工（种子期） | ≈65.07 | ≈1,952 | ≈23,751 | ≈2,811 |
| 10万矿工（成长期） | ≈6.51 | ≈195.2 | ≈2,375 | ≈281.1 |
| 100万矿工（规模期） | ≈0.65 | ≈19.5 | ≈237.5 | ≈28.1 |

**合伙人级（50邀请，20%分成，满加成）：**

| 网络规模 | 自身(含加成) | 邀请分成 | 日综合 | 月综合 |
|---------|------------|---------|--------|--------|
| 1万矿工 | ≈93.7 | ≈650.7 | ≈744.4 | ≈22,332 |
| 10万矿工 | ≈9.37 | ≈65.07 | ≈74.44 | ≈2,233 |
| 100万矿工 | ≈0.94 | ≈6.51 | ≈7.45 | ≈223.4 |

### 5.7 空投增长计划

**经济模型：** 空投总预算 = 目标触达用户 × 人均空投 × (1+浪费率) = 100,000 × 150 LIGHT × 1.3 ≈ 1,950万枚（获取类）+ 3,550万枚（生态类）= **5,500万枚**（占生态基金4亿的13.75%）。

| 空投类型 | 触发条件 | 单次额度 | 预算 |
|---------|---------|---------|------|
| 首挖空投 | 首次完成4小时有效挖矿 | 50 LIGHT | 1,500万枚 |
| 地理扩张 | 目标市场用户完成ZK-KYC | 100 LIGHT | 1,000万枚 |
| Learn-to-Earn | 完成教育模块+测验 | 30 LIGHT | 600万枚 |
| 治理首投 | 首次参与投票 | 20 LIGHT | 300万枚 |
| 流动性提供 | LP注入≥$50锁仓30天 | 200 LIGHT | 1,000万枚 |
| 内容创作 | 经社区验证的教程/翻译 | 50-200 LIGHT | 600万枚 |
| 合作渠道 | 通过合作方注册+首挖 | 80 LIGHT | 500万枚 |

**CAC验证：** 5,500万枚×$0.03 = $165万 ÷ 30,000留存活跃矿工 = **$55/人**（行业区间$50-200，处于低端）。学术依据：Zheng (2023) "Operation Dumbo Drop: To Airdrop or Not to Airdrop for Initial Coin Offering Success?" 证明活动绑定型空投留存率为纯空投的3-5倍。

**防滥用：** 唯一浏览器指纹+ZK-KYC；每类每地址限领1次；30天锁定期；领取后30天无链上活动自动回收。

### 5.8 双引擎飞轮与资金池

飞轮：投票→金库LIGHT销毁→USDC支付→利润回流→回购销毁→价格支撑→更多用户。

双轨制：稳定金库（USDC，利润截留）+ 弹性金库（LIGHT层，投资时销毁不流入市场）。回购采用TWAP拆单，单笔≤日均交易量5%。

### 5.9 子代币发行与交易

发行总量=投资金额÷$1；兑换价以30天VWAP为基准；兑换所得LIGHT全部销毁；分配50%赞成者/30%空投/20%运营储备（锁仓6月）。单地址分红上限15%。子代币在链内AMM交易，发行后30天锁定期，退出后标记"已清算"下架。

### 5.10 初始流动性与价格发现

**TGE（Token Generation Event，代币生成事件）安排：**

| 项目 | 方案 |
|------|------|
| 初始流动性池 | 从生态发展基金TGE释放的1.2亿枚中，划拨7,200万枚（60%）注入DEX流动性池 |
| 配对资产 | USDC（主池）、USDT（辅池） |
| 空投 | 剩余4,800万枚（40%）用于种子用户空投（见5.7节空投计划） |
| 上线交易所 | TGE后首先上线去中心化交易所（如Osmosis、JunoSwap）；第6个月起视合规情况申请中心化交易所上市 |

**荷兰式拍卖（Dutch Auction）详细机制：**

荷兰式拍卖是一种"价格由高至低递减"的定价方式。与英式拍卖（价格由低至高竞价）相反，荷兰式拍卖中卖方设定一个起始高价，价格随时间自动下降，直到买方在某个价格点提交认购。第一个使总认购额达到目标的价格即为最终开盘价。

**为什么选择荷兰式拍卖而非固定价格或英式拍卖：**

| 定价方式 | 优点 | 缺点 | 适用性 |
|---------|------|------|--------|
| 固定价格预售 | 简单 | 定价主观，过高则卖不出，过低则被机器人抢购 | 不适合（无价格发现功能） |
| 英式拍卖（竞价） | 价格发现充分 | 大额买家可策略性等待、抬价；gas war | 不适合（链上gas war排斥小额用户） |
| **荷兰式拍卖** | **自动价格发现；无需竞价（无gas war）；大小买家平等参与；防机器人（价格递减机制天然抑制抢跑）** | 需要合理设定起始价和递减速率 | **最适合（公平+高效+防操纵）** |

**LightDAO荷兰式拍卖具体参数：**

| 参数 | 设定 | 说明 |
|------|------|------|
| 拍卖标的 | LIGHT代币（从生态基金TGE释放的7,200万枚中划拨） | 拍卖所得USDC注入稳定金库 |
| 目标募集额 | **$1,500万 USDC** | $500万→稳定金库最低储备；$1,000万→初始投资资本 |
| 起始价 | $0.20/LIGHT | 高于预期均衡价，确保不会"秒光" |
| 递减速率 | 每小时下降5% | 从$0.20起，约48小时后降至$0.017（若无人认购） |
| 最低保留价 | $0.01/LIGHT | 若降至保留价仍未达目标，拍卖延期24小时或调整标的数量 |
| 认购方式 | 用户提交"我愿意以当前价格购买X USDC等值的LIGHT" | 无需竞价，系统按最终统一价格结算（多退少不补） |
| 单用户上限 | 不超过目标募集额的5%（即$75万） | 防止单一买家垄断初始筹码 |
| KYC要求 | 增强验证（税务居民身份） | 合规要求 |

**拍卖结果的资金去向：**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**价格发现保护期：** TGE后前72小时设价格波动熔断——若DEX交易价格较拍卖开盘价偏离超过±50%，暂停子代币兑换功能（不影响挖矿和转账），防止极端投机行为干扰生态启动。72小时后熔断自动解除。

**为什么$1,500万而非更低：** 初始投资资本$1,000万需支撑首年3-5笔投资（单笔$200-500万，见9.1节启动期规模）。若仅募集$500万（全部作为储备），则首年无任何可部署投资资本，飞轮无法启动。$1,500万 = 储备$500万 + 投资$1,000万，是"安全底线"与"飞轮启动"的最小可行平衡。

### 5.11 通缩机制与底线

**流通量 = 挖矿释放 + 生态释放 + 战略基金已释放 − 兑换销毁 − Gas销毁 − 回购销毁。** 投资金库8.5亿枚从未进入流通。流通量理论上限 = 10+4+2.5 = **16.5亿枚**。

| 触发条件 | 系统行为 |
|---------|---------|
| 流通量≤15亿枚 | 减速信号（极端低销毁情景） |
| 流通量≤12亿枚 | 预警公示，暂停主动销毁（基准情景约第8年） |
| 流通量≤10亿枚 | 硬停止，所有销毁永久关闭（基准情景约第11-12年） |

### 5.12 价格稳定机制（防死亡螺旋）

**核心原则：** LightDAO 不干预日常市场价格发现。协议仅在极端下跌情形下调整自身参数，以降低陷入"死亡螺旋"的风险。

**分级逻辑：** 在不同波动环境中，同等跌幅所代表的异常程度不同。低波动市场中的大幅下跌属于更强的异常信号，需要更高强度的干预；高波动市场中的大幅下跌相对常见，可采用较轻干预。因此，干预强度与信号的异常程度正相关，而非仅取决于跌幅的绝对值。

**机制全流程表：**

| 市场状态 | 30日历史波动率 | 触发条件 | 信号等级 | 触发后执行 | 恢复条件 |
|---------|--------------|---------|---------|-----------|---------|
| 低波动 | ≤30% | 连续5日累计跌幅≥40% | I级 | 挖矿产出降至50%；销毁比例由20%提升至35%；风险参数调整公示期由72h缩短至12h；影子委员会进入激活状态（仅可依法行使临时暂停权） | 价格站上30日均线，且较触发价反弹≥80%，并连续保持10日 |
| 中波动 | 30%—60% | 连续7日累计跌幅≥50% | II级 | 挖矿产出降至50%；销毁比例由20%提升至30%；公示期缩短至24h；影子委员会进入激活状态 | 价格站上30日均线，且较触发价反弹≥60%，并连续保持7日 |
| 高波动 | 60%—100% | 连续10日累计跌幅≥55% | III级 | 挖矿产出降至75%；销毁比例由20%提升至25%；公示期缩短至48h；影子委员会进入待命状态 | 价格站上30日均线，且较触发价反弹≥40%，并连续保持5日 |
| 极端波动 | >100% | 连续10日累计跌幅≥65% | III级 | 按高波动状态的III级措施执行 | 按高波动状态的III级恢复条件执行 |

**排除条件：** 仅当同期比特币跌幅低于 LIGHT 跌幅的50%时，上述机制方可触发，以排除系统性市场崩盘情形（即：若BTC同期也暴跌，则属于市场整体事件，不单独对LIGHT启动干预）。

**恢复逻辑说明：** 反弹要求与持续时间随异常等级递减：I级要求最高反弹幅度（80%）和最长确认时间（10日），III级要求相对较低（40%/5日）。该安排符合"异常信号越强、干预越强、恢复确认越严格"的递进逻辑。

**波动率与价格数据来源：** 30日历史波动率和累计跌幅均由链上价格预言机（见4.10节）提供，以每日UTC 00:00区块的TWAP快照为计算基准，不依赖任何外部数据源。

### 5.13 收益可持续性压力测试

| 压力情景 | 假设条件 | 协议应对 | 最坏结果 |
|---------|---------|---------|---------|
| 全部投资失败 | 所有被投企业亏损或退出失败 | 保险基金（利润10%计提）覆盖部分损失；稳定金库储备（≥$800万）维持运营；暂停新投资直至社区重新评估 | 子代币持有者无法获得分红；LIGHT价格承压但不归零（挖矿和治理功能持续运行） |
| 市场暴跌80% | LIGHT价格较峰值下跌80% | 触发防死亡螺旋机制（II级或III级）；挖矿产出削减50-75%；销毁比例提升；影子委员会可暂停高危操作 | 用户收益缩水但网络持续运行；恢复条件达成后机制自动解除 |
| 主要市场监管禁令 | 某大国全面禁止加密资产 | 前端切换 IPFS 镜像保持可访问；链上资产与已有用户权益不受影响；仅在法律强制范围内调整第三方服务可用性；SPV在开曼群岛运营不受单一国家管辖 | 该区域用户增长停滞；全球其他区域不受影响 |
| 用户大规模流失 | 活跃矿工下降超70% | BaseReward自动重新分配（分母缩小→留存用户人均收益上升）；邀请激励加权吸引回流；治理门槛临时下调（5.14节动态机制） | 网络安全性下降但不会停链（Tendermint BFT容忍<1/3验证者离线） |
| 智能合约重大漏洞 | 核心合约被发现可利用漏洞 | 多签紧急暂停资金流出（72小时时间锁提供响应窗口）；发起备用合约迁移投票（L4级紧急修复，见4.12节）；保险基金覆盖用户损失 | 部分资金可能受损；迁移完成后恢复正常运营 |

### 5.14 代际平衡机制

治理门槛动态调整：每新增100万累计活跃矿工，提案门槛自动下调5%（下限2,500 LIGHT）。

> **【本章术语】**
> **TGE**（Token Generation Event，代币生成事件）：代币首次通过智能合约创建并分发的时点，通常伴随初始流动性池建立、荷兰式拍卖定价和首次公开交易。类似于传统金融中的IPO，但不涉及证券交易所上市。
> **减半**（Halving）：挖矿产出每隔固定周期（LightDAO为2年/730天）自动减少50%的机制。目的是制造渐进稀缺性——随着时间推移，新增供应越来越少，若需求不减则价格获得支撑。比特币采用每4年减半。
> **金库**（Treasury）：由多签合约锁定的代币储备，仅可通过治理决议释放。LightDAO设有两类金库：投资金库（持有LIGHT，投资执行时销毁）和稳定金库（持有USDC，用于支付投资对价和运营开支）。
> **通缩**（Deflation）：代币总供应量或流通量持续减少的过程。LightDAO通过四种机制实现通缩：投资执行销毁、子代币兑换销毁、Gas费销毁（50%）、利润回购销毁。
> **死亡螺旋**（Death Spiral）：代币价格下跌→矿工收益缩水→矿工退出→网络安全性/贡献度下降→信心进一步丧失→价格继续下跌的恶性循环。第5.12节的分级干预机制专为阻断此循环而设计。
> **子代币**（Sub-token）：每完成一次企业投资后按规则发行的SPV收益分配请求权凭证（如收购咖啡品牌→CAFE代币）。持有子代币=持有对未来利润的分配资格，不代表股东权利或公司治理权。
> **LP**（Liquidity Provider，流动性提供者）：向DEX流动性池注入等值两种资产（如LIGHT+USDC）的参与者，赚取交易手续费作为回报。LP是DEX正常运行的基础。
> **VWAP**（Volume-Weighted Average Price，成交量加权平均价格）：将一段时间内的价格按每笔交易的成交量加权平均，反映真实市场成交成本。LightDAO用30天VWAP作为子代币兑换的定价基准。
> **CAC**（Customer Acquisition Cost，用户获取成本）：获取一个有效活跃用户的平均成本。LightDAO空投计划的目标CAC为$55/留存活跃矿工（行业区间$50-200）。
> **wLIGHT**（Wrapped LIGHT，封装LIGHT）：通过跨链桥在Ethereum或Solana上发行的LIGHT等价代币，由桥合约锁定等量原生LIGHT作为1:1储备。目的是让非Cosmos生态用户也能获取和持有LIGHT。
> **荷兰式拍卖**（Dutch Auction）：一种"价格由高至低递减"的定价方式。卖方设定起始高价，价格随时间自动下降，直到买方在某个价格点提交认购。第一个使总认购额达到目标的价格即为最终成交价。优点是无需竞价（无gas war）、大小买家平等、天然防机器人抢跑。

---

## 第六章：治理机制

### 6.1 双维度投票模型

持币权重（含声誉+层级加成，总上限+40%）+ 地址数量（1地址=1票，关联地址合并）。投票权90天有效，5枚LIGHT转账可激活。声誉加成：持币满1年+15次有效投票→最高+30%。

### 6.2 动态通过率

最低通过率＝50%＋（50%－实际投票率）。投票率≥50%时简单多数。

### 6.3 提案参数

| 类型 | 保证金 | 持币投票率 | 地址投票率 | 通过率 | 执行延迟 |
|------|--------|-----------|-----------|--------|---------|
| 微型 | $100 | ≥15% | ≥20% | 动态≥55% | 24h |
| 收购型 | $500 | ≥25% | ≥30% | 动态≥60% | 72h |
| 风投型 | $500 | ≥35% | ≥40% | 动态≥60% | 72h |
| 重大 | $1,000 | ≥45% | ≥50% | 动态≥66% | 72h |
| 紧急 | $2,000 | ≥50% | ≥60% | ≥75% | 非资金6h/高危1h；资金操作仍受72h时间锁 |

### 6.4 提案生命周期

提交资格：≥5,000枚LIGHT + 连续质押30天 + 保证金。公示72h（修订≤2次）。投票7日（快速通道48h，≤50万USDC）。否决冷却90天。生效延迟24h。

**门槛说明：** 5,000枚在种子期（1万矿工）≈77天基础产出；合伙人级≈7天。治理第7月激活，早期用户有充足积累时间。

### 6.5 投票激励

参与有基础激励（均分），判断正确有额外加成（押注池50%）。押注区间5—500 LIGHT。抑制羊群效应：反对者即使"站错队"仍获基础激励。

### 6.6 成败奖惩

善意失败：退50%保证金+30天冷却。恶意失败（造假/重复）：全额没收+永久禁止。造假举证：封顶5,000 LIGHT，成立奖40%罚没金+500 LIGHT。

### 6.7 财务透明

链上实时仪表盘+季度财务报告+年度独立审计（TGE前须完成首次审计）+投资标的即时披露。

---

## 第七章：权力制衡与角色定义

### 7.1 初始监护人

权限仅限文档/格式/官网信息。任期≤24月。须指定备选监护人（连续30天无法签名→自动接管）。同时失能→48h紧急投票指定临时管理人。

### 7.2 权力转移路线图

| 阶段 | 时间 | 权限 | 投资审批 |
|------|------|------|---------|
| 创世期 | 0—6月 | 监护人（非资金类） | 监护人+社区多签3/5 |
| 过渡期 | 7—12月 | 监护人+核心贡献者联名 | 同上+核心贡献者 |
| 成熟期 | 13—24月 | 治理委员会3/5 | 常规双维度投票 |
| 自治期 | 25月+ | 全体持有者 | 同成熟期 |

### 7.3 治理委员会

五人分权（轮值主席/财务/技术/社区/密钥），季度轮换，任期6月可连任1次。竞选质押50,000 LIGHT + 100地址联名。决策≥3人且覆盖≥3职位。

**门槛说明：** 50,000枚在种子期≈合伙人67天（2.2月）；成长期≈672天（22月）。委员会第13月首选举，早期合伙人可达。

### 7.4 影子委员会

仅限"违法/制裁/重大欺诈"临时暂停。72h内须全体追认（反对>60%→解除）。连续2次被否决→自动弹劾解散。

### 7.5—7.6 竞选验证与密钥预案

SimHash>80%取消资格；AI内容须补充说明；缺席质询扣20%得票。密钥分片备份+季度健康检查+7天公示判定+投票更换。

---

## 第八章：信任与安全机制

### 8.1 五大安全机制

时间锁72h（紧急提案不可豁免资金操作）；多签3/5；季度轮换≤2届；造假罚没100%；全交易上链。

### 8.2 保险基金

成功投资利润的**10%**计提。理赔须独立报告+DAO 66%赞成+单次≤池20%。补充来源：造假罚没金的30%。定位"部分缓冲"非全额保障。

### 8.3 极端预案

监管黑天鹅→IPFS+移除管理员权限；欺诈→影子委员会暂停（72h追认）+保险基金+SPV仲裁；死亡螺旋→5.12节机制；合约漏洞→多签暂停+迁移投票；验证者集体作恶→BFT容忍<1/3，超过则链暂停+紧急投票迁移。

---

## 第九章：投资运营与退出策略

### 9.1 投资标的筛选与规模

**投资规模分阶段成长轨迹（公式：金库剩余×15%×LIGHT价格）：**

| 阶段 | LIGHT价格 | 金库初始期单笔上限 | 适配标的 | 行业对标 |
|------|----------|-----------------|---------|---------|
| 启动期(Y1-2) | $0.02—$0.05 | $255万—$637万 | 单店/小型连锁、天使轮 | 微型PE |
| 成长期(Y3-5) | $0.05—$0.30 | $637万—$3,825万 | 区域连锁30-200店、Seed-A轮 | Lower Middle Market PE |
| 成熟期(Y5-8) | $0.30—$1.00 | $3,825万—$1.275亿 | 跨国连锁/中型科技、B-C轮 | Middle Market PE |
| 规模期(Y8+) | $1.00+ | $1.275亿+ | 大型收购、Pre-IPO | 大型PE/成长期VC |

### 9.2 投资决策流程

项目发现（≥5,000 LIGHT）→独立尽调→72h公示→双维度投票→24/72h执行。

### 9.3 退出与利润分配

年度分红：**40%**子代币持有者 / **30%**稳定金库 / **20%**回购LIGHT销毁 / **10%**保险基金。
退出收益：**70%**稳定金库 / **30%**回购销毁。

### 9.4 投资纪律

| 规则 | 内容 |
|------|------|
| 单笔销毁上限 | 金库剩余×15%（初始8.5亿×15%=1.275亿枚） |
| 单一标的 | ≤金库总价值25% |
| 行业集中 | ≤组合40% |
| 地域集中 | ≤组合30% |
| 稳定金库储备 | TGE时$500万（拍卖），第24月前达$800万 |
| 冷静期 | 连续2次失败→180天 |

**金库容量：** 8.5亿枚×$0.10=$8,500万（初始总容量）；×$0.30=$2.55亿；×$1.00=$8.5亿。15%单笔上限使投资节奏与价格正相关。

> **【本章术语】**
> **EBITDA**（Earnings Before Interest, Taxes, Depreciation and Amortization，息税折旧摊销前利润）：衡量企业核心经营盈利能力的指标，排除了财务结构（利息）、税务政策（税）、会计选择（折旧/摊销）的干扰，便于跨企业、跨行业比较。EBITDA margin = EBITDA ÷ 营业收入。
> **DCF**（Discounted Cash Flow，现金流折现法）：将企业未来预期现金流按一定折现率换算为当前价值的估值方法。适用于现金流稳定的成熟企业（如消费连锁），不适用于尚无盈利的早期科技公司。
> **IPO**（Initial Public Offering，首次公开募股）：企业首次在证券交易所公开发行股票并上市交易。对LightDAO而言，被投企业IPO是增长引擎标的的主要退出路径之一。
> **Pre-IPO**：企业在正式上市前的最后一轮私募融资，通常估值已接近上市后水平，风险低于早期轮次但回报倍数也较低。
> **TWAP执行**（Time-Weighted Average Price Execution）：将大额回购订单拆分为多笔小额订单，在一段时间内均匀执行，以避免单笔大单对市场价格造成冲击。LightDAO规定单笔回购不超过日均交易量的5%。

---

## 第十章：路线图

| 阶段 | 时间 | 核心目标 | 关键里程碑 | 前置条件 |
|------|------|---------|-----------|---------|
| 筹备期 | 2026年Q4 | 法律实体+团队+资金到位 | 开曼/BVI实体注册完成；技术合伙人或开发团队签约；战略投资者意向确认（2-3家）；启动资金≥$15万到位 | 创始人确定身份公开方式；完成BP和Pitch Deck |
| 开发期 | 2027年Q1—Q2 | 核心系统开发 | 10个智能合约模块开发完成；PWA前端开发完成；7个验证者测试网部署；内部Alpha测试通过 | 开发团队到位；需求文档（技术Spec）定稿 |
| 审计与测试期 | 2027年Q3 | 安全性与合规性验证 | 独立安全审计报告发布（≥1家顶级机构）；法律合规意见书发布（MLM+证券法）；5万并发压力测试通过；反作弊系统误报率<2%；治理投票演练完成 | 合约开发冻结（Code Freeze）；审计费用到位 |
| TGE与主网上线 | 2027年Q4 | 代币发行+网络启动 | 荷兰式拍卖完成（目标$1,500万）；主网上线（≥10验证者）；挖矿平台公开开放；DEX流动性池建立；种子空投发放 | 审计通过；验证者≥7（硬性底线）；拍卖合约部署 |
| 信仰构建期 | 2028年Q1（TGE后第1-3月） | 3—5万种子用户 | 活跃矿工突破3万；首次治理投票演练；社区多语言频道建立（英/中/西/葡/菲）；首份月度社区报告发布 | TGE完成；社区运营团队到位 |
| 价值锚定期 | 2028年Q2—Q3（TGE后第4-9月） | 首笔投资+过渡期治理 | 首个投资提案通过（第4-6月内适用创世期多签审批；第7月起适用过渡期联名审批）；首笔SPV交割完成；验证者开放竞选（第7月起）；首份季度财务报告发布 | 稳定金库USDC≥$500万；投资标的尽调完成 |
| 治理成熟期 | 2028年Q4—2029年Q1（TGE后第10-15月） | 委员会选举+去中心化过渡 | 治理委员会首次选举（第13月）；进入成熟期（委员会3/5决策）；wLIGHT跨链桥上线；CEX上市申请提交；开发者资助计划启动 | 活跃矿工≥10万；≥100个地址联名候选人 |
| 生态扩张期 | 2029年Q2起（TGE后第16月+） | 规模化复制 | 活跃矿工突破20—50万；完成2—3笔投资；首笔利润回流验证；LIGHT回购销毁启动 | 治理委员会运转正常；投资模式已验证 |
| 成熟运营期 | 2029年Q4起（TGE后第25月+） | 飞轮自转+完全自治 | 进入自治期（全体持有者重大提案）；投资组合累计部署≥$3,000万；通缩数据公开可验证 | 治理完全去中心化 |

**路线图设计原则：**

- **审计先于TGE：** 绝不在未完成独立安全审计的情况下发行代币。这是用户资金安全的基本保障。
- **验证者先于用户：** 主网上线时验证者≥10个（BFT容错f≥3），确保网络不会因单点故障停摆。
- **投资先于扩张：** 首笔投资成功并产生可验证的利润回流后，方进入规模化扩张。避免"先圈人后找项目"的本末倒置。
- **时间缓冲：** 每个阶段预留20-30%时间缓冲。技术开发、审计修复、法律流程均可能超预期，路线图不应是"最乐观情景"。

**与白皮书发布日（2026年8月4日）的关系：** 白皮书于2026年8月发布，作为项目愿景和技术设计的公开声明。实际执行从2026年Q4开始（筹备期），TGE目标为2027年Q4。白皮书发布与TGE之间约14个月的间隔用于团队组建、开发、审计和合规准备。

---

## 第十一章：社区文化与开发者生态

### 11.1 四条价值观

- **透明优于完美** ——有瑕疵的公开，胜过完美的隐藏。所有金库流动、投资决策、治理投票永久上链可查。
- **渐进优于激进** ——小步快跑，持续迭代。首笔投资从$200-500万起步，验证模式后再扩大规模。
- **责任优于权利** ——权力与义务对等。治理委员会成员须质押50,000 LIGHT并公开施政纲领，失职则罚没。
- **多元优于同质** ——不同声音是系统的免疫力。双维度投票（持币+地址）确保巨鲸和散户都有话语权。

### 11.2 陪审团制度

| 维度 | 规则 |
|------|------|
| 组成 | 随机抽取12名持有≥10,000枚LIGHT且无违规记录的用户 |
| 任期 | 30天，届满后重新随机抽取 |
| 职责 | 审理反作弊处罚申诉、提案造假指控、社区争议 |
| 流程 | 被处罚用户可在72小时内提交证据；陪审团须在48小时内作出裁决 |
| 裁决标准 | 12人中≥8人（2/3多数）同意方可维持或撤销处罚 |
| 回避 | 与当事方存在邀请关系或同一IP段的陪审员自动替换 |
| 报酬 | 任期内每日获得5 LIGHT的陪审服务补贴（从生态基金列支） |

### 11.3 开发者生态计划

| 模块 | 内容 | 资金来源 | 申请方式 |
|------|------|---------|---------|
| 开发者资助（Grants） | 面向在LightDAO链上构建dApp、工具、基础设施的团队，单个资助$5—50万等值LIGHT | 生态发展基金（线性释放期二） | 提交提案→技术审核官评估→治理投票（微型提案流程） |
| SDK与API | 提供JavaScript/TypeScript SDK、REST API、WebSocket接口，降低第三方开发门槛 | 技术审核官主导开发 | 开源，GitHub公开 |
| 黑客松 | 每季度举办一次线上黑客松，奖金池$10万等值LIGHT | 生态发展基金 | 公开报名，无门槛 |
| 漏洞赏金（Bug Bounty） | 核心合约漏洞赏金计划，单个有效漏洞奖励$1,000—$50,000（按严重度分级） | 保险基金 + 生态发展基金 | 通过Immunefi或自建平台提交 |
| CosmWasm合约市场 | 鼓励第三方部署智能合约，Gas费收入的20%回流生态金库支持开发者 | Gas费分配（见4.5节） | 自动，无需申请 |

### 11.4 多语言与本地化策略

| 维度 | 规划 |
|------|------|
| 平台语言 | 首发支持英语、中文、西班牙语、葡萄牙语、菲律宾语；第6个月起增加法语、阿拉伯语、斯瓦希里语、印尼语 |
| 治理语言 | 提案和竞选纲领接受任何语言提交，系统提供机器翻译+社区人工校对 |
| 社区运营 | 按语言设立独立社区频道（Discord/Telegram），各频道配备本地化社区联络志愿者 |
| 文档翻译 | 白皮书及核心文档由社区翻译志愿者完成，翻译贡献计入"内容贡献"行为加成（5%） |
| 本地化资助 | 生态发展基金中预留10%（4,000万枚）专项用于本地化社区建设和翻译激励 |

---

## 第十二章：团队与顾问

### 12.1 核心角色定义

| 角色 | 职责 | 背景要求 | 披露方式 |
|------|------|---------|---------|
| 初始监护人/项目发起人 | 部署初始合约、维护文档、协调早期运营 | 区块链行业≥3年经验，有智能合约部署或DeFi协议运营记录 | TGE前公开真实身份或提供第三方身份验证报告（如公证人签名+链上消息验证） |
| 技术负责人 | 合约架构设计、开发团队管理、审计对接 | Cosmos SDK/CosmWasm开发经验，有生产链部署记录 | 同上 |
| 投资负责人 | 标的筛选、尽调协调、SPV设立、退出管理 | 私募股权/风险投资行业经验，有已完成退出案例 | 同上 |
| 合规顾问 | 法律架构设计、监管对接、MLM合规意见 | 持有美国/欧盟/开曼执业资格的律师 | 公开律所名称（个人姓名除非本人同意否则不公开） |

### 12.2 顾问委员会

- 由3—5名独立顾问组成，涵盖：DePIN技术、跨境投资合规、社区运营、消费行业；
- 顾问以LIGHT代币形式获得咨询报酬（从战略运营基金"服务换代币"部分列支），锁仓12个月；
- 顾问名单在TGE前公开，并接受社区质询（去中心化文字质询会，见7.5节）；
- 顾问不得同时担任治理委员会成员（利益冲突隔离）。

### 12.3 团队承诺与约束

| 约束 | 规则 |
|------|------|
| 代币锁仓 | 核心团队持有的LIGHT（含战略运营基金分配）须锁仓12个月，解锁后线性释放36个月 |
| 出售限制 | 初始监护人在任期内（≤24个月）不得出售通过任何渠道获得的LIGHT（含空投、奖励、薪酬） |
| 利益冲突 | 团队成员的利益冲突须在任命时完整披露（是否持有其他DAO代币、是否与潜在投资标的存在关联） |
| 未披露后果 | 未披露利益冲突一经查实，永久禁止参与治理，已解锁代币的50%罚没至保险基金 |
| 替换机制 | 核心角色离职或失能时，由治理委员会（成立前由初始监护人+备选监护人）指定继任者，须经社区公示72小时无异议 |

### 12.4 核心贡献者薪酬（战略运营基金20%部分）

- 总额：5,000万枚LIGHT（占总量2%）
- 覆盖人数：3—5人
- 释放规则：12月cliff + 36月线性（即第13个月起每月释放约115.7万枚）
- 里程碑绑定：每季度由治理委员会（成立前由初始监护人+独立第三方）确认里程碑达成后方可释放当季额度
- 披露规则：仅披露总额和释放规则，不公开个人姓名和单人额度（保护隐私，同时通过链上多签地址可验证总额不超发）

---

## 第十三章：风险提示与免责声明

### 13.1 风险提示

| 风险类型 | 说明 | 缓解措施 |
|---------|------|---------|
| 市场风险 | LIGHT价格可能出现大幅波动，历史价格不代表未来表现。TGE初期流动性有限，价格可能剧烈波动 | 荷兰式拍卖公平定价；TGE后72小时±50%熔断；防死亡螺旋四级干预机制 |
| 项目风险 | 投资标的可能亏损，风投项目可能失败，本金可能全部损失。PE/VC行业历史平均失败率约50-70%（单笔） | 双引擎分散（70%现金流+30%增长）；单一标的≤25%；行业≤40%；地域≤30%；保险基金10%计提 |
| 技术风险 | 智能合约可能存在未被发现的漏洞；浏览器兼容性可能影响挖矿体验；跨链桥可能被攻击 | TGE前独立审计+形式化验证；Bug Bounty $1K-$50K；72小时时间锁；多签暂停机制 |
| 监管风险 | 各国及地区监管政策可能发生变化，可能导致部分功能受限或特定区域用户无法参与 | 开曼 SPV 架构；默认零验证（核验由持牌第三方在其服务侧承担）；前端 IPFS 镜像抗审查；不面向特定国家营销 |
| 流动性风险 | 子代币在早期可能缺乏足够交易深度；LIGHT在TGE初期可能面临抛售压力 | 子代币AMM初始流动性（发行量6%）；30天转让锁定期；团队/投资者12月cliff+36月线性 |
| 稀释风险 | 随活跃矿工增长，人均挖矿收益将自然稀释（BaseReward分母增大） | 设计意图：早期参与者承担更高风险获得更高回报；后期用户可通过邀请分成加速积累；治理门槛动态下调 |
| 运营风险 | 被投企业经营管理可能不达预期；SPV运营依赖第三方董事；投资团队可能流失 | SPV章程约束+独立董事；DAO可投票更换董事；SIAC/ICC仲裁条款；关键人保险（探索中） |
| 跨链桥风险 | wLIGHT跨链桥由第三方运营，桥合约漏洞可能导致资产损失（历史上跨链桥是最大单点损失来源） | 桥上线前独立审计；桥接资产不超过总供应量5%；风险披露；用户可选择仅使用原生链 |
| 验证者风险 | 验证者集体离线或作恶可能导致链暂停出块，所有用户操作（挖矿、投票、转账）暂时不可用 | Tendermint BFT容忍<1/3作恶；验证者≥21个（f=6）；Slashing惩罚；紧急迁移投票机制 |

### 13.2 免责声明

- LIGHT 及子代币不是证券，不具有内在价值，价格可能归零。本白皮书不构成任何形式的证券发行文件、投资要约或投资建议。
- 协议收入分配取决于底层资产的实际经营表现，历史数据不代表未来收益。任何关于投资回报的描述均为前瞻性估计，非承诺。
- 用户须自行承担私钥丢失、泄露导致的全部损失，协议不提供找回服务。使用第一层（Passkey）或第二层（社交恢复）钱包可降低此风险，但不消除。
- 本协议面向全球用户（受限于适用法律法规），用户应自行确认其所在司法辖区对加密资产、DAO组织及SPV收益凭证的法律态度，并确保参与行为合法合规。
- 本白皮书中的前瞻性陈述（包括路线图、收益模型、通缩估算、投资规模预测）均为基于当前假设的预测，实际结果可能因市场、技术、监管、团队执行等因素而重大偏离。
- 邀请激励为单层分成机制，不构成多层次营销或金字塔计划。但用户仍应自行确认其所在司法辖区对推荐奖励的法律态度。
- 参与LightDAO生态的最低年龄为18岁（或所在司法辖区的法定成年年龄，以较高者为准）。未成年人不得参与挖矿、治理或投资。

---

## 附录A：关键参数汇总表

| 类别 | 参数 | 数值 |
|------|------|------|
| 发行 | 总量 | 25亿枚，永不增发 |
| 发行 | 挖矿 | 40% = 10亿枚 |
| 发行 | 投资金库 | 34% = 8.5亿枚 |
| 发行 | 生态基金 | 16% = 4亿枚 |
| 发行 | 战略运营 | 10% = 2.5亿枚（服务50%/融资30%/贡献者20%） |
| 发行 | 减半周期 | 每2年 |
| 发行 | 第一纪元日释放 | ≈68.49万枚（矿工95%=65.07万，验证者5%=3.42万） |
| 发行 | 每区块奖励池 | ≈13.87 LIGHT |
| 挖矿 | 贡献权重 | 带宽40%/会话30%/验证20%/稳定10% |
| 挖矿 | 满加成 | 1.44倍 |
| 邀请 | 布道者/大使/合伙人 | 3人10%+100L / 10人15%+500L+5% / 50人20%+2500L+10% |
| 行为 | 四项×5% | 上限20% |
| Gas费 | 定价机制 | USD等值锚定，每24h由预言机自动换算为LIGHT数量 |
| Gas费 | 普通转账 | $0.001等值（@$0.05时=0.02 LIGHT） |
| Gas费 | 治理投票 | $0.005等值（@$0.05时=0.10 LIGHT） |
| Gas费 | 分配规则 | 50%销毁 / 30%验证者 / 20%生态金库 |
| 通缩 | 减速/预警/底线 | ≤15亿/≤12亿/≤10亿（流通量） |
| 通缩 | 理论上限 | 16.5亿（10+4+2.5，金库8.5亿永不流通） |
| 治理 | 提案门槛 | ≥5,000 LIGHT + 30天质押 |
| 治理 | 委员会质押 | 50,000 LIGHT + 100地址 |
| 治理 | 陪审团 | 10,000 LIGHT |
| 治理 | 押注 | 5—500 LIGHT |
| 治理 | 声誉加成 | 1年+15次投票→+30%（总上限+40%） |
| 投资 | 单笔上限 | 金库剩余×15%（初始1.275亿枚） |
| 投资 | 基准可部署 | 8.5亿×$0.15×75% = $9,563万≈$1亿 |
| 投资 | 利润分配(年度) | 40/30/20/10 |
| 投资 | 利润分配(退出) | 70/30 |
| 拍卖 | 目标 | $1,500万（$500万储备+$1,000万投资资本） |
| 储备 | 稳定金库 | TGE $500万→第24月$800万 |
| 保险 | 计提 | 利润10% |
| 空投 | 总预算 | 5,500万枚（生态基金13.75%），CAC≈$55/留存用户 |
| 验证者 | 初始/上限 | 21（最低10）/ 100 |
| 验证者 | 最低质押 | 500,000 LIGHT |
| 验证者 | TGE硬性底线 | ≥7个，否则不得上线 |

---

## 附录B：数值推导与校验

### B.1 挖矿产出

2A=10亿→A=5亿。日释放=5亿÷730=684,932≈68.49万。矿工池=684,932×95%=650,685≈65.07万。验证者=684,932×5%=34,247≈3.42万。每区块=684,932÷49,371≈13.87。校验：684,932×730=499,999,960≈5亿 ✓

### B.2 治理门槛可达性

10万矿工基准（6.51/天，合伙人74.44/天）：提案5,000→768天/67天；委员会50,000→7,684天(21年)/672天(22月)；陪审团10,000→1,537天(4.2年)/134天(4.5月)；押注500→77天/6.7天。

种子期（1万矿工，65.07/天，合伙人744.4/天）：提案→77天(2.5月)/6.7天；委员会→768天(25月)/67天(2.2月)；陪审团→154天(5月)/13.4天。

### B.3 通缩时间线

流通量=挖矿+生态+战略(vested)−兑换−Gas−回购。金库8.5亿永不流通。

| 年 | 累计挖矿 | 生态 | 战略 | 兑换 | Gas | 回购 | 流通量 |
|----|---------|------|------|------|-----|------|--------|
| 1 | 2.50 | 2.80 | 0 | 0 | 0.01 | 0 | ≈5.29 |
| 2 | 5.00 | 4.00 | 0.83 | 0.05 | 0.02 | 0 | ≈9.76 |
| 3 | 6.25 | 4.00 | 1.67 | 0.20 | 0.03 | 0.05 | ≈11.64 |
| 4 | 7.50 | 4.00 | 2.50 | 0.45 | 0.04 | 0.20 | ≈13.31(峰值) |
| 5 | 8.13 | 4.00 | 2.50 | 0.80 | 0.05 | 0.50 | ≈13.28 |
| 6 | 8.75 | 4.00 | 2.50 | 1.20 | 0.06 | 0.90 | ≈13.09 |
| 7 | 9.06 | 4.00 | 2.50 | 1.60 | 0.07 | 1.40 | ≈12.49 |
| 8 | 9.38 | 4.00 | 2.50 | 2.00 | 0.08 | 1.90 | ≈11.89 |
| 9 | 9.53 | 4.00 | 2.50 | 2.40 | 0.09 | 2.30 | ≈11.24 |
| 10 | 9.69 | 4.00 | 2.50 | 2.80 | 0.10 | 2.70 | ≈10.59 |
| 11 | 9.77 | 4.00 | 2.50 | 3.10 | 0.11 | 3.00 | ≈10.06 |
| 12 | 9.84 | 4.00 | 2.50 | 3.40 | 0.12 | 3.30 | ≈9.52 |

结论：峰值Y4≈13.31亿；预警线12亿约Y8触及；底线10亿约Y11-12触及；减速线15亿仅极端低销毁情景。

---

## 附录C：审计修正日志（累计36项）

含原22项（L1-5, A1-4, D1-4, M1-8, G1-3）+ 技术架构7项（T1-7）+ 本轮经济模型优化7项：

| 编号 | 修正 |
|------|------|
| E-1 | 总量21亿→25亿（投资容量约束驱动） |
| E-2 | 分配50/30/20→40/34/16/10（新增战略运营基金10%） |
| E-3 | 荷兰拍卖$1,000万→$1,500万（初始投资资本$500万→$1,000万） |
| E-4 | 新增5.7节空投增长计划（5,500万枚，CAC $55/人） |
| E-5 | 验证者分阶段启动（测试网7→TGE最低10/目标21→开放100） |
| E-6 | 通缩触发线调整（14/12/10→15/12/10，适配16.5亿流通上限） |
| E-7 | 外部引用全部替换为可验证来源（移除不可验证SSRN论文） |

---

## 附录D：术语速查索引

各术语的完整解释已标注于其首次出现章节末尾的【本章术语】注释块中。本索引按字母顺序列出所有术语及其所在章节，便于快速定位。

| 术语 | 定义所在章节 |
|------|------------|
| AMM（自动做市商） | 第四章 |
| BFT（拜占庭容错） | 第四章 |
| CAC（用户获取成本） | 第五章 |
| CEX（中心化交易所） | 第四章 |
| Cosmos SDK | 第四章 |
| CosmWasm | 第四章 |
| DAO（去中心化自治组织） | 第二章 |
| DCF（现金流折现法） | 第九章 |
| DePIN（去中心化物理基础设施网络） | 第二章 |
| DEX（去中心化交易所） | 第四章 |
| EBITDA（息税折旧摊销前利润） | 第九章 |
| Gas费 | 第四章 |
| IBC（跨链通信协议） | 第三章 |
| IPFS（星际文件系统） | 第四章 |
| KYC（了解你的客户） | 第三章 |
| LIGHT（原生代币） | 第四章 |
| LP（流动性提供者） | 第五章 |
| Lower Middle Market PE（下游中端私募股权） | 第二章 |
| Merkle Tree（默克尔树） | 第四章 |
| MiFID II（欧盟金融工具市场指令II） | 第三章 |
| MLM（多层次营销） | 第三章 |
| PII（个人可识别信息） | 第三章 |
| PoC（贡献证明） | 第四章 |
| PoS（权益证明） | 第四章 |
| PoW（工作量证明） | 第四章 |
| Pre-IPO | 第九章 |
| PWA（渐进式Web应用） | 第四章 |
| Reg D / Reg S（美国证券法D/S条例） | 第三章 |
| Slashing（罚没） | 第四章 |
| SPV（特殊目的载体） | 第二章 |
| TGE（代币生成事件） | 第五章 |
| TWAP（时间加权平均价格） | 第四章 |
| TWAP执行（回购拆单） | 第九章 |
| VWAP（成交量加权平均价格） | 第五章 |
| wLIGHT（封装LIGHT） | 第五章 |
| ZK-KYC（零知识证明KYC） | 第三章 |
| 子代币（Sub-token） | 第五章 |
| 死亡螺旋（Death Spiral） | 第五章 |
| 减半（Halving） | 第五章 |
| 金库（Treasury） | 第五章 |
| 荷兰式拍卖（Dutch Auction） | 第五章 |
| 预言机（Oracle） | 第四章 |

---

**白皮书全文完**

**版权说明：** 本文档为开源社区文档，可自由转载，但须保留完整内容。

---

# 附录:主网已验证参数与地址(V2.4 实况)

## A. §4.5 Gas 经济实测参数
- min-gas-price 公式:`(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas`;当前 TransferUsdTarget=$0.001、UsdPerLight=$0.05、RefTransferGas=100000 → **0.2 ulight/gas**
- 分配实测(总 fee 300000 ulight):销毁 150000(50%)/ 金库 60000(20%)/ 验证者 90000(30%),精确匹配
- 销毁地址:`wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu`(确定性死地址)
- 金库:`treasury_multisig` 合约(3/5 多签;链上 `signers` 查询返回 5 名签名人,阈值本身不在查询接口内)

## B. 核心合约地址
见仓库 `docs/MAINNET_STATUS.md`(light_token / mining_reward / governance / treasury_multisig / oracle_twap / vesting 等 10 合约)。

## C. 遗留 denom(stake)处置
genesis 误配 mint_denom=stake 已归零停止增发;存量 stake(约 2.56e11 微单位)为无用途遗留,处置方案(兑换/销毁)待治理提案,不影响 ulight 经济模型。

## D. §4.4 vesting 实况
vault 250,000,000 LIGHT,3 个独立 schedule:75M(cliff 0)/ 100M(cliff 1 年)/ 75M(cliff 2 年),已上链。

## E. 安全实践
- 主网升级为 x/upgrade 治理 + 全节点同块高协调 + auto-swap 看门狗,测试网端到端彩排后执行
- Passkey 种子仅密文存储;Shamir 分片本地不保存
- 合约挖矿根提交阈值 5(链上每笔 `submit_root` 事件实测 threshold=5;当前 5 个授权账户在签,7 席为设计目标);反女巫/反作弊见 §4.8
