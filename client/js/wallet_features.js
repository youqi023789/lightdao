// wallet_features.js — Transfer + Delegate UI wiring. Loaded after app_2 (LD API) before app_3.
(function(){
  function t(k){ // zh-only mini i18n (fallback to key)
    return {send:"转账", delegate:"委托", undelegate:"解除委托"}[k]||k;
  }
  async function ensureLD(){ return window.LD && window.LD.addr; }

  // validator list for delegate dropdown
  async function loadValidators(){
    var sel = document.getElementById('delVal'); if(!sel) return;
    try {
      var m = await import("/js/vendor/-cosmjs-cosmwasm-stargate-0.32.4.js?v=2").catch(function(){return null;});
      var c = await m.CosmWasmClient.connect("https://lightdao.net/rpc/");
      var vals = await c.getValidators();
      sel.innerHTML = "";
      (vals||[]).forEach(function(v){
        var o = document.createElement("option");
        o.value = v.operatorAddress;
        o.textContent = (v.description && v.description.moniker ? v.description.moniker : v.operatorAddress.slice(0,20)) + " · " + (v.tokens/1e6).toFixed(0) + "L";
        sel.appendChild(o);
      });
      var info = document.getElementById('delInfo');
      if(info) info.textContent = "委托后可随时解除(解绑期约21天),收益自动累积,用上方「一键领取验证者/质押收益」提取。";
    } catch(e) {
      sel.innerHTML = "<option>加载验证者失败</option>";
    }
  }

  // send
  var btnSend = document.getElementById('btnSend');
  if(btnSend) btnSend.onclick = async function(){
    if(!await ensureLD()){ toast("请先登录钱包"); return; }
    var to = document.getElementById('sendTo').value.trim();
    var amt = parseFloat(document.getElementById('sendAmt').value);
    if(!to || !to.startsWith("wasm1") || to.length < 40){ toast("收款地址无效"); return; }
    if(!(amt > 0)){ toast("金额无效"); return; }
    if(amt > 500000){ toast("单笔超过 50 万 LIGHT,请确认后分批或联系团队"); return; }
    if(!confirm("确认转账 " + amt + " LIGHT 至\\n" + to + " ?\\n转账不可撤销。")) return;
    try {
      var r = await window.LD.sendTokens(to, Math.round(amt*1e6), "转账");
      toast("已提交,等待链上确认...");
      if(r && r.transactionHash){ toast("✓ 转账成功 " + r.transactionHash.slice(0,10)); setTimeout(function(){ location.reload(); }, 2000); }
    } catch(e){ toast("转账失败: " + (e.message||e).toString().slice(0,120)); }
  };

  // delegate / undelegate
  var btnDel = document.getElementById('btnDelegate');
  var btnUndel = document.getElementById('btnUndelegate');
  async function doDelegate(un){
    if(!await ensureLD()){ toast("请先登录钱包"); return; }
    var sel = document.getElementById('delVal');
    var amt = parseFloat(document.getElementById('delAmt').value);
    var val = sel && sel.value;
    if(!val || !val.startsWith("wasmvaloper")){ toast("请选择验证者"); return; }
    if(!(amt > 0)){ toast("金额无效"); return; }
    if(!confirm("确认" + (un?"解除委托":"委托") + " " + amt + " LIGHT 给 " + val.slice(0,20) + "... ?")) return;
    try {
      var fn = un ? window.LD.undelegate : window.LD.delegate;
      var r = await fn(val, Math.round(amt*1e6));
      toast((un?"解除委托":"委托") + "已提交,等待确认...");
      if(r && r.transactionHash) toast("✓ 成功 " + r.transactionHash.slice(0,10));
    } catch(e){ toast("失败: " + (e.message||e).toString().slice(0,120)); }
  }
  if(btnDel) btnDel.onclick = function(){ doDelegate(false); };
  if(btnUndel) btnUndel.onclick = function(){ doDelegate(true); };

  // init when wallet ready (app_3 sets myAddr on enter)
  var tries = 0;
  var iv = setInterval(function(){
    tries++;
    if(window.LD && window.LD.addr){ clearInterval(iv); loadValidators(); }
    if(tries > 60) clearInterval(iv); // 30s give up
  }, 500);
})();
