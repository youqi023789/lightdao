window.LDBUILD="v9";
function terr(e){ return "[" + window.LDBUILD + "] " + String(e.message||e).slice(0,90); }

window.CFG = {
  gw: location.origin + "/gw",
  rpc: location.origin + "/rpc/",
  chainId: "lightdao-mainnet-1", denom: "ulight", prefix: "wasm",
  miningReward: "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx",
  heartbeatSec: 20,
};
const I18N = {
 zh:{heroT:"把闲置设备变成收益",heroS:"运行轻节点贡献带宽与算力，赚取原生 LIGHT 代币",createW:"新建钱包",importW:"导入助记词",createHint:"将生成 12 词助记词，请务必离线备份——它是你资产的唯一凭证。",btnCreate:"生成新钱包",btnImport:"导入",warn:"⚠ 测试网阶段，请勿投入真实资产。助记词只存本机浏览器。",idle:"未运行",running:"挖矿运行中",estLabel:"今日预计奖励 (LIGHT)",startMining:"开始挖矿",stopMining:"停止挖矿",yourAddr:"你的地址",logout:"退出",balance:"余额 (LIGHT)",claimable:"可领取",claim:"领取奖励",contrib:"实时贡献",cBw:"带宽",cSess:"在线时长",cVerif:"验证任务",cStab:"稳定性",footer:"LightDAO 轻节点",claimed:"领取成功！",nothing:"暂无可领取奖励",saving:"请妥善保存助记词",walletFail:"钱包组件加载失败(网络受限)，挖矿/贡献仍可用，领取暂不可用",pkTab:"Passkey 钱包",pkHint:"用指纹/面容登录，无需助记词；可设 3-5 人社交恢复。",pkCreate:"创建 Passkey 钱包",pkUnlock:"Passkey 解锁",pkSocial:"社交恢复(分片)",pkCreated:"✓ Passkey 钱包已创建，助记词已加密(不落地)",pkUnlocked:"✓ 解锁成功",pkPinPrompt:"此浏览器不支持 Passkey PRF，请设 PIN(≥6位)作为加密密钥:",pkSocialHint:"已生成 5 份分片，任 3 份可恢复。请抄给 5 位监护人(本地不保存):",pkRecoverPrompt:"粘贴任意 ≥3 份分片(每行一份)以恢复:",pkRecoverOk:"✓ 重建成功，正在用恢复的助记词重设 Passkey…",pkFail:"Passkey 操作失败: ",pkUnsupported:"此浏览器不支持 WebAuthn，请改用「助记词」标签页",pkSocialFirst:"请先创建/解锁 Passkey 钱包再做社交恢复",inviteT:"邀请好友,赚 TA 首周贡献的 10%",copy:"复制"},
 en:{heroT:"Turn idle devices into yield",heroS:"Run a light node, contribute bandwidth & compute, earn native LIGHT",createW:"New Wallet",importW:"Import Seed",createHint:"A 12-word seed will be generated. Back it up offline — it is the only key to your funds.",btnCreate:"Generate Wallet",btnImport:"Import",warn:"⚠ Testnet phase, no real value. Seed stays in this browser only.",idle:"Idle",running:"Mining active",estLabel:"Est. reward today (pro-rata of network, live) (LIGHT)",blkInfo:"Per-block pool ≈13.87 LIGHT (shared network-wide, pro-rata by contribution) · daily pool ≈650,685 LIGHT",startMining:"Start Mining",stopMining:"Stop Mining",yourAddr:"Your address",logout:"Logout",balance:"Balance (LIGHT)",claimable:"Claimable",claim:"Claim Rewards",contrib:"Live contribution",cBw:"Bandwidth",cSess:"Uptime",cVerif:"Tasks",cStab:"Stability",footer:"LightDAO light node",claimed:"Claimed!",nothing:"Nothing to claim",saving:"Save your seed phrase",walletFail:"Wallet lib failed to load (network). Mining still works; claiming unavailable.",pkTab:"Passkey Wallet",pkHint:"Login with fingerprint/face, no seed phrase; optional 3-5 guardian social recovery.",pkCreate:"Create Passkey Wallet",pkUnlock:"Unlock with Passkey",pkSocial:"Social Recovery (shares)",pkCreated:"✓ Passkey wallet created, seed encrypted (never stored in plain)",pkUnlocked:"✓ Unlocked",pkPinPrompt:"This browser lacks Passkey PRF. Set a PIN (≥6) as encryption key:",pkSocialHint:"5 shares generated; any 3 recover. Give to 5 guardians (not stored locally):",pkRecoverPrompt:"Paste any ≥3 shares (one per line) to recover:",pkRecoverOk:"✓ Recovered! Re-creating Passkey with restored seed…",pkFail:"Passkey error: ",pkUnsupported:"WebAuthn unsupported here, use the Seed Phrase tab",pkSocialFirst:"Create/unlock a Passkey wallet first",inviteT:"Invite friends, earn 10% of their first-week contribution",copy:"Copy"},
 es:{heroT:"Convierte dispositivos en ingresos",heroS:"Ejecuta un nodo ligero y gana LIGHT",createW:"Nueva cartera",importW:"Importar",createHint:"Se generará una frase de 12 palabras. Cópiala offline.",btnCreate:"Generar",btnImport:"Importar",warn:"⚠ Fase de prueba, sin valor real.",idle:"Inactivo",running:"Minando",estLabel:"Recompensa est. hoy (LIGHT)",startMining:"Empezar",stopMining:"Parar",yourAddr:"Tu dirección",logout:"Salir",balance:"Saldo (LIGHT)",claimable:"Reclamable",claim:"Reclamar",contrib:"Contribución",cBw:"Banda",cSess:"Tiempo",cVerif:"Tareas",cStab:"Estab.",footer:"Nodo ligero LightDAO",claimed:"¡Reclamado!",nothing:"Nada que reclamar",saving:"Guarda tu frase",walletFail:"Lib de cartera no cargó. Minar funciona; reclamar no.",pkTab:"Cartera Passkey",pkHint:"Inicia con huella/rostro, sin frase semilla; recuperación social 3-5 opcional.",pkCreate:"Crear cartera Passkey",pkUnlock:"Desbloquear con Passkey",pkSocial:"Recuperación social",pkCreated:"✓ Cartera Passkey creada, semilla cifrada",pkUnlocked:"✓ Desbloqueado",pkPinPrompt:"Este navegador no soporta PRF. Define un PIN (≥6):",pkSocialHint:"5 fragmentos generados; 3 cualesquiera recuperan. Dalos a 5 guardianes:",pkRecoverPrompt:"Pega ≥3 fragmentos (uno por línea):",pkRecoverOk:"✓ Recuperado! Re-creando Passkey…",pkFail:"Error Passkey: ",pkUnsupported:"WebAuthn no soportado, usa la pestaña de semilla",pkSocialFirst:"Crea/desbloquea una cartera Passkey primero",inviteT:"Invita amigos y gana el 10% de su contribución de la 1ª semana",copy:"Copiar"},
 pt:{heroT:"Transforme dispositivos ociosos em renda",heroS:"Rode um nó leve, contribua banda e computação, ganhe LIGHT nativo",createW:"Nova carteira",importW:"Importar seed",createHint:"Uma seed de 12 palavras será gerada. Faça backup offline — é a única chave dos seus fundos.",btnCreate:"Gerar carteira",btnImport:"Importar",warn:"⚠ Fase de testes, sem valor real. A seed fica só neste navegador.",idle:"Parado",running:"Mineração ativa",estLabel:"Recompensa est. hoje (LIGHT)",startMining:"Começar",stopMining:"Parar",yourAddr:"Seu endereço",logout:"Sair",balance:"Saldo (LIGHT)",claimable:"A receber",claim:"Resgatar",contrib:"Contribuição ao vivo",cBw:"Banda",cSess:"Uptime",cVerif:"Tarefas",cStab:"Estabilidade",footer:"Nó leve LightDAO",claimed:"Resgatado!",nothing:"Nada a resgatar",saving:"Guarde sua seed",walletFail:"Biblioteca da carteira falhou (rede). Mineração funciona; resgate indisponível.",pkTab:"Carteira Passkey",pkHint:"Entre com digital/rosto, sem seed; recuperação social 3-5 opcional.",pkCreate:"Criar carteira Passkey",pkUnlock:"Desbloquear com Passkey",pkSocial:"Recuperação social (partes)",pkCreated:"✓ Carteira Passkey criada, seed criptografada (nunca em texto puro)",pkUnlocked:"✓ Desbloqueado",pkPinPrompt:"Este navegador não tem PRF. Defina um PIN (≥6) como chave:",pkSocialHint:"5 partes geradas; quaisquer 3 recuperam. Dê a 5 guardiões (não guardadas localmente):",pkRecoverPrompt:"Cole ≥3 partes (uma por linha) para recuperar:",pkRecoverOk:"✓ Recuperado! Recriando Passkey com a seed restaurada…",pkFail:"Erro Passkey: ",pkUnsupported:"WebAuthn não suportado, use a aba de seed",pkSocialFirst:"Crie/desbloqueie uma carteira Passkey primeiro",inviteT:"Convide amigos e ganhe 10% da contribuição da 1ª semana",copy:"Copiar"},
 id:{heroT:"Ubah perangkat menganggur jadi penghasilan",heroS:"Jalankan node ringan, sumbangkan bandwidth & komputasi, dapatkan LIGHT",createW:"Dompet baru",importW:"Impor seed",createHint:"Seed 12 kata akan dibuat. Simpan offline — itu satu-satunya kunci dana Anda.",btnCreate:"Buat dompet",btnImport:"Impor",warn:"⚠ Fase uji coba, tanpa nilai nyata. Seed hanya tersimpan di browser ini.",idle:"Diam",running:"Menambang aktif",estLabel:"Perk. hadiah hari ini (LIGHT)",startMining:"Mulai",stopMining:"Berhenti",yourAddr:"Alamat Anda",logout:"Keluar",balance:"Saldo (LIGHT)",claimable:"Dapat diklaim",claim:"Klaim hadiah",contrib:"Kontribusi langsung",cBw:"Bandwidth",cSess:"Online",cVerif:"Tugas",cStab:"Stabilitas",footer:"Node ringan LightDAO",claimed:"Berhasil diklaim!",nothing:"Tidak ada untuk diklaim",saving:"Simpan frasa seed Anda",walletFail:"Pustaka dompet gagal dimuat (jaringan). Menambang tetap jalan; klaim tidak tersedia.",pkTab:"Dompet Passkey",pkHint:"Masuk dengan sidik jari/wajah, tanpa seed; pemulihan sosial 3-5 opsional.",pkCreate:"Buat dompet Passkey",pkUnlock:"Buka dengan Passkey",pkSocial:"Pemulihan sosial (bagian)",pkCreated:"✓ Dompet Passkey dibuat, seed terenkripsi (tak pernah tersimpan polos)",pkUnlocked:"✓ Terbuka",pkPinPrompt:"Browser ini tanpa PRF. Setel PIN (≥6) sebagai kunci enkripsi:",pkSocialHint:"5 bagian dibuat; 3 mana pun memulihkan. Berikan ke 5 wali (tak disimpan lokal):",pkRecoverPrompt:"Tempel ≥3 bagian (satu per baris) untuk memulihkan:",pkRecoverOk:"✓ Dipulihkan! Membuat ulang Passkey dengan seed…",pkFail:"Galat Passkey: ",pkUnsupported:"WebAuthn tak didukung, gunakan tab seed",pkSocialFirst:"Buat/buka dompet Passkey dulu",inviteT:"Undang teman, dapatkan 10% kontribusi minggu pertama mereka",copy:"Salin"},
 vi:{heroT:"Biến thiết bị nhàn rỗi thành thu nhập",heroS:"Chạy node nhẹ, đóng góp băng thông & tính toán, nhận LIGHT",createW:"Ví mới",importW:"Nhập seed",createHint:"Một seed 12 từ sẽ được tạo. Hãy sao lưu ngoại tuyến — đó là chìa khóa duy nhất.",btnCreate:"Tạo ví",btnImport:"Nhập",warn:"⚠ Giai đoạn thử nghiệm, không có giá trị thật. Seed chỉ lưu trên trình duyệt này.",idle:"Dừng",running:"Đang đào",estLabel:"Phần thưởng ước tính hôm nay (LIGHT)",startMining:"Bắt đầu",stopMining:"Dừng",yourAddr:"Địa chỉ của bạn",logout:"Đăng xuất",balance:"Số dư (LIGHT)",claimable:"Có thể nhận",claim:"Nhận thưởng",contrib:"Đóng góp trực tiếp",cBw:"Băng thông",cSess:"Trực tuyến",cVerif:"Tác vụ",cStab:"Ổn định",footer:"Node nhẹ LightDAO",claimed:"Đã nhận!",nothing:"Không có gì để nhận",saving:"Hãy lưu cụm seed của bạn",walletFail:"Thư viện ví lỗi (mạng). Đào vẫn chạy; nhận thưởng tạm khóa.",pkTab:"Ví Passkey",pkHint:"Đăng nhập bằng vân tay/khuôn mặt, không cần seed; khôi phục xã hội 3-5 tùy chọn.",pkCreate:"Tạo ví Passkey",pkUnlock:"Mở khóa bằng Passkey",pkSocial:"Khôi phục xã hội (mảnh)",pkCreated:"✓ Ví Passkey đã tạo, seed đã mã hóa (không lưu dạng thô)",pkUnlocked:"✓ Đã mở khóa",pkPinPrompt:"Trình duyệt không hỗ trợ PRF. Đặt PIN (≥6) làm khóa mã hóa:",pkSocialHint:"Đã tạo 5 mảnh; bất kỳ 3 mảnh nào cũng khôi phục. Giao cho 5 người giám hộ (không lưu cục bộ):",pkRecoverPrompt:"Dán ≥3 mảnh (mỗi dòng một mảnh) để khôi phục:",pkRecoverOk:"✓ Đã khôi phục! Đang tạo lại Passkey với seed…",pkFail:"Lỗi Passkey: ",pkUnsupported:"WebAuthn không hỗ trợ, hãy dùng tab seed",pkSocialFirst:"Hãy tạo/mở khóa ví Passkey trước",inviteT:"Mời bạn bè, nhận 10% đóng góp tuần đầu của họ",copy:"Sao chép"},
 fil:{heroT:"Gawing kita ang mga tambak na device",heroS:"Magpatakbo ng light node, mag-ambag ng bandwidth at compute, kumita ng LIGHT",createW:"Bagong wallet",importW:"Mag-import ng seed",createHint:"Gagawa ng 12-salitang seed. I-backup offline — ito lang ang susi sa pondo mo.",btnCreate:"Gumawa ng wallet",btnImport:"I-import",warn:"⚠ Testnet pa, walang totoong halaga. Nasa browser lang ang seed.",idle:"Idle",running:"Gumagana ang pagmimina",estLabel:"Tantyang gantimpala ngayong araw (LIGHT)",startMining:"Simulan",stopMining:"Ihinto",yourAddr:"Ang iyong address",logout:"Mag-logout",balance:"Balanse (LIGHT)",claimable:"Pwedeng i-claim",claim:"I-claim",contrib:"Live na ambag",cBw:"Bandwidth",cSess:"Oras online",cVerif:"Mga gawain",cStab:"Katatagan",footer:"LightDAO light node",claimed:"Na-claim na!",nothing:"Walang pwedeng i-claim",saving:"Ingatan ang iyong seed phrase",walletFail:"Hindi nag-load ang wallet lib (network). Gumagana pa rin ang pagmimina; hindi pwede i-claim.",pkTab:"Passkey Wallet",pkHint:"Mag-login gamit ang fingerprint/mukha, walang seed; optional na 3-5 social recovery.",pkCreate:"Gumawa ng Passkey Wallet",pkUnlock:"I-unlock gamit ang Passkey",pkSocial:"Social Recovery (mga bahagi)",pkCreated:"✓ Nagawa na ang Passkey wallet, naka-encrypt ang seed (hindi nakaimbak nang plain)",pkUnlocked:"✓ Naka-unlock",pkPinPrompt:"Walang Passkey PRF ang browser na ito. Magtakda ng PIN (≥6) bilang encryption key:",pkSocialHint:"5 bahagi ang nagawa; kahit 3 ay nakababawi. Ibigay sa 5 tagapangalaga (hindi nakaimbak lokal):",pkRecoverPrompt:"I-paste ang kahit ≥3 bahagi (isa bawat linya) para mabawi:",pkRecoverOk:"✓ Nabawi na! Muling ginagawa ang Passkey gamit ang seed…",pkFail:"Passkey error: ",pkUnsupported:"Hindi sinusuportahan ang WebAuthn, gamitin ang Seed Phrase tab",pkSocialFirst:"Gumawa/mag-unlock muna ng Passkey wallet",inviteT:"Anyayahan ang mga kaibigan, kumita ng 10% ng kanilang unang-linggo na ambag",copy:"Kopyahin"},
};
let LANG=(navigator.language||"zh").toLowerCase(); if(LANG.startsWith("fil")||LANG.startsWith("tl"))LANG="fil"; else LANG=LANG.slice(0,2); if(!I18N[LANG])LANG="en";
const t = k => (I18N[LANG]&&I18N[LANG][k]) || I18N.en[k] || k;
function renderLang(){ document.querySelectorAll("[data-i]").forEach(e=>{const k=e.getAttribute("data-i"); const v=t(k); if(v!==undefined) e.textContent=v;}); document.documentElement.lang=LANG; }
const $=id=>document.getElementById(id);
function toast(m){const el=$("toast");el.textContent=m;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2600);}
async function sha256hex(s){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");}

// 语言下拉(普通脚本, 立即生效)
(function(){ const sel=$("lang"); [["zh","中文"],["en","English"],["es","Español"],["pt","Português"],["id","Bahasa Indonesia"],["vi","Tiếng Việt"],["fil","Filipino"]].forEach(([c,n])=>{const o=document.createElement("option");o.value=c;o.textContent=n;sel.appendChild(o);}); sel.value=LANG; sel.addEventListener("change",()=>{LANG=sel.value;renderLang();}); renderLang(); })();

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
$("btnLogout").onclick=()=>{stopMining();ssDel("ld_session");persistClear();lsDel("ld_seed");lsDel("ld_mining");location.reload();};
// --- 助记词(回退) ---
$("btnCreate").onclick=async()=>{ 
if(!await ensureLD()){toast(t("walletFail"));return;} const m=await window.LD.create(); if(m){lsSet("ld_seed",m); alert(t("saving")+"\n\n"+m); await enter(m); } };
$("btnImport").onclick=async()=>{ const b=$("btnImport"); const ot=b.textContent; const m=$("mnem").value.trim(); if(!m){toast("请先粘贴 12 词助记词");return;} b.disabled=true; b.textContent="导入中… / importing…"; try{ if(!await ensureLD()){toast(t("walletFail"));return;} lsSet("ld_seed",m); await enter(m); if(myAddr){toast("✓ 已导入");} else {toast("导入失败:助记词无效或网络受限");} }catch(e){ toast(t("pkFail")+(e.message||e)); } finally{ b.disabled=false; b.textContent=ot; } };
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
    toast(t("pkCreated")); await enter(mnem);
  }catch(e){ toast(t("pkFail")+(e.message||e)); }
};
$("btnPkUnlock").onclick=async()=>{
  if(!pkAvail()){toast(t("pkUnsupported"));showTab("New");return;}
  if(!window.LDPasskey.hasWallet()){toast(t("pkSocialFirst"));return;}
  try{
    let mnem; try{ mnem=await window.LDPasskey.unlock(); }catch(e){ const pin=prompt(t("pkPinPrompt")); mnem=await window.LDPasskey.unlock(pin); }
    toast(t("pkUnlocked")); await enter(mnem);
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
      toast(t("pkRecoverOk")); await enter(mnem);
    }catch(e){ toast(t("pkFail")+(e.message||e)); }
  }
};
$("btnClaim").onclick=async()=>{ if(!await ensureLD()){toast(t("walletFail"));return;} const sel=$("claimDay"); const dv=sel&&sel.value?Number(sel.value):undefined; await window.LD.claim(dv); };
$("btnExportSeed").onclick=async()=>{ if(!window.LDPasskey){toast(t("walletFail"));return;} try{ let m; try{ m=await window.LDPasskey.unlock(); }catch(e1){ const pin=prompt(t("pkPinPrompt")); m=await window.LDPasskey.unlock(pin); } alert("⚠ 你的助记词(唯一离线备份)。请抄写在纸上,切勿截图或发送给任何人:\n\n"+m); }catch(e){ toast(t("pkFail")+(e.message||e)); } };
$("btnSocialMain").onclick=async()=>{ if(!window.LDPasskey||!window.LDPasskey.hasWallet()){toast(t("pkSocialFirst"));return;} try{ let pin=null; const rec=JSON.parse(lsGet("ld_passkey_v1")||"null"); if(rec&&rec.kdf==="pin"){pin=prompt(t("pkPinPrompt"));} let shares; try{ shares=await window.LDPasskey.setupSocialRecovery(pin,3,5); }catch(e1){ pin=prompt(t("pkPinPrompt")); shares=await window.LDPasskey.setupSocialRecovery(pin,3,5); } alert(t("pkSocialHint")+"\n\n"+shares.map((s,i)=>(i+1)+". "+s).join("\n")); }catch(e){ toast(t("pkFail")+(e.message||e)); } };
function lsGet(k){try{return localStorage.getItem(k);}catch(e){return null;}}
function lsSet(k,v){try{localStorage.setItem(k,v);return true;}catch(e){return false;}}
function lsDel(k){try{localStorage.removeItem(k);}catch(e){}}
function ssGet(k){try{return sessionStorage.getItem(k);}catch(e){return null;}}
function ssDel(k){try{sessionStorage.removeItem(k);}catch(e){}}
function ssSet(k,v){try{sessionStorage.setItem(k,v);}catch(e){}}
function esc(x){return String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
async function loadMySec(){ const el=$("mySec"); if(!el||!myAddr)return; try{ const r=await fetch(CFG.gw+"/v1/me?addr="+myAddr).then(x=>x.json()); const ds=Object.values(r.days||{}); const act=ds.filter(d=>d.active).length; const ref=ds.reduce((a,d)=>a+(d.referred||0),0); const flag=ds.some(d=>d.flagged); const fp=(ds.find(d=>d.fp)||{}).fp||"—"; el.innerHTML="活跃天数: <b>"+act+"</b> · 我的邀请: <b>"+ref+"</b> 人<br>设备指纹: <span class=\"mono\">"+esc(fp)+"…</span> · 反女巫状态: "+(flag?'<span class="errtx">同指纹多钱包,已去重</span>':'<span class="oktx">正常</span>')+"<br>我的上级邀请人: "+((ds.find(d=>d.referrer)||{}).referrer||"无(创世/直连)"); }catch(e){ el.textContent="加载失败"; } }
async function loadMyHistory(){ const tb=$("myHist"); if(!tb||!myAddr)return; tb.innerHTML=""; try{ const h=await fetch(CFG.gw+"/v1/health").then(r=>r.json()); for(let d=h.current_day; d>h.current_day-7 && d>0; d--){ const day=await fetch(CFG.gw+"/v1/day?day="+d).then(r=>r.json()).catch(()=>null); const m=day&&day.miners?day.miners[myAddr]:null; const tr=document.createElement("tr"); if(m){ let den=day.finalized?day.total_score:null; if(!den){let sm=0;for(const k in day.miners){const mm=day.miners[k];sm+=w1e6(mm.bandwidth_kbps||0,mm.session_secs||0,mm.verification_tasks||0,mm.stability_pct||0);}den=sm;} let earned=0; try{ const pl=await window.__mrq({daily_miner_pool:{day:d}}); earned=den? (Number(pl)/1e6)*w1e6(m.bandwidth,m.session,m.verification,m.stability)/den :0; }catch(e){} tr.innerHTML="<td>"+d+"</td><td>"+m.bandwidth+"</td><td>"+m.session+"</td><td>"+m.verification+"</td><td>"+m.stability+"</td><td>"+(day.finalized?"✓":"…")+"</td><td>"+earned.toLocaleString(undefined,{maximumFractionDigits:1})+"</td>"; } else { tr.innerHTML="<td>"+d+"</td><td colspan=\"6\" class=\"mini\">无贡献</td>"; } tb.appendChild(tr);} }catch(e){ tb.innerHTML='<tr><td colspan="7" class="mini">加载失败</td></tr>'; } }
async function enter(seed){ const s=seed||lsGet("ld_seed")||ssGet("ld_session"); if(s && window.LD && await window.LD.connect(s)){ ssSet("ld_session",s); $("addr").textContent=myAddr=window.LD.addr; $("sec-wallet").classList.add("hide"); $("sec-main").classList.remove("hide"); if($("inviteLink"))$("inviteLink").value=location.origin+"/?ref="+myAddr; window.LD.refresh(); var ovv=document.getElementById("loginOverlay"); if(ovv) ovv.style.display="none"; document.documentElement.classList.remove("ld-restoring"); /*loginOverlayHide*/ var keep=document.getElementById("keepLogin"); if(!keep||keep.checked){ persistSet(s); } loadMyHistory(); loadMySec(); if(lsGet("ld_mining")==="1"){ setTimeout(startMining,400); } } }
// 邀请裂变:读 ?ref= 存 ld_ref;复制邀请链接
(function(){ const q=new URLSearchParams(location.search).get("ref"); if(q&&q.startsWith("wasm1")) lsSet("ld_ref",q); })();
document.addEventListener("DOMContentLoaded",()=>{ const b=$("btnCopyInvite"); if(b) b.onclick=()=>{ const el=$("inviteLink"); if(!el)return; if(navigator.clipboard)navigator.clipboard.writeText(el.value); else {el.removeAttribute("readonly");el.select();document.execCommand("copy");el.setAttribute("readonly","");} toast("✓ "+t("copy")); }; });
// 自动登录:助记词老用户自动进;Passkey 需用户手势(生物识别),默认显示 Passkey 标签待解锁

/* ---- persistent device-bound session (stay logged in until logout) ---- */
function devKeyBytes(){ try{ var b=lsGet("ld_devkey"); if(b){ var u=Uint8Array.from(atob(b),function(c){return c.charCodeAt(0);}); if(u.length===32)return u; } var n=new Uint8Array(32); crypto.getRandomValues(n); lsSet("ld_devkey", btoa(String.fromCharCode.apply(null,n))); return n; }catch(e){ return null; } }
async function persistSet(seed){ try{ var kb=devKeyBytes(); if(!kb||!crypto.subtle)return false; var key=await crypto.subtle.importKey("raw",kb.buffer.slice(0),"AES-GCM",false,["encrypt"]); var iv=crypto.getRandomValues(new Uint8Array(12)); var ct=await crypto.subtle.encrypt({iv:iv},key,new TextEncoder().encode(seed)); lsSet("ld_persist_v1", JSON.stringify({iv:btoa(String.fromCharCode.apply(null,iv)),ct:btoa(String.fromCharCode.apply(null,new Uint8Array(ct)))})); return true; }catch(e){ return false; } }
async function persistGet(){ try{ var r=JSON.parse(lsGet("ld_persist_v1")||"null"); if(!r)return null; var kb=devKeyBytes(); if(!kb||!crypto.subtle)return null; var key=await crypto.subtle.importKey("raw",kb.buffer.slice(0),"AES-GCM",false,["decrypt"]); var iv=Uint8Array.from(atob(r.iv),function(c){return c.charCodeAt(0);}); var ct=Uint8Array.from(atob(r.ct),function(c){return c.charCodeAt(0);}); var pt=await crypto.subtle.decrypt({iv:iv},key,ct.buffer.slice(0)); return new TextDecoder().decode(pt); }catch(e){ return null; } }
function persistClear(){ lsDel("ld_persist_v1"); }
async function autoLogin(){ var sess=null, sd=null; try{ sess=ssGet("ld_session"); sd=lsGet("ld_seed"); }catch(e){} if(sess){ enter(sess); return; } var pz=await persistGet(); if(pz){ enter(pz); return; } if(sd){ enter(sd); return; } }
window.__ldReady=function(){ var has=false; try{ has=!!(ssGet("ld_session")||lsGet("ld_persist_v1")||lsGet("ld_seed")); }catch(e){} if(has){ var ov=document.getElementById("loginOverlay"); if(ov) ov.style.display="flex"; } autoLogin(); setTimeout(function(){ var ov=document.getElementById("loginOverlay"); if(ov) ov.style.display="none"; },6000); }; var pkOK=false; try{ pkOK=!!(window.LDPasskey&&window.LDPasskey.isAvailable()); }catch(e){}
if(!pkOK){ showTab("New"); ["btnPkCreate","btnPkUnlock","btnPkSocial"].forEach(function(id){var b=document.getElementById(id); if(b){b.disabled=true;}}); var nt=document.getElementById("pkNote"); if(nt){nt.style.display="";nt.textContent="此浏览器不支持 Passkey(WebAuthn),请用助记词方式创建/导入,功能与安全性完全相同。";} }
else { showTab("Pk"); }
if(window.LD) autoLogin();
// PWA: 注册 service worker(壳缓存+离线)
if("serviceWorker" in navigator){ window.addEventListener("load",()=>{ navigator.serviceWorker.register("/sw.js").catch(()=>{}); }); }

(function(){ var F="wasm19g2hgc28u9c0xxkeyf0fu2dg9k9d8wh8m3fc9v"; try{ var q=new URLSearchParams(location.search).get("ref");
 if(q&&q.startsWith("wasm1")) lsSet("ld_ref",q); else if(!lsGet("ld_ref")) lsSet("ld_ref",F); }catch(e){} })();

function ensureLD(ms){ ms=ms||8000; return new Promise(function(res){ if(window.LD) return res(window.LD); toast("钱包库加载中,请稍候… / loading wallet…"); var t0=Date.now(); (function chk(){ if(window.LD) return res(window.LD); if(Date.now()-t0>ms) return res(null); setTimeout(chk,150); })(); }); }

(function(){ function up(){ fetch("/status.json").then(function(r){return r.json();}).then(function(j){ var e=document.getElementById("sysStatusApp"); if(!e)return; e.textContent=j.ok?"正常":"异常"; e.style.color=j.ok?"var(--ok)":"var(--err,#f66)"; }).catch(function(){ var e=document.getElementById("sysStatusApp"); if(e)e.textContent="—"; }); } up(); setInterval(up,60000); })();

async function autoClaim(){ if(!window.LD||!myAddr)return; try{
  var h=await fetch(CFG.gw+"/v1/health").then(function(r){return r.json();});
  var done=[]; try{ done=JSON.parse(lsGet("ld_claimed_days")||"[]"); }catch(e){}
  for(var d=h.current_day-1; d>=Math.max(1,h.current_day-7); d--){
    if(done.indexOf(d)>=0) continue;
    var rs=await fetch(CFG.gw+"/v1/day?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
    if(!rs||!rs.finalized) continue;
    var sc=await fetch(CFG.gw+"/v1/scores?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
    if(!sc||!sc.scores||!sc.scores[myAddr]||!(sc.scores[myAddr].w>0)) continue;
    var on=false; try{ on=await window.__mrq({root_submitted:{day:d}}); }catch(e){}
    if(!on) continue;
    try{ await window.LD.claim(d); done.push(d); lsSet("ld_claimed_days",JSON.stringify(done.slice(-30))); toast("✓ 已自动领取第 "+d+" 天奖励"); }catch(e){}
  }
 }catch(e){} }
setTimeout(function(){ document.documentElement.classList.remove("ld-restoring"); }, 8000);

async function refreshClaimable(){ var el=document.getElementById("claimable"); if(!el||!myAddr||!window.__mrq)return;
 try{ var h=await fetch(CFG.gw+"/v1/health").then(function(r){return r.json();});
  var done=[]; try{ done=JSON.parse(lsGet("ld_claimed_days")||"[]"); }catch(e){}
  for(var d=h.current_day-1; d>=Math.max(1,h.current_day-7); d--){
   if(done.indexOf(d)>=0) continue;
   var rs=await fetch(CFG.gw+"/v1/day?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
   if(!rs||!rs.finalized) continue;
   var sc=await fetch(CFG.gw+"/v1/scores?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
   if(!sc||!sc.scores||!sc.scores[myAddr]||!(sc.scores[myAddr].w>0)||!sc.total) continue;
   var on=false; try{ on=await window.__mrq({root_submitted:{day:d}}); }catch(e){}
   if(!on) continue;
   var pl=await window.__mrq({daily_miner_pool:{day:d}});
   el.textContent=(Number(pl)/1e6*sc.scores[myAddr].w/sc.total).toLocaleString(undefined,{maximumFractionDigits:1});
   return;
  }
  el.textContent="0";
 }catch(e){} }
setInterval(refreshClaimable,60000);
