> Terjemahan mesin tanpa pemeriksaan manusia. Jika ada perbedaan, versi asli bahasa Mandarin yang berlaku.
[中文原文 / Chinese original](/whitepaper.md)

# Buku Putih LightDAO V2.4 (Versi Langsung Mainnet 26-09-2026)

> Versi ini didasarkan pada draf desain V2.0, dengan "penerapan mainnet langsung" dan "perubahan versi" di depan, dan ditambahkan dengan parameter on-chain yang terverifikasi. Teks utama (Bab 1~12) tetap tidak berubah dari desain V2.0; untuk setiap penyimpangan dari situasi sebenarnya, catatan sebelumnya dan lampiran dari bagian ini yang akan berlaku.

## Perubahan versi (V2.0 → V2.4)
- Kesalahan 04-11-2026 (jangan ubah nomor versi, tetap V2.4): Vault asli `treasury_multisig` dalam lampiran "Parameter dan Alamat Terverifikasi Mainnet" adalah 5/7 multisig, yang bertentangan dengan 3/5 teks §7.2/§7.3/§8.1, dan juga bertentangan dengan pengukuran sebenarnya pada rantai (`{"penandatangan":{}}` mengembalikan 5 alamat, tidak ada 7 penanda tangan); itu telah disatukan sebagai 3/5 menurut teks, dan diindikasikan bahwa ambang batas itu sendiri tidak berada dalam antarmuka kueri kontrak dan hanya dapat didukung oleh catatan penerapan. Root penambangan asli yang ditulis di bagian yang sama adalah "5/7 verifier multi-signature", dan pengujian sebenarnya hanya dapat membuktikan ambang batas 5 (ambang batas dari 115 peristiwa `submit_root` semuanya 5, dan jumlah sebenarnya dari akun penandatanganan tepat 5). Otorisasi 7 kursi adalah tujuan desain, dan saat ini tidak ada bukti yang ada. Kata-katanya telah diubah.

1. **§4.5 Ekonomi Gas: Dikerahkan dan diverifikasi di mainnet**. Harga gas min dinamis berlabuh USD dan penghancuran 50% / 30% validator / 20% alokasi perbendaharaan diterapkan pada 24-09-2026 setelah proposal tata kelola (v2-lightfee) diluncurkan di ketinggian 58627, 7 validator mengoordinasikan peralihan, dan jaringan pengujian dilatih secara end-to-end. Pengukuran aktual pada jaringan utama: biaya yang tidak mencukupi ditolak, dan biaya penuh dialokasikan secara akurat sesuai dengan 30/50/20.
2. **Klarifikasi denom asli**: Staking/tata kelola/Gas semuanya `ulight` (LIGHT, 6 desimal, total pasokan 2,5 miliar). Inflasi `saham` yang tidak sesuai dengan asal usulnya telah disetel ulang ke nol (inflasi mint=0) melalui proposal tata kelola pada 24-09-2026. Penerbitan LIGHT sepenuhnya ditanggung oleh kontrak mining_reward, menghilangkan penerbitan ganda; pasak yang ada adalah denominasi warisan yang akan dilepas (lihat Lampiran C).
3. **§4.7 Relai WebRTC: Dikerahkan**. 8 node coturn (TURN/STUN, sertifikat TLS turn-*.lightdao.net) + sinyal WSS + sertifikat sementara REST (HMAC-SHA1); saluran data P2P klien saling direlai, dan byte relai dihitung sebagai kontribusi bandwidth 40%; pengukuran aktual ujung ke ujung berhasil melalui transmisi relai TURN. NAT simetris menggunakan TURN dan gagal menurunkan versi ke mode autentikasi murni (konsisten dengan §4.7).
4. **§4.9 Dompet Cerdas: Online**. Login tanpa biji Passkey/WebAuthn (kunci turunan PRF + penyimpanan teks sandi AES-GCM, teks biasa tidak jatuh ke tanah) + pemulihan sosial Shamir 3-dari-5; frase mnemonik dipertahankan sebagai opsi cadangan.
5. **§4.10 Harga Oracle: Umpan harga telah dijalankan**. 7 Pemverifikasi cron bergiliran mengirimkan external_median ke Oracle_twap (harga referensi saat ini 50000 = $0,05); TWAP pada rantai akan diaktifkan setelah kumpulan likuiditas LIGHT/USDC terbentuk. Setelah peningkatan v3, lightfee langsung membaca external_median dan mengubah gas min dinamis.
6. **Tata Kelola Parameter**: Peningkatan v3 akan memindahkan BurnPct/TreasuryPct/TransferUsd/StaticPrice/OracleContract lightfee ke paramstore on-chain. Proposal parameter tata kelola dapat disesuaikan pada saat runtime, sehingga menghilangkan kebutuhan untuk mengoordinasikan peningkatan.

## Penerapan mainnet langsung (26-09-2026)

- Rantai `lightdao-mainnet-1`, 7 validator (JP/KR/SG/US/HK/FR/UK) semuanya OBLIGASI, tidak ada yang dipenjara; memenuhi garis bawah keras §4.7 "Verifikator <7 tidak diizinkan untuk TGE"
- Klien https://lightdao.net (PWA): Dompet kunci sandi + penambangan + relai WebRTC + koleksi, multi-bahasa (Cina/Inggris/Spanyol)
- Penambangan loop tertutup: Kontribusi browser → Finalisasi harian gateway → Merkle root 5 ditandatangani pada rantai (ambang batas 5, dapat diperiksa pada rantai) → Penambang menerima bukti dengan bukti; root harian terus dikirimkan
- Manajemen peningkatan: v2-lightfee (diterapkan @58627), mint zeroing (diterapkan), v3-lightfee (lulus dengan suara bulat, ketinggian 118055 otomatis beralih)
- Untuk endpoint lengkap/alamat kontrak/riwayat peningkatan, silakan lihat gudang `docs/MAINNET_STATUS.md`

---

#Buku Putih LightDAO V2.0

**Verifikasi teks lengkap dan versi proofreading yang dioptimalkan (klien web internasional · audit numerik · audit pihak ketiga · versi model ekonomi yang dioptimalkan) **

Tanggal rilis: 4 Agustus 2026

Prinsip inti: Browser adalah simpul, semua orang dapat berpartisipasi, dan keuntungan dibagi sesuai aturan

Posisi hukum: LIGHT dan sub-token diposisikan sebagai poin kontribusi ekologis dan sertifikat hak klaim distribusi pendapatan SPV, dan bukan merupakan produk sekuritas atau keuangan; atribut hukum tertentu tunduk pada pendapat hukum yang sah di yurisdiksi terkait.

> Dokumen ini adalah versi teks lengkap buku putih yang terverifikasi dan dioptimalkan dan bukan merupakan nasihat investasi, dokumen penerbitan sekuritas, deskripsi produk keuangan, atau segala bentuk komitmen jaminan modal. Silakan berkonsultasi dengan profesional hukum, pajak, dan keuangan sebelum berpartisipasi.

---

## Daftar isi

- Deklarasi sebelumnya
- Prolog : Kisah tiga orang
- Bab 1: Kebenaran yang kita lihat
- Bab 2: Jawaban LightDAO
- Bab 3: Kepatuhan dan isolasi hukum
- Bab 4: Arsitektur Teknis
- Bab 5: Model Ekonomi Token
- Bab 6: Mekanisme Tata Kelola
- Bab 7: Pemeriksaan dan keseimbangan kekuasaan dan definisi peran
- Bab 8: Mekanisme Kepercayaan dan Keamanan
- Bab 9: Operasi investasi dan strategi keluar
- Bab 10: Peta Jalan
- Bab 11: Budaya komunitas dan ekologi pengembang
- Bab 12: Tim dan Konsultan
- Bab 13: Peringatan Risiko dan Penafian
- Lampiran A: Tabel ringkasan parameter utama
- Lampiran B: Derivasi dan verifikasi numerik
- Lampiran C: Log Koreksi Audit
- Lampiran D: Indeks Referensi Cepat Istilah

---

## Ringkasan Eksekutif

**Apa itu LightDAO:** Sebuah organisasi otonom terdesentralisasi yang memungkinkan orang-orang biasa di seluruh dunia untuk berpartisipasi dalam investasi bisnis nyata dan berbagi keuntungan melalui browser. Pengguna tidak perlu membeli mesin penambangan, memiliki latar belakang teknis, atau memenuhi ambang batas investor yang memenuhi syarat - hanya dengan browser dan sedikit waktu, pengguna dapat menyumbangkan sumber daya jaringan untuk menerima hadiah token LIGHT, dan berpartisipasi dalam keputusan investasi melalui pemungutan suara tata kelola.

**Masalah yang bisa dipecahkan:** Kelompok 50% populasi terbawah (sekitar 4 miliar orang) hanya memiliki 2% dari total kekayaan (World Inequality Lab, 2026). Aset berkualitas tinggi (ekuitas swasta, modal ventura) tidak termasuk dalam ambang batas investor yang memenuhi syarat ($200,000 pendapatan tahunan/$1 juta kekayaan bersih). Meskipun ada narasi "partisipasi universal" di bidang mata uang kripto, sebagian besar token pada akhirnya kembali ke nol (CoinGecko 2025: 11,56 juta token mati), dan tingkat partisipasi tata kelola DAO hanya sekitar 3-12%.

**Cara mengatasinya:** Model mesin ganda - 70% dana diinvestasikan pada aset konsumen kaku tingkat komunitas (mesin arus kas), dan 30% diinvestasikan pada teknologi mutakhir (mesin pertumbuhan). Investasi dieksekusi melalui Cayman SPV, dan keuntungan didistribusikan sesuai dengan aturan on-chain: 40% kepada pemegang sub-token, 30% kembali ke brankas untuk diinvestasikan kembali, 20% pembelian kembali CAHAYA untuk penghancuran, dan 10% dikumpulkan ke dana asuransi.

**Data Inti:**

| Indikator | Nilai |
|------|------|
| Jumlah total CAHAYA | 2,5 Miliar, tidak akan pernah dikeluarkan |
| Gudang Investasi | 850 juta (dasar yang dapat diterapkan ≈ $100 juta) |
| Hasil penambangan | 1 miliar, berkurang setengahnya setiap 2 tahun |
| Dirilis pada Hari Era Pertama | ≈684,900 lembar (rata-rata 6,51/hari ketika 100,000 penambang bekerja) |
| Intinya untuk deflasi | Menghentikan pembakaran secara permanen ketika sirkulasi ≤ 1 miliar (tahun 11-12 dari skenario dasar) |
| Ambang Batas Tata Kelola | Usulan ≥ 5.000 CAHAYA; Panitia ≥ 50.000 CAHAYA |
| Tumpukan Teknologi | Cosmos SDK + Tendermint PoS + CosmWasm + PWA |
| Verifikator | Awal 21 (minimal 10), batas atas 100 |
| Pembiayaan awal | Lelang Belanda $15 juta + Pembiayaan strategis Pra-TGE $2,25-3,75 juta |

**Diferensiasi:** Saat ini satu-satunya proyek yang menggabungkan "penambangan web tanpa batas" dengan "investasi entitas SPV yang sesuai". Berbeda dari Pi Network (tidak ada utilitas praktis), Helium (membutuhkan perangkat keras $200+), dan DAO tradisional (tata kelola elit ambang batas tinggi).

**Peta Jalan:** Persiapan Q4 2026 → Pengembangan Q1-Q2 2027 → Uji audit Q3 → Q4 TGE online → Pengguna benih Q1 2028 → Investasi pertama Q2-Q3 → Skala Q4 dan seterusnya.

---

## Deklarasi sebelumnya

**Ini bukan proposal investasi**

"Imbalan ekologis" dan "distribusi pendapatan perjanjian" yang dijelaskan dalam buku putih ini adalah pengaturan insentif yang dihasilkan oleh mekanisme endogen perjanjian dan bukan merupakan bentuk penerbitan sekuritas, penjualan produk keuangan, komitmen jaminan modal, atau nasihat investasi apa pun.

LIGHT dan sub-token tidak memiliki nilai intrinsik dan harganya mungkin kembali ke nol. Sebelum berpartisipasi, silakan berkonsultasi dengan profesional hukum, pajak, dan keuangan Anda, dan bertanggung jawab penuh atas penyimpanan kunci pribadi, deklarasi pajak, dan partisipasi.

---

## Prolog: Kisah tiga orang

Maria bekerja sebagai pengantar makanan di Manila, bekerja 12 jam sehari dan berpenghasilan sekitar 15.000 peso Filipina (sekitar US$270) per bulan. Dia ingin berinvestasi pada merek jaringan teh susu populer di sebelahnya, tetapi pihak lain mengatakan kepadanya: "Investasi minimum dimulai dari US$25.000." Maria tidak dapat memberikan US$25.000.

Kwame mengemudikan layanan ride-hailing di Lagos. Dia optimis dengan jalur kecerdasan buatan dan ingin berinvestasi di perusahaan teknologi keuangan kecil. Lembaga tersebut mengatakan kepadanya: "Jumlah berlangganan minimum adalah US$100.000, dan periode penguncian adalah 5 tahun." Kwame tidak dapat memberikan US$100.000.

Elena adalah pensiunan guru di São Paulo dengan pensiun bulanan sekitar 3.000 real Brasil (sekitar US$550). Dia mendengar bahwa anak-anak tetangganya menghasilkan uang dengan bekerja di perusahaan blockchain, tetapi dia tidak bisa membaca kertas putih dan tidak tahu cara membeli dan mengkonfigurasi peralatan pertambangan profesional.

Ketiganya mewakili sebagian besar masyarakat awam di seluruh dunia: mereka memiliki penilaian dan kemauan untuk berpartisipasi, namun mereka tidak memiliki saluran partisipasi yang rendah, transparan, dan terjangkau.

LightDAO dirancang untuk orang-orang ini. Dengan perangkat berkemampuan Internet, browser, dan sejumlah kecil uang, Anda dapat berpartisipasi dalam pembangunan ekologi; melalui struktur SPV yang patuh, pengguna juga memiliki kesempatan untuk mengakses secara tidak langsung distribusi arus kas perusahaan-perusahaan berkualitas tinggi dan pertumbuhan awal proyek-proyek teknologi mutakhir.

---

## Bab 1: Kebenaran yang kita lihat

### 1.1 Distribusi kekayaan global yang tidak seimbang

Menurut Laporan Ketimpangan Dunia 2026 (selanjutnya disebut “Laporan”) oleh World Inequality Lab:

| Data | Sumber |
|------|------|
| Kekayaan yang dimiliki oleh 0,001% penduduk terkaya dunia (sekitar 60.000 orang) adalah sekitar tiga kali lipat kekayaan gabungan 50% penduduk terbawah (sekitar 4 miliar orang) | Lab Ketimpangan Dunia, 2026 |
| 1% populasi teratas dunia menguasai 23% total pendapatan dan 38% total kekayaan | Lab Ketimpangan Dunia, 2026 |
| 10% populasi teratas dunia menguasai 53% total pendapatan dan 75% total kekayaan | Lab Ketimpangan Dunia, 2026 |
| Kelompok 50% terbawah populasi global hanya menerima 8% dari total pendapatan dan 2% dari total kekayaan | Lab Ketimpangan Dunia, 2026 |

Laporan tersebut menyatakan: "Ketimpangan global masih berada pada tingkat yang ekstrem sepanjang sejarah. Ketimpangan tidak hanya timbul dari operasi alami pasar, namun mencerminkan pilihan kebijakan, struktur kelembagaan, dan distribusi kekuatan ekonomi dan politik yang tidak merata."

**Catatan Sumber:** Data di atas dikutip dari Laporan Ketimpangan Dunia 2026 oleh World Inequality Lab. Laporan ini dipimpin oleh Lucas Chancel, Ricardo Gómez-Carrera, Rowaida Moshrif dan Thomas Piketty (dikonfirmasi oleh situs resmi wid.world). Sebelum rilis resmi, disarankan untuk menandai lebih lanjut nomor bagan tertentu dalam laporan untuk mengurangi kemungkinan kesalahan dalam terjemahan sekunder.

**Pemeriksaan konsistensi data:** Proporsi di atas terus berada dalam tren yang wajar dengan kesimpulan dari Laporan Ketimpangan Dunia tahun 2022 (10% kelompok teratas memiliki 76% dari total kekayaan, 50% kelompok terbawah memiliki 2% dari total kekayaan), dan deviasi berada dalam kisaran yang dapat diterima secara statistik.

### 1.2 Masyarakat biasa dikecualikan dari aset berkualitas tinggi

Yurisdiksi global utama mempunyai ambang batas kualifikasi investor yang ketat untuk ekuitas swasta dan modal ventura:

**Amerika Serikat (Peraturan SEC D, Aturan 501, 17 CFR §230.501):** Investor yang memenuhi syarat (Investor Terakreditasi) harus memenuhi salah satu ketentuan berikut - pendapatan tahunan individu tidak kurang dari US$200.000 (atau total tidak kurang dari US$300.000 dengan pasangan) dan telah memenuhi standar selama dua tahun berturut-turut; atau kekayaan bersih (tidak termasuk tempat tinggal utama) tidak kurang dari US$1.000.000.

**EU (MiFID II, 2014/65/EU, Lampiran II):** Investor profesional (Investor Profesional) harus memenuhi setidaknya dua ketentuan berikut - portofolio investasi instrumen keuangan tidak kurang dari 500.000 euro; memegang jabatan profesional di bidang industri keuangan paling sedikit satu tahun; melaksanakan transaksi skala besar tidak kurang dari 10 per kuartal.

**Praktik Dana Ekuitas Swasta Global:** Jumlah langganan minimum untuk satu dana biasanya antara US$250.000 dan US$1.000.000; aturan peraturan umumnya melarang perilaku mengelak seperti "membagi saham, menurunkan ambang batas, dan memegang perintah atas nama orang lain."

| Jenis aset | Bisakah orang awam berpartisipasi | Alasan utama |
|----------|---------------|----------|
| Ekuitas di perusahaan-perusahaan berkualitas tinggi yang tidak terdaftar | Biasanya tidak bisa | Ambang batas bagi investor yang memenuhi syarat lebih tinggi, misalnya Amerika Serikat mensyaratkan kekayaan bersih tidak kurang dari US$1 juta atau pendapatan tahunan tidak kurang dari US$200,000 |
| Modal ventura (perusahaan teknologi tahap awal) | Biasanya tidak | Terutama terbuka untuk investor yang memenuhi syarat, jumlah investasi satu dana biasanya tidak kurang dari US$250,000 |
| Saham perusahaan tercatat | Ya, tapi keuntungan awal biasanya diraih oleh pelaku pasar primer | Penetapan harga pasar sekunder biasanya mencakup ekspektasi masa depan, dan investor tidak berpartisipasi langsung dalam distribusi keuntungan awal perusahaan |

### 1.3 Tiga kelemahan utama dalam bidang mata uang kripto

**Kekurangan 1: Tingkat kegagalan yang sangat tinggi**

Menurut laporan statistik tahunan CoinGecko pada tahun 2025, sekitar **11,56 juta token** akan kembali ke nol atau menghentikan perdagangan pada tahun 2025 saja (termasuk token ekor panjang di setiap rantai). Dari lebih dari 20 juta token yang CoinGecko lacak secara historis, sebagian besar berada dalam keadaan "mati" (tidak ada volume perdagangan, tidak ada aktivitas pengembangan, dan harga telah turun lebih dari 99% dari harga tertinggi dalam sejarah).

Pada saat yang sama, tingkat kegagalan pasar saham tradisional jauh lebih rendah dibandingkan mata uang kripto. Menurut makalah Bessembinder (2018) "Apakah Saham Mengungguli Treasury Bills?" diterbitkan dalam "Journal of Financial Economics", sebuah studi terhadap semua saham AS dari tahun 1926 hingga 2016:

| Metrik | Data | Sumber |
|------|------|------|
| Proporsi saham yang menciptakan total kekayaan bersih | Hanya sekitar 4% (1.092 saham) | Bessembinder (2018), JFE 129(3):440-475 |
| Pengembalian saham rata-rata seumur hidup | Negatif (berkinerja buruk pada Treasury bills) | Bessembinder (2018), JFE |
| Sekitar 58% dari kinerja seumur hidup saham AS | Tagihan Treasury berkinerja buruk pada periode yang sama | Bessembinder (2018), JFE |
| Jumlah token yang akan direset ke nol/penghentian perdagangan pada tahun 2025 | ≈11,56 juta | Laporan Tahunan CoinGecko 2025 |

**Kesimpulan Perbandingan:** Tingkat kehilangan modal permanen di dunia mata uang kripto jauh lebih tinggi dibandingkan di pasar saham tradisional. Meskipun sekitar 58% saham individual di pasar saham AS berkinerja buruk pada obligasi Treasury, investor masih dapat memperoleh imbal hasil pasar rata-rata melalui dana indeks; di pasar mata uang kripto, sebagian besar token akhirnya kembali ke nol, dan kurangnya alat diversifikasi efektif yang mirip dengan "indeks".

**Sumber pernyataan:** Bessembinder, H. (2018). "Apakah Saham Mengungguli Treasury Bills?" *Jurnal Ekonomi Keuangan*, 129(3), 440-475. Universitas Negeri Arizona. Makalah ini adalah dokumen yang banyak dikutip di bidang keuangan (kutipan >2.000), dan datanya mencakup semua saham AS di database CRSP dari tahun 1926 hingga 2016. Data CoinGecko berasal dari Laporan Statistik Status Ketahanan Token 2025 (dirilis pada Januari 2026), yang telah dilaporkan oleh banyak media keuangan (Sina Finance, Phemex, RBC Crypto).

**Kekurangan 2: Penambangan sangat terpusat**

Penambangan Bitcoin telah menunjukkan tingkat konsentrasi yang tinggi:

| Kolam penambangan | Rasio tingkat hash |
|------|---------|
| Pengecoran AS | Sekitar 30% |
| Kolam Semut | Sekitar 19% |
| MelaluiBTC | Sekitar 14,5% |
| F2Kolam | Sekitar 10% |
| Kolam MARA | Sekitar 5% |
| Gabungan dua kumpulan penambangan teratas | Lebih dari 50% |
| Gabungan empat kumpulan penambangan teratas | Sekitar 75% |

**Catatan Sumber:** Data di atas dikumpulkan dari laporan distribusi hashrate bulanan tahun 2025 (CoinGradient 2025.3 "Foundry, Antpool, dan Viabtc Dominate Bitcoin Mining"; HashrateIndex "10 Kumpulan Penambangan Bitcoin Teratas tahun 2025"). Nilai spesifik dari sumber data yang berbeda mungkin sedikit berbeda (biasanya dalam ±2%), namun kesimpulan bahwa "empat kumpulan penambangan teratas mengendalikan sekitar 75% daya komputasi" tercermin dalam berbagai platform pemantauan arus utama.

**Kekurangan 3: Tingkat partisipasi tata kelola DAO sangat rendah**

| Data | Sumber |
|------|------|
| Tingkat partisipasi pemungutan suara di sebagian besar DAO hanya sekitar 3%-12% (median sekitar 6%) | DeepDAO (2025) Agregasi data tata kelola on-chain; Laporan Tata Kelola DAO Ruang Rapat (2024) |
| Sejumlah kecil pemegang mata uang mengendalikan sebagian besar hak suara (konsentrasi kekuasaan tata kelola yang tinggi) | ACM (2024) "Tata Kelola DAO: Hak Suara, Partisipasi, dan Kontroversi" DOI:10.1145/3777416 |

### 1.4 Wawasan Inti

Saya punya penilaian, tapi tidak ada tiket masuk; Aku punya penglihatan, tapi tak punya hak untuk berbicara; Saya ingin berpartisipasi, tetapi saya terhalang oleh ambang batas yang tinggi.

---

## Bab 2: Jawaban LightDAO

### 2.1 Penentuan posisi inti

LightDAO adalah organisasi otonom investasi nasional dengan tata kelola on-chain sebagai inti dan SPV kepatuhan sebagai pembawa pelaksanaan investasi. Melalui rantai publik yang dirancang khusus untuk node web ringan, pengguna global dapat berpartisipasi dalam pemeliharaan jaringan, pemungutan suara tata kelola, dan berbagi manfaat ekologis sesuai aturan hanya dengan satu browser.

### 2.2 Model mesin ganda

| Mesin | Arah Investasi | Sasaran | Karakteristik Pendapatan |
|------|---------|------|---------|
| Mesin Satu: Mesin Arus Kas (Shou) | Aset layanan konsumsi kaku tingkat komunitas | Membentuk arus kas yang berkesinambungan dan mendistribusikan keuntungan sesuai aturan | Kejar stabilitas relatif, tapi jangan menjanjikan pendapatan tetap |
| Mesin 2: Mesin pertumbuhan (serangan) | Perusahaan teknologi mutakhir | Dapatkan apresiasi ekuitas dan exit return | Fleksibilitas potensial tinggi, tetapi mungkin juga menghadapi kerugian atau kegagalan keluar |

**Disiplin alokasi:** Prinsipnya, alokasikan 70% dana pada aset dengan arus kas stabil dan 30% pada target pertumbuhan tinggi.

**Jalur pertumbuhan skala investasi:** Ukuran investasi tunggal tumbuh secara dinamis seiring dengan harga LIGHT dan kapasitas brankas - periode awal (LIGHT $0,02-$0,05) cocok untuk aset kecil tingkat komunitas sebesar $2,55 juta-$6,37 juta; tahap pertumbuhan ($0,05-$0,30) memasuki rantai regional dan putaran Seed-A sebesar $6,37 juta-$38,25 juta (membandingkan PE Pasar Menengah Bawah); pada tahap matang ($0,30-$1,00), mencapai tingkat PE pasar menengah sebesar $38,25 juta hingga $127,5 juta; dalam tahap skala ($1,00+), perusahaan dapat melakukan akuisisi skala besar dan investasi Pra-IPO lebih dari $127,5 juta. Batasan keras: satu transaksi tidak boleh melebihi 15% dari sisa jumlah perbendaharaan investasi (lihat Bab 9 untuk rinciannya).

**Prinsip penentuan posisi target yang pertama:** Daripada mengasumsikan nama perusahaan tertentu, pertama-tama buatlah kerangka penyaringan - berikan prioritas pada aset layanan konsumen yang kaku di tingkat komunitas, yang memerlukan model ekonomi satu toko yang terbukti, catatan arus kas yang stabil (margin EBITDA dalam tiga tahun terakhir tidak kurang dari 10%, dan volatilitas antar tahun tidak lebih tinggi dari 15%) dan jalur ekspansi regional yang jelas. Target spesifiknya ditentukan oleh usulan masyarakat.

### 2.3 Proposisi nilai inti

**Browser adalah simpulnya** - Tidak perlu membeli mesin penambangan atau memiliki latar belakang teknis profesional. Anda dapat berpartisipasi dalam kontribusi jaringan dengan mengunjungi platform web resmi.

**Semua orang dapat berpartisipasi** - Setelah mencapai ambang batas tata kelola, pemegang LIGHT dalam jumlah kecil juga dapat berpartisipasi dalam pemungutan suara untuk bersama-sama memutuskan arah alokasi dana.

**Pembagian keuntungan sesuai aturan** - Keuntungan operasional perusahaan yang diinvestasikan dan hasil keluar dari proyek teknologi akan didistribusikan sesuai dengan aturan on-chain dan pengaturan SPV.

### 2.4 Slogan

“Browser Anda juga bisa menjadi pintu masuk ke aset berkualitas tinggi.”

### 2.5 Analisis diferensiasi produk kompetitif

| Dimensi | Jaringan Pi | Helium | DAO Tradisional (MakerDAO, dll.) | CahayaDAO |
|------|-----------|--------|---------------------|----------|
| Metode partisipasi | Klik pada aplikasi seluler | Beli hotspot perangkat keras ($200-$1000) | Token pembelian + operasi on-chain | Akses browser, tanpa biaya perangkat keras |
| Biaya masuk | Nol (tetapi tidak ada kegunaan praktisnya) | Tinggi (perangkat keras + instalasi) | Sedang hingga tinggi (perlu membeli token tata kelola) | Nol (hanya browser) |
| Jumlah total token | 100 miliar | 223 juta | Bervariasi | 2,5 miliar |
| Fungsi Investasi Aktual | Tidak ada | Tidak ada (hanya jangkauan jaringan) | Ya (tetapi ambang batasnya sangat tinggi) | Ya (Struktur SPV, semua orang dapat berpartisipasi) |
| Sumber pendapatan | Tidak jelas | Biaya penggunaan jaringan | Biaya perjanjian | Keuntungan perusahaan + pengembalian keluar + Biaya bahan bakar |
| Isolasi hukum | Tidak ada | Tidak ada | Beberapa ya | Cayman SPV+ZK-KYC |
| Tingkat partisipasi pemerintahan | Sangat rendah (tidak ada tata kelola yang substansial) | Rendah | Sekitar 6% | Target >15% (pemungutan suara dua dimensi + insentif) |

**Perbedaan inti LightDAO:** Saat ini merupakan satu-satunya proyek yang menggabungkan "penambangan web tanpa batas" dengan "investasi entitas SPV yang sesuai". Pengguna tidak hanya menyumbangkan sumber daya jaringan untuk mendapatkan hadiah token, tetapi juga secara langsung berpartisipasi dalam keputusan investasi perusahaan nyata melalui pemungutan suara tata kelola dan berbagi keuntungan operasi.

> **[Terminologi dalam bab ini]**
> **DAO** (Organisasi Otonomi Terdesentralisasi): Suatu bentuk organisasi di mana aturan tata kelola dikodekan melalui kontrak pintar dan keputusan kolektif dibuat oleh pemegang token. Tidak ada hierarki perusahaan tradisional.
> **SPV** (Special Purpose Vehicle): badan hukum independen (biasanya terdaftar di Kepulauan Cayman) yang didirikan untuk transaksi atau investasi tertentu guna mencapai isolasi risiko - hutang dan tanggung jawab hukum SPV tidak dialihkan ke DAO itu sendiri.
> **DePIN** (Jaringan Infrastruktur Fisik Terdesentralisasi, jaringan infrastruktur fisik terdesentralisasi): Model jaringan yang menggunakan token untuk mendorong pengguna menyumbangkan sumber daya fisik (bandwidth, penyimpanan, daya komputasi, jangkauan nirkabel, dll.) untuk membangun infrastruktur.
> **PE Pasar Menengah Bawah** (ekuitas swasta kelas menengah hilir): segmen pasar industri ekuitas swasta global. Ukuran satu transaksi biasanya $10 juta hingga $100 juta, dan EBITDA perusahaan target adalah antara $2 juta dan $15 juta.

---

## Bab 3: Kepatuhan dan isolasi hukum

### 3.1 Lapisan isolasi hukum SPV

DAO tidak secara langsung memiliki ekuitas di perusahaan fisik mana pun. Seluruh investasi eksternal dilaksanakan melalui special Purpose Vehicle (SPV) yang didirikan di Kepulauan Cayman.

| Poin Desain | Deskripsi |
|---------|------|
| Piagam SPV | Disepakati dengan jelas bahwa pengoperasian SPV harus mematuhi resolusi efektif DAO |
| Definisi hukum sub-token | Sub-tokennya adalah "Sertifikat hak klaim distribusi pendapatan SPV", yang hanya mewakili kualifikasi distribusi arus kas masa depan |
| Tidak membawa hak pemegang saham | Tidak memiliki hak tata kelola perusahaan, preferensi likuidasi, atau hak pemegang saham apa pun |
| Direktur SPV | dilayani oleh pihak ketiga yang independen; DAO dapat mengganti direktur dengan memberikan resolusi yang valid |
| Pengawasan dana | Rekening bank diawasi oleh lembaga kustodian berlisensi, dan transfer dana harus melewati verifikasi multi-tanda tangan dan kepatuhan |
| Penyelesaian sengketa SPV | Piagam SPV menetapkan klausul arbitrase (SIAC atau ICC), dan DAO dapat memulai proses arbitrase melalui resolusi tata kelola |

### 3.2 Verifikasi opsional dan perlindungan privasi

**Tidak diperlukan identifikasi untuk berpartisipasi dalam protokol itu sendiri. ** Kunjungi halaman web, buat dompet, sumbangkan sumber daya, terima CAHAYA, mulai dan berpartisipasi dalam pemungutan suara tata kelola - tidak perlu mengunggah dokumen selama keseluruhan proses, dan tidak ada informasi identitas pribadi (PII) yang disimpan di rantai.

Hanya ketika pengguna secara aktif menggunakan layanan pihak ketiga yang diatur, verifikasi bahwa layanan itu sendiri harus berfungsi sesuai dengan hukum akan dilakukan. Verifikasi ini dikumpulkan, dilakukan dan disimpan oleh pihak layanan. LightDAO tidak mengumpulkan, mentransfer, atau menyimpan data apa pun:

| Skenario | Siapa yang melakukan verifikasi | Apa yang perlu dilakukan pengguna |
|---|---|---|
| Membeli/menjual melalui saluran fiat | Pihak ketiga berlisensi (seperti MoonPay, Ramp Network, Transak) | Selesaikan proses kepatuhan sesuai dengan persyaratan penyedia layanan itu sendiri |
| Pertukaran sub-token (sertifikat saham investasi) | Tergantung pada kebutuhan produk tertentu dan penyedia layanannya | Anda hanya dapat melakukan penambangan dan tata kelola, tanpa verifikasi sama sekali |
| Penarikan ke kartu bank/pembayaran lokal | Penyedia layanan penarikan dan pembayaran | Selesaikan proses kepatuhan seperti yang diminta oleh penyedia layanan |

Prinsip inti: **Tidak ada verifikasi secara default; verifikasi hanya terjadi pada saat pengguna aktif memasuki layanan yang diatur, dan ditanggung oleh penyedia layanan. **Tidak seorang pun akan kehilangan hak untuk menambang, menahan, mentransfer, atau memilih karena "kegagalan memverifikasi".

> Teknologi dicadangkan: Jika jenis aset tertentu memerlukan ambang batas kualifikasi di masa mendatang, pengguna akan memegang sertifikat dalam bentuk bukti tanpa pengetahuan (ZK), dan rantai hanya akan memverifikasi "apakah terpenuhi" tanpa informasi identitas apa pun - ini adalah bagian dari peta jalan dan bukan merupakan persyaratan saat ini.

### 3.3 Pernyataan Tanggung Jawab Pajak

Perjanjian tersebut tidak menyediakan layanan deklarasi pajak, dan kewajiban pajak atas semua imbalan ekologis dan pendapatan terkait ditanggung oleh penggunanya sendiri. Pengguna harus mematuhi undang-undang dan peraturan yang relevan di lokasi domisili pajak mereka.

### 3.4 Akses pengguna: terbuka untuk semua orang

**Tidak ada batasan untuk pendaftaran dan partisipasi**: Tidak diperlukan email, nomor ponsel, akun sosial, atau bukti identitas; hanya perangkat yang dapat membuka halaman web yang Anda perlukan. LightDAO** tidak secara aktif membatasi partisipasi pengguna di negara atau wilayah mana pun, juga tidak menerapkan geofencing. **

Satu-satunya kendala eksternal berasal dari layanan pihak ketiga: jika undang-undang di suatu tempat memiliki persyaratan lain untuk layanan tertentu (seperti penyetoran dan penarikan mata uang fiat), layanan tersebut akan dilakukan oleh lembaga berlisensi lokal sesuai dengan hukum di pihak mereka dan tidak akan memengaruhi penggunaan fungsi on-chain oleh siapa pun (penambangan, penyimpanan, transfer, pemungutan suara, proposal).

Jika yurisdiksi tertentu mengeluarkan peraturan yang secara eksplisit melarang di masa depan, urutan respons protokol adalah:

1. Pertama, pastikan bahwa hak pelepasan aset dari pengguna yang ada tidak terpengaruh - aset dalam rantai tidak dapat dibekukan, dan siapa pun dapat mentransfer LIGHT dan sub-tokennya kapan saja;
2. Tetap dapat diakses melalui beberapa portal front-end (termasuk mirror IPFS dan mirror komunitas);
3. Langkah terakhir adalah menyesuaikan cakupan **layanan pihak ketiga** yang tersedia dalam lingkup penegakan hukum.

Singkatnya: pembatasan hanya dapat diterapkan pada layanan, bukan pada manusia. **

### 3.5 Setoran dan penarikan mata uang legal serta saluran lintas rantai

**Saluran mata uang Fiat (agregasi layanan pihak ketiga):** Protokol itu sendiri tidak mengoperasikan layanan penyetoran dan penarikan mata uang legal, namun platform web mengintegrasikan saluran pihak ketiga yang patuh (MoonPay, Ramp Network, Transak, dll.), yang mencakup pasar utama di Amerika Utara, Eropa, Asia Tenggara, dan Amerika Latin; agregasi pasar P2P lokal mencakup Afrika dan Asia Selatan; penarikan mendukung metode pembayaran lokal seperti GCash, M-Pesa, Pix, dan GrabPay.

**Jembatan lintas rantai dan saluran akuisisi LIGHT:** Transaksi AMM bawaan dalam rantai LightDAO setelah TGE; interoperabilitas dengan ekosistem Cosmos melalui IBC; merencanakan wLIGHT (Ethereum/Solana) mulai bulan ke-6; permohonan pencatatan CEX mulai bulan ke-6 tergantung kepatuhan. Jembatan lintas rantai dioperasikan oleh pihak ketiga yang independen, dan laporan audit independen diperlukan sebelum jembatan tersebut online.

### 3.6 Pernyataan Kepatuhan Mekanisme Undangan (Analisis Anti-MLM)

Insentif undangan LightDAO adalah **berbagi satu lapis** (hanya pengundang langsung yang menerima proporsi tetap dari imbalan penambangan yang diundang), dan tidak memiliki fitur inti pemasaran berjenjang (MLM): tidak ada komisi rekursif multi-level; pendapatan berasal dari pelepasan token yang telah ditetapkan sebelumnya dalam protokol, bukan dari prinsipal pendatang baru; tidak ada biaya dan tidak ada biaya masuk untuk berpartisipasi dalam penambangan. Struktur ini lebih dekat dengan "penghargaan rekomendasi kontributor proyek sumber terbuka". Sebelum beroperasi secara formal, pengacara berlisensi di pasar sasaran akan dipekerjakan untuk mengeluarkan pendapat kepatuhan khusus.

> **[Terminologi dalam bab ini]**
> **KYC** (Kenali Pelanggan Anda, Kenali Pelanggan Anda): Proses kepatuhan lembaga keuangan untuk memverifikasi identitas pengguna, biasanya memerlukan penyerahan dokumen identitas, bukti alamat, dll.
> **ZK-KYC** (Zero-Knowledge KYC, zero-knowledge proof KYC): Pengguna tidak perlu mengungkapkan informasi pribadi spesifik dalam perjanjian, dan hanya menggunakan kriptografi untuk membuktikan metode verifikasi kepatuhan "Saya memenuhi persyaratan tertentu" (seperti usia ≥ 18 tahun, kewarganegaraan yang tidak terkena sanksi). Tidak ada data dokumen asli yang disimpan di rantai.
> **PII** (Informasi Identifikasi Pribadi, Informasi Identifikasi Pribadi): Data yang dapat mengidentifikasi orang tertentu secara individu atau gabungan, seperti nama, nomor ID, alamat, karakteristik biometrik, dll.
> **Reg D / Reg S** (Peraturan D/Peraturan S Undang-Undang Sekuritas A.S.): Reg D mengizinkan penempatan swasta kepada "investor yang memenuhi syarat" di Amerika Serikat tanpa registrasi publik (standar definisi Peraturan 501); Reg S mengizinkan penjualan sekuritas kepada orang di luar Amerika Serikat tanpa memicu persyaratan pendaftaran AS.
> **MiFID II** (EU Markets in Financial Instruments Directive II, 2014/65/EU): Kerangka peraturan keuangan UE, Lampiran II-nya menetapkan kriteria identifikasi untuk "investor profesional" (portofolio instrumen keuangan senilai €500 ribu, pengalaman industri keuangan 1 tahun, 10 transaksi skala besar per kuartal, memenuhi persyaratan kedua).
> **MLM** (Pemasaran Bertingkat, pemasaran berjenjang): model bisnis melalui komisi rekursif multi-level (pengembangan downline, pengembangan downline, dan komisi upline lapis demi lapis). Ini pada dasarnya berbeda dari hadiah rekomendasi satu lapis - LightDAO hanya satu lapis (A mengundang B, A mendapat bagian dari B; B mengundang C, A tidak mendapat bagian apa pun dari C).
> **IBC** (Komunikasi Antar-Blockchain, protokol komunikasi lintas rantai): standar lintas rantai asli ekosistem Cosmos, memungkinkan transfer aset dan pesan yang aman antar blockchain yang berbeda tanpa memerlukan perantara terpusat.

---

## Bab 4: Arsitektur Teknis

### 4.1 Apa yang dimaksud dengan rantai publik?

Rantai publik LightDAO dapat dipahami sebagai "buku rekening publik dengan aturan transparan dan tidak dapat diubah sesuka hati": aturan tata kelola ditulis ke dalam kode, dan catatan suara, aliran modal, dan distribusi keuntungan siapa pun dapat ditanyakan dan diverifikasi di rantai tersebut.

### 4.2 Parameter teknis dan demonstrasi pemilihan

| Barang teknis | Seleksi | Dasar seleksi |
|--------|------|---------|
| Kerangka yang mendasari | SDK Kosmos | Arsitektur modular, verifikasi beberapa rantai produksi |
| Mekanisme konsensus | PoS tendermint | Kepastian instan; pembuatan blok membutuhkan waktu 1,5-2 detik; Toleransi kesalahan BFT ≤ 1/3 jahat |
| Kontrak Cerdas | KosmWasm | WebAssembly + Rust, keamanan memori waktu kompilasi |
| Kemampuan lintas rantai | Protokol IBC | Standar lintas rantai asli kosmos |
| Interaksi ujung depan | Aplikasi Web Progresif (PWA) | Browser berjalan, adaptif desktop/seluler, tidak perlu instalasi |

### 4.3 Mekanisme penambangan node yang ringan dan model insentif

#### 4.3.1 Metode penambangan

Pengguna mengakses platform web resmi melalui browser, membuat dompet, dan klik "Mulai Menambang". Selama proses penambangan, pengguna menyumbangkan bandwidth jaringan (relai data dan verifikasi) dan sumber daya komputasi lokal (verifikasi header blok ringan) melalui browser, dan tidak bergantung pada daya komputasi berenergi tinggi.

**Penerapan teknologi sisi web:** Relai P2P saluran data WebRTC; Verifikasi header blok latar belakang Pekerja Web; Cache dan detak jantung offline Service Worker; Koneksi panjang WebSocket.

**Adaptasi browser seluler:** Mengadopsi sistem sesi kumulatif yang valid (4 jam sehari = skor 100%); tidak ada poin yang akan dikurangi untuk menyambung kembali dalam waktu 5 menit setelah pemutusan; Pengguna yang menginstal PWA akan menerima tambahan bonus waktu online sebesar 10%; mekanisme online yang didelegasikan (70% untuk delegasi/30% untuk node relai).

#### 4.3.2—4.3.3 Skema insentif dan model tiga mesin

Ini mengadopsi model tiga mesin "bukti kontribusi PoC + insentif fisi undangan + insentif bonus perilaku".

#### 4.3.4 Kontribusi dimensi dan berat

| Dimensi kontribusi | Berat | Metode pengukuran |
|---------|------|---------|
| Kontribusi relai bandwidth | 40% | Rasio lalu lintas relai unggahan terhadap volume data verifikasi |
| Durasi sesi efektif | 30% | Sesi efektif kumulatif harian (4 jam = 100%) |
| Blokir kontribusi verifikasi | 20% | Jumlah dan keakuratan header blok yang diverifikasi secara efektif |
| Stabilitas jaringan | 10% | Penundaan koneksi, tingkat kehilangan paket, waktu respons |

#### 4.3.5 Rumus perhitungan imbalan

**Hadiah Penambangan Harian = Hadiah Dasar × Skor Bobot Kontribusi × (1 + Bonus Undangan) × (1 + Bonus Perilaku)**

- BaseReward = Jumlah total yang dikeluarkan oleh seluruh jaringan pada hari itu *** Jumlah total penambang aktif pada hari itu
- Bonus undangan = jumlah undangan efektif × 1% (batas atas 20%)
- Bonus perilaku = 5% partisipasi pemungutan suara + 5% kontribusi konten + 5% aktivitas komunitas + 5% kualitas verifikasi node (batas atas 20%)
- Koefisien bonus penuh = (1+20%) × (1+20%) = 1,44 kali

#### 4.3.6 Mengundang insentif fisi

| Tingkat | Jumlah undangan yang valid | Rasio pembagian undangan | Hadiah tambahan satu kali | Bonus bobot tata kelola |
|------|------------|------------|--------------|------------|
| Penambang | 0 orang | — | Hadiah penambangan dasar | Tidak ada |
| Pengkhotbah | Tidak kurang dari 3 orang | 10% | 100 CAHAYA | Tidak ada |
| Duta Besar | Tidak kurang dari 10 orang | 15% | 500 CAHAYA + lencana rantai | Bobot suara +5% |
| Mitra | Tidak kurang dari 50 orang | 20% | 2.500 CAHAYA + lencana rantai | Bobot suara +10% |

Bonus bobot tata kelola dan bonus reputasi (hingga +30%) disusun secara independen, dengan total batas atas +40%. Bonus undangan mencapai puncaknya ketika ada 20 orang (20×1%=20%).

#### 4.3.7 Mekanisme anti-cheat

Deteksi integritas lingkungan browser (sidik jari Canvas/WebGL/WebRTC), deteksi kedalaman paket, pengelompokan IP dan analisis pola perilaku, sidik jari perilaku multidimensi (lintasan mouse/irama keyboard/perilaku gulir), verifikasi keaslian alamat undangan. Biaya serangan anti-Sybil: $50.000-$200.000 untuk membuat 10.000 sidik jari independen; target tingkat deteksi >90-95%.

### 4.4 Matriks Fungsi Token CAHAYA

Bahan bakar jaringan (Biaya gas), hak tata kelola (pemungutan suara/proposal/kampanye), pengikatan janji (margin/kampanye/verifier), pertukaran investasi (sub-token), insentif ekologi (penambangan/undangan/perilaku), ekspansi di masa depan (dApp/NFT/cross-chain).

### 4.5 Mekanisme biaya gas dan biaya transaksi

**Prinsip Desain:** Biaya bahan bakar ditetapkan dengan setara USD, dan jumlah sebenarnya CAHAYA yang dibebankan secara otomatis dikonversi setiap 24 jam oleh oracle on-chain (Bagian 4.10). Hal ini memastikan bahwa tidak peduli apakah harga LIGHT naik atau turun, biaya pembayaran aktual pengguna (dalam dolar AS) tetap stabil, menghindari masalah "harga mata uang naik 100 kali lipat → biaya transfer menjadi $10" atau "harga mata uang turun 90% → penukaran tiket tanpa biaya".

**Target biaya bahan bakar USD:**

| Jenis transaksi | Target setara USD | Koleksi nyata saat LIGHT=$0,05 | Koleksi nyata saat LIGHT=$0,50 | Niat desain |
|---------|------------|------------------|------------------|----------|
| Pemindahan biasa | $0,001 | 0,02 CAHAYA | 0,002 CAHAYA | Ambang batas yang sangat rendah untuk memastikan bahwa pengguna dalam jumlah kecil dapat mentransfer uang dengan bebas |
| Pemungutan Suara Tata Kelola | $0,005 | 0,10 CAHAYA | 0,01 CAHAYA | Sedikit lebih tinggi dari transfer untuk mencegah penyikatan suara yang tidak memerlukan biaya |
| Kirimkan proposal | $0,10 | 2.0 CAHAYA | 0,2 CAHAYA | Bekerjasama dengan sistem simpanan untuk meningkatkan keseriusan proposal |
| Pertukaran sub-token | $0,50 | 10.0 CAHAYA | 1.0 CAHAYA | Biaya lebih tinggi, sesuai dengan keseriusan operasi skala besar |
| Pelaporan detak jantung penambangan | $0 (gratis) | 0 | 0 | Tidak ada Gas yang dikenakan biaya untuk kontribusi penambangan, memastikan partisipasi tanpa biaya |

**Aturan konversi dinamis:**

- 实际Gas费（LIGHT）= USD目标 ÷ 预言机24h TWAP价格
- 每24小时（UTC 00:00区块）由oracle_twap合约自动更新换算比率
- 设置下限：任何交易类型的Gas费不低于0.001 LIGHT（防止价格为零时Gas归零）
- 设置上限：任何交易类型的Gas费不高于100 LIGHT（防止价格极低时Gas过高阻碍使用）
- USD目标值本身可通过微型提案（$100保证金）由治理调整

**Peraturan alokasi biaya bahan bakar:**

| Tujuan | Proporsi | Fungsi |
|------|------|------|
| Hancur secara permanen | 50% | Deflasi yang terus berlanjut, mengurangi pasokan sirkulasi |
| Hadiah validator | 30% | Berikan insentif kepada validator untuk menjaga keamanan jaringan dan menghasilkan blok |
| Perbendaharaan Ekologis | 20% | Pendanaan tambahan pengembang dan dana operasional komunitas |

**Perkiraan deflasi biaya bahan bakar:** Dengan asumsi rata-rata 100.000 transaksi aktif harian dan rata-rata biaya bahan bakar sebesar $0,005 (terutama voting dan transfer), setara dengan USD yang dimusnahkan per hari = 100.000 × $0,005 × 50% = $250/hari. Jika LIGHT=$0,05, setara dengan 5.000 LIGHT/hari≈1,825 juta/tahun; ketika LIGHT=$0,50, itu setara dengan 500 LIGHT/hari≈182,500/tahun. Kuantitas CAHAYA dengan deflasi biaya bahan bakar menurun seiring dengan kenaikan harga (setara dengan USD konstan), namun dukungannya terhadap harga tercermin dari "pembelian yang setara secara terus-menerus" - setiap transaksi menghancurkan token dengan kurs USD yang tetap.

### 4.6 Sistem verifikasi

| Dimensi | Validator | Node cahaya (penambang browser) |
|------|--------|-------------------|
| Tanggung jawab | Pembuatan blok, konsensus, simpul penuh | Verifikasi header blok, relai data |
| Mempertaruhkan | Minimal 500.000 CAHAYA | Tidak ada |
| Pendapatan | Biaya bahan bakar 30% + kumpulan pelepasan harian 5% | Hadiah penambangan PoC (kumpulan rilis harian 95%) |
| Kuantitas | Awal 21, batas atas 100 | Tidak ada batas atas |
| Menebas | Penalti 5% untuk penandatanganan ganda + larangan 180 hari | Tidak ada |

**Mulai secara bertahap (toleransi kesalahan BFT: N≥3f+1):**

| Fase | Jumlah validator | Toleransi kesalahan f | Kondisi penghentian rantai | Pengalaman pengguna |
|------|-----------|-------|-----------|----------|
| Testnet (3 bulan sebelum TGE) | 7 | 2 | 3 offline secara bersamaan | Pengujian internal dapat mentolerir interupsi singkat |
| Jaringan Utama TGE | Minimal 10, target 21 | 3-6 | 4-7 offline secara bersamaan | Interupsi sesekali (<1 kali per kuartal) untuk memperlancar |
| Terbuka untuk pemilihan mulai bulan ke 7 | 21-100 | 6-33 | 7-34 offline secara bersamaan | Pengguna tidak menyadari |

**Intinya: TGE tidak boleh dieksekusi ketika ada <7 validator. ** Kurang dari 7 berarti f ≤ 1. Setiap kegagalan satu titik akan menyebabkan seluruh rantai terhenti, yang setara dengan "tidak tersedianya produk" untuk pengguna non-teknis.

### 4.7 Lapisan infrastruktur jaringan

Node validator membawa gateway akses WebSocket secara terdistribusi (setiap validator memiliki batas atas 50.000 koneksi); Pensinyalan P2P disediakan oleh validator + node relai komunitas; agregasi Merkle detak jantung hanya mengirimkan hash Root per blok (O(1) overhead on-chain); ujung depan didistribusikan melalui IPFS+CDN.

Jaringan P2P: Kerangka WebRTC ICE (prioritas STUN/penggantian TURN); sekitar 70-80% pengguna dapat terhubung secara langsung, 20-30% pengguna NAT simetris melewati relai TURN; ketika P2P gagal, versinya diturunkan ke "mode otentikasi murni".

Spesifikasi kinerja: TPS teoritis 1.000-3.000; ukuran blok 2MB (tata kelola dapat disesuaikan); sinkronisasi simpul cahaya <30 detik; juta node detak jantung Agregasi Merkle <500ms.

### 4.8 Mekanisme verifikasi bukti kontribusi

Arsitektur verifikasi tiga tingkat: (1) Tantangan pengambilan sampel silang acak pemverifikasi (5% node setiap 10 menit, waktu respons 30 detik); (2) Verifikasi timbal balik rekan P2P (8-16 rekan secara mandiri mencatat volume pertukaran data, ambil median); (3) Agregasi Merkle on-chain (setiap blok mengirimkan Root skor kontribusi, pengguna dapat memeriksa sendiri melalui Merkle Proof). Gagal menantang 3 kali berturut-turut → skor hari itu akan diatur ulang ke nol; total 5 kali dalam 7 hari → tinjauan anti-kecurangan akan dipicu.

### 4.9 Dompet dan Manajemen Kunci

Arsitektur tiga tingkat: (1) Dompet pintar tertanam (Passkey/WebAuthn, tidak memerlukan frasa mnemonik, menargetkan 80%+ pengguna); (2) Dompet pemulihan sosial (3-5 restorasi, Shamir sharding, 2/3 konfirmasi mayoritas); (3) Dompet yang dihosting sendiri (frasa mnemonik BIP-39 + kompatibel dengan dompet perangkat keras). Biaya bahan bakar untuk 100 transaksi pertama pengguna baru akan dibayar oleh dana ekologi (model Paymaster).

### 4.10 Harga Oracle

TWAP on-chain (harga rata-rata tertimbang waktu 30 hari dari kumpulan LIGHT/USDC) adalah sumber harga utama; 3+ agregasi DEX/CEX eksternal ditambahkan (validator mengirimkan secara bergilir, mengambil median); deviasi >±15% memicu tanda pengecualian; deviasi blok tunggal >5% tidak termasuk dalam TWAP (manipulasi pinjaman anti-flash); mundur ke TWAP on-chain murni ketika semua oracle eksternal gagal.

### 4.11 Arsitektur Modul Kontrak Cerdas

10 kontrak inti: light_token, mining_reward, governance, treasury_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, Insurance_fund. Kontrak inti harus menyelesaikan verifikasi formal sebelum TGE.

### 4.12 Peningkatan Protokol dan Tata Kelola Rantai

Peningkatan level 4: Penyesuaian parameter L1 (pemungutan suara tata kelola 24-72 jam) → Migrasi kontrak L2 (proposal utama + audit + penundaan 72 jam) → Perubahan konsensus L3 (66% lolos + 2/3 sinyal validator + periode perlindungan fork 7 hari) → Perbaikan darurat L4 (penangguhan komite bayangan + perbaikan terbaru multi-tanda tangan + ratifikasi 72 jam).

> **[Terminologi dalam bab ini]**
> **Cosmos SDK**: Kerangka kerja pengembangan blockchain modular yang memungkinkan pengembang merakit rantai publik khusus seperti blok penyusun. Beberapa rantai produksi (seperti Cosmos Hub dan Osmosis) telah memverifikasi kematangannya.
> **Tendermint PoS** (Proof of Stake, Proof of Stake): Mekanisme konsensus di mana validator memperoleh hak untuk memproduksi blok dengan menjaminkan token (daripada bersaing untuk mendapatkan daya komputasi). Memberikan "finalitas instan" - setelah sebuah blok dilakukan, blok tersebut tidak dapat dibatalkan.
> **BFT** (Toleransi Kesalahan Bizantium, Toleransi Kesalahan Bizantium): Sebuah mekanisme dalam sistem terdistribusi yang dapat mentolerir beberapa node yang melakukan kejahatan atau tidak berfungsi dan tetap mencapai konsensus dengan benar. Tendermint BFT dapat mentolerir tidak lebih dari 1/3 validator yang bertindak jahat atau offline pada saat yang bersamaan.
> **CosmWasm**: Mesin kontrak pintar ekosistem Cosmos, berdasarkan teknologi WebAssembly, mendukung penggunaan bahasa Rust untuk menulis kontrak, dan memiliki fitur keamanan memori waktu kompilasi (mencegah kerentanan umum seperti buffer overflows).
> **PWA** (Aplikasi Web Progresif, Aplikasi Web Progresif): Teknologi web yang berjalan di browser namun memiliki pengalaman aplikasi seperti aslinya. Ini mendukung caching offline, pemberitahuan push, dan menambahkan ke layar beranda tanpa mengunduh dan menginstal melalui toko aplikasi.
> **WebRTC/WebSocket**: Dua teknologi komunikasi real-time browser. WebRTC digunakan untuk relai data P2P (transmisi langsung antar node); WebSocket digunakan untuk menjaga koneksi jangka panjang antara klien dan verifikator (detak jantung, pemberitahuan hadiah).
> **PoC** (Bukti Kontribusi): Mekanisme insentif yang diadopsi oleh LightDAO memberikan imbalan dengan memverifikasi sumber daya jaringan (relai bandwidth, verifikasi blok, waktu online) yang benar-benar disumbangkan oleh pengguna, daripada mengandalkan persaingan daya komputasi atau janji modal.
> **Merkle Tree** (Merkle Tree): Struktur data pohon hash yang memungkinkan verifikasi efisien atas integritas entri tertentu dalam sejumlah besar data. Buku putih ini digunakan untuk menggabungkan jutaan detak jantung node cahaya ke dalam satu hash Root dan mengunggahnya ke overhead penyimpanan rantai (O(1)).
> **Biaya bahan bakar**: Biaya penanganan yang diperlukan untuk melaksanakan transaksi atau mengontrak operasi di blockchain, digunakan untuk mengkompensasi verifikator atas sumber daya komputasi dan penyimpanan. Biaya Gas LightDAO ditetapkan dalam setara USD, dan secara otomatis dikonversi menjadi jumlah LIGHT oleh oracle setiap 24 jam.
> **Pemotongan** (penalti): Mekanisme penalti di mana verifikator terpaksa memotong sebagian token yang dijanjikan karena melakukan kejahatan (seperti penandatanganan ganda) atau offline dalam waktu lama. Ini adalah jaminan ekonomi untuk keamanan jaringan PoS.
> **Oracle** (Oracle): Komponen infrastruktur yang secara aman mentransmisikan data off-chain (seperti harga pasar, cuaca, skor olahraga) ke dalam kontrak pintar on-chain. LightDAO menggunakan arsitektur oracle hybrid dari agregasi multi-sumber TWAP + on-chain.
> **TWAP** (Harga Rata-Rata Tertimbang Waktu): Harga setiap blok dalam suatu periode waktu diberi bobot yang sama berdasarkan waktu untuk mengurangi dampak manipulasi transaksi seketika dalam jumlah besar pada referensi harga.
> **AMM** (Pembuat Pasar Otomatis): Protokol perdagangan terdesentralisasi yang mewujudkan pertukaran token melalui kumpulan likuiditas (bukan buku pesanan). Harga secara otomatis ditentukan oleh proporsi aset dalam kumpulan berdasarkan rumus.
> **DEX / CEX**: DEX (Pertukaran Terdesentralisasi, pertukaran terdesentralisasi) tidak perlu menghosting aset pengguna dan memperdagangkan peer-to-peer melalui kontrak pintar; CEX (Pertukaran Terpusat, pertukaran terpusat) mengharuskan operator untuk menyimpan aset dan mencocokkan transaksi.
> **IPFS** (Sistem File AntarPlanetary, Sistem File AntarPlanetary): Penyimpanan file terdesentralisasi dan protokol distribusi, digunakan dalam buku putih ini untuk hosting aplikasi front-end yang tahan sensor (meskipun nama domain diblokir, pengguna masih dapat mengakses platform melalui IPFS).

---

## Bab 5: Model Ekonomi Token

### 5.1 Dasar desain total

**Total pasokan RINGAN: 2,5 miliar (2.500.000.000), dan tidak akan pernah diterbitkan tambahan. **

| Pembandingan proyek | Jumlah total | Metode partisipasi | Perbandingan dengan LightDAO |
|---------|------|---------|------------------|
| Bitcoin | 21 juta | Mesin penambangan PoW | Referensi naratif, ambang batasnya jauh tinggi |
| Helium (HNT) | 223 juta | Hotspot perangkat keras $200+ | Tolok ukur DePIN, skala perangkat keras terbatas |
| Filecoin (FIL) | 2 miliar | Perangkat keras penyimpanan | Yang paling dekat besarnya, keduanya "menyumbangkan sumber daya dengan imbalan token" |
| Kaspa (KAS) | 28,7 miliar | Kartu grafis PoW | Penurunan yang terlalu besar dan mulus memiliki nilai referensi |
| Jaringan Pi | 100 miliar | Klik seluler | Bahan ajar negatif: Jumlah terlalu besar → persepsi nilai sangat rendah |

**Alasan inti memilih 2,5 miliar koin:**

1. **Kapasitas investasi (kendala utama):** 850 juta koin di brankas × harga dasar $0,15 × 75% tingkat pemanfaatan = **$95,63 juta ≈ $100 juta** modal yang dapat diterapkan, mencapai ambang batas minimum yang dapat dipercaya dari PE Pasar Menengah Bawah. Dasar akademis: Cong, Li & Wang (2021) "Tokenomics: Adopsi dan Penilaian Dinamis" (*Ulasan Studi Keuangan* 34(3):1105-1155, NBER w27222) membuktikan bahwa utilitas platform (pengembalian investasi → pembelian kembali → dukungan harga) adalah pendorong mendasar dari nilai token, bukan luasnya distribusi.
2. **Panduan jaringan:** 1 miliar koin ditambang, dan 684.900 koin dilepaskan pada hari pertama epoch tersebut. Ketika terdapat 100.000 penambang aktif, rata-rata per kapita adalah 6,51 CAHAYA/hari, mempertahankan "persepsi bilangan bulat".
3. **Kelayakan operasional:** 10% dana operasional strategis (250 juta koin) untuk mengatasi kesenjangan pendanaan pengembangan/audit/legal sebelum TGE ($1,10-2,85 juta). Model komunitas murni tidak dapat menutupi biaya ini.
4. **Kelayakan deflasi:** Keuntungan 1 miliar koin tercapai pada tahun ke-11 hingga ke-12 berdasarkan skenario dasar (25-30% lebih pendek dibandingkan 15 tahun+ dari rencana 21 miliar).
5. **Pembandingan yang wajar:** Level yang sama dengan Filecoin (2 miliar), yang merupakan salah satu dari lima proyek teratas di bidang DePIN berdasarkan nilai pasar.

### 5.2 Rencana distribusi Token

| Kategori Alokasi | Rasio | Kuantitas | Tujuan | Metode Rilis |
|---------|------|------|------|---------|
| Penambangan node ringan | 40% | 1 miliar | Hadiahi kontributor jaringan | Dibelah dua setiap 2 tahun, dirilis secara real time berdasarkan kontribusi |
| Gudang Investasi Perusahaan | 34% | 850 juta keping | Eksekusi investasi di bawah tata kelola DAO (hancur saat berinvestasi) | Penguncian multi-tanda tangan, hanya dilepaskan dan dimusnahkan melalui resolusi yang valid |
| Dana Pembangunan Ekologi | 16% | 400 juta | Likuiditas, airdrop, pendanaan pengembang, operasi komunitas | Rilis bertahap (lihat Bagian 5.3) |
| Dana operasional strategis | 10% | 250 juta koin | Tim, audit, hukum, infrastruktur, investor strategis | Cliff 12 bulan + linear 36 bulan (lihat bagian 5.X) |

**Tolok Ukur Industri (tolak ukur kohort Tokenomics.net 2024-2025):** Penghargaan komunitas/pengguna 20-35% (LightDAO: 40% penambangan + 16% ekologi = 56%, lebih tinggi karena tidak ada putaran VC); perbendaharaan/cadangan 15-25% (LightDAO: 34%, karena fungsi investasi); tim/investor 15-45% (LightDAO: 10%, jauh lebih rendah dibandingkan industri, mempertahankan narasi "DAO Nasional").

### 5.3 Rencana Pencairan Dana Pembangunan Ekologis

| Tahap | Waktu | Proporsi | Kuantitas | Tujuan |
|------|------|------|------|------|
| TGE | Hari 0 | 30% | 120 juta keping | Likuiditas DEX (60%=72 juta) + seed airdrop (40%=48 juta) |
| Rilis linier periode 1 | bulan ke-1 hingga ke-12 | 40% | 160 juta koin | 13,33 juta koin per bulan: insentif komunitas, pemasaran, rencana airdrop |
| Rilis linier periode 2 | 13 hingga 24 | 30% | 120 juta koin | 10 juta koin per bulan: pendanaan pengembang, konstruksi ekologi, cadangan |

### 5.4 Dana Operasi Strategis (250 juta koin)

| Subkategori | Proporsi | Kuantitas | Objek | Aturan Rilis |
|--------|------|------|------|---------|
| Layanan pertukaran token | 50% | 125 juta koin | Perusahaan pembangunan, lembaga audit, firma hukum, operator verifikator | Tebing 12 bulan + 36 bulan linier; 30-50% biaya layanan dibayarkan dalam LIGHT |
| Pembiayaan strategis | 30% | 75 juta keping | 2-3 Dana ekologi DePIN/Cosmos atau pihak strategis industri konsumen | Pra-TGE dijual seharga $0,03-$0,05 (mengumpulkan $2,25-3,75 juta); Tebing 12 bulan + 24 bulan linier; investor tunggal ≤ 2% dari total |
| Kontributor inti | 20% | 50 juta koin | 3-5 sponsor/pembangun inti | Tebing 12 bulan + 36 bulan linier; dirilis berdasarkan penilaian pencapaian triwulanan; tidak ada penjualan selama jangka waktu |

**Persyaratan investor strategis:** Kontribusi non-finansial (salah satu alur kesepakatan, layanan verifikasi, sumber daya kepatuhan) harus disediakan, dan investor finansial murni tidak diterima.

**Kepatuhan terhadap Peraturan:** Penjualan pra-TGE mengadopsi pengecualian jalur ganda Reg S (investor non-AS) + Reg D Rule 506(c) (investor yang memenuhi syarat AS).

**Peraturan pengungkapan kontributor inti:** Hanya jumlah total (50 juta = 2% dari jumlah total) dan aturan pelepasan yang diungkapkan, dan nama pribadi serta kuota individu tidak diungkapkan. Kategori peran yang diungkapkan: Teknologi/Investasi/Kepatuhan/Komunitas.

### 5.5 Hasil penambangan dan rencana separuhnya

**Derivasi:** 2A = 1 miliar → A = 500 juta (Era Pertama). Pelepasan harian = 500 juta 730 = 684.932 lembar ≈ 684.900/hari. Setiap blok = 684,932 49,371 ≈ 13,87 CAHAYA.

**Catatan:** Kumpulan hadiah untuk setiap blok dibagikan oleh seluruh jaringan, yang mana 5% dialokasikan untuk validator (34.200/hari) dan 95% dialokasikan untuk penambang light node (650.700/hari).

| Zaman | Waktu | Jumlah keluaran | Rilis harian | Kumpulan hadiah per blok |
|------|------|---------|---------|------------|
| Era ke-1 | 0-24 bulan | 500 juta | ≈684.900 | ≈13,87 CAHAYA |
| Era ke-2 | 25-48 bulan | 250 juta keping | ≈342.500 | ≈6.93 CAHAYA |
| Era ke-3 | 49-72 bulan | 125 juta keping | ≈171.200 | ≈3.47 CAHAYA |
| Era ke-4 | 73-96 bulan | 62,5 juta keping | ≈85.600 | ≈1,73 CAHAYA |
| Era ke-5 | 97-120 bulan | 31,25 juta keping | ≈42.800 | ≈0,87 CAHAYA |

**Cek:** 5+2,5+1,25+0,625+0,3125+… = 5×2 = 1 miliar ✓. 97% selesai dalam 10 tahun pertama.

### 5.6 Model referensi pendapatan pengguna

| Ukuran jaringan | Pendapatan harian per kapita | Pendapatan bulanan | Pendapatan tahunan | Markup penuh (1,44x) pendapatan bulanan |
|---------|-----------|--------|--------|-------------------|
| 10.000 penambang (tahap benih) | ≈65.07 | ≈1.952 | ≈23.751 | ≈2.811 |
| 100.000 penambang (tahap pertumbuhan) | ≈6.51 | ≈195.2 | ≈2,375 | ≈281.1 |
| 1 juta penambang (periode skala) | ≈0,65 | ≈19.5 | ≈237,5 | ≈28.1 |

**Tingkat mitra (50 undangan, 20% pembagian, bonus penuh):**

| Skala jaringan | Mandiri (termasuk bonus) | Bagikan undangan | Komprehensif harian | Komprehensif bulanan |
|---------|------------|---------|--------|--------|
| 10.000 penambang | ≈93,7 | ≈650,7 | ≈744.4 | ≈22.332 |
| 100.000 penambang | ≈9.37 | ≈65.07 | ≈74,44 | ≈2,233 |
| 1 juta penambang | ≈0,94 | ≈6.51 | ≈7.45 | ≈223,4 |

### 5.7 Rencana Pertumbuhan Airdrop

**Model ekonomi:** Total anggaran airdrop = target yang dicapai pengguna × airdrop per kapita × (1+tingkat limbah) = 100.000 × 150 CAHAYA × 1,3 ≈ 19,5 juta (jenis akuisisi) + 35,5 juta (jenis ekologi) = **55 juta** (terhitung 13,75% dari dana ekologi sebesar 400 juta).

| Jenis tetesan udara | Kondisi pemicu | Kuota tunggal | Anggaran |
|---------|---------|---------|------|
| Airdrop Penambangan Pertama | Menyelesaikan 4 jam penambangan efektif untuk pertama kalinya | 50 CAHAYA | 15 juta keping |
| Perluasan geografis | Target pasar pengguna ZK-KYC lengkap | 100 CAHAYA | 10 juta keping |
| Belajar untuk Menghasilkan | Modul Pendidikan Lengkap + Kuis | 30 CAHAYA | 6 Juta Koin |
| Pemungutan Suara Pemerintahan Pertama | Partisipasi Pertama dalam Voting | 20 CAHAYA | 3 juta koin |
| Penyediaan likuiditas | Injeksi LP ≥$50 penguncian selama 30 hari | 200 CAHAYA | 10 juta keping |
| Pembuatan konten | Tutorial/terjemahan yang diverifikasi komunitas | 50-200 CAHAYA | 6 juta keping |
| Saluran kerjasama | Pendaftaran + penambangan pertama melalui mitra | 80 CAHAYA | 5 juta keping |

**Verifikasi CAC:** 55 juta koin × $0,03 = $1,65 juta 30.000 penambang aktif yang dipertahankan = **$55/orang** (kisaran industri $50-200, pada kisaran harga paling rendah). Dasar akademis: Zheng (2023) "Operasi Dumbo Drop: Melakukan Airdrop atau Tidak untuk Melakukan Airdrop agar Penawaran Koin Awal Sukses?" membuktikan bahwa tingkat retensi airdrop yang terikat peristiwa adalah 3-5 kali lipat dari airdrop murni.

**Anti-penyalahgunaan:** Sidik jari browser unik + ZK-KYC; terbatas pada 1 klaim per kategori per alamat; periode penguncian 30 hari; daur ulang otomatis tanpa aktivitas on-chain dalam waktu 30 hari setelah klaim.

### 5.8 Roda Gila Mesin Ganda dan Kumpulan Modal

Roda Gila: Voting → Penghancuran Vault LIGHT → Pembayaran USDC → Perubahan laba → Pembelian kembali dan penghancuran → Dukungan harga → Lebih banyak pengguna.

Sistem jalur ganda: perbendaharaan stabil (USDC, retensi laba) + perbendaharaan fleksibel (lapisan CAHAYA, hancur saat berinvestasi dan tidak mengalir ke pasar). Pembelian kembali dibagi menggunakan TWAP, dengan satu pesanan ≤ 5% dari rata-rata volume perdagangan harian.

### 5.9 Penerbitan dan perdagangan sub-token

Jumlah total penerbitan = jumlah investasi $1; harga pertukaran didasarkan pada VWAP 30 hari; semua CAHAYA yang diperoleh dari pertukaran akan dimusnahkan; 50% pendukung/30% airdrop/20% cadangan operasi akan didistribusikan (dikunci selama 6 bulan). Batas dividen untuk satu alamat adalah 15%. Sub-token diperdagangkan di AMM on-chain, dengan periode penguncian 30 hari setelah penerbitan, dan akan ditandai "dilikuidasi" setelah penarikan.

### 5.10 Likuiditas Awal dan Penemuan Harga

**Pengaturan TGE (Acara Pembuatan Token, acara pembuatan token): **

| Proyek | Rencana |
|------|------|
| Kumpulan likuiditas awal | Dari 120 juta keping yang dikeluarkan oleh dana pengembangan ekologi TGE, 72 juta keping (60%) dialokasikan dan disuntikkan ke dalam kumpulan likuiditas DEX |
| Aset berpasangan | USDC (kumpulan utama), USDT (kumpulan tambahan) |
| Tetesan Udara | Sisanya 48 juta (40%) akan digunakan untuk airdrop kepada pengguna seed (lihat Bagian 5.7 Rencana Airdrop) |
| Terdaftar di bursa | Pertama kali terdaftar di bursa terdesentralisasi (seperti Osmosis, JunoSwap) setelah TGE; mengajukan permohonan pencatatan di bursa terpusat mulai dari bulan ke-6 tergantung pada ketentuan kepatuhan |

**Detail mekanisme Lelang Belanda:**

Lelang Belanda adalah metode penetapan harga di mana harga diturunkan dari tinggi ke rendah. Berbeda dengan lelang Inggris (di mana harga ditawar dari rendah ke tinggi), dalam lelang Belanda penjual menetapkan harga awal yang tinggi dan harga secara otomatis menurun seiring waktu hingga pembeli mengajukan langganan pada titik harga tertentu. Harga pertama di mana jumlah total berlangganan mencapai target adalah harga pembukaan akhir.

**Mengapa memilih lelang Belanda dibandingkan harga tetap atau lelang Inggris:**

| Harga | Keuntungan | Kekurangan | Penerapan |
|---------|------|------|--------|
| Pra-penjualan harga tetap | Sederhana | Penetapan harga itu subjektif, kalau terlalu tinggi tidak laku, kalau terlalu rendah akan diambil robot | Tidak cocok (tidak ada fungsi penemuan harga) |
| Lelang Inggris (penawaran) | Penemuan harga penuh | Pembeli besar dapat menunggu secara strategis dan menaikkan harga; perang gas | Tidak cocok (perang gas on-chain tidak termasuk pengguna kecil) |
| **Lelang Belanda** | **Penemuan harga otomatis; tidak diperlukan penawaran (tidak ada perang gas); partisipasi yang setara antara pembeli besar dan kecil; anti-bot (mekanisme penurunan harga secara alami menghambat front-running)** | Harga awal dan tingkat perlambatan perlu ditetapkan secara wajar | **Paling cocok (adil + efisien + anti manipulasi)** |

**Parameter khusus lelang LightDAO Belanda:**

| Parameter | Pengaturan | Deskripsi |
|------|------|------|
| Target lelang | Token LIGHT (dialokasikan dari 72 juta yang dikeluarkan oleh dana ekologi TGE) | USDC dari lelang akan disuntikkan ke brankas stabil |
| Target jumlah penggalangan dana | **$15 juta USDC** | $5 juta → cadangan minimum perbendaharaan stabil; $10 juta → modal investasi awal |
| Harga awal | $0,20/CAHAYA | Lebih tinggi dari harga keseimbangan yang diharapkan, memastikan tidak hilang dalam hitungan detik |
| Tingkat perlambatan | Turun 5% setiap jam | Mulai dari $0,20, turun menjadi $0,017 setelah sekitar 48 jam (jika tidak ada yang berlangganan) |
| Harga cadangan minimum | $0,01/CAHAYA | Jika harga cadangan diturunkan dan target masih belum tercapai, maka lelang ditunda 24 jam atau jumlah barang disesuaikan |
| Metode berlangganan | Pengguna mengirimkan "Saya bersedia membeli CAHAYA setara X USDC dengan harga saat ini" | Tidak diperlukan penawaran, sistem akan menyelesaikan sesuai dengan harga akhir yang terpadu (kelebihan akan dikembalikan tanpa kompensasi) |
| Batas atas pengguna tunggal | Tidak lebih dari 5% dari jumlah target penggalangan dana (yaitu $750.000) | Mencegah satu pembeli memonopoli chip awal |
| Persyaratan KYC | Verifikasi yang Ditingkatkan (Domisili Pajak) | Persyaratan Kepatuhan |

**Tujuan dana dari hasil lelang:**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**Periode perlindungan penemuan harga:** Pemutus sirkuit fluktuasi harga disiapkan dalam 72 jam pertama setelah TGE - jika harga transaksi DEX menyimpang lebih dari ±50% dari harga pembukaan lelang, fungsi pertukaran sub-token akan ditangguhkan (penambangan dan transfer tidak akan terpengaruh) untuk mencegah spekulasi ekstrem mengganggu startup ekologis. Sekring akan terlepas secara otomatis setelah 72 jam.

**Mengapa $15 juta bukannya lebih rendah:** Modal investasi awal sebesar $10 juta perlu mendukung 3-5 investasi pada tahun pertama (satu investasi bernilai $2-5 juta, lihat skala periode permulaan di Bagian 9.1). Jika hanya $5 juta yang dikumpulkan (semuanya sebagai cadangan), tidak akan ada modal investasi yang dapat digunakan pada tahun pertama dan roda gila tidak akan dimulai. $15 juta = cadangan $5 juta + investasi $10 juta, yang merupakan keseimbangan minimum yang layak antara "safety bottom line" dan "flywheel start".

### 5.11 Mekanisme deflasi dan laba

**Volume sirkulasi = pelepasan penambangan + pelepasan ekologi + pelepasan dana strategis − pertukaran dan pemusnahan − pemusnahan gas − pembelian kembali dan pemusnahan. **850 juta koin dari brankas investasi tidak pernah beredar. Batas atas peredaran teoritis = 10+4+2,5 = **1,65 miliar**.

| Kondisi pemicu | Perilaku sistem |
|---------|---------|
| Peredaran ≤ 1,5 miliar keping | Sinyal perlambatan (skenario kehancuran yang sangat rendah) |
| Volume peredaran ≤ 1,2 miliar keping | Pengumuman peringatan dini, penghentian penghancuran aktif (sekitar tahun ke-8 dari skenario dasar) |
| Volume peredaran ≤ 1 miliar | Berhenti keras, semua kehancuran ditutup secara permanen (skenario dasar adalah sekitar tahun 11-12) |

### 5.12 Mekanisme stabilisasi harga (spiral anti kematian)

**Prinsip Inti:** LightDAO tidak mengganggu penemuan harga pasar harian. Protokol hanya menyesuaikan parameternya dalam skenario penurunan ekstrem untuk mengurangi risiko jatuh ke dalam "spiral kematian".

**Logika penilaian:** Di lingkungan yang mudah berubah, penurunan yang sama menunjukkan tingkat kelainan yang berbeda. Penurunan tajam di pasar dengan volatilitas rendah merupakan sinyal abnormal yang lebih kuat dan memerlukan intervensi dengan intensitas lebih tinggi; penurunan tajam di pasar dengan volatilitas tinggi relatif umum terjadi dan intervensi yang lebih ringan dapat digunakan. Oleh karena itu, intensitas intervensi berhubungan positif dengan kelainan sinyal, bukan hanya bergantung pada nilai absolut penurunan.

**Bagan alur lengkap mekanismenya:**

| Status pasar | Volatilitas historis 30 hari | Kondisi pemicu | Tingkat sinyal | Eksekusi setelah pemicu | Kondisi pemulihan |
|---------|--------------|---------|---------|----------|---------|
| Volatilitas rendah | ≤30% | Penurunan kumulatif ≥40% selama 5 hari berturut-turut | Tingkat I | Output pertambangan turun hingga 50%; rasio kehancuran meningkat dari 20% menjadi 35%; periode publisitas penyesuaian parameter risiko dipersingkat dari 72 jam menjadi 12 jam; panitia bayangan memasuki keadaan aktif (hanya hak pemberhentian sementara yang dapat dilaksanakan sesuai dengan peraturan perundang-undangan) | Harga berada di atas rata-rata pergerakan 30 hari, dan memantul ≥80% dari harga pemicu, dan tetap demikian selama 10 hari berturut-turut |
| Fluktuasi sedang | 30%-60% | Penurunan kumulatif selama 7 hari berturut-turut ≥ 50% | Tingkat II | Output pertambangan turun hingga 50%; rasio kehancuran meningkat dari 20% menjadi 30%; periode publisitas dipersingkat menjadi 24 jam; komite bayangan memasuki keadaan aktif | Harga berada di atas rata-rata pergerakan 30 hari, dan memantul ≥ 60% dari harga pemicu, dan tetap demikian selama 7 hari berturut-turut |
| Volatilitas tinggi | 60%-100% | Penurunan kumulatif 10 hari berturut-turut ≥55% | Tingkat III | Output pertambangan turun menjadi 75%; rasio kehancuran meningkat dari 20% menjadi 25%; periode publisitas dipersingkat menjadi 48 jam; panitia bayangan masuk standby | Harga berada di atas rata-rata pergerakan 30 hari, dan memantul ≥40% dari harga pemicu, dan tetap demikian selama 5 hari berturut-turut |
| Volatilitas ekstrim | >100% | Penurunan kumulatif selama 10 hari berturut-turut ≥ 65% | Tingkat III | Diimplementasikan sesuai dengan langkah-langkah Level III untuk volatilitas tinggi | Diimplementasikan sesuai kondisi pemulihan Level III untuk volatilitas tinggi |

**Kondisi pengecualian:** Hanya ketika penurunan Bitcoin pada periode yang sama kurang dari 50% penurunan LIGHT, mekanisme di atas dapat dipicu untuk mengesampingkan keruntuhan pasar sistemik (yaitu jika BTC juga anjlok pada periode yang sama, ini adalah peristiwa pasar secara keseluruhan, dan tidak ada intervensi terpisah yang dimulai untuk LIGHT).

**Deskripsi logika pemulihan:** Persyaratan dan durasi pantulan menurun seiring dengan tingkat kelainan: Tingkat I memerlukan amplitudo pantulan tertinggi (80%) dan waktu konfirmasi terlama (10 hari), sedangkan Tingkat III memerlukan persyaratan yang relatif lebih rendah (40%/5 hari). Pengaturan ini sejalan dengan logika progresif “semakin kuat sinyal abnormal, semakin kuat intervensi, dan semakin ketat konfirmasi pemulihan”.

**Sumber data volatilitas dan harga:** Riwayat volatilitas dan penurunan kumulatif selama 30 hari disediakan oleh ramalan harga on-chain (lihat Bagian 4.10), berdasarkan cuplikan TWAP dari blok harian UTC 00:00, dan tidak bergantung pada sumber data eksternal apa pun.

### 5.13 Uji Stres Keberlanjutan Pendapatan

| Skenario stres | Bagaimana-jika | Tanggapan protokol | Hasil terburuk |
|---------|---------|---------|---------|
| Semua investasi gagal | Semua perusahaan yang diinvestasikan mengalami kerugian atau gagal keluar | Dana asuransi (10% dari keuntungan yang diperoleh) menanggung sebagian kerugian; cadangan perbendaharaan yang stabil (≥$8 juta) untuk mempertahankan operasi; investasi baru ditangguhkan sampai masyarakat mengevaluasi kembali | Pemegang sub-token tidak dapat menerima dividen; Harga RINGAN tertekan namun belum kembali ke nol (fungsi pertambangan dan tata kelola tetap berjalan) |
| Pasar anjlok 80% | Harga RINGAN anjlok 80% dari puncaknya | Memicu mekanisme spiral anti kematian (level II atau level III); hasil penambangan berkurang 50-75%; rasio kehancuran meningkat; komite bayangan dapat menghentikan operasi berisiko tinggi | Pendapatan pengguna menyusut namun jaringan terus beroperasi; mekanisme otomatis terangkat ketika kondisi pemulihan terpenuhi |
| Larangan peraturan pasar utama | Sebuah negara besar telah sepenuhnya melarang aset kripto | Cermin IPFS peralihan front-end tetap dapat diakses; aset on-chain serta hak dan kepentingan pengguna yang ada tidak terpengaruh; ketersediaan layanan pihak ketiga hanya disesuaikan dalam lingkup penegakan hukum; Operasi SPV di Kepulauan Cayman tidak tunduk pada yurisdiksi satu negara | Pertumbuhan pengguna di kawasan ini mengalami stagnasi; wilayah lain di seluruh dunia tidak terpengaruh |
| Hilangnya pengguna dalam skala besar | Penambang aktif turun lebih dari 70% | BaseReward didistribusikan ulang secara otomatis (penyebut menyusut → pendapatan per kapita pengguna tetap meningkat); insentif undangan ditimbang untuk menarik arus pengembalian; ambang batas tata kelola diturunkan untuk sementara (mekanisme dinamis di Bagian 5.14) | Keamanan jaringan berkurang namun rantai tidak akan dihentikan (Tendermint BFT mentolerir <1/3 validator sedang offline) |
| Kerentanan kontrak pintar utama | Kerentanan yang dapat dieksploitasi ditemukan dalam kontrak inti | Penangguhan darurat multi-tanda tangan atas arus keluar dana (penguncian waktu 72 jam memberikan jendela respons); Memulai pemungutan suara migrasi kontrak cadangan (perbaikan darurat tingkat L4, lihat Bagian 4.12); Dana asuransi menanggung kerugian pengguna | Beberapa dana mungkin rusak; Operasi normal dilanjutkan setelah migrasi selesai |

### 5.14 Mekanisme keseimbangan antargenerasi

Penyesuaian dinamis ambang batas tata kelola: untuk setiap 1 juta penambang aktif kumulatif baru, ambang batas proposal secara otomatis diturunkan sebesar 5% (batas bawah 2,500 LIGHT).

> **[Terminologi dalam bab ini]**
> **TGE** (Acara Pembuatan Token): Titik ketika token pertama kali dibuat dan didistribusikan melalui kontrak pintar, biasanya disertai dengan pembentukan kumpulan likuiditas awal, penetapan harga lelang Belanda, dan transaksi publik pertama. Mirip dengan IPO di bidang keuangan tradisional, tetapi tidak melibatkan pencatatan di bursa saham.
> **Halving** (Halving): Mekanisme yang mengurangi hasil penambangan secara otomatis sebesar 50% setiap periode tetap (2 tahun/730 hari untuk LightDAO). Tujuannya adalah untuk menciptakan kelangkaan yang progresif - seiring berjalannya waktu, pasokan baru semakin sedikit, dan jika permintaan tidak menurun, harga akan terdukung. Bitcoin mengadopsi halving setiap 4 tahun.
> **Perbendaharaan** (Perbendaharaan): Cadangan token dikunci oleh kontrak multi-tanda tangan, yang hanya dapat dilepaskan melalui resolusi tata kelola. LightDAO memiliki dua jenis brankas: brankas investasi (yang menampung LIGHT dan dimusnahkan saat investasi dieksekusi) dan brankas stabil (yang menampung USDC dan digunakan untuk membayar pertimbangan investasi dan biaya operasional).
> **Deflasi** (Deflasi): Proses di mana total pasokan atau peredaran token terus berkurang. LightDAO mencapai deflasi melalui empat mekanisme: eksekusi dan penghancuran investasi, pertukaran dan penghancuran sub-token, penghancuran biaya gas (50%), dan pembelian kembali dan penghancuran keuntungan.
> **Death Spiral** (Death Spiral): Harga token turun → pendapatan penambang menyusut → penambang berhenti → keamanan/kontribusi jaringan menurun → hilangnya kepercayaan lebih lanjut → lingkaran setan di mana harga terus turun. Mekanisme intervensi bertahap di Bagian 5.12 dirancang untuk memutus siklus ini.
> **Sub-token** (Sub-token): Sertifikat klaim distribusi pendapatan SPV diterbitkan sesuai dengan aturan setelah setiap investasi perusahaan selesai (seperti akuisisi merek kopi → token CAFE). Memegang sub-token = memegang kualifikasi untuk pembagian keuntungan di masa depan dan tidak mewakili hak pemegang saham atau hak tata kelola perusahaan.
> **LP** (Penyedia Likuiditas): Peserta yang memasukkan dua aset dengan nilai yang sama (seperti LIGHT+USDC) ke dalam kumpulan likuiditas DEX mendapatkan biaya transaksi sebagai imbalannya. LP adalah dasar untuk pengoperasian normal DEX.
> **VWAP** (Harga Rata-Rata Tertimbang Volume): Harga dalam jangka waktu tertentu ditimbang berdasarkan volume setiap transaksi, yang mencerminkan biaya transaksi pasar sebenarnya. LightDAO menggunakan VWAP 30 hari sebagai patokan harga untuk pertukaran sub-token.
> **CAC** (Biaya Akuisisi Pelanggan, biaya akuisisi pengguna): Biaya rata-rata untuk memperoleh pengguna aktif yang efektif. Target CAC program airdrop LightDAO adalah $55/penambang aktif yang dipertahankan (kisaran industri $50-200).
> **wLIGHT** (Wrapped LIGHT, encapsulated LIGHT): Token setara LIGHT yang diterbitkan di Ethereum atau Solana melalui jembatan lintas rantai, dan LIGHT asli dalam jumlah yang sama dikunci oleh kontrak jembatan sebagai cadangan 1:1. Tujuannya adalah untuk memungkinkan pengguna ekosistem non-Cosmos memperoleh dan menyimpan CAHAYA.
> **Lelang Belanda** (Lelang Belanda): Metode penetapan harga di mana harga diturunkan dari harga tertinggi ke harga terendah. Penjual menetapkan harga awal yang tinggi, dan harga secara otomatis menurun seiring waktu hingga pembeli mengajukan langganan pada titik harga tertentu. Harga pertama saat jumlah total langganan mencapai target adalah harga transaksi akhir. Keuntungannya adalah tidak diperlukan penawaran (tidak ada perang gas), pembeli dari semua ukuran setara, dan secara alami tahan terhadap preemption robot.

---

## Bab 6: Mekanisme Tata Kelola

### 6.1 Model pemungutan suara dua dimensi

Bobot kepemilikan mata uang (termasuk reputasi + bonus level, total batas atas +40%) + jumlah alamat (1 alamat = 1 suara, alamat terkait digabungkan). Hak suara berlaku selama 90 hari dan dapat diaktifkan dengan mentransfer 5 LAMPU. Bonus reputasi: Memegang mata uang selama 1 tahun + 15 suara sah → hingga +30%.

### 6.2 Tingkat kelulusan dinamis

Tingkat kelulusan minimum = 50% + (50% - tingkat pemungutan suara aktual). Mayoritas sederhana ketika tingkat suara ≥50%.

### 6.3 Parameter proposal

| Ketik | Margin | Tingkat pemungutan suara token | Alamat tingkat pemungutan suara | Tingkat kelulusan | Penundaan eksekusi |
|------|--------|-----------|-----------|--------|---------|
| Mikro | $100 | ≥15% | ≥20% | Dinamis ≥55% | 24 jam |
| Jenis akuisisi | $500 | ≥25% | ≥30% | Dinamis ≥60% | 72 jam |
| Jenis modal ventura | $500 | ≥35% | ≥40% | Dinamis ≥60% | 72 jam |
| Mayor | $1.000 | ≥45% | ≥50% | Dinamis ≥66% | 72 jam |
| Darurat | $2.000 | ≥50% | ≥60% | ≥75% | Non-pendanaan 6 jam/risiko tinggi 1 jam; operasi modal masih tunduk pada kunci waktu 72 jam |

### 6.4 Siklus hidup proposal

Kualifikasi pengiriman: ≥5.000 LIGHT + janji + deposit selama 30 hari berturut-turut. Pengumuman publik 72 jam (direvisi ≤ 2 kali). Pemungutan suara dilakukan dalam waktu 7 hari (48 jam untuk jalur cepat, ≤500.000 USDC). Veto pendinginan selama 90 hari. Efektivitasnya tertunda selama 24 jam.

**Deskripsi ambang batas:** 5.000 koin dalam tahap awal (10.000 penambang) ≈ 77 hari hasil dasar; tingkat mitra ≈ 7 hari. Tata kelola akan diaktifkan pada bulan ketujuh, dan pengguna awal akan memiliki waktu akumulasi yang cukup.

### 6.5 Insentif pemungutan suara

Ada insentif dasar untuk partisipasi (bahkan berbagi), dan ada bonus tambahan untuk penilaian yang benar (50% dari kumpulan taruhan). Bertaruh pada kisaran 5-500 CAHAYA. Menekan efek penggembalaan: Lawan tetap menerima insentif dasar meskipun mereka “berada di tim yang salah”.

### 6.6 Hadiah dan penalti atas keberhasilan atau kegagalan

Kegagalan dengan itikad baik: pengembalian deposit 50% + cooldown 30 hari. Kegagalan berbahaya (pemalsuan/pengulangan): jumlah penuh disita + larangan permanen. Bukti penipuan: dibatasi hingga 5.000 LIGHT, penalti 40% dari bonus pendirian + 500 LIGHT.

### 6.7 Transparansi Keuangan

Dasbor real-time pada rantai + laporan keuangan triwulanan + audit independen tahunan (audit pertama harus diselesaikan sebelum TGE) + pengungkapan target investasi secara real-time.

---

## Bab 7: Pemeriksaan dan keseimbangan kekuasaan dan definisi peran

### 7.1 Wali Awal

Izin terbatas pada dokumen/format/informasi situs resmi. Jangka waktu ≤ 24 bulan. Wali alternatif harus ditunjuk (tidak dapat menandatangani selama 30 hari berturut-turut → diambil alih secara otomatis). Cacat serentak → pemungutan suara darurat selama 48 jam untuk menunjuk manajer sementara.

### 7.2 Peta Jalan Transfer Daya

| Tahap | Waktu | Izin | Persetujuan Investasi |
|------|------|------|---------|
| Periode penciptaan | 0-6 bulan | Wali (non-keuangan) | Wali + komunitas multi-tanda tangan 3/5 |
| Masa transisi | Juli-Desember | Wali + kontributor inti menandatangani bersama | Sama seperti di atas + kontributor inti |
| Masa jatuh tempo | 13-24 bulan | Komite Tata Kelola 3/5 | Pemungutan suara dua dimensi reguler |
| Masa otonomi | 25 bulan + | Semua pemegang | Jangka waktu yang sama |

### 7.3 Komite Tata Kelola

Kekuasaan dibagi di antara lima orang (ketua bergilir/keuangan/teknologi/komunitas/kunci), rotasi triwulanan, dan masa jabatan enam bulan dan dapat dipilih kembali satu kali. Kampanye ini menjanjikan 50.000 LIGHT + 100 alamat tanda tangan bersama. Pengambilan keputusan melibatkan ≥3 orang dan mencakup ≥3 posisi.

**Deskripsi ambang batas:** 50.000 koin dalam tahap awal ≈ 67 hari (2,2 bulan) untuk mitra; dalam tahap pertumbuhan ≈ 672 hari (22 bulan). Pemilihan komite pertama di bulan ke-13 tersedia untuk mitra awal.

### 7.4 Komite Bayangan

Penangguhan sementara hanya untuk "pelanggaran/sanksi/penipuan besar". Semua suara harus disahkan dalam waktu 72 jam (oposisi >60%→dibubarkan). Ditolak dua kali berturut-turut → otomatis dimakzulkan dan dibubarkan.

### 7.5—7.6 Verifikasi kampanye dan rencana utama

SimHash>80% diskualifikasi; Konten AI harus dilengkapi dengan penjelasan; 20% suara akan dikurangi untuk pertanyaan yang tidak hadir. Pencadangan pecahan kunci + pemeriksaan kesehatan triwulanan + pengumuman publik 7 hari + penggantian pemungutan suara.

---

## Bab 8: Mekanisme Kepercayaan dan Keamanan

### 8.1 Lima mekanisme keamanan utama

Penguncian waktu 72 jam (usulan darurat tidak dikecualikan dari operasi modal); multi-penandatanganan 3/5; rotasi triwulanan ≤ 2 sesi; Denda 100% untuk penipuan; semua transaksi ada dalam rantai.

### 8.2 Dana Asuransi

**10%** keuntungan investasi yang berhasil diperoleh. Klaim harus dilaporkan secara independen + DAO 66% mendukung + tunggal ≤ kumpulan 20%. Sumber tambahan: 30% denda karena pemalsuan. Memposisikan "buffer parsial" bukanlah perlindungan penuh.

### 8.3 Rencana ekstrem

Pengawasan angsa hitam → IPFS + penghapusan hak administrator; penipuan → penangguhan komite bayangan (ratifikasi 72 jam) + dana asuransi + arbitrase SPV; spiral kematian → Mekanisme Bagian 5.12; kerentanan kontrak → penangguhan multi-tanda tangan + pemungutan suara migrasi; validator secara kolektif melakukan kejahatan → Toleransi BFT <1/3, jika terlampaui, rantai akan ditangguhkan + migrasi pemungutan suara darurat.

---

## Bab 9: Operasi Investasi dan Strategi Keluar

### 9.1 Penapisan dan skala target investasi

**Lintasan pertumbuhan skala investasi bertahap (rumus: surplus Treasury × 15% × Harga RINGAN): **

| Tahap | Harga RINGAN | Batas transaksi tunggal pada periode awal vault | Target adaptasi | Pembandingan industri |
|------|----------|------------------|----------|----------|
| Periode permulaan (Y1-2) | $0,02—$0,05 | $2,55 juta—$6,37 juta | Toko tunggal/rantai kecil, bulat malaikat | Mikro PE |
| Tahap Pertumbuhan (Y3-5) | $0,05—$0,30 | $6,37 juta—$38,25 juta | Jaringan regional 30-200 toko, putaran Seed-A | PE Pasar Menengah Bawah |
| Tahap kedewasaan (Y5-8) | $0,30—$1,00 | $38,25 juta—$127,5 juta | Rantai multinasional/teknologi menengah, putaran B-C | PE Pasar Menengah |
| Periode skala (Y8+) | $1,00+ | $127,5 juta+ | Akuisisi skala besar, Pra-IPO | PE Skala Besar/VC Tahap Pertumbuhan |

### 9.2 Proses pengambilan keputusan investasi

Penemuan proyek (≥5.000 LIGHT) → uji tuntas independen → pengumuman publik 72 jam → pemungutan suara dua dimensi → eksekusi 24/72 jam.

### 9.3 Keluar dan distribusi keuntungan

Dividen tahunan: **40%** pemegang sub-token / **30%** brankas stabil / **20%** pembelian kembali CAHAYA untuk kehancuran / **10%** dana asuransi.
Pendapatan keluar: **70%** Stable Vault / **30%** Pembelian Kembali dan Pembakaran.

### 9.4 Disiplin Investasi

| Aturan | Konten |
|------|------|
| Batas kehancuran tunggal | Sisa Vault × 15% (awal 850 juta × 15% = 127,5 juta koin) |
| Sasaran tunggal | ≤25% dari total nilai brankas |
| Konsentrasi industri | ≤40% portofolio |
| Konsentrasi geografis | ≤30% portofolio |
| Cadangan Treasury yang stabil | $5 juta di TGE (lelang), mencapai $8 juta pada bulan ke-24 |
| Periode pendinginan | 2 kegagalan berturut-turut → 180 hari |

**Kapasitas penyimpanan:** 850 juta keping × $0,10 = $85 juta (kapasitas total awal); × $0,30 = $255 juta; × $1,00 = $850 juta. Batasan transaksi tunggal sebesar 15% membuat kecepatan investasi berhubungan positif dengan harga.

> **[Terminologi dalam bab ini]**
> **EBITDA** (Pendapatan Sebelum Bunga, Pajak, Depresiasi dan Amortisasi): Indikator yang mengukur profitabilitas operasi inti perusahaan, menghilangkan campur tangan struktur keuangan (bunga), kebijakan perpajakan (pajak), dan pilihan akuntansi (depresiasi/amortisasi), memfasilitasi perbandingan lintas perusahaan dan lintas industri. Margin EBITDA = EBITDA pendapatan operasional.
> **DCF** (Discounted Cash Flow, metode arus kas yang didiskontokan): Metode penilaian yang mengubah perkiraan arus kas masa depan perusahaan menjadi nilai saat ini pada tingkat diskonto tertentu. Cocok untuk perusahaan matang dengan arus kas stabil (seperti rantai konsumen), namun tidak cocok untuk perusahaan teknologi tahap awal yang belum menghasilkan keuntungan.
> **IPO** (Initial Public Offering): Pertama kali suatu perusahaan menerbitkan saham secara publik di bursa efek dan dicatatkan untuk diperdagangkan. Bagi LightDAO, IPO perusahaan yang berinvestasi adalah salah satu jalan keluar utama bagi mesin pertumbuhan.
> **Pra-IPO**: Putaran terakhir pembiayaan ekuitas swasta sebelum perusahaan resmi tercatat di bursa. Biasanya valuasinya mendekati tingkat pasca-IPO, risikonya lebih rendah dibandingkan putaran sebelumnya tetapi kelipatan keuntungannya juga lebih rendah.
> **Eksekusi TWAP** (Eksekusi Harga Rata-Rata Tertimbang Waktu): Bagi pesanan pembelian kembali dalam jumlah besar menjadi beberapa pesanan dalam jumlah kecil dan jalankan secara merata selama periode waktu tertentu untuk menghindari dampak satu pesanan besar pada harga pasar. LightDAO menetapkan bahwa pembelian kembali tunggal tidak boleh melebihi 5% dari rata-rata volume perdagangan harian.

---

## Bab 10: Peta Jalan

| Fase | Waktu | Tujuan Inti | Tonggak Penting | Prasyarat |
|------|------|---------|-----------|---------|
| Masa persiapan | Q4 2026 | Badan hukum + tim + dana tersedia | Pendaftaran entitas Cayman/BVI selesai; mitra teknis atau tim pengembangan ditandatangani; niat investor strategis terkonfirmasi (2-3 perusahaan); modal awal ≥ $150,000 di tempat | pendiri menentukan metode pengungkapan identitas; penyelesaian BP dan Pitch Deck |
| Masa Perkembangan | Q1-Q2 2027 | Pengembangan sistem inti | 10 modul kontrak pintar telah dikembangkan; Pengembangan front-end PWA telah selesai; 7 testnet verifikator telah dikerahkan; pengujian Alpha internal telah lulus | Tim pengembangan sudah ada; dokumen persyaratan (Spesifikasi teknis) diselesaikan |
| Periode audit dan pengujian | Q3 2027 | Verifikasi keamanan dan kepatuhan | Penerbitan laporan audit keamanan independen (≥1 institusi teratas); penerbitan surat pendapat kepatuhan hukum (MLM + undang-undang sekuritas); 50.000 stress test bersamaan lulus; tingkat positif palsu sistem anti-kecurangan <2%; latihan pemungutan suara tata kelola selesai | Pembekuan pengembangan kontrak (Code Freeze); biaya audit di tempat |
| TGE dan mainnet online | Q4 2027 | Penerbitan token + peluncuran jaringan | Lelang Belanda selesai (target $15 juta); mainnet online (≥10 validator); platform penambangan terbuka untuk umum; Kumpulan likuiditas DEX terbentuk; benih airdrop dikeluarkan | Audit lulus; validator ≥7 (garis bawah); penerapan kontrak lelang |
| Periode pembangunan kepercayaan | Q1 2028 (bulan ke-1 hingga ke-3 setelah TGE) | 30.000-50.000 pengguna benih | Penambang aktif melebihi 30,000; pelaksanaan pemungutan suara tata kelola yang pertama; saluran komunitas multi-bahasa yang didirikan (Inggris/Mandarin/Spanyol/Portugis/Filipina); laporan komunitas bulanan pertama dirilis | TGE selesai; tim operasi komunitas ada |
| Nilai periode jangkar | Q2-Q3 tahun 2028 (bulan ke-4 hingga ke-9 setelah TGE) | Investasi pertama + pemerintahan masa transisi | Proposal investasi pertama yang lolos (persetujuan multi-tanda tangan selama periode awal berlaku pada bulan ke-4 hingga ke-6; persetujuan bersama selama masa transisi berlaku mulai bulan ke-7); pengiriman SPV pertama selesai; validator terbuka untuk pemilihan (mulai bulan ke-7); laporan keuangan triwulan pertama dirilis | perbendaharaan stabil USDC≥$5 juta; uji tuntas target investasi selesai |
| Masa jatuh tempo tata kelola | Q4-2029 Q1 2028 (bulan ke-10 hingga ke-15 setelah TGE) | Pemilihan komite + transisi desentralisasi | Pemilihan pertama komite tata kelola (bulan ke-13); Memasuki masa jatuh tempo (3/5 keputusan panitia); wLIGHT jembatan lintas rantai mulai online; Permohonan pencatatan CEX diajukan; Rencana pendanaan pengembang dimulai | Penambang aktif ≥ 100.000; ≥ 100 alamat calon gabungan |
| Periode ekspansi ekologi | Mulai Q2 tahun 2029 (bulan ke-16 + setelah TGE) | Replikasi skala besar | Penambang aktif melebihi 200,000-500,000; 2-3 investasi telah selesai; verifikasi repatriasi keuntungan pertama; Pembelian kembali dan penghancuran CAHAYA dimulai | Komite tata kelola beroperasi secara normal; model investasi telah diverifikasi |
| Masa operasi yang matang | Mulai Q4 tahun 2029 (bulan ke-25 + setelah TGE) | Rotasi roda gila + otonomi penuh | Memasuki masa otonomi (usulan utama dari seluruh pemegang); penyebaran portofolio investasi kumulatif ≥ $30 juta; data deflasi dapat diverifikasi secara publik | Tata Kelola sepenuhnya terdesentralisasi |

**Prinsip desain peta jalan:**

- **Audit sebelum TGE:** Token tidak akan pernah diterbitkan tanpa menyelesaikan audit keamanan independen. Ini adalah jaminan dasar keamanan dana pengguna.
- **Verifikator datang sebelum pengguna:** Saat mainnet online, akan ada ≥10 verifikator (toleransi kesalahan BFT f≥3), yang memastikan bahwa jaringan tidak akan mati karena satu titik kegagalan.
- **Investasi mendahului ekspansi:** Hanya setelah investasi pertama berhasil dan menghasilkan keuntungan yang dapat diverifikasi, barulah kita dapat memasuki ekspansi skala besar. Hindari menempatkan kereta di depan kuda dengan "mengedarkan orang terlebih dahulu dan mencari proyek kemudian".
- **Time Buffer:** Cadangan 20-30% time buffer untuk setiap tahapan. Perkembangan teknologi, perbaikan audit, dan proses hukum mungkin melebihi ekspektasi, dan peta jalan tersebut tidak boleh menjadi “skenario paling optimis”.

**Hubungan dengan Tanggal Peluncuran Buku Putih (4 Agustus 2026):** Buku Putih dirilis pada Agustus 2026 sebagai pernyataan publik mengenai visi dan desain teknis proyek. Implementasi sebenarnya akan dimulai pada Q4 tahun 2026 (masa persiapan), dan target TGE adalah Q4 tahun 2027. Jeda sekitar 14 bulan antara penerbitan buku putih dan TGE digunakan untuk pembentukan tim, pengembangan, audit, dan persiapan kepatuhan.

---

## Bab 11: Budaya Komunitas dan Ekologi Pengembang

### 11.1 Empat Nilai

- **Transparansi lebih baik daripada kesempurnaan** - Lebih baik mengungkapkan ketidaksempurnaan daripada menyembunyikan kesempurnaan. Semua aliran perbendaharaan, keputusan investasi, dan suara tata kelola tersedia secara permanen di rantai tersebut.
- **Bertahap lebih baik daripada radikal** - Ambil langkah kecil dan terus mengulanginya. Investasi pertama akan dimulai dari $2-5 juta, dan skalanya akan diperluas setelah model diverifikasi.
- **Tanggung jawab lebih baik daripada hak** - Hak dan kewajiban setara. Anggota komite tata kelola harus menjanjikan 50.000 LIGHT dan mengungkapkan agenda kebijakan mereka. Jika mereka gagal menjalankan tugasnya, mereka akan didenda.
- **Keberagaman lebih baik daripada homogenitas** - Suara yang berbeda adalah kekebalan sistem. Pemungutan suara dua dimensi (koin + alamat) memastikan bahwa investor paus dan ritel memiliki hak untuk berbicara.

### 11.2 Sistem juri

| Dimensi | Aturan |
|------|------|
| Komposisi | Pilih secara acak 12 pengguna yang memiliki ≥10.000 LIGHT dan tidak memiliki catatan pelanggaran |
| Istilah | 30 hari, akan diundi lagi secara acak setelah habis masa berlakunya |
| Tanggung jawab | Mendengarkan keluhan penalti anti kecurangan, tuduhan penipuan proposal, dan perselisihan komunitas |
| Proses | Pengguna yang dihukum dapat menyerahkan bukti dalam waktu 72 jam; juri harus mengambil keputusan dalam waktu 48 jam |
| Standar penilaian | ≥8 dari 12 orang (2/3 mayoritas) harus setuju untuk mempertahankan atau mencabut hukuman |
| Penghindaran | Penggantian otomatis juri yang memiliki hubungan undangan dengan para pihak atau berada dalam rentang IP yang sama |
| Remunerasi | Menerima subsidi layanan juri harian sebesar 5 CAHAYA selama jangka waktu tersebut (disalurkan dari dana ekologi) |

### 11.3 Rencana Ekologis Pengembang

| Modul | Konten | Sumber Pendanaan | Cara Mendaftar |
|------|------|---------|---------|
| Pendanaan Pengembang (Hibah) | Untuk tim yang membangun dApps, alat, dan infrastruktur pada rantai LightDAO, hibah tunggal sebesar $5-500.000 setara dengan LIGHT | Dana Pembangunan Ekologis (Rilis Linier Tahap 2) | Kirimkan proposal → Evaluasi petugas peninjau teknis → Pemungutan suara tata kelola (proses proposal mikro) |
| SDK dan API | Menyediakan antarmuka JavaScript/TypeScript SDK, REST API, dan WebSocket untuk menurunkan ambang batas pengembangan pihak ketiga | Petugas peninjau teknis memimpin pengembangan | Sumber terbuka, publik di GitHub |
| Hackathon | Hackathon online diadakan setiap kuartal, dengan total hadiah sebesar $100.000 setara dengan LIGHT | Dana Pembangunan Ekologi | Buka pendaftaran, tanpa ambang batas |
| Hadiah Bug | Program hadiah bug kontrak inti, hadiah $1.000-$50.000 untuk satu kerentanan yang valid (dinilai berdasarkan tingkat keparahan) | Dana Asuransi + Dana Pembangunan Ekologi | Kirim melalui Immunefi atau platform buatan sendiri |
| Pasar Kontrak CosmWasm | Mendorong pihak ketiga untuk menerapkan kontrak pintar, dan 20% pendapatan biaya bahan bakar akan dikembalikan ke perbendaharaan ekologi untuk mendukung pengembang | Distribusi biaya gas (lihat Bagian 4.5) | Otomatis, tidak perlu aplikasi |

### 11.4 Strategi multi-bahasa dan lokalisasi

| Dimensi | Perencanaan |
|------|------|
| Bahasa platform | Awalnya mendukung bahasa Inggris, Cina, Spanyol, Portugis, dan Filipina; Bahasa Prancis, Arab, Swahili, dan Indonesia akan ditambahkan mulai bulan ke-6 |
| Bahasa pemerintahan | Proposal dan platform kampanye diterima dalam bahasa apa pun, dan sistem menyediakan terjemahan mesin + koreksi manual komunitas |
| Operasi Komunitas | Membentuk saluran komunitas independen (Discord/Telegram) berdasarkan bahasa, dan setiap saluran dilengkapi dengan relawan penghubung komunitas lokal |
| Penerjemahan Dokumen | Kertas putih dan dokumen inti diselesaikan oleh sukarelawan penerjemah komunitas, dan kontribusi terjemahan disertakan dalam bonus perilaku "Kontribusi Konten" (5%) |
| Pendanaan Lokalisasi | 10% (40 juta koin) dari dana pembangunan ekologi dicadangkan khusus untuk pembangunan komunitas lokalisasi dan insentif penerjemahan |

---

## Bab 12: Tim dan Konsultan

### 12.1 Definisi peran inti

| Peran | Tanggung jawab | Persyaratan Latar Belakang | Metode Pengungkapan |
|------|------|---------|---------|
| Wali Awal/Sponsor Proyek | Menyebarkan kontrak awal, memelihara dokumen, dan mengoordinasikan operasi awal | ≥ 3 tahun pengalaman di industri blockchain, dengan penerapan kontrak pintar atau catatan operasi protokol DeFi | Ungkapkan identitas asli Anda di hadapan TGE atau berikan laporan verifikasi identitas pihak ketiga (seperti tanda tangan notaris + verifikasi pesan on-chain) |
| Pemimpin teknis | Desain arsitektur kontrak, manajemen tim pengembangan, audit docking | Pengalaman pengembangan Cosmos SDK/CosmWasm, catatan penerapan rantai produksi | Sama seperti di atas |
| Penanggung Jawab Investasi | Penyaringan target, koordinasi uji tuntas, pembentukan SPV, manajemen keluar | Pengalaman di industri ekuitas swasta/modal ventura, dengan kasus keluar yang lengkap | Sama seperti di atas |
| Konsultan Kepatuhan | Desain struktur hukum, peraturan docking, saran kepatuhan MLM | Pengacara dengan kualifikasi AS/EU/Cayman | Nama firma hukum publik (nama pribadi tidak akan diungkapkan kecuali saya setuju) |

### 12.2 Dewan Penasehat

- Terdiri dari 3-5 konsultan independen, yang meliputi: teknologi DePIN, kepatuhan investasi lintas batas, operasi komunitas, dan industri konsumen;
- Konsultan menerima remunerasi konsultasi dalam bentuk token LIGHT (dicairkan dari bagian "Service Token Exchange" dari dana operasional strategis), dan posisinya dikunci selama 12 bulan;
- Daftar konsultan dipublikasikan di hadapan TGE dan terbuka untuk pertanyaan masyarakat (pertemuan penyelidikan teks terdesentralisasi, lihat Bagian 7.5);
- Penasihat tidak boleh merangkap sebagai anggota Komite Tata Kelola (segregasi konflik kepentingan).

### 12.3 Komitmen dan Kendala Tim

| Kendala | Aturan |
|------|------|
| Penguncian Token | LIGHT (termasuk alokasi dana operasional strategis) yang dipegang oleh tim inti harus dikunci selama 12 bulan dan dilepaskan secara linier selama 36 bulan setelah dibuka |
| Pembatasan penjualan | Wali awal tidak diperbolehkan menjual CAHAYA yang diperoleh melalui saluran apapun (termasuk airdrop, reward, dan kompensasi) selama masa jabatan (≤24 bulan) |
| Konflik kepentingan | Konflik kepentingan anggota tim harus diungkapkan sepenuhnya pada saat penunjukan (apakah mereka memegang token DAO lain, apakah terkait dengan target investasi potensial) |
| Konsekuensi dari kegagalan untuk mengungkapkan | Setelah kegagalan untuk mengungkapkan konflik kepentingan diverifikasi, Anda akan dilarang berpartisipasi secara permanen dalam tata kelola, dan 50% dari token yang tidak terkunci akan disita ke dana asuransi |
| Mekanisme penggantian | Ketika peran inti keluar atau menjadi tidak mampu, komite tata kelola (wali awal + wali alternatif sebelum pembentukan) akan menunjuk penggantinya, yang harus diumumkan secara publik oleh komunitas selama 72 jam tanpa keberatan |

### 12.4 Kompensasi kontributor inti (20% dari dana operasional strategis)

- Jumlah total: 50 juta LAMPU (terhitung 2% dari jumlah total)
- Jumlah orang yang ditanggung: 3-5 orang
- Aturan rilis: Tebing Desember + linier 36 bulan (yaitu, sekitar 1,157 juta koin akan dirilis setiap bulan mulai bulan ke-13)
- Pengikatan pencapaian: Setiap triwulan, komite tata kelola (wali awal + pihak ketiga independen sebelum pendirian) mengonfirmasi bahwa pencapaian tersebut tercapai sebelum kuota triwulanan dapat dilepaskan.
- Aturan pengungkapan: hanya jumlah total dan aturan pelepasan yang diungkapkan, dan nama pribadi serta kuota satu orang tidak diungkapkan (untuk melindungi privasi, dan pada saat yang sama, jumlah total dapat diverifikasi melalui alamat multi-tanda tangan di rantai bahwa jumlah total tidak terlampaui)

---

## Bab 13: Peringatan Risiko dan Penafian

### 13.1 Peringatan risiko

| Jenis risiko | Deskripsi | Langkah-langkah mitigasi |
|---------|------|---------|
| Risiko Pasar | Harga RINGAN dapat berfluktuasi secara signifikan, dan harga historis tidak mewakili kinerja masa depan. TGE memiliki likuiditas awal yang terbatas dan harga mungkin berfluktuasi dengan hebat | Penetapan harga lelang yang adil di Belanda; ±50% pemutus sirkuit 72 jam setelah TGE; mekanisme intervensi empat tingkat spiral anti-kematian |
| Risiko Proyek | Target investasi bisa mengalami kerugian, proyek modal ventura bisa gagal, dan pokoknya bisa hilang seluruhnya. Tingkat kegagalan rata-rata historis industri PE/VC adalah sekitar 50-70% (kesepakatan tunggal) | Desentralisasi mesin ganda (arus kas 70% + pertumbuhan 30%); target tunggal ≤ 25%; industri ≤ 40%; wilayah ≤ 30%; Penyisihan 10% untuk dana asuransi |
| Risiko teknis | Kontrak pintar mungkin memiliki kerentanan yang belum ditemukan; kompatibilitas browser dapat mempengaruhi pengalaman penambangan; jembatan lintas rantai mungkin diserang | Audit independen + verifikasi formal sebelum TGE; Hadiah Bug $1K-$50K; kunci waktu 72 jam; mekanisme suspensi multi-tanda tangan |
| Resiko regulasi | Kebijakan peraturan di berbagai negara dan wilayah dapat berubah, yang dapat mengakibatkan terbatasnya fungsi atau ketidakmampuan pengguna di wilayah tertentu untuk berpartisipasi | Struktur SPV Cayman; verifikasi nol default (verifikasi dilakukan oleh pihak ketiga berlisensi di sisi layanannya); cermin IPFS front-end tahan sensor; tidak dipasarkan ke negara tertentu |
| Risiko Likuiditas | Sub-token mungkin kurang memiliki kedalaman perdagangan pada tahap awal; LIGHT mungkin menghadapi tekanan jual di tahap awal TGE | Likuiditas awal sub-token AMM (6% dari penerbitan); periode penguncian transfer 30 hari; Tim/investor Tebing 12 bulan + linier 36 bulan |
| Resiko pengenceran | Ketika jumlah penambang aktif meningkat, pendapatan penambangan per kapita secara alami akan terdilusi (penyebut BaseReward meningkat) | Tujuan desain: peserta awal mengambil risiko lebih tinggi untuk memperoleh keuntungan lebih tinggi; nantinya pengguna dapat mempercepat akumulasi melalui berbagi undangan; ambang batas tata kelola diturunkan secara dinamis |
| Risiko operasional | Operasi dan pengelolaan perusahaan yang diinvestasikan mungkin tidak memenuhi harapan; Operasi SPV bergantung pada direktur pihak ketiga; tim investasi mungkin hilang | Pembatasan piagam SPV + direktur independen; DAO dapat memilih untuk mengganti direktur; klausul arbitrase SIAC/ICC; asuransi orang kunci (dalam eksplorasi) |
| Risiko jembatan lintas rantai | wLIGHT jembatan lintas rantai dioperasikan oleh pihak ketiga, dan celah kontrak jembatan dapat menyebabkan hilangnya aset (sejarah, jembatan lintas rantai adalah sumber kerugian terbesar) | Audit independen sebelum jembatan online; aset jembatan tidak melebihi 5% dari total pasokan; pengungkapan risiko; pengguna dapat memilih untuk hanya menggunakan rantai asli |
| Risiko validator | Validator secara kolektif offline atau melakukan kejahatan dapat menyebabkan rantai menghentikan produksi blok, dan semua operasi pengguna (penambangan, pemungutan suara, transfer) untuk sementara tidak tersedia | Tendermint BFT mentolerir <1/3 kejahatan; validator ≥ 21 (f=6); Hukuman pemotongan; mekanisme pemungutan suara migrasi darurat |

### 13.2 Penafian

- LIGHT dan sub-token bukanlah sekuritas, tidak memiliki nilai intrinsik, dan harganya dapat kembali ke nol. Buku putih ini bukan merupakan dokumen penerbitan sekuritas, penawaran investasi, atau nasihat investasi dalam bentuk apa pun.
- Distribusi pendapatan dari perjanjian bergantung pada kinerja operasional aktual dari aset yang mendasarinya, dan data historis tidak mewakili pendapatan di masa depan. Setiap deskripsi hasil investasi merupakan perkiraan masa depan dan bukan janji.
- Pengguna harus menanggung semua kerugian yang disebabkan oleh hilangnya atau kebocoran kunci pribadi, dan perjanjian tidak menyediakan layanan pengambilan. Menggunakan dompet Tingkat 1 (Kunci Sandi) atau Tingkat 2 (Pemulihan Sosial) mengurangi risiko ini, namun tidak menghilangkannya.
- Perjanjian ini terbuka untuk pengguna di seluruh dunia (tunduk pada hukum dan peraturan yang berlaku). Pengguna harus mengonfirmasi sikap hukum terhadap aset terenkripsi, organisasi DAO, dan sertifikat pendapatan SPV di yurisdiksi mereka, dan memastikan bahwa partisipasi mereka sah dan patuh.
- Pernyataan berwawasan ke depan dalam buku putih ini (termasuk peta jalan, model pendapatan, perkiraan deflasi, perkiraan skala investasi) adalah prediksi berdasarkan asumsi saat ini, dan hasil sebenarnya mungkin berbeda secara signifikan karena pasar, teknologi, peraturan, eksekusi tim, dan faktor lainnya.
- Insentif undangan merupakan mekanisme pembagian satu tingkat dan bukan merupakan pemasaran berjenjang atau skema piramida. Namun, pengguna tetap harus mengonfirmasi sikap hukum terhadap imbalan rujukan di yurisdiksi mereka.
- Usia minimum untuk berpartisipasi dalam ekosistem LightDAO adalah 18 tahun (atau usia mayoritas yang sah di yurisdiksi Anda, mana saja yang lebih tinggi). Anak di bawah umur tidak diperbolehkan berpartisipasi dalam pertambangan, tata kelola, atau investasi.

---

## Lampiran A: Tabel ringkasan parameter utama

| Kategori | Parameter | Nilai |
|------|------|------|
| Penerbitan | Jumlah total | 2,5 miliar keping, tidak pernah diterbitkan lagi |
| Penerbitan | Pertambangan | 40% = 1 miliar koin |
| Penerbitan | Gudang Investasi | 34% = 850 juta koin |
| Penerbitan | Dana Ekologi | 16% = 400 juta keping |
| Penerbitan | Operasi Strategis | 10% = 250 juta koin (layanan 50%/pembiayaan 30%/kontributor 20%) |
| Penerbitan | Siklus separuh | Setiap 2 tahun |
| Penerbitan | Rilis Hari Era Pertama | ≈684,900 (penambang 95% = 650,700, validator 5% = 34,200) |
| Penerbitan | Kumpulan hadiah per blok | ≈13,87 CAHAYA |
| Pertambangan | Bobot kontribusi | Bandwidth 40%/sesi 30%/verifikasi 20%/stabilitas 10% |
| Pertambangan | Bonus penuh | 1,44 kali |
| Undangan | Penginjil/Duta Besar/Mitra | 3 orang 10%+100L/10 orang 15%+500L+5%/50 orang 20%+2500L+10% |
| Perilaku | Empat item × 5% | Batas atas 20% |
| Biaya bahan bakar | Mekanisme penetapan harga | Penahan setara USD, secara otomatis diubah menjadi kuantitas CAHAYA oleh oracle setiap 24 jam |
| Biaya bahan bakar | Pemindahan biasa | Setara dengan $0,001 (@$0,05=0,02 CAHAYA) |
| Biaya bahan bakar | Pemungutan suara pemerintahan | Setara dengan $0,005 (@$0,05=0,10 CAHAYA) |
| Biaya bahan bakar | Aturan Distribusi | 50% kehancuran / 30% validator / 20% perbendaharaan ekologi |
| Deflasi | Perlambatan/peringatan dini/intinya | ≤1,5 miliar/≤1,2 miliar/≤1 miliar (volume peredaran) |
| Deflasi | Batas atas teoritis | 1,65 miliar (10+4+2,5, 850 juta di kas tidak akan pernah beredar) |
| Tata Kelola | Ambang Usulan | ≥5.000 CAHAYA + 30 hari staking |
| Tata Kelola | Taruhan Komite | 50.000 CAHAYA + 100 Alamat |
| TATA KELOLA | JURI | 10.000 CAHAYA |
| Tata Kelola | Taruhan | 5—500 CAHAYA |
| Tata Kelola | Bonus reputasi | 1 tahun +15 suara → +30% (batas total +40%) |
| Investasi | Batas tunggal | Sisa brankas × 15% (127,5 juta koin awal) |
| Investasi | Dasar dapat diterapkan | 850 juta × $0,15 × 75% = $95,63 juta ≈ $100 juta |
| Investasi | Distribusi keuntungan (tahunan) | 40/30/20/10 |
| Investasi | Distribusi keuntungan (keluar) | 70/30 |
| Lelang | Sasaran | $15 juta ($5 juta cadangan + $10 juta modal yang diinvestasikan) |
| Cadangan | Perbendaharaan Stabil | TGE $5 juta → Bulan 24 $8 juta |
| Asuransi | Keuntungan | Untung 10% |
| Tetesan Udara | Jumlah anggaran | 55 juta (dana ekologi 13,75%), CAC≈$55/pengguna tetap |
| Validator | Awal/Batas | 21 (minimal 10) / 100 |
| Validator | Taruhan minimal | 500.000 CAHAYA |
| Verifikator | Intinya keras TGE | ≥7, jika tidak maka tidak diperbolehkan online |

---

## Lampiran B: Derivasi dan verifikasi numerik

### B.1 Hasil penambangan

2A=1 miliar→A=500 juta. Pelepasan harian = 500 juta 730 = 684.932 ≈ 684.900. Kumpulan penambangan=684,932×95%=650,685≈650,700. Verifikator=684,932×5%=34,247≈34,200. Setiap blok=684,932 49,371≈13,87. Verifikasi: 684.932×730=499.999.960≈500 juta ✓

### B.2 Aksesibilitas ambang batas tata kelola

Tolok ukur 100,000 penambang (6,51/hari, mitra 74,44/hari): proposal 5,000→768 hari/67 hari; panitia 50.000→7.684 hari (21 tahun)/672 hari (22 bulan); juri 10,000→1,537 hari (4,2 tahun)/134 hari (4,5 bulan); taruhan 500→77 hari/6,7 hari.

Periode benih (10,000 penambang, 65,07/hari, mitra 744,4/hari): proposal → 77 hari (2,5 bulan) / 6,7 hari; panitia → 768 hari (25 bulan) / 67 hari (2,2 bulan); juri → 154 hari (5 bulan) / 13,4 hari.

### B.3 Garis Waktu Deflasi

Volume sirkulasi = penambangan + ekologi + strategi (dimiliki) − pertukaran − Gas − pembelian kembali. 850 juta di kas tidak akan pernah beredar.

| Tahun | Penambangan Kumulatif | Ekologi | Strategi | Pertukaran | Gas | Pembelian kembali | Sirkulasi |
|----|---------|------|------|------|-----|------|--------|
| 1 | 2.50 | 2.80 | 0 | 0 | 0,01 | 0 | ≈5.29 |
| 2 | 5.00 | 4.00 | 0,83 | 0,05 | 0,02 | 0 | ≈9.76 |
| 3 | 6.25 | 4.00 | 1.67 | 0,20 | 0,03 | 0,05 | ≈11.64 |
| 4 | 7.50 | 4.00 | 2.50 | 0,45 | 0,04 | 0,20 | ≈13.31(puncak) |
| 5 | 8.13 | 4.00 | 2.50 | 0,80 | 0,05 | 0,50 | ≈13.28 |
| 6 | 8.75 | 4.00 | 2.50 | 1.20 | 0,06 | 0,90 | ≈13.09 |
| 7 | 9.06 | 4.00 | 2.50 | 1.60 | 0,07 | 1.40 | ≈12.49 |
| 8 | 9.38 | 4.00 | 2.50 | 2.00 | 0,08 | 1.90 | ≈11.89 |
| 9 | 9.53 | 4.00 | 2.50 | 2.40 | 0,09 | 2.30 | ≈11.24 |
| 10 | 9.69 | 4.00 | 2.50 | 2.80 | 0,10 | 2.70 | ≈10.59 |
| 11 | 9.77 | 4.00 | 2.50 | 3.10 | 0,11 | 3.00 | ≈10.06 |
| 12 | 9.84 | 4.00 | 2.50 | 3.40 | 0,12 | 3.30 | ≈9.52 |

Kesimpulan: Puncak Y4≈1,331 miliar; garis peringatan 1,2 miliar tersentuh oleh Y8; bottom line 1 miliar tersentuh oleh Y11-12; garis perlambatan sebesar 1,5 miliar hanyalah skenario kehancuran yang sangat rendah.

---

## Lampiran C: Log koreksi audit (total 36 item)

Berisi 22 item asli (L1-5, A1-4, D1-4, M1-8, G1-3) + 7 item arsitektur teknis (T1-7) + 7 item optimasi model ekonomi di babak ini:

| Nomor | Koreksi |
|------|------|
| E-1 | Jumlah total 2,1 miliar → 2,5 miliar (didorong oleh kendala kapasitas investasi) |
| E-2 | Alokasi 30/50/20→40/34/16/10 (10% dari dana operasional strategis baru) |
| E-3 | Lelang Belanda $10 juta→$15 juta (modal investasi awal $5 juta→$10 juta) |
| E-4 | Rencana pertumbuhan airdrop 5,7 bagian baru (55 juta keping, CAC $55/orang) |
| E-5 | Verifikator diluncurkan secara bertahap (Testnet 7→TGE minimum 10/Target 21→Open 100) |
| E-6 | Penyesuaian garis pemicu deflasi (14/12/10 → 15/12/10, disesuaikan dengan batas edar 1,65 miliar) |
| E-7 | Ganti semua kutipan eksternal dengan sumber yang dapat diverifikasi (hapus makalah SSRN yang tidak dapat diverifikasi) |

---

## Lampiran D: Indeks Istilah Singkat

Penjelasan lengkap setiap istilah terdapat di blok komentar [Istilah dalam Bab ini] di akhir bab tempat istilah tersebut pertama kali muncul. Indeks ini mencantumkan semua istilah dan babnya dalam urutan abjad untuk navigasi cepat.

| Terminologi | Bab Definisi |
|------|------------|
| AMM (Pembuat Pasar Otomatis) | Bab 4 |
| BFT (Toleransi Kesalahan Bizantium) | Bab 4 |
| CAC (Biaya Akuisisi Pelanggan) | Bab 5 |
| CEX (Pertukaran Terpusat) | Bab 4 |
| SDK Kosmos | Bab 4 |
| KosmWasm | Bab 4 |
| DAO (Organisasi Otonomi Terdesentralisasi) | Bab 2 |
| DCF (Metode Arus Kas Terdiskonto) | Bab 9 |
| DePIN (Jaringan Infrastruktur Fisik Terdesentralisasi) | Bab 2 |
| DEX (Pertukaran Terdesentralisasi) | Bab 4 |
| EBITDA (laba sebelum bunga, pajak, depresiasi dan amortisasi) | Bab 9 |
| Biaya Bahan Bakar | Bab 4 |
| IBC (Protokol Komunikasi Antar Rantai) | Bab 3 |
| IPFS (Sistem File AntarPlanet) | Bab 4 |
| KYC (Kenali Pelanggan Anda) | Bab 3 |
| CAHAYA (token asli) | Bab 4 |
| LP (Penyedia Likuiditas) | Bab 5 |
| PE Pasar Menengah Bawah (Ekuitas Swasta Pasar Menengah Hilir) | Bab 2 |
| Pohon Merkle | Bab 4 |
| MiFID II (Pasar UE dalam Petunjuk Instrumen Keuangan II) | Bab 3 |
| MLM (Pemasaran Bertingkat) | Bab 3 |
| PII (Informasi Identifikasi Pribadi) | Bab 3 |
| PoC (Bukti Kontribusi) | Bab 4 |
| PoS (Bukti Taruhan) | Bab 4 |
| PoW (Bukti Kerja) | Bab 4 |
| Pra-IPO | Bab 9 |
| PWA (Aplikasi Web Progresif) | Bab 4 |
| Reg D / Reg S (Peraturan D/S Undang-Undang Sekuritas AS) | Bab 3 |
| Menebas | Bab 4 |
| SPV (Kendaraan Tujuan Khusus) | Bab 2 |
| TGE (Acara Pembuatan Token) | Bab 5 |
| TWAP (Harga Rata-Rata Tertimbang Waktu) | Bab 4 |
| Eksekusi TWAP (Pembelian Kembali dan Pemisahan Pesanan) | Bab 9 |
| VWAP (Harga Rata-Rata Tertimbang Volume) | Bab 5 |
| wLIGHT (CAHAYA yang dienkapsulasi) | Bab 5 |
| ZK-KYC (KYC Tanpa Pengetahuan Bukti) | Bab 3 |
| Sub-token | Bab 5 |
| Spiral Kematian | Bab 5 |
| Membelah dua | Bab 5 |
| Perbendaharaan (Perbendaharaan) | Bab 5 |
| Lelang Belanda | Bab 5 |
| Peramal | Bab 4 |

---

**Buku putih lengkap berakhir**

**Pernyataan Hak Cipta:** Dokumen ini adalah dokumen komunitas sumber terbuka dan dapat direproduksi secara bebas, namun konten lengkapnya harus dipertahankan.

---

# Lampiran: Parameter dan alamat terverifikasi Mainnet (V2.4 live)

## A. §4.5 Parameter Terukur Ekonomi Gas
- rumus harga gas minimum: `(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas`; TransferUsdTarget saat ini=$0,001, UsdPerLight=$0,05, RefTransferGas=100000 → **0,2 ulight/gas**
- Pengukuran distribusi (total biaya 300000 ulight): pemusnahan 150000 (50%)/perbendaharaan 60000(20%)/verifikator 90000(30%), pencocokan tepat
- Alamat pemusnahan: `wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu` (alamat mati deterministik)
- Perbendaharaan: kontrak `treasury_multisig` (3/5 multi-tanda tangan; kueri `penandatangan` pada rantai mengembalikan 5 penandatangan, ambang batasnya sendiri tidak ada di antarmuka kueri)

## B. Alamat kontrak inti
Lihat repositori `docs/MAINNET_STATUS.md` (light_token / mining_reward / governance / treasury_multisig / oracle_twap / vesting dan 10 kontrak lainnya).

## C. Pembuangan denom (saham) warisan
genesis mismatch mint_denom=stake telah disetel ulang ke nol dan penerbitan tambahan telah dihentikan; pasak yang ada (sekitar 2,56e11 unit mikro) dibiarkan tanpa tujuan, dan rencana pembuangan (penukaran/penghancuran) masih menunggu usulan tata kelola dan tidak akan mempengaruhi model ekonomi yang buruk.

## D. §4.4 vesting langsung
Vault 250.000.000 CAHAYA, 3 jadwal independen: 75M (tebing 0)/ 100M (tebing 1 tahun)/ 75M (tebing 2 tahun), sudah ada dalam rantai.

## E. Praktik Keselamatan
- Jaringan utama ditingkatkan ke x/peningkatan tata kelola + koordinasi tinggi semua node di blok yang sama + pengawas pertukaran otomatis, dijalankan setelah latihan jaringan pengujian ujung ke ujung
- Benih kunci sandi hanya menyimpan teks tersandi; Pecahan Shamir tidak menyimpannya secara lokal.
- Ambang penyerahan akar penambangan kontrak 5 (ambang batas pengukuran aktual=5 untuk setiap peristiwa `submit_root` pada rantai; saat ini 5 akun resmi sedang ditandatangani, dan 7 kursi adalah target desain); untuk anti-penyihir/anti-kecurangan, lihat §4.8
