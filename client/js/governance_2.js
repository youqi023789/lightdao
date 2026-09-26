
const $=id=>document.getElementById(id);
const GOV="wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt";
const LT="wasm13c9t6xmar22xclseua6xevw4t4cnrampy6y5ajdydhyv5k0znrcsth555z";
const TM="wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u";
const DENOM="ulight";
function log(m,c){const e=$("log");if(!e)return;e.innerHTML=(c?`<span class="${c}">`:"")+String(m).replace(/</g,"&lt;")+(c?"</span>":"");e.scrollIntoView({block:"nearest"});}
let client=null,addr=null;
const VEN=p=>"/js/vendor/-cosmjs-"+p+"-0.32.4.js?v=2";
const CDNU=p=>"https://cdn.jsdelivr.net/npm/@cosmjs/"+p+"@0.32.4/+esm";
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
async function refreshBal(){
  try{
    const b=await client.getBalance(addr,DENOM); $("bal").textContent=(Number(b.amount)/1e6).toLocaleString(undefined,{maximumFractionDigits:2});
    const st=await client.queryContractSmart(GOV,{staked_balance:{address:addr}}); $("staked").textContent=(Number(st)/1e6).toLocaleString(undefined,{maximumFractionDigits:2});
    const cfg=await client.queryContractSmart(GOV,{config:{}}); $("minStake").textContent=(Number(cfg.proposal_min_stake)/1e6).toLocaleString();
  }catch(e){}
}
async function refreshProps(){
  try{
    const ps=await client.queryContractSmart(GOV,{active_proposals:{}});
    const el=$("props"); el.innerHTML="";
    if(!ps||!ps.length){el.innerHTML='<span class="mut">暂无进行中提案</span>';return;}
    ps.forEach(p=>{
      const tot=Number(p.yes_weight)+Number(p.no_weight)+Number(p.abstain_weight);
      const yp=tot?Math.round(Number(p.yes_weight)/tot*100):0, np=tot?Math.round(Number(p.no_weight)/tot*100):0, ap=tot?100-yp-np:0;
      const endLeft=Math.round((p.end-Date.now()/1000)/3600);
      const d=document.createElement("div"); d.className="prop";
      d.innerHTML=`<h3>#${p.id} ${esc(p.title)} <span class="mut">[${p.ptype}]</span></h3>
        <div class="mut" class="fs12">${esc(p.description).slice(0,120)}</div>
        <div class="bar"><i class="y" data-w="${yp}"></i><i class="n" data-w="${np}"></i><i class="a" data-w="${ap}"></i></div>
        <div class="mut" class="fs11">赞成 ${yp}%(${p.yes_addrs}人) · 反对 ${np}%(${p.no_addrs}人) · 弃权 ${ap}% · ${endLeft>0?endLeft+"h 后截止":"已截止"} ${p.executed?'· <span class="ok">已执行</span>':''}</div>
        <button class="btn sm" data-v="yes" data-id="${p.id}">赞成</button><button class="btn ghost sm" data-v="no" data-id="${p.id}">反对</button><button class="btn ghost sm" data-v="abstain" data-id="${p.id}">弃权</button><button class="btn ghost sm" data-e="1" data-id="${p.id}">执行</button>`;
      el.appendChild(d);
    });
    el.querySelectorAll("[data-v]").forEach(b=>b.onclick=()=>vote(b.dataset.id,b.dataset.v));
    el.querySelectorAll("[data-e]").forEach(b=>b.onclick=()=>exec(b.dataset.id));
  }catch(e){$("props").innerHTML='<span class="err">加载失败 '+e.message+'</span>';}
}
function esc(s){return String(s||"").replace(/[<>&]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));}
async function vote(id,opt){
  if(!client){log("先连接钱包","err");return;}
  log("投票 #"+id+" "+opt+"…");
  try{ const r=await client.execute(addr,GOV,{vote:{proposal_id:Number(id),option:opt,bet:"0"}},"auto"); log("✓ 已投票 "+r.transactionHash.slice(0,12),"ok"); await refreshProps(); }
  catch(e){ log("投票失败: "+(e.message||e).slice(0,120),"err"); }
}
async function exec(id){
  if(!client)return; log("执行 #"+id+"…");
  try{ const r=await client.execute(addr,GOV,{execute_proposal:{proposal_id:Number(id)}},"auto"); log("✓ 已执行 "+r.transactionHash.slice(0,12),"ok"); await refreshProps(); }
  catch(e){ log("执行失败(可能未通过): "+(e.message||e).slice(0,120),"err"); }
}
$("btnStake").onclick=async()=>{
  if(!client){log("先连接钱包","err");return;}
  const amt=Math.floor(Number($("stakeAmt").value||0)*1e6); if(amt<=0){log("输入数量","warn");return;}
  log("授权 light_token → governance…");
  try{
    await client.execute(addr,LT,{increase_allowance:{spender:GOV,amount:String(amt)}},"auto");
    log("质押…");
    const r=await client.execute(addr,GOV,{stake:{amount:String(amt)}},"auto");
    log("✓ 已质押 "+r.transactionHash.slice(0,12),"ok"); await refreshBal();
  }catch(e){log("质押失败: "+(e.message||e).slice(0,140),"err");}
};
$("btnUnstake").onclick=async()=>{
  if(!client)return; const amt=Math.floor(Number($("stakeAmt").value||0)*1e6); if(amt<=0){log("输入数量","warn");return;}
  try{ const r=await client.execute(addr,GOV,{unstake:{amount:String(amt)}},"auto"); log("✓ 已赎回 "+r.transactionHash.slice(0,12),"ok"); await refreshBal(); }
  catch(e){log("赎回失败: "+(e.message||e).slice(0,120),"err");}
};
$("btnPropose").onclick=async()=>{
  if(!client){log("先连接钱包","err");return;}
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
  try{ const b=await client.getBalance(TM,DENOM); const sg=await client.queryContractSmart(TM,{signers:{}}).catch(()=>null);
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
    if(!seed){ try{ seed=localStorage.getItem("ld_seed"); }catch(e){} }
    if(!seed){ try{
      var rec=JSON.parse(localStorage.getItem("ld_persist_v1")||"null");
      if(rec){ var kb=localStorage.getItem("ld_devkey"); if(kb){ var key=await crypto.subtle.importKey("raw",Uint8Array.from(atob(kb),c=>c.charCodeAt(0)).buffer.slice(0),"AES-GCM",false,["decrypt"]);
        var iv=Uint8Array.from(atob(rec.iv),c=>c.charCodeAt(0)); var ct=Uint8Array.from(atob(rec.ct),c=>c.charCodeAt(0));
        var pt=await crypto.subtle.decrypt({iv:iv},key,ct.buffer.slice(0)); seed=new TextDecoder().decode(pt); } }
    }catch(e){} }
    if(seed){ var ok=await connect(seed); if(ok){ var el=$("addrLine"); if(el) el.textContent="已连接(沿用主客户端登录): "+addr; } }
  }catch(e){}
})();
