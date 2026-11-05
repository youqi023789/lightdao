/* LD-I18N-B7-20261105  同批的英→es,pt,id,vi（键回指英文，由展开器写进同一个中文键）。 */
(function () {
  "use strict";
  var L = ["es","pt","id","vi"];
  var T = {
    "checking": "comprobando|verificando|sedang memeriksa|đang kiểm tra",
    "unavailable": "no disponible|não disponível|hindi mabasa|không đọc được",
    "block height": "altura de bloque|altura do bloco|tinggi blok|chiều cao khối",
    "channel": "canal|canal|kanal|kênh",
    "unconfirmed packets": "paquetes sin confirmar|pacotes não confirmados|paket belum terkonfirmasi|gói chưa xác nhận",
    "escrow": "retención (escrow)|custódia (escrow)|escrow|kẽm giữ hộ (escrow)",
    "relayer account": "cuenta del relayer|conta do relayer|akun relayer|tài khoản relayer",
    "mainnet cross-chain": "intercadena de la red principal|cross-chain da rede principal|cross-chain mainnet|cross-chain mainnet",
    "enabled": "activado|ativado|diaktifkan|đã bật",
    "not enabled": "no activado|não ativado|belum diaktifkan|chưa bật",
    "updated": "actualizado|atualizado|diperbarui|đã cập nhật",
    "connected": "conectado|conectado|terhubung|đã kết nối",
    "abnormal": "anomalía|anomalia|anomali|bất thường",
    "asset": "activo|ativo|aset|tài sản",
    "price (USD)": "precio (USD)|preço (USD)|harga (USD)|giá (USD)",
    "24h change": "variación 24 h|variação 24h|perubahan 24 jam|thay đổi 24h",
    "external cross-chain trading": "acceso de intercambio intercadena externo|acesso cross-chain externo|akses perdagangan lintas rantai|lối giao dịch cross-chain",
    "market data": "datos de mercado|dados de mercado|data pasar|dữ liệu thị trường",
    "cross-chain status": "estado intercadena|estado cross-chain|status lintas rantai|trạng thái cross-chain",
    "language": "idioma|idioma|bahasa|ngôn ngữ",
    "block time": "tiempo de bloque|tempo de bloco|waktu blok|thời gian block",
    "n/a": "n/d|s/d|tidak tersedia|không có",
    "testnet A": "testnet A|testnet A|testnet A|testnet A",
    "testnet B": "testnet B|testnet B|testnet B|testnet B",
    "mainnet": "red principal|rede principal|jaringan utama|mạng chính",
    "syncing": "sincronizando|sincronizando|sedang sinkron|đang đồng bộ",
    "{n}s ago": "hace {n} s|há {n} s|{n} dtk lalu|{n} giây trước",
    "no market data for these assets": "sin datos de mercado para estos activos|sem dados desses ativos|tidak ada data aset ini|không có dữ liệu cho các tài sản này",
    "EVM cross-chain swap (Li.Fi)": "intercambio EVM entre cadenas (Li.Fi)|troca EVM cross-chain (Li.Fi)|swap EVM lintas rantai (Li.Fi)|swap EVM cross-chain (Li.Fi)",
    "Solana swap (Jupiter)": "intercambio Solana (Jupiter)|troca Solana (Jupiter)|swap Solana (Jupiter)|swap Solana (Jupiter)",
    "LIGHT market page": "página de mercado LIGHT|página de mercado LIGHT|halaman pasar LIGHT|trang thị trường LIGHT",
    "cross-chain": "intercadena|cross-chain|lintas rantai|cross-chain",
    "These are third-party aggregators: trades settle in your own wallet and their routes. LightDAO does not custody assets, does not match orders, and does not guarantee outcomes.": "Son agregadores de terceros: la operación se ejecuta en tu propia billetera y en sus rutas; LightDAO no custodia activos, no empareja órdenes y no garantiza resultados.|São agregadores de terceiros: a negociação ocorre na sua própria carteira e nas rotas deles; a LightDAO não custodia ativos, não casa ordens e não garante resultados.|Ini adalah aggregator pihak ketiga: transaksi diselesaikan di dompet Anda sendiri dan pada rute mereka; LightDAO tidak menyimpan aset, tidak mempertemukan pesanan, dan tidak menjamin hasil.|Đây là bên thứ ba tổng hợp: giao dịch diễn ra trong ví của bạn và trên tuyến đường của họ; LightDAO không giữ tài sản, không khớp lệnh, không bảo đảm kết quả.",
    "prices from CoinGecko, cached 60s by this site": "precios de CoinGecko, en caché 60 s por este site|preços do CoinGecko, em cache 60 s por este site|harga dari CoinGecko, di-cache 60 dtk oleh situs ini|giá từ CoinGecko, được trang này lưu bộ nhớ đệm 60 giây",
    "data sampled every {n}s by this site's read-only probe": "datos muestreados cada {n} s por la sonda de solo lectura|dados coletados a cada {n} s pela sonda somente leitura|data diambil setiap {n} dtk oleh probe baca-saja|dữ liệu được lấy mỗi {n} giây bởi đầu đọc chỉ xem",
    "chain": "cadena|cadeia|rantai|chuỗi",
    "mainnet IBC light clients": "clientes ligeros IBC de la red principal|clientes leves IBC da rede principal|jumlah light client IBC mainnet|số light client IBC của mainnet",
    "the probe reported gaps": "la sonda informa huecos|o sensor reporta lacunas|probe melaporkan celah|đầu dò báo có khoảng trống",
    "Mainnet cross-chain is not enabled yet: LIGHT is a contract token (CW20), IBC only moves native coins; the wrapped route and governance approval are not finished.": "La intercadena de red principal aún no está habilitada: LIGHT es un token de contrato (CW20), IBC solo mueve monedas nativas; faltan la ruta envuelta y la aprobación de gobernanza.|A intercadeia da rede principal ainda não está ativada: LIGHT é um token de contrato (CW20), o IBC só move moedas nativas; faltam a rota embrulhada e a aprovação de governança.|Cross-chain mainnet belum diaktifkan: LIGHT adalah token kontrak (CW20), IBC hanya memindahkan koin native; rute wrapped dan persetujuan tata kelola belum selesai.|Cross-chain mainnet chưa bật: LIGHT là token hợp đồng (CW20), IBC chỉ chuyển coin gốc; tuyến wrapped và phê duyệt quản trị chưa xong.",
    "loading…": "cargando…|carregando…|memuat…|đang tải…",
    "send a testnet cross-chain transfer (A→B)": "enviar una transferencia intercadena de testnet (A→B)|enviar uma transferência cross-chain de testnet (A→B)|kirim transfer cross-chain testnet (A→B)|gửi một giao dịch cross-chain testnet (A→B)",
    "sending…": "enviando…|enviando…|mengirim…|đang gửi…",
    "failed: {e}": "falló: {e}|falhou: {e}|gagal: {e}|thất bại: {e}",
    "on-chain, waiting for the relayer: tx {h}": "en cadena, esperando al relayer: tx {h}|na cadeia, aguardando o relayer: tx {h}|sudah on-chain, menunggu relayer: tx {h}|đã lên chain, đang chờ relayer: tx {h}",
    "{n} demo transfers left this hour": "quedan {n} transferencias demo esta hora|restam {n} transferências demo nesta hora|sisa {n} transfer demo jam ini|còn {n} lượt chuyển demo trong giờ này",
    "cross-chain quote (1 ETH → USDC, Ethereum → Optimism)": "cotización intercadena (1 ETH → USDC, Ethereum → Optimism)|cotação cross-chain (1 ETH → USDC, Ethereum → Optimism)|kuotasi lintas rantai (1 ETH → USDC, Ethereum → Optimism)|báo giá cross-chain (1 ETH → USDC, Ethereum → Optimism)",
    "via {t}, expected {a}, gas ${g}, about {d}": "vía {t}, esperado {a}, gas ${g}, duración ~{d}|via {t}, esperado {a}, gás ${g}, duração ~{d}|via {t}, perkiraan {a}, gas ${g}, durasi ~{d}|qua {t}, dự kiến {a}, gas ${g}, thời gian ~{d}",
    "open this route in the aggregator": "abrir esta ruta en el agregador|abrir esta rota no agregador|buka rute ini di aggregator|mở tuyến này trong aggregator",
  };
  if (typeof window.__ldExpandLangs !== "function") {
    var tb = (window.__ldTables = window.__ldTables || []);
    var has = false;
    for (var qi = 0; qi < tb.length; qi++) { if (tb[qi][1] === T) { has = true; break; } }
    if (!has) tb.push([L, T]);
    window.__ldLat6Stats = { pending: "expander-not-yet-defined；boot 时统一展开" };
  } else {
    window.__ldLat6Stats = window.__ldExpandLangs(L, T);
  }
})();
