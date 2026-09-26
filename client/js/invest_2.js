
document.getElementById("themeT").onclick=function(){var c=document.documentElement.getAttribute("data-theme");var n=c==="light"?"dark":"light";document.documentElement.setAttribute("data-theme",n);try{localStorage.setItem("ld_theme",n);}catch(e){}this.textContent=n==="light"?"◑":"◐";};
const SUB="wasm1uykr2f24sdj9f4la0wv78gvjuyqqnqk9r8jggcqd9ha9vxjrrkksum5x0g";
const TRE="wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u";
const f=n=>(Number(n)/1e6).toLocaleString(undefined,{maximumFractionDigits:2});
let cw=null;
(async()=>{
  const m=await import("/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2").catch(function(){return import("https://cdn.jsdelivr.net/npm/@cosmjs/cosmwasm-stargate@0.32.4/+esm");}).catch(()=>null);
  if(!m){document.querySelectorAll("tbody").forEach(t=>t.innerHTML='<tr><td colspan="3">cosmjs 加载失败</td></tr>');return;}
  cw=await m.CosmWasmClient.connect(location.origin+"/rpc/");
  // sub tokens
  let list=[]; try{ list=await cw.queryContractSmart(SUB,{all_sub_tokens:{}}); }catch(e){}
  const stb=document.querySelector("#stt tbody"); stb.innerHTML="";
  if(!list||!list.length){ stb.innerHTML='<tr><td colspan="3"><span class="pill">暂无子代币</span></td></tr>'; }
  else list.forEach(s=>{ const tr=document.createElement("tr"); tr.innerHTML="<td>"+(s.symbol||s)+"</td><td>"+f(s.total||s.amount||0)+"</td><td>"+(s.liquidated?"已清算":"活跃")+"</td>"; stb.appendChild(tr); });
  window.__sublist=list||[];
  // signers
  let sg=[]; try{ sg=await cw.queryContractSmart(TRE,{signers:{}}); }catch(e){}
  const sgb=document.querySelector("#sgt tbody"); sgb.innerHTML="";
  (sg||[]).forEach((a,i)=>{ const tr=document.createElement("tr"); tr.innerHTML="<td>"+(i+1)+"</td><td class="mono12">"+a+"</td>"; sgb.appendChild(tr); });
  if(!sg||!sg.length) sgb.innerHTML='<tr><td colspan="2">无</td></tr>';
  // pending txs: iterate ids
  const txb=document.querySelector("#txt tbody"); txb.innerHTML=""; let any=false;
  for(let id=0; id<20; id++){
    let t=null; try{ t=await cw.queryContractSmart(TRE,{tx:{id:id}}); }catch(e){ break; }
    if(!t) break; any=true;
    const tr=document.createElement("tr"); tr.innerHTML="<td>"+id+"</td><td>"+(t.executed?"已执行":"待签")+"</td><td>"+(t.signs||t.approvals||"?")+"</td>"; txb.appendChild(tr);
  }
  if(!any) txb.innerHTML='<tr><td colspan="3"><span class="pill">暂无待执行交易</span></td></tr>';
  // balances on input
  const q=async()=>{ const a=document.getElementById("addr").value.trim(); const tb=document.querySelector("#bal tbody"); tb.innerHTML="";
    if(!a.startsWith("wasm1")){ tb.innerHTML='<tr><td colspan="2">地址无效</td></tr>'; return; }
    if(!window.__sublist||!window.__sublist.length){ tb.innerHTML='<tr><td colspan="2"><span class="pill">暂无子代币可查</span></td></tr>'; return; }
    for(const s of window.__sublist){ const sym=s.symbol||s; let b="0"; try{ b=await cw.queryContractSmart(SUB,{balance_of:{symbol:sym,address:a}}); }catch(e){}
      const tr=document.createElement("tr"); tr.innerHTML="<td>"+sym+"</td><td>"+f(b)+"</td>"; tb.appendChild(tr); }
  };
  document.getElementById("addr").onchange=q;
  const qa=new URLSearchParams(location.search).get("addr"); if(qa){ document.getElementById("addr").value=qa; q(); }
})();
