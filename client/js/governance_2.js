
const $=id=>document.getElementById(id);
/* SEC-LOCK step-up gate: false => user failed/cancelled verification => abort. */
async function ldGate(label){ if(!window.LDStepUp)return true; try{ return !!(await window.LDStepUp(label)); }catch(e){ return false; } }
function ldGateFail(){ log("已取消:未通过安全验证 / Cancelled: security check not passed","warn"); }
const GOV="wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt";
const LT="wasm13c9t6xmar22xclseua6xevw4t4cnrampy6y5ajdydhyv5k0znrcsth555z";
const TM="wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u";
const DENOM="ulight";
/* 1.2.0 native-stake flag - see docs/PROPOSAL_GOV_MIGRATION.md. Keep false until the
   governance x/gov migration (~2026-10-05) executes; then flip to true + bump version. */
const STAKE_NATIVE=false;
function log(m,c){const e=$("log");if(!e)return;e.innerHTML=(c?`<span class="${c}">`:"")+String(m).replace(/</g,"&lt;")+(c?"</span>":"");e.scrollIntoView({block:"nearest"});}
let client=null,addr=null,ro=null;   /* ro = 只读客户端，未连钱包也能查链上 */
const VEN=p=>"/js/vendor/-cosmjs-"+p+"-0.32.4.js?v=2";
const CDNU=p=>"/js/vendor/-cosmjs-"+p+"-0.32.4.js?v=2";
async function loadCosmjs(){if(window.__c)return window.__c;
 for(const src of [VEN,CDNU]){ try{ const [cs,ps,sg]=await Promise.all([import(src("cosmwasm-stargate")),import(src("proto-signing")),import(src("stargate"))]); window.__c={cs,ps,sg}; return window.__c; }catch(e){} }
 return null;}
async function connect(mnem){
  const c=await loadCosmjs(); if(!c){log("cosmjs 加载失败(网络)","err");return false;}
  const{SigningCosmWasmClient}=c.cs,{DirectSecp256k1HdWallet}=c.ps,{GasPrice}=c.sg;
  try{
    const w=await DirectSecp256k1HdWallet.fromMnemonic(mnem,{prefix:"wasm"});
    const[a]=await w.getAccounts(); addr=a.address;
    client=await SigningCosmWasmClient.connectWithSigner(location.origin+"/rpc/",w,{gasPrice:GasPrice.fromString("0.25"+DENOM)});
    $("addrLine").textContent="已连接: "+addr;
    await refreshBal(); await refreshProps(); await refreshTreas();
    return true;
  }catch(e){log("连接失败: "+e.message,"err");return false;}
}
/* LD-GOV-READONLY-BOOT-20261016 首屏用只读客户端加载公开治理信息；连钱包后才启用签名能力。
   之前 refreshProps 只在 connect() 里调用，未连钱包的访客永远停在"加载中…"。 */
async function initReadOnly(){
  const el=document.getElementById("props");
  try{
    const c=await loadCosmjs();
    if(!c){ if(el) el.innerHTML='<span class="err">链上查询组件加载失败（网络受限），提案列表暂不可读</span>'; return; }
    ro=await c.cs.CosmWasmClient.connect(location.origin+"/rpc/");
    await refreshProps();
    try{ await refreshTreas(); }catch(e){}
  }catch(e){
    if(el) el.innerHTML='<span class="err">读取链上提案失败：'+String((e&&e.message)||e).slice(0,80)+'</span>';
  }
}
if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",initReadOnly);
else initReadOnly();

async function refreshBal(){
  try{
    const b=await client.getBalance(addr,DENOM); $("bal").textContent=(Number(b.amount)/1e6).toLocaleString(undefined,{maximumFractionDigits:2});
    const st=await (client||ro).queryContractSmart(GOV,{staked_balance:{address:addr}}); $("staked").textContent=(Number(st)/1e6).toLocaleString(undefined,{maximumFractionDigits:2});
    const cfg=await (client||ro).queryContractSmart(GOV,{config:{}}); $("minStake").textContent=(Number(cfg.proposal_min_stake)/1e6).toLocaleString();
  }catch(e){}
}
async function refreshProps(){
  try{
    /* LD-GOV-STATE-CLASSIFY-20261016 active_proposals 会连同"${GOVL.voided}"的提案一起返回（链上实测
       proposal_state: voided=true, expired=true），旧代码把它们一律显示成"进行中"，
       还给了可点击的投票/执行按钮。这里逐个查状态后分组显示：不隐藏任何提案，
       只如实标注，并禁用已结束提案的按钮。 */
    const ps0=await (client||ro).queryContractSmart(GOV,{active_proposals:{}});
    const el=$("props"); el.innerHTML="";
    if(!ps0||!ps0.length){el.innerHTML='<span class="mut">暂无进行中提案</span>';return;}
    const st=await Promise.all(ps0.map(p=>(client||ro).queryContractSmart(GOV,{proposal_state:{id:p.id}})
      .catch(function(){return null;})));
    const ps=[], dead=[];
    ps0.forEach(function(p,i){
      var s=st[i];
      /* 查不到状态时保守当作进行中，绝不因为查询失败就把提案藏掉 */
      if(s && (s.voided || s.expired || s.executed)) dead.push({p:p,s:s});
      else ps.push(p);
    });
    function renderCard(p,off){
      const tot=Number(p.yes_weight)+Number(p.no_weight)+Number(p.abstain_weight);
      const yp=tot?Math.round(Number(p.yes_weight)/tot*100):0, np=tot?Math.round(Number(p.no_weight)/tot*100):0, ap=tot?100-yp-np:0;
      const endLeft=Math.round((p.end-Date.now()/1000)/3600);
      const ended=(Number(p.end)*1000)<=Date.now();
      const dis=(ended||off)?" disabled":"";
      const d=document.createElement("div"); d.className="prop";
      d.innerHTML=`<h3>#${p.id} ${esc(p.title)} <span class="mut">[${p.ptype}]</span>${off?' <span class="err">已作废/已过期</span>':(ended?' <span class="err">已结束</span>':"")}</h3>
        <div class="mut" class="fs12">${esc(p.description).slice(0,120)}</div>
        <div class="bar"><i class="y" data-w="${yp}"></i><i class="n" data-w="${np}"></i><i class="a" data-w="${ap}"></i></div>
        <div class="mut" class="fs11">${govTally(yp, np, ap, p.yes_addrs, p.no_addrs, endLeft > 0 ? endLeft + GOVL.dueIn : GOVL.closed)}</div>
        <button class="btn sm" data-v="yes" data-id="${p.id}"${dis}>${GOVL.yes}</button><button class="btn ghost sm" data-v="no" data-id="${p.id}"${dis}>${GOVL.no}</button><button class="btn ghost sm" data-v="abstain" data-id="${p.id}"${dis}>${GOVL.abstain}</button><button class="btn ghost sm" data-e="1" data-id="${p.id}"${dis}>${GOVL.exec}</button>`;
      if(off){ d.style.opacity=".55"; }
      el.appendChild(d);
    }
    if(!ps.length){ el.innerHTML='<span class="mut">暂无可投票的进行中提案</span>'; }
    ps.forEach(p=>renderCard(p,false));
    if(dead.length){
      const tip=document.createElement("p"); tip.className="mut"; tip.style.marginTop="10px";
      tip.textContent = GOVL.tip(dead.length);
      el.appendChild(tip);
      dead.forEach(x=>renderCard(x.p,true));
    }
    el.querySelectorAll("[data-v]").forEach(b=>b.onclick=()=>vote(b.dataset.id,b.dataset.v));
    el.querySelectorAll("[data-e]").forEach(b=>b.onclick=()=>exec(b.dataset.id));
  }catch(e){$("props").innerHTML='<span class="err">加载失败 '+e.message+'</span>';}
}
/* LD-GOV-L10N-20261017 运行时文案标签表：这些句子是 JS 拼出来的（票数/百分比/剩余小时每次都变），
     词典按整句精确匹配命中不了，只能在这里本地化。语种只认真正有译值的
     zh/es/pt/id/vi，其余英文兜底（与站内 ?lang 兜底策略一致）。 */
  var GOVL = (function () {
    var l = "";
    try { l = (new URLSearchParams(location.search).get("lang") || "").toLowerCase(); } catch (e) { }
    if (!l) { try { l = (localStorage.getItem("ld_lang") || "").toLowerCase(); } catch (e) { l = ""; } }
    if (!l) { l = (document.documentElement.lang || "").toLowerCase(); }
    if (!l) { l = String(navigator.language || "").toLowerCase(); }
    l = l.slice(0, 2);
    var M = {
      zh: { yes: "赞成", no: "反对", abstain: "弃权", exec: "执行", unit: "人",
            dueIn: "h 后截止", closed: "已截止", voided: "已作废/已过期",
            tip: function (n) { return "以下 " + n + " 个提案已作废或已过期，不计入进行中，也不可再操作："; } },
      es: { yes: "A favor", no: "En contra", abstain: "Abstención", exec: "Ejecutar", unit: "dir.",
            dueIn: " h para cerrar", closed: "Cerrado", voided: "Anulada/vencida",
            tip: function (n) { return n + " propuestas anuladas o vencidas: no cuentan como activas ni admiten acciones."; } },
      pt: { yes: "A favor", no: "Contra", abstain: "Abstenção", exec: "Executar", unit: "pess.",
            dueIn: " h para encerrar", closed: "Encerrado", voided: "Anulada/vencida",
            tip: function (n) { return n + " propostas anuladas ou vencidas: não contam como ativas nem aceitam ações."; } },
      id: { yes: "Setuju", no: "Tolak", abstain: "Abstain", exec: "Jalankan", unit: "orang",
            dueIn: " jam lagi", closed: "Ditutup", voided: "Batal/kedaluwarsa",
            tip: function (n) { return n + " usulan dibatalkan/kedaluwarsa: tidak dihitung aktif, tidak bisa dijalankan."; } },
      vi: { yes: "Đồng ý", no: "Phản đối", abstain: "Bỏ phiếu trắng", exec: "Thực thi", unit: "người",
            dueIn: " giờ nữa", closed: "Đã đóng", voided: "Hủy/hết hạn",
            tip: function (n) { return n + " đề xuất đã hủy/hết hạn: không tính là đang mở, không thao tác được."; } },
      en: { yes: "Yes", no: "No", abstain: "Abstain", exec: "Execute", unit: "voters",
            dueIn: "h left", closed: "Closed", voided: "Voided/expired",
            tip: function (n) { return n + " proposals voided or expired — not counted as active, actions disabled."; } },
    };
    var t = M[l] || M.en;
    t._lang = (M[l] ? l : "en");
    return t;
  })();
  function govTally(yp, np, ap, ya, na, tail) {
    if (GOVL._lang === "zh") {
      return "赞成 " + yp + "%(" + ya + "人) · 反对 " + np + "%(" + na + "人) · 弃权 " + ap + "% · " + tail;
    }
    return GOVL.yes + " " + yp + "% (" + ya + " " + GOVL.unit + ") · " + GOVL.no + " " + np
      + "% (" + na + ") · " + GOVL.abstain + " " + ap + "% · " + tail;
  }
  function esc(s){return String(s||"").replace(/[<>&]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));}
async function vote(id,opt){
  if(!client){log("先连接钱包","err");return;}
  try{ const sb=await (client||ro).queryContractSmart(GOV,{staked_balance:{address:addr}});
    if(!Number((sb&&sb.amount)||0)){ log("投票需先质押 LIGHT(治理权重=质押额)。质押通道维护中,迁移完成后即可质押并投票。","warn"); return; } }
  catch(e){ log("查询质押额失败: "+(e.message||e).slice(0,80),"err"); return; }
  if(!await ldGate("治理投票 #"+id+" / Governance vote")){ldGateFail();return;}
  log("投票 #"+id+" "+opt+"…");
  try{ const r=await client.execute(addr,GOV,{vote:{proposal_id:Number(id),option:opt,bet:"0"}},"auto"); log("✓ 已投票 "+r.transactionHash.slice(0,12),"ok"); await refreshProps(); }
  catch(e){ log("投票失败: "+(e.message||e).slice(0,120),"err"); }
}
async function exec(id){
  if(!client)return;
  if(!await ldGate("执行提案 #"+id+" / Execute proposal")){ldGateFail();return;}
  log("执行 #"+id+"…");
  try{ const r=await client.execute(addr,GOV,{execute_proposal:{proposal_id:Number(id)}},"auto"); log("✓ 已执行 "+r.transactionHash.slice(0,12),"ok"); await refreshProps(); }
  catch(e){ log("执行失败(可能未通过): "+(e.message||e).slice(0,120),"err"); }
}
/* 1.2.0 native-funds staking (docs/PROPOSAL_GOV_MIGRATION.md). While STAKE_NATIVE=false
   the maintenance notice below is kept verbatim (identical to current live behavior).
   After the governance x/gov migration (~2026-10-05), flip STAKE_NATIVE=true + bump the
   version: stake then attaches native LIGHT as msg funds; the light_token CW20
   allowance step is removed. This flag flip + version bump is the ONLY web change. */
$("btnStake").onclick=async()=>{
  if(!client){log("先连接钱包","err");return;}
  if(!STAKE_NATIVE){
    log("质押通道维护中:链上治理合约(旧CW20质押)与代币合约版本不兼容,需一次合约迁移(改为原生质押,已排期治理提案)。迁移完成前质押不可用,不影响挖矿/领取/委托。","warn");
    return;
  }
  const amt=Math.floor(Number($("stakeAmt").value||0)*1e6); if(amt<=0){log("输入数量","warn");return;}
  if(!await ldGate("质押 / Stake")){ldGateFail();return;}
  log("质押(原生 LIGHT 随消息附带)…");
  try{
    const r=await client.execute(addr,GOV,{stake:{amount:String(amt)}},"auto","",[{denom:DENOM,amount:String(amt)}]);
    log("✓ 已质押 "+r.transactionHash.slice(0,12),"ok"); await refreshBal();
  }catch(e){log("质押失败: "+(e.message||e).slice(0,140),"err");}
};
/* native unstake (contract returns native LIGHT post-migration); message shape unchanged. */
$("btnUnstake").onclick=async()=>{
  if(!client)return; const amt=Math.floor(Number($("stakeAmt").value||0)*1e6); if(amt<=0){log("输入数量","warn");return;}
  if(!await ldGate("赎回质押 / Unstake")){ldGateFail();return;}
  try{ const r=await client.execute(addr,GOV,{unstake:{amount:String(amt)}},"auto"); log("✓ 已赎回 "+r.transactionHash.slice(0,12),"ok"); await refreshBal(); }
  catch(e){log("赎回失败: "+(e.message||e).slice(0,120),"err");}
};
$("btnPropose").onclick=async()=>{
  if(!client){log("先连接钱包","err");return;}
  if(!await ldGate("发起提案 / Create proposal")){ldGateFail();return;}
  const kind=$("pkind").value;
  const msg={create_proposal:{ptype:$("ptype").value,title:$("ptitle").value,description:$("pdesc").value,
    symbol:kind==="investment"?$("psym").value:null, investment_usd:kind==="investment"?String(Math.floor(Number($("pinv").value||0)*1e6)):null,
    target:kind==="general"&&$("ptarget").value?$("ptarget").value:null,
    call_msg:kind==="general"&&$("pcall").value?$("pcall").value:null,
    migrate_code_id:kind==="general"&&$("pmig").value?Number($("pmig").value):null}};
  log("提交提案…");
  try{ const r=await client.execute(addr,GOV,msg,"auto"); log("✓ 提案已提交 "+r.transactionHash.slice(0,12),"ok"); await refreshProps(); }
  catch(e){ log("提交失败(需质押≥门槛): "+(e.message||e).slice(0,140),"err"); }
};
$("pkind").onchange=()=>{const inv=$("pkind").value==="investment";$("kinv").style.display=inv?"":"none";$("kgen").style.display=inv?"none":"";};
async function refreshTreas(){
  try{ const b=await client.getBalance(TM,DENOM); const sg=await (client||ro).queryContractSmart(TM,{signers:{}}).catch(()=>null);
    $("treasLine").textContent="金库余额: "+(Number(b.amount)/1e6).toLocaleString(undefined,{maximumFractionDigits:2})+" LIGHT"+(sg?" · 签名人: "+JSON.stringify(sg).slice(0,80):""); }catch(e){$("treasLine").textContent="查询失败";}
}
$("btnTreas").onclick=refreshTreas;
$("btnRefresh").onclick=refreshProps;
$("btnPk").onclick=async()=>{ if(!window.LDPasskey||!LDPasskey.hasWallet()){log("无 Passkey 钱包,先用主客户端创建","warn");return;} let m; try{m=await LDPasskey.unlock();}catch(e){const p=prompt("PIN:");m=await LDPasskey.unlock(p);} await connect(m); };
$("btnMnem").onclick=()=>{const i=$("mnem");i.style.display=i.style.display==="none"?"":"none";if(i.style.display!=="none"){i.onchange=async()=>{if(i.value.trim())await connect(i.value.trim());};}};

/* ---- shared-session SSO: reuse login from app (same origin) ---- */
(async function ssAutoConnect(){
  try{
    var seed=null;
    try{ seed=sessionStorage.getItem("ld_session"); }catch(e){}
    /* SEC-LOCK: a fresh tab was never verified, so require an unlock before the wallet
       is reused. The legacy plaintext ld_seed and the device-key blob ld_persist_v1 are
       deliberately NOT read here: reading them would bypass the lock, and deleting
       ld_seed here could destroy a user's only copy before app.html has migrated them
       (app.html shows the seed, forces a password, then removes both). */
    if(!seed && window.LDLock && window.LDLock.hasLock()){
      var okL=await window.LDLock.showUnlock();
      if(okL){ seed=window.LDLock.currentSeed(); }
    }
    if(seed){ var ok=await connect(seed); if(ok){ var el=$("addrLine"); if(el) el.textContent="已连接(沿用主客户端登录): "+addr; } }
  }catch(e){}
})();
