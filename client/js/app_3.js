
const CDN = ["https://cdn.jsdelivr.net/npm/","https://esm.sh/"];
async function loadCosmjs(){
  if(window.__c) return window.__c;
  for(const base of CDN){
    try{
      const url = base==="https://esm.sh/" ? base : base;
      const [cs, ps, sg] = await Promise.all([
        import(base+"@cosmjs/cosmwasm-stargate@0.32.4"+(base==="https://esm.sh/"?"":"/+esm")),
        import(base+"@cosmjs/proto-signing@0.32.4"+(base==="https://esm.sh/"?"":"/+esm")),
        import(base+"@cosmjs/stargate@0.32.4"+(base==="https://esm.sh/"?"":"/+esm")),
      ]);
      window.__c={cs,ps,sg}; return window.__c;
    }catch(e){}
  }
  return null;
}
const PAYMASTER="wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj"; // feegrant granter for gasless first txs
window.LD = null;
(async()=>{
  const c = await loadCosmjs();
  if(!c){ return; } // 优雅降级: 挖矿仍可用, 钱包/领取提示不可用
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
    async claim(){ try{ const h=await (await fetch(CFG.gw+"/v1/health")).json(); const d=h.current_day-1;
      const p=await fetch(CFG.gw+"/v1/proof?day="+d+"&miner="+this.addr).then(r=>r.ok?r.json():null);
      if(!p){ toast(t("nothing")); return; }
      const msg={claim:{day:d,proof:p.proof,score:{bandwidth:String(p.score.bandwidth),session:String(p.score.session),verification:String(p.score.verification),stability:String(p.score.stability)}}};
      let res; try{ res=await client.execute(this.addr,CFG.miningReward,msg,{amount:[],gas:"300000",granter:PAYMASTER}); }catch(e){ res=await client.execute(this.addr,CFG.miningReward,msg,"auto"); }
      toast(t("claimed")+" "+res.transactionHash.slice(0,10)+"…"); this.refresh();
    }catch(e){ toast(String(e.message||e).slice(0,70)); } },
  };
if(window.__ldReady)window.__ldReady();
})();
document.getElementById("themeT").onclick=function(){var c=document.documentElement.getAttribute("data-theme");var n=c==="light"?"dark":"light";document.documentElement.setAttribute("data-theme",n);try{localStorage.setItem("ld_theme",n);}catch(e){}this.textContent=n==="light"?"◑":"◐";};
(function(){ const b=$("pwaBadge"); if(!b)return; const stand=matchMedia("(display-mode: standalone)").matches||navigator.standalone; if(stand){ b.style.display=""; } else { window.addEventListener("beforeinstallprompt",function(e){ e.preventDefault(); b.style.display=""; b.textContent="📲 安装 PWA · 离线可用/心跳更稳"; b.style.cursor="pointer"; b.onclick=function(){ e.prompt(); }; }); } })();
