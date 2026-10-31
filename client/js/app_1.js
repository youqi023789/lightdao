window.LDBUILD="1.8.7";
function terr(e){
  var raw = String((e && e.message) || e || "");
  /* LD-UX-ERR-20261031 链上原文对新人等于一堵墙：先翻成"发生了什么 + 现在该怎么办"，
     再把原文留在括号里给排查用。 */
  var hint = "";
  if (/does not allow to pay fee|code 38/i.test(raw)) {
    hint = "免手续费授权已过期，且钱包余额不够自付本次手续费（约 0.075 LIGHT）。系统会自动补授权，请在数小时后重试。";
  } else if (/insufficient fee|too small gas fee|insufficient funds/i.test(raw)) {
    hint = "余额不足以支付本次链上手续费，请先取得 LIGHT 或等待免手续费授权续期。";
  } else if (/already claimed/i.test(raw)) {
    hint = "这一天此前已经领过了，无需重复领取。";
  } else if (/closed|not finalized|no such root|proof/i.test(raw)) {
    hint = "这一天的结算还没完成（每日 00:00 UTC 之后才开放领取），稍后再试。";
  }
  var tail = hint ? ("\n" + hint) : "";
  return "[" + window.LDBUILD + "] " + raw.slice(0, 180) + tail;
}
(function(){try{var t=lsGet("ld_theme")||(matchMedia("(prefers-color-scheme: light)").matches?"light":"dark");document.documentElement.setAttribute("data-theme",t);}catch(e){}})();

(function(){var miss=[];if(!window.Promise)miss.push("Promise");if(!window.fetch)miss.push("fetch");if(!(window.crypto&&window.crypto.subtle))miss.push("WebCrypto");if(!window.HTMLScriptElement||!("noModule" in HTMLScriptElement.prototype))miss.push("ESModule");if(miss.length){var d=document.createElement("div");d.setAttribute("style","position:fixed;left:0;right:0;top:0;z-index:99;background:#8a2b2b;color:#fff;padding:10px 14px;font-size:14px;text-align:center");d.textContent="你的浏览器缺少:"+miss.join(", ")+"。请升级到最新版 Chrome/Edge/Safari,或改用电脑端。";document.addEventListener("DOMContentLoaded",function(){document.body.insertBefore(d,document.body.firstChild);});}})();

try{ if(sessionStorage.getItem("ld_session")||localStorage.getItem("ld_lock_v1")||localStorage.getItem("ld_persist_v1")||localStorage.getItem("ld_seed")){ document.documentElement.classList.add("ld-restoring"); } }catch(e){}

var APPV="1.8.7";
(function(){ try{ var done=sessionStorage.getItem("ld_verreload"); fetch("/js/ver.json?ts="+Date.now(),{cache:"no-store"}).then(function(r){return r.json();}).then(function(j){ if(j.v!==APPV && done!==String(j.v)){ sessionStorage.setItem("ld_verreload",String(j.v)); location.reload(); } }).catch(function(){}); }catch(e){} })();


(function(){ function rep(m){ try{ fetch(((window.CFG&&window.CFG.gw)||"/gw")+"/v1/clienterr",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({msg:String(m).slice(0,300),build:(window.LDBUILD||"?"),ua:navigator.userAgent,url:location.pathname})}).catch(function(){}); }catch(e){} }
 window.addEventListener("error",function(e){ var st=""; try{ if(e.error&&e.error.stack){ st=" | "+String(e.error.stack).split("\n").slice(0,3).join(" <- "); } }catch(x){} rep((e.message||"error")+" @"+(e.lineno||"?")+st); });
 window.addEventListener("unhandledrejection",function(e){ rep((e.reason&&e.reason.message)||"unhandledrejection"); });
 window.__ldReport=rep; })();

document.addEventListener("DOMContentLoaded",function(){ try{ var bb=document.getElementById("ld-build"); if(bb) bb.textContent=window.LDBUILD; }catch(e){} });
