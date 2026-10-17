
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
    /* LD-GOV-STATE-CLASSIFY-20261016 active_proposals 会连同已作废/已过期的提案一起返回（链上实测
       proposal_state: voided=true, expired=true），旧代码把它们一律显示成"进行中"，
       还给了可点击的投票/执行按钮。这里逐个查状态后分组显示：不隐藏任何提案，
       只如实标注，并禁用已结束提案的按钮。 */
    const ps0=await (client||ro).queryContractSmart(GOV,{active_proposals:{}});
    const el=$("props"); el.innerHTML="";
    if(!ps0||!ps0.length){el.innerHTML='<span class="mut">'+gl("暂无进行中提案")+'</span>';return;}
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
      d.innerHTML=`<h3>#${p.id} ${esc(p.title)} <span class="mut">[${p.ptype}]</span>${off?' <span class="err">'+gl("已作废/已过期")+'</span>':(ended?' <span class="err">'+gl("已结束")+'</span>':"")}</h3>
        <div class="mut" class="fs12">${esc(p.description).slice(0,120)}</div>
        <div class="bar"><i class="y" data-w="${yp}"></i><i class="n" data-w="${np}"></i><i class="a" data-w="${ap}"></i></div>
        <div class="mut" class="fs11">${govTally(yp, np, ap, p.yes_addrs, p.no_addrs, endLeft > 0 ? gl("{h} 小时后截止", {h: endLeft}) : gl("已截止"))}</div>
        <button class="btn sm" data-v="yes" data-id="${p.id}"${dis}>${gl("赞成")}</button><button class="btn ghost sm" data-v="no" data-id="${p.id}"${dis}>${gl("反对")}</button><button class="btn ghost sm" data-v="abstain" data-id="${p.id}"${dis}>${gl("弃权")}</button><button class="btn ghost sm" data-e="1" data-id="${p.id}"${dis}>${gl("执行")}</button>`;
      if(off){ d.style.opacity=".55"; }
      el.appendChild(d);
    }
    if(!ps.length){ el.innerHTML='<span class="mut">'+gl("暂无可投票的进行中提案")+'</span>'; }
    ps.forEach(p=>renderCard(p,false));
    if(dead.length){
      const tip=document.createElement("p"); tip.className="mut"; tip.style.marginTop="10px";
      tip.textContent = gl("{n} 个提案已作废或已过期，不计入进行中，也不可再操作", {n: dead.length});
      el.appendChild(tip);
      dead.forEach(x=>renderCard(x.p,true));
    }
    el.querySelectorAll("[data-v]").forEach(b=>b.onclick=()=>vote(b.dataset.id,b.dataset.v));
    el.querySelectorAll("[data-e]").forEach(b=>b.onclick=()=>exec(b.dataset.id));
  }catch(e){$("props").innerHTML='<span class="err">加载失败 '+e.message+'</span>';}
}
  /* LD-GOV-L10N-20261017 v2 运行时文案统一从全站词典取词，本网件不再自带翻译表。
     上一版在这里内置了一张只覆盖 zh/es/pt/id/vi 的表，等于"第二份译文事实源"：
     同一句话在两处各译一遍必然漂移——实测 de/ar/ja 下页面其余部分已本地化、按钮仍是英文。
     现在：中文键 → window.__ldT（i18n.js 暴露，词表在 /js/i18n_gov_labels.js，
     与 DOM 遍历共用同一份 LDI18N 与同一套英文/中文回退）。缺词由 __ldT 记进 __ldTgaps
     并被真机渲染巡检抓到，不再静默把中文丢给外国用户。 */
  function gl(zh, vars) {
    if (typeof window.__ldT === "function") return window.__ldT(zh, vars);
    /* i18n.js 尚未加载（只可能是脚本顺序问题）：诚实回落中文原串并记下缺口 */
    window.__ldTgaps = window.__ldTgaps || {};
    window.__ldTgaps["noload|" + zh] = 1;
    var out = zh;
    if (vars) { for (var v in vars) { out = out.split("{" + v + "}").join(String(vars[v])); } }
    return out;
  }
  function govTally(yp, np, ap, ya, na, tail) {
    return gl("赞成 {y}%（{ya} 人） · 反对 {n}%（{na} 人） · 弃权 {a}% · {tail}",
              { y: yp, n: np, a: ap, ya: ya, na: na, tail: tail });
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
