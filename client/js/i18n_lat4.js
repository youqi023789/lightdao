/* LD-I18N-B5-20261104  同批标签的英→es,pt,id,vi（人工，列序同 i18n_lat.js） */
(function () {
  "use strict";
  var L = ["es","pt","id","vi"];
  var T = {
    "Undelegate": "Desvincular|Desvincular|Lepas delegasi|Hủy liên kết",
    "Verified": "Verificado|Verificado|Terverifikasi|Đã xác minh",
    "Settled": "Liquidado|Liquidado|Diselesaikan|Đã đối soát",
    "Bandwidth kbps": "Ancho de banda kbps|Largura de banda kbps|Bandwidth kbps|Băng thông kbps",
    "Uptime s": "Tiempo en línea (s)|Tempo online (s)|Waktu online (s)|Thời gian trực tuyến (giây)",
    "Stability %": "Estabilidad %|Estabilidade %|Stabilitas %|Độ ổn định %",
    "LIGHT earned": "LIGHT ganados|LIGHT ganhos|LIGHT diperoleh|LIGHT nhận được",
    "Save delegation": "Guardar delegación|Salvar delegação|Simpan delegasi|Lưu ủy quyền",
    "Querying…": "Consultando…|Consultando…|Mengkueri…|Đang truy vấn…",
    "Load claimable history": "Cargar historial reclamable|Carregar histórico reivindicável|Muat riwayat yang bisa diklaim|Tải lịch sử có thể nhận",
    "Waiting for network data…": "Esperando datos de la red…|Aguardando dados da rede…|Menunggu data jaringan…|Đang chờ dữ liệu mạng…",
    "Social recovery (shards)": "Recuperación social (fragmentos)|Recuperação social (fragmentos)|Pemulihan sosial (serpihan)|Phục hồi xã hội (mảnh)",
    "Not delegated (online yourself)": "Sin delegar (en línea usted mismo)|Sem delegação (online você mesmo)|Tidak didelegasikan (online sendiri)|Chưa ủy quyền (tự trực tuyến)",
    "Please don't click again to avoid mistakes": "No vuelva a hacer clic para evitar errores|Não clique novamente para evitar erros|Jangan klik lagi untuk menghindari kesalahan|Đừng bấm lại để tránh nhầm",
    "Claim validator / staking rewards in one tap": "Reclama recompensas de validador / staking con un toque|Receba recompensas de validador / staking com um toque|Klaim imbalan validator / staking sekali sentuh|Nhận thưởng validator / staking bằng một chạm",
    "Wallet security": "Seguridad del monedero|Segurança da carteira|Keamanan dompet|Bảo mật ví",
    "Governance (voting / proposals / treasury)": "Gobernanza (votación / propuestas / tesorería)|Governança (votação / propostas / tesouraria)|Tata kelola (pemungutan / proposal / kas)|Quản trị (bỏ phiếu / đề xuất / quỹ)",
    "Airdrops (whitepaper §5.7)": "Airdrops (libro blanco §5.7)|Airdrops (livro branco §5.7)|Airdrop (whitepaper §5.7)|Airdrop (sách trắng §5.7)",
    "Anti-Sybil notice": "Aviso anti-Sybil|Aviso anti-Sybil|Pemberitahuan anti-Sybil|Thông báo anti-Sybil",
    "Sub-token exchange": "Intercambio de sub-token|Troca de sub-token|Pertukaran sub-token|Trao đổi sub-token",
    "Delegate uptime (70/30)": "Delegar tiempo en línea (70/30)|Delegar tempo online (70/30)|Delegasikan uptime (70/30)|Ủy quyền thời gian trực tuyến (70/30)",
    "My contribution history": "Mi historial de contribución|Meu histórico de contribuição|Riwayat kontribusi saya|Lịch sử đóng góp của tôi",
    "Titles & achievements": "Títulos y logros|Títulos e conquistas|Julukan dan pencapaian|Danh hiệu và thành tích",
    "Remove this device's login": "Quitar el inicio de sesión de este dispositivo|Remover o login deste dispositivo|Hapus login perangkat ini|Xóa đăng nhập thiết bị này",
    "My security & referrals": "Mi seguridad y referidos|Minha segurança e referências|Keamanan dan referral saya|Bảo mật và giới thiệu của tôi",
    "Restoring session…": "Restaurando sesión…|Restaurando sessão…|Memulihkan sesi…|Đang khôi phục phiên…",
    "Treasury pool": "Fondo del tesoro|Fundo do tesouro|Pool kas|Hồ sơ quỹ",
  };
  if (typeof window.__ldExpandLangs !== "function") {
    window.__ldLat4Stats = { error: "expander-missing" }; return;
  }
  window.__ldLat4Stats = window.__ldExpandLangs(L, T);
})();
