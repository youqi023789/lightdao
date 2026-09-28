window.LDBUILD="1.1.3";
function terr(e){ return "[" + window.LDBUILD + "] " + String(e.message||e).slice(0,300); }
(function(){try{var t=lsGet("ld_theme")||(matchMedia("(prefers-color-scheme: light)").matches?"light":"dark");document.documentElement.setAttribute("data-theme",t);}catch(e){}})();

(function(){var miss=[];if(!window.Promise)miss.push("Promise");if(!window.fetch)miss.push("fetch");if(!(window.crypto&&window.crypto.subtle))miss.push("WebCrypto");if(!window.HTMLScriptElement||!("noModule" in HTMLScriptElement.prototype))miss.push("ESModule");if(miss.length){var d=document.createElement("div");d.setAttribute("style","position:fixed;left:0;right:0;top:0;z-index:99;background:#8a2b2b;color:#fff;padding:10px 14px;font-size:14px;text-align:center");d.textContent="你的浏览器缺少:"+miss.join(", ")+"。请升级到最新版 Chrome/Edge/Safari,或改用电脑端。";document.addEventListener("DOMContentLoaded",function(){document.body.insertBefore(d,document.body.firstChild);});}})();

try{ if(sessionStorage.getItem("ld_session")||localStorage.getItem("ld_lock_v1")||localStorage.getItem("ld_persist_v1")||localStorage.getItem("ld_seed")){ document.documentElement.classList.add("ld-restoring"); } }catch(e){}

var APPV="1.1.3";
(function(){ try{ var done=sessionStorage.getItem("ld_verreload"); fetch("/js/ver.json?ts="+Date.now(),{cache:"no-store"}).then(function(r){return r.json();}).then(function(j){ if(j.v!==APPV && done!==String(j.v)){ sessionStorage.setItem("ld_verreload",String(j.v)); location.reload(); } }).catch(function(){}); }catch(e){} })();


(function(){ function rep(m){ try{ fetch(((window.CFG&&window.CFG.gw)||"/gw")+"/v1/clienterr",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({msg:String(m).slice(0,300),build:(window.LDBUILD||"?"),ua:navigator.userAgent,url:location.pathname})}).catch(function(){}); }catch(e){} }
 window.addEventListener("error",function(e){ var st=""; try{ if(e.error&&e.error.stack){ st=" | "+String(e.error.stack).split("\n").slice(0,3).join(" <- "); } }catch(x){} rep((e.message||"error")+" @"+(e.lineno||"?")+st); });
 window.addEventListener("unhandledrejection",function(e){ rep((e.reason&&e.reason.message)||"unhandledrejection"); });
 window.__ldReport=rep; })();

document.addEventListener("DOMContentLoaded",function(){ try{ var bb=document.getElementById("ld-build"); if(bb) bb.textContent=window.LDBUILD; }catch(e){} });
