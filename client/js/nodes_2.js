
document.getElementById("themeT").onclick=function(){var c=document.documentElement.getAttribute("data-theme");var n=c==="light"?"dark":"light";document.documentElement.setAttribute("data-theme",n);try{localStorage.setItem("ld_theme",n);}catch(e){}this.textContent=n==="light"?"◑":"◐";};
(async()=>{
  const f=n=>(Number(n)/1e6).toLocaleString(undefined,{maximumFractionDigits:0});
  try{
    const m=await import("https://cdn.jsdelivr.net/npm/@cosmjs/stargate@0.32.4/+esm");
    const c=await m.StargateClient.connect(location.origin+"/rpc/");
    const vs=await c.getValidators();
    const tb=document.querySelector("#vt tbody"); tb.innerHTML="";
    vs.forEach(v=>{const tr=document.createElement("tr");
      tr.innerHTML="<td>"+(v.description?.moniker||"?")+"</td><td>"+(v.status==="BOND_STATUS_BONDED"?'<span class="pill ok">BONDED</span>':'<span class="pill no">'+v.status.replace("BOND_STATUS_","")+"</span>")+"</td><td>"+f(v.tokens)+"</td><td>"+(Number(v.commission?.commissionRates?.rate||0)*100).toFixed(0)+"%</td>";
      tb.appendChild(tr);});
  }catch(e){document.querySelector("#vt tbody").innerHTML='<tr><td colspan="4">加载失败:'+e.message+"</td></tr>";}
})();
