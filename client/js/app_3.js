
const CDN = ["/js/vendor/"];
async function loadCosmjs(){
  if(window.__c) return window.__c;
  const L=p=>"/js/vendor/-cosmjs-"+p+"-0.32.4.js?v=2";
  const C=p=>"https://cdn.jsdelivr.net/npm/@cosmjs/"+p+"@0.32.4/+esm";
  for(const src of [L,C]){
    try{
      const [cs,ps,sg]=await Promise.all([import(src("cosmwasm-stargate")),import(src("proto-signing")),import(src("stargate"))]);
      window.__c={cs,ps,sg}; return window.__c;
    }catch(e){}
  }
  return null;
}
window.LD = null;
(async()=>{
  const c = await loadCosmjs();
  if(!c){ return; }
  const { SigningCosmWasmClient } = c.cs;
  const { DirectSecp256k1HdWallet } = c.ps;
  const { GasPrice } = c.sg;
  let wallet=null, client=null;
window.__mrq=(m)=>client.queryContractSmart(CFG.miningReward,m);
  window.LD = {
    addr:null,
    async create(){ const w=await DirectSecp256k1HdWallet.generate(12,{prefix:CFG.prefix}); this._w=w; return w.mnemonic; },
    async connect(seed){ try{ wallet=await DirectSecp256k1HdWallet.fromMnemonic(seed,{prefix:CFG.prefix}); const [a]=await wallet.getAccounts(); this.addr=a.address; client=await SigningCosmWasmClient.connectWithSigner(CFG.rpc,wallet,{gasPrice:GasPrice.fromString("0.0025"+CFG.denom)}); return true; }catch(e){ return false; } },
    async refresh(){ try{ const b=await client.getBalance(this.addr,CFG.denom); document.getElementById("bal").textContent=(Number(b.amount)/1e6).toLocaleString(undefined,{maximumFractionDigits:2}); }catch(e){} },
    async claim(day){ try{ const h=await (await fetch(CFG.gw+"/v1/health")).json(); const d= day|| (h.current_day-1);
      const p=await fetch(CFG.gw+"/v1/proof?day="+d+"&miner="+this.addr).then(r=>r.ok?r.json():null);
      if(!p){ toast(t("nothing")); return; }
      const msg={claim:{day:d,proof:p.proof,score:{bandwidth:String(p.score.bandwidth),session:String(p.score.session),verification:String(p.score.verification),stability:String(p.score.stability)}}};
      let res; try{ res=await client.execute(this.addr,CFG.miningReward,msg,{amount:[],gas:"300000",granter:PAYMASTER}); }catch(e){ res=await client.execute(this.addr,CFG.miningReward,msg,"auto"); }
      toast(t("claimed")+" "+res.transactionHash.slice(0,10)+"…"); this.refresh();
    }catch(e){ toast(String(e.message||e).slice(0,70)); } },
  };
if(window.__ldReady)window.__ldReady();
})();
document.getElementById("themeT").onclick=function(){var c=document.documentElement.getAttribute("data-theme");var n=c==="light"?"dark":"light";document.documentElement.setAttribute("data-theme",n);try{lsSet("ld_theme",n);}catch(e){}this.textContent=n==="light"?"◑":"◐";};
(function(){ const b=$("pwaBadge"); if(!b)return; const stand=matchMedia("(display-mode: standalone)").matches||navigator.standalone; if(stand){ b.style.display=""; } else { window.addEventListener("beforeinstallprompt",function(e){ e.preventDefault(); b.style.display=""; b.textContent="📲 安装 PWA · 离线可用/心跳更稳"; b.style.cursor="pointer"; b.onclick=function(){ e.prompt(); }; }); } })();


(function(){
  var inp=document.getElementById("dlgAddr"), btn=document.getElementById("btnDlg"), st=document.getElementById("dlgStatus");
  if(!inp||!btn)return;
  function show(){ var d=lsGet("ld_delegate"); inp.value=d||""; st.textContent=d?("当前委托给 "+d):"未委托(自己在线)"; }
  btn.onclick=function(){ var v=inp.value.trim(); if(v && !/^wasm1[a-z0-9]{38,}$/.test(v)){ st.textContent="地址格式无效"; return; }
    if(v) lsSet("ld_delegate",v); else lsDel("ld_delegate"); show(); };
  show();
})();
(function(){
  var el=document.getElementById("subList"); if(!el)return;
  (async()=>{ try{
    var m=await import("/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2").catch(function(){return import("https://cdn.jsdelivr.net/npm/@cosmjs/cosmwasm-stargate@0.32.4/+esm");});
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
  }catch(e){ toast(String(e.message||e).slice(0,60)); } };
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
