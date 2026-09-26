
const RPC=location.origin+"/rpc/";
const BURN="wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu";
const TREAS="wasm192u2pm80ndmh608mmvhrzhje0sjaq0txr5md77lr70ucy0j3lfys8l633u";
const INS="wasm1wj3369pug9sdn5wcqu74yr00vtcntqvwgqrmcs0k0twwnvgm8m2qu77ewf";
const ORACLE="wasm1f622csg2af6utlxvxgch2l9qf64ce3s4h5vseaph5ku8vzcgp6qqmsyace";
const VEST="wasm16l8mdmawaq4538ajr89dpfxh7cyll584yw7jqnhgmp5clwp6m8fqtwkz4x";
const VEST_BEN=["wasm13c2cjh3fhkesj47tsc5a0vm6pdds39qpcmykhj","wasm16sm2nlg2sp9zy2dha5a80rjthjsatzcm2ue8za","wasm182d06dcj2upp9hkxqsxzp5ngws6kqdnq5yvu2g"];

const CDN=["/js/vendor/"];
let client=null;
async function load(){ const VEN=p=>"/js/vendor/-cosmjs-"+p+"-0.32.4.js?v=2"; const CDNU=p=>"https://cdn.jsdelivr.net/npm/@cosmjs/"+p+"@0.32.4/+esm";
for(const src of [VEN,CDNU]){ try{ const m=await import(src("cosmwasm-stargate")); const st=await import(src("stargate")); return {cw:m,st:st}; }catch(e){} } return null; }
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=(n,d=6)=>(Number(n)/10**d).toLocaleString(undefined,{maximumFractionDigits:2});
async function init(){
  const L=await load(); if(!L){document.getElementById("stats").innerHTML='<div class="stat err">cosmjs 加载失败</div>';return;}
  
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
client=pf(await L.st.StargateClient.connect(RPC),RPC);
  const cw=await L.cw.CosmWasmClient.connect(RPC);
  const h=await client.getHeight();
  const ul={denom:"ulight",amount:"2500000000000000"}; // hard cap 2.5B LIGHT, never inflated (WP 5.1)
  const burn=await client.getBalance(BURN,"ulight").catch(()=>({amount:"0"}));
  const tre=await client.getBalance(TREAS,"ulight").catch(()=>({amount:"0"}));
  const ins=await client.getBalance(INS,"ulight").catch(()=>({amount:"0"})); if(document.getElementById("insB"))document.getElementById("insB").textContent=fmt(ins.amount);
  let oracle="—"; try{ oracle=fmt(await cw.queryContractSmart(ORACLE,{external_median:{}})); }catch(e){}
  let day="—",miners="—"; try{ const hh=await fetch(location.origin+"/gw/v1/health").then(r=>r.json()); day=hh.current_day; const dd=await fetch(location.origin+"/gw/v1/day?day="+hh.current_day).then(r=>r.json()); miners=Object.keys(dd.miners||{}).length; }catch(e){}
  const vals=await client.getValidators();
  document.getElementById("stats").innerHTML=`
   <div class="stat"><span>最新高度</span><b>${h}</b></div>
   <div class="stat"><span>总供应 LIGHT</span><b>${fmt(ul?ul.amount:0)}</b></div>
   <div class="stat"><span>已销毁 LIGHT</span><b class="ok">${fmt(burn.amount)}</b></div>
   <div class="stat"><span>金库 LIGHT</span><b>${fmt(tre.amount)}</b></div>
   <div class="stat"><span>保险基金 LIGHT</span><b id="insB">—</b></div>
   <div class="stat"><span>oracle 价($)</span><b>${oracle}</b></div>
   <div class="stat"><span>验证者</span><b>${vals.length}</b></div>
   <div class="stat"><span>当前赛季日</span><b>${day}</b></div>
   <div class="stat"><span>今日矿工</span><b>${miners}</b></div>`;
  // blocks
  const chain=await client.getBlocks? null : null;
  const tb=document.getElementById("blocks"); tb.innerHTML="";
  for(let i=h;i>h-12;i--){
    try{ const b=await client.getBlock(i);
      const tr=document.createElement("tr");
      tr.innerHTML=`<td>${i}</td><td class="mut">${(b.header.time||"").replace("T"," ").slice(0,19)}</td><td>${(b.txs||[]).length}</td><td class="mono">${(b.header.proposerAddress||"").slice(0,14)}…</td>`;
      tb.appendChild(tr);
    }catch(e){}
  }
  // validators
  const tv=document.getElementById("vals"); tv.innerHTML="";
  for(const v of vals){
    const tr=document.createElement("tr");
    tr.innerHTML=`<td>${(v.description&&v.description.moniker)||"?"}</td><td class="${v.status==="BOND_STATUS_BONDED"?"ok":"mut"}">${v.status==="BOND_STATUS_BONDED"?"绑定":"其他"}</td><td>${fmt(v.tokens)}</td><td>${(Number((v.commission&&v.commission.commissionRates&&v.commission.commissionRates.rate)||0)*100).toFixed(0)}%</td>`;
    tv.appendChild(tr);
  }
  window.__cw=cw; window.__st=L.st;
}
document.getElementById("btnQ").onclick=async()=>{
  const q=document.getElementById("q").value.trim(); const out=document.getElementById("qres");
  if(!client){out.textContent="未连接";return;}
  try{
    if(/^wasm1/.test(q)){
      const b=await client.getBalance(q,"ulight");
      let extra=""; try{ const st=await window.__cw.queryContractSmart("wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt",{staked_balance:{address:q}}); extra=" · 治理质押 "+fmt(st); }catch(e){}
      out.innerHTML=`地址 ${q}<br>余额: <span class="ok">${fmt(b.amount)} LIGHT</span>${extra}`;
    } else if(/^[0-9A-Fa-f]{64}$/.test(q)){
      const t=await client.getTx(q.toUpperCase());
      if(!t){out.textContent="未找到该交易";return;}
      out.innerHTML=`tx ${q.slice(0,16)}…<br>高度 ${t.height} · code <span class="${t.code===0?"ok":"err"}">${t.code}</span> · gas ${t.gasUsed}/${t.gasWanted}<br>log: ${esc((t.rawLog||"").slice(0,200))||"(空)"}`;
    } else if(/^wasmvaloper1/.test(q)){
      out.textContent="验证者查询请用下方验证者表";
    } else out.textContent="无法识别的输入";
  }catch(e){ out.innerHTML='<span class="err">'+e.message+"</span>"; }
};

const yrs=s=>{s=Number(s);if(s<=1)return "即时";if(s>=31536000){const y=s/31536000;return (Number.isInteger(y)?y:y.toFixed(1))+"年";}if(s>=86400)return (s/86400).toFixed(0)+"天";return s+"秒";};
async function loadVesting(){
  const tb=document.getElementById("vestbody"); if(!tb) return;
  try{
    const L=await load(); if(!L){tb.innerHTML='<tr><td colspan="8" class="err">cosmjs 加载失败</td></tr>';return;}
    const cw=await L.cw.CosmWasmClient.connect(RPC);
    const now=Math.floor(Date.now()/1000);
    let vault="0"; try{vault=await cw.queryContractSmart(VEST,{vault_balance:{}});}catch(e){}
    let rows="",sumTotal=0,sumVested=0,sumClaimed=0;
    for(const a of VEST_BEN){
      let s,v="0";
      try{s=await cw.queryContractSmart(VEST,{schedule:{address:a}});}catch(e){continue;}
      try{v=await cw.queryContractSmart(VEST,{vested:{address:a,at_time:now}});}catch(e){}
      const total=Number(s.total),vested=Number(v),claimed=Number(s.claimed||0);
      sumTotal+=total;sumVested+=vested;sumClaimed+=claimed;
      const pct=total?Math.min(100,vested/total*100):0;
      const start=new Date(Number(s.start)*1000).toISOString().replace("T"," ").slice(0,10);
      rows+='<tr><td class="mono">'+a.slice(0,10)+'…'+a.slice(-6)+'</td><td>'+fmt(total)+'</td><td class="ok">'+fmt(vested)+'</td><td>'+fmt(claimed)+'</td><td>'+yrs(s.cliff_secs)+'</td><td>'+yrs(s.linear_secs)+'</td><td class="mut">'+start+'</td><td><div class="vbar"><i data-w="'+pct.toFixed(1)+'"></i></div><span class="mut" class="fs11s">'+pct.toFixed(1)+'%</span></td></tr>';
    }
    tb.innerHTML=rows||'<tr><td colspan="8" class="mut">无归属计划</td></tr>';
    const vs=document.getElementById("veststats");
    if(vs) vs.innerHTML='<div class="stat"><span>金库总额 LIGHT</span><b>'+fmt(vault)+'</b></div>'
      +'<div class="stat"><span>已归属 LIGHT</span><b class="ok">'+fmt(sumVested)+'</b></div>'
      +'<div class="stat"><span>已领取 LIGHT</span><b>'+fmt(sumClaimed)+'</b></div>'
      +'<div class="stat"><span>未归属 LIGHT</span><b class="mut">'+fmt(sumTotal-sumVested)+'</b></div>';
  }catch(e){ tb.innerHTML='<tr><td colspan="8" class="err">'+e.message+'</td></tr>'; }
}

init();
loadVesting();
