
document.getElementById("themeT").onclick=function(){var c=document.documentElement.getAttribute("data-theme");var n=c==="light"?"dark":"light";document.documentElement.setAttribute("data-theme",n);try{localStorage.setItem("ld_theme",n);}catch(e){}this.textContent=n==="light"?"◑":"◐";};
(async()=>{
  const f=n=>(Number(n)/1e6).toLocaleString(undefined,{maximumFractionDigits:0});
  try{
    const m=await import("/js/vendor/-cosmjs-stargate-0.32.4.js?v=2").catch(function(){return import("https://cdn.jsdelivr.net/npm/@cosmjs/stargate@0.32.4/+esm");});
    
function pf(client, RPC){
  try{
    if(typeof client.getValidators!=="function") client.getValidators=async function(){ var r=await fetch(RPC+"validators?per_page=100").then(function(x){return x.json();}); return (r.result.validators||[]).map(function(v){ return {description:{moniker:(v.description&&v.description.moniker)||"?"}, status:"BOND_STATUS_BONDED", tokens:String((Number(v.voting_power)||0)*1000000), commission:{commissionRates:{rate:(v.commission&&v.commission.rate)||"0"}}, validatorAddress:v.address}; }); };
    if(typeof client.getSupply!=="function") client.getSupply=async function(){ return [{denom:"ulight",amount:"2500000000000000"}]; };
    if(typeof client.getHeight!=="function") client.getHeight=async function(){ var r=await fetch(RPC+"status").then(function(x){return x.json();}); return parseInt(r.result.sync_info.latest_block_height,10); };
    if(typeof client.getBlock!=="function") client.getBlock=async function(h){ var r=await fetch(RPC+"block?height="+h).then(function(x){return x.json();}); var b=r.result.block; return {header:{time:b.header.time,proposerAddress:b.header.proposer_address},txs:(b.data&&b.data.txs)||[]}; };
    if(typeof client.getTx!=="function") client.getTx=async function(h){ var r=await fetch(RPC+"tx?hash=0x"+h).then(function(x){return x.json();}); if(!r.result)return null; return {height:parseInt(r.result.height,10),code:r.result.tx_result.code,gasUsed:r.result.tx_result.gas_used,gasWanted:r.result.tx_result.gas_wanted,rawLog:r.result.tx_result.log}; };
  }catch(e){}
  return client;
}
const c=pf(await m.StargateClient.connect(location.origin+"/rpc/"),location.origin+"/rpc/");
    const vs=await c.getValidators();
    const tb=document.querySelector("#vt tbody"); tb.innerHTML="";
    vs.forEach(v=>{const tr=document.createElement("tr");
      tr.innerHTML="<td>"+((v.description&&v.description.moniker)||"?")+"</td><td>"+(v.status==="BOND_STATUS_BONDED"?'<span class="pill ok">BONDED</span>':'<span class="pill no">'+v.status.replace("BOND_STATUS_","")+"</span>")+"</td><td>"+f(v.tokens)+"</td><td>"+(Number((v.commission&&v.commission.commissionRates&&v.commission.commissionRates.rate)||0)*100).toFixed(0)+"%</td>";
      tb.appendChild(tr);});
  }catch(e){document.querySelector("#vt tbody").innerHTML='<tr><td colspan="4">加载失败:'+e.message+"</td></tr>";}
})();


(async()=>{ try{
  var m=await import("/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2").catch(function(){return import("https://cdn.jsdelivr.net/npm/@cosmjs/cosmwasm-stargate@0.32.4/+esm");});
  var c=await m.CosmWasmClient.connect(location.origin+"/rpc/");
  var VR="wasm1egt8ut5swmck6xt5lqeuhkmhp44rwsv73ka8jfp7rn2kg629cdeqdlh6qf";
  var cnt=await c.queryContractSmart(VR,{count:{}}).catch(()=>null);
  var act=await c.queryContractSmart(VR,{active_validators:{}}).catch(()=>[]);
  var tb=document.querySelector("#vrt tbody"); if(!tb)return; tb.innerHTML="";
  var list=(act&&act.length)?act:[];
  if(!list.length){ tb.innerHTML='<tr><td colspan="2">暂无注册候选(注册开放后显示)</td></tr>'; }
  else list.forEach(function(v){ var tr=document.createElement("tr"); tr.innerHTML="<td>"+(v.addr||v)+"</td><td>"+(v.active||v.banned?"see chain":"active")+"</td>"; tb.appendChild(tr); });
  var n=document.createElement("caption"); 
}catch(e){ var tb2=document.querySelector("#vrt tbody"); if(tb2)tb2.innerHTML='<tr><td colspan="2">加载失败</td></tr>'; } })();
