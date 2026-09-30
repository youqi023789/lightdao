window.LDBUILD="1.1.9";
function terr(e){ return "[" + window.LDBUILD + "] " + String(e.message||e).slice(0,300); }

const CDN = ["/js/vendor/"];
async function loadCosmjs(){
  if(window.__c) return window.__c;
  const L=p=>"/js/vendor/-cosmjs-"+p+"-0.32.4.js?v=2";
  const C=p=>"/js/vendor/-cosmjs-"+p+"-0.32.4.js?v=2";
  for(const src of [L,C]){
    try{
      const [cs,ps,sg]=await Promise.all([import(src("cosmwasm-stargate")),import(src("proto-signing")),import(src("stargate"))]);
      window.__c={cs,ps,sg}; return window.__c;
    }catch(e){}
  }
  return null;
}
function contractDay(){ return Math.floor((Date.now()/1000-1789102088)/86400); }
const PAYMASTER="wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj";
window.LD = null;
(async()=>{
  const c = await loadCosmjs();
  if(!c){ return; }
  const { SigningCosmWasmClient } = c.cs;
  const { DirectSecp256k1HdWallet } = c.ps;
  const { GasPrice } = c.sg;
  let wallet=null, client=null;
function pf(client, RPC){ try{ if(typeof client.getValidators!=="function") client.getValidators=async function(){ var r=await fetch(RPC+"validators?per_page=100").then(function(x){return x.json();}); return (r.result.validators||[]).map(function(v){ return {description:{moniker:(v.description&&v.description.moniker)||"?"}, status:"BOND_STATUS_BONDED", tokens:String((Number(v.voting_power)||0)*1000000), commission:{commissionRates:{rate:(v.commission&&v.commission.rate)||"0"}}, validatorAddress:v.address}; }); }; if(typeof client.getSupply!=="function") client.getSupply=async function(){ return [{denom:"ulight",amount:"2500000000000000"}]; }; if(typeof client.getDelegation!=="function") client.getDelegation=async function(a,v){ var r=await fetch(RPC+"abci_query?path=%22/custom/staking/delegation/%22").catch(function(){return null;}); return null; }; }catch(e){} return client; }
window.__mrq=(m)=>client.queryContractSmart(CFG.miningReward,m);
  window.LD = {
    addr:null,
    async create(){ const w=await DirectSecp256k1HdWallet.generate(12,{prefix:CFG.prefix}); this._w=w; return w.mnemonic; },
    async connect(seed){ try{ wallet=await DirectSecp256k1HdWallet.fromMnemonic(seed,{prefix:CFG.prefix}); const [a]=await wallet.getAccounts(); this.addr=a.address; client=pf(await SigningCosmWasmClient.connectWithSigner(CFG.rpc,wallet,{gasPrice:GasPrice.fromString("0.2"+CFG.denom)}),CFG.rpc); return true; }catch(e){ return false; } },
    async refresh(){ try{ const b=await client.getBalance(this.addr,CFG.denom); document.getElementById("bal").textContent=(Number(b.amount)/1e6).toLocaleString(undefined,{maximumFractionDigits:2}); }catch(e){} },

    async claimStaking(){ try{
      const vals=await client.getValidators();
      const msgs=[];
      for(const v of vals){ try{ let dg=null; try{ dg=await client.getDelegation(this.addr,v.validatorAddress); }catch(e){ dg=null; } if(dg&&dg.amount&&Number(dg.amount.amount)>0){ msgs.push({typeUrl:"/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward",value:{delegatorAddress:this.addr,validatorAddress:v.validatorAddress}}); } }catch(e){} }
      if(!msgs.length) return null;
      const res=await ldBroadcast(msgs,"auto",null); /* withdraw-rewards = claim: frictionless, no step-up */
      return res.transactionHash;
    }catch(e){ throw e; } },
    async claim(day){ try{ const h=await (await fetch(CFG.gw+"/v1/health")).json(); const d= day|| (h.current_day-1); if(d>=contractDay()){ throw new Error("第 "+d+" 天将于合约日界(每日 04:48 UTC / 北京 12:48)后开放领取,请稍后再试 / opens after 04:48 UTC"); }
      const p=await fetch(CFG.gw+"/v1/proof?day="+d+"&miner="+this.addr).then(r=>r.ok?r.json():null);
      if(!p){ toast(t("nothing")); return; }
      const msg={claim:{day:d,proof:p.proof,score:{bandwidth:String(p.score.bandwidth),session:String(p.score.session),verification:String(p.score.verification),stability:String(p.score.stability)}}};
      let res; const FEE=[["75000","300000"],["200000","400000"],["400000","400000"]]; let lastE=null; for(const [fa,ga] of FEE){ try{ res=await client.execute(this.addr,CFG.miningReward,msg,{amount:[{denom:CFG.denom,amount:fa}],gas:ga,granter:PAYMASTER}); lastE=null; break; }catch(e){ lastE=e; var em=String(e.message||e); if(em.indexOf("code 13")>=0) continue; if(em.indexOf("code 38")>=0){ try{ res=await client.execute(this.addr,CFG.miningReward,msg,"auto"); lastE=null; break; }catch(e2){ lastE=e2; continue; } } break; } } if(lastE) throw lastE;
      toast(t("claimed")+" "+res.transactionHash.slice(0,10)+"…"); this.refresh();
    }catch(e){ toast(terr(e)); } },
  };
/* ---- SEC-LOCK: step-up gated signing paths --------------------------------
   Every value-moving signature (bank send, delegate/undelegate, sub-token
   exchange, generic contract execute) must pass window.LDStepUp first.
   Reward claims (claim / claimStaking) pass gateLabel=null and stay
   frictionless by design - they only credit the user.                          */
async function ldStepUpOk(label){ if(!window.LDStepUp)return true; try{ return !!(await window.LDStepUp(label)); }catch(e){ return false; } }
async function ldBroadcast(msgs,fee,gateLabel){ if(gateLabel){ const okG=await ldStepUpOk(gateLabel); if(!okG){ throw new Error("step-up-cancelled"); } } return client.signAndBroadcast(window.LD.addr,msgs,fee||"auto"); }
async function ldExecute(contract,msg,fee,gateLabel){ if(gateLabel){ const okG=await ldStepUpOk(gateLabel); if(!okG){ throw new Error("step-up-cancelled"); } } return client.execute(window.LD.addr,contract,msg,fee||"auto"); }
window.LD.signGated=async function(msgs,label,fee){ return ldBroadcast(msgs,fee,label||"敏感操作签名 / Sensitive signing"); };
window.LD.executeGated=async function(contract,msg,label,fee){ return ldExecute(contract,msg,fee,label||"合约执行 / Contract execute"); };
window.LD.sendTokens=async function(to,amountUl,label){ return ldBroadcast([{typeUrl:"/cosmos.bank.v1beta1.MsgSend",value:{fromAddress:window.LD.addr,toAddress:to,amount:[{denom:CFG.denom,amount:String(amountUl)}]}}],"auto",label||"转账 / Send tokens"); };
window.LD.delegate=async function(validator,amountUl,label){ return ldBroadcast([{typeUrl:"/cosmos.staking.v1beta1.MsgDelegate",value:{delegatorAddress:window.LD.addr,validatorAddress:validator,amount:{denom:CFG.denom,amount:String(amountUl)}}}],"auto",label||"委托 / Delegate"); };
window.LD.undelegate=async function(validator,amountUl,label){ return ldBroadcast([{typeUrl:"/cosmos.staking.v1beta1.MsgUndelegate",value:{delegatorAddress:window.LD.addr,validatorAddress:validator,amount:{denom:CFG.denom,amount:String(amountUl)}}}],"auto",label||"撤委托 / Undelegate"); };
window.LD.exchangeSubToken=async function(exchangeContract,symbol,amountUl,label){ return ldExecute(exchangeContract,{exchange:{symbol:String(symbol),amount_in:String(amountUl)}},"auto",label||"子代币兑换 / Sub-token exchange"); };
if(window.__ldReady)window.__ldReady();
})();
document.getElementById("themeT").onclick=function(){var c=document.documentElement.getAttribute("data-theme");var n=c==="light"?"dark":"light";document.documentElement.setAttribute("data-theme",n);try{lsSet("ld_theme",n);}catch(e){}this.textContent=n==="light"?"◑":"◐";};
(function(){ const b=$("pwaBadge"); if(!b)return; const stand=matchMedia("(display-mode: standalone)").matches||navigator.standalone; if(stand){ b.style.display=""; } else { window.addEventListener("beforeinstallprompt",function(e){ e.preventDefault(); b.style.display=""; b.textContent="📲 安装 PWA · 离线可用/心跳更稳"; b.style.cursor="pointer"; b.onclick=function(){ e.prompt(); }; }); } })();


(function(){
  var inp=document.getElementById("dlgAddr"), btn=document.getElementById("btnDlg"), st=document.getElementById("dlgStatus");
  if(!inp||!btn)return;
  function show(){ var d=lsGet("ld_delegate"); inp.value=d||""; st.textContent=d?("当前委托给 "+d):"未委托(自己在线)"; }
  btn.onclick=function(){ var v=inp.value.trim(); if(v && !/^wasm1[a-z0-9]{38,}$/.test(v)){ st.textContent="地址格式无效"; return; }
    if(v && !/^wasm1[a-z0-9]{20,}$/.test(v)){ if(window.toast)toast("委托地址须为 wasm1… 或留空(=不委托)"); return; }
    if(v) lsSet("ld_delegate",v); else lsDel("ld_delegate"); show(); };
  show();
})();
(function(){
  var el=document.getElementById("subList"); if(!el)return;
  (async()=>{ try{
    var m=await import("/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2").catch(function(){return null;});
    var c=await m.CosmWasmClient.connect(CFG.rpc);
    var list=await c.queryContractSmart("wasm1uykr2f24sdj9f4la0wv78gvjuyqqnqk9r8jggcqd9ha9vxjrrkksum5x0g",{all_sub_tokens:{}});
    el.textContent = (list&&list.length)? list.map(function(s){return s.symbol||s;}).join(", ") : "暂无已发行子代币";
  }catch(e){ el.textContent="查询失败"; } })();
})();

(function(){ var b=document.getElementById("btnScan"); if(!b)return;
 b.onclick=async function(){ var sel=document.getElementById("claimDay"); sel.innerHTML="";
  try{ var h=await fetch(CFG.gw+"/v1/health").then(function(r){return r.json();});
   for(var d=h.current_day-1;d>=Math.max(1,h.current_day-30);d--){
     var sc=await fetch(CFG.gw+"/v1/scores?day="+d).then(function(r){return r.json();}).catch(function(){return null;});
     if(sc&&sc.finalized&&sc.scores&&sc.scores[myAddr]&&sc.scores[myAddr].w>0){ var o=document.createElement("option"); o.value=d; o.textContent="第"+d+"天"; sel.appendChild(o); } }
   if(!sel.options.length){ toast(t("nothing")); } else { toast("可领 "+sel.options.length+" 天"); }
  }catch(e){ toast(terr(e)); } };
})();


(async function(){ var el=document.getElementById("myBadges"); if(!el||!myAddr)return;
 var F="wasm19g2hgc28u9c0xxkeyf0fu2dg9k9d8wh8m3fc9v";
 try{ var r=await fetch(CFG.gw+"/v1/me?addr="+myAddr).then(function(x){return x.json();});
  var ref=r.referred_total||0, fd=r.first_day, st=r.streak||0, ad=r.active_days||0;
  var b=[];
  if(myAddr===F) b.push(["创始人 Founder","var(--acc,#7c8cff)"]);
  if(fd&&fd<=3) b.push(["创世矿工 Genesis","var(--ok,#3ddc84)"]);
  if(ref>=50) b.push(["合伙人 Partner(50+)","var(--acc2,#a06bff)"]);
  else if(ref>=10) b.push(["大使 Ambassador(10+)","var(--acc2,#a06bff)"]);
  else if(ref>=3) b.push(["布道者 Evangelist(3+)","var(--ok,#3ddc84)"]);
  if(st>=7) b.push(["坚守者 7天连续","var(--warn,#ffb454)"]);
  if(ad>=1) b.push(["活跃贡献者","var(--mut,#9aa3b2)"]);
  var nxt = ref>=50?null:(ref>=10?{n:50,t:"合伙人"}:(ref>=3?{n:10,t:"大使"}:{n:3,t:"布道者"}));
  var html = b.length? b.map(function(x){return '<span style="display:inline-block;margin:2px 6px 2px 0;padding:4px 12px;border-radius:999px;border:1px solid '+x[1]+';color:'+x[1]+'">'+x[0]+"</span>";}).join("") : '<span>暂无头衔,开始邀请与贡献吧</span>';
  if(nxt) html += '<div style="margin-top:6px">距离「'+nxt.t+'」还差 '+(nxt.n-ref)+" 人(当前 "+ref+" 人)</div>";
  el.innerHTML=html;
 }catch(e){ el.textContent="加载失败"; } })();

(function(){ var b=document.getElementById("btnClaimStake"); if(!b)return;
 b.onclick=async function(){ if(!window.LD){toast(t("walletFail"));return;} b.disabled=true; var ot=b.textContent; b.textContent="领取中…";
  try{ var h=await window.LD.claimStaking(); if(h){toast("✓ 已领取 "+h.slice(0,10)+"…"); window.LD.refresh();} else {toast("当前无委托收益可领(你未质押/委托)");} }
  catch(e){ toast(terr(e)); } finally{ b.disabled=false; b.textContent=ot; } }; })();


(async function(){ var el=document.getElementById("airFirst"); if(!el||!myAddr)return;
 try{ var r=await fetch(CFG.gw+"/v1/me?addr="+myAddr).then(function(x){return x.json();});
  var a=r.airdrop_first_mine; var best=r.best_day_session_secs||0;
  if(a){ el.innerHTML='<span style="color:var(--ok,#3ddc84)">✓ 首挖空投已达成:+50 LIGHT(第'+a.day+"天首次满 4 小时有效挖矿,TGE 发放)</span>"; }
  else { var h=Math.min(4,(best/3600)); el.innerHTML="首挖空投(50 LIGHT):单日有效在线 "+h.toFixed(2)+" / 4.00 小时"+(best>0?"(继续挖满 4 小时即达成)":"(今日开始累计)"); }
 }catch(e){ el.textContent="加载失败"; } })();




(async function(){ var el=document.getElementById("airFirst"); if(!el||!myAddr)return;
 try{ var r=await fetch(CFG.gw+"/v1/me?addr="+myAddr).then(function(x){return x.json();});
  var ref=r.referred_total||0; var led=r.airdrop_list||[];
  var got=function(t){ for(var i=0;i<led.length;i++){ if(led[i].type===t) return true; } return false; };
  var rows=[];
  rows.push(["首挖空投 50L", got("first_mine_4h")?"✓ 已达成":"进行中(单日满4h)"]);
  var tier = ref>=50?"✓ 合伙人 2500L":(ref>=10?"✓ 大使 500L":(ref>=3?"✓ 布道者 100L":"进行中"));
  rows.push(["邀请档 100/500/2500L", tier+"(当前 "+ref+" 人)"]);
  rows.push(["Learn-to-Earn 30L", got("learn_to_earn")?"✓ 已达成":(lsGet("ld_quiz_passed")?"待结算":"去 /quiz.html 答题")]);
  rows.push(["治理首投 20L", got("first_vote")?"✓ 已达成":(lsGet("ld_voted")?"待结算":"去治理投一票")]);
  rows.push(["行为加成 4×5%(上限20%)", "PWA/委托/社交恢复/测验 各+5%"]);
  rows.push(["地理扩张 100L","⏳ 待 ZK-KYC(TGE 后)"]);
  rows.push(["流动性提供 200L","⏳ 待 DEX 池"]);
  rows.push(["内容创作 50-200L","⏳ 经治理/资助审核"]);
  rows.push(["合作渠道 80L","⏳ 待合作方接入"]);
  var html="";
  for(var i=0;i<rows.length;i++){ html += "<div>"+rows[i][0]+"：<b>"+rows[i][1]+"</b></div>"; }
  el.innerHTML=html;
 }catch(e){ el.textContent="加载失败"; } })();


(async function(){ var nb=document.getElementById("sybilNote"); var nt=document.getElementById("sybilTxt"); if(!nb||!myAddr)return;
 try{ var h=await fetch(CFG.gw+"/v1/health").then(function(r){return r.json();});
  var me=await fetch(CFG.gw+"/v1/me?addr="+myAddr).then(function(r){return r.json();});
  var peers=[]; var zeroed=false;
  for(var k in (me.days||{})){ var rec=me.days[k]; if(rec.fp_peers&&rec.fp_peers.length){ peers=rec.fp_peers; } if(rec.active&&rec.score){ var w=(Math.min(rec.score.bandwidth||0,10000)*40+Math.min(rec.score.session||0,3600)*30+Math.min(rec.score.verification||0,100)*20+Math.min(rec.score.stability||0,100)*10)/100; if(w===0) zeroed=true; } }
  if(peers.length||zeroed){ nb.style.display=""; nt.innerHTML="本设备(同指纹)今日有多个钱包在挖矿:"+peers.map(function(p){return p.slice(0,10)+"…";}).join(", ")+"。按白皮书 §4.8,每日仅最高分钱包计分,其余归零——<b>一台设备请只保留一个钱包挖矿</b>,关闭其它钱包的标签页,明日即正常计分。"; }
 }catch(e){} })();
