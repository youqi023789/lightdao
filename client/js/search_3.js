
var IDX=null;
fetch("/search-index.json").then(function(r){return r.json();}).then(function(j){IDX=j;}).catch(function(){});
function esc(s){return s.replace(/[&<>]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
function hl(s,q){var i=s.toLowerCase().indexOf(q.toLowerCase());if(i<0)return esc(s);return esc(s.slice(0,i))+"<mark>"+esc(s.slice(i,i+q.length))+"</mark>"+esc(s.slice(i+q.length));}
function snip(s,q){var i=s.toLowerCase().indexOf(q.toLowerCase());var st=Math.max(0,i-60);return (st>0?"…":"")+s.slice(st,st+180)+(st+180<s.length?"…":"");}
document.getElementById("q").oninput=function(){
  var q=this.value.trim().toLowerCase();var res=document.getElementById("res");res.innerHTML="";
  if(!IDX||q.length<1){return;}
  var out=[];
  IDX.forEach(function(pg){
    pg.sections.forEach(function(sec){
      var hay=(pg.title+" "+sec.text).toLowerCase();
      if(hay.indexOf(q)>=0){out.push({url:pg.url+(sec.id?"#"+sec.id:""),title:pg.title,crumb:sec.head||"",text:sec.text,q:q});}
    });
  });
  out.slice(0,20).forEach(function(o){
    var d=document.createElement("div");d.className="r";
    d.innerHTML='<a href="'+o.url+'">'+hl(o.title,o.q)+(o.crumb?" › "+hl(o.crumb,o.q):"")+'</a><div class="crumb">'+esc(o.url)+'</div><p>'+hl(snip(o.text,o.q),o.q)+"</p>";
    res.appendChild(d);
  });
  if(!out.length)res.innerHTML='<p style="color:var(--mut)">无结果 / no results</p>';
};
