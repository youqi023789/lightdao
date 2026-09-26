
fetch("/whitepaper.md").then(r=>r.text()).then(t=>{
  if(window.marked){ document.getElementById("md").innerHTML = marked.parse(t); }
  else { document.getElementById("md").innerHTML = "<pre>"+t.replace(/</g,"&lt;")+"</pre>"; }
}).catch(e=>{ document.getElementById("md").innerHTML = "<p>加载失败,请用上方 GitHub 源。</p>"; });
