document.getElementById("themeT").onclick=function(){var c=document.documentElement.getAttribute("data-theme");var n=c==="light"?"dark":"light";document.documentElement.setAttribute("data-theme",n);try{localStorage.setItem("ld_theme",n);}catch(e){}this.textContent=n==="light"?"◑":"◐";};

(async()=>{ try{
  var m=await import("/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2").catch(function(){return import("https://cdn.jsdelivr.net/npm/@cosmjs/cosmwasm-stargate@0.32.4/+esm");});
  var c=await m.CosmWasmClient.connect(location.origin+"/rpc/");
  var tw=await c.queryContractSmart("wasm1f622csg2af6utlxvxgch2l9qf64ce3s4h5vseaph5ku8vzcgp6qqmsyace",{twap30d:{}});
  var em=await c.queryContractSmart("wasm1f622csg2af6utlxvxgch2l9qf64ce3s4h5vseaph5ku8vzcgp6qqmsyace",{external_median:{}});
  var f=function(n){return (Number(n)/1e6).toLocaleString(undefined,{maximumFractionDigits:4});};
  var grid=document.getElementById("stats"); if(!grid)return;
  var d1=document.createElement("div"); d1.className="stat"; d1.innerHTML="<span>链上 TWAP30d($)</span><b>"+f(tw)+"</b>"; grid.appendChild(d1);
  var d2=document.createElement("div"); d2.className="stat"; d2.innerHTML="<span>外部中位价($·当前主源)</span><b>"+f(em)+"</b>"; grid.appendChild(d2);
}catch(e){} })();
