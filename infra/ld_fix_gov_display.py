#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修治理页"活跃提案"虚高：active_proposals 会把已作废/已过期提案一起返回，
原代码全部当"进行中"渲染，还给了可点击的投票/执行按钮。
做法：逐个查 proposal_state 分类；不隐藏任何提案，只分组标注，
并对 voided/expired 的提案禁用投票与执行按钮（点了必然报错）。"""
import io
import os
import subprocess
import sys

CAND = sys.argv[1]
P = os.path.join(CAND, "js", "governance_2.js")
t = io.open(P, encoding="utf-8").read()
SENT = "LD-GOV-STATE-CLASSIFY-20261016"
if SENT in t:
    print("已应用，跳过"); sys.exit(0)

OLD = """    const ps=await client.queryContractSmart(GOV,{active_proposals:{}});
    const el=$("props"); el.innerHTML="";
    if(!ps||!ps.length){el.innerHTML='<span class="mut">暂无进行中提案</span>';return;}
    ps.forEach(p=>{"""
NEW = """    /* %s active_proposals 会连同"已作废/已过期"的提案一起返回（链上实测
       proposal_state: voided=true, expired=true），旧代码把它们一律显示成"进行中"，
       还给了可点击的投票/执行按钮。这里逐个查状态后分组显示：不隐藏任何提案，
       只如实标注，并禁用已结束提案的按钮。 */
    const ps0=await client.queryContractSmart(GOV,{active_proposals:{}});
    const el=$("props"); el.innerHTML="";
    if(!ps0||!ps0.length){el.innerHTML='<span class="mut">暂无进行中提案</span>';return;}
    const st=await Promise.all(ps0.map(p=>client.queryContractSmart(GOV,{proposal_state:{id:p.id}})
      .catch(function(){return null;})));
    const ps=[], dead=[];
    ps0.forEach(function(p,i){
      var s=st[i];
      /* 查不到状态时保守当作进行中，绝不因为查询失败就把提案藏掉 */
      if(s && (s.voided || s.expired || s.executed)) dead.push({p:p,s:s});
      else ps.push(p);
    });
    function renderCard(p,off){""" % SENT

OLD2 = """      const endLeft=Math.round((p.end-Date.now()/1000)/3600);
      const ended=(Number(p.end)*1000)<=Date.now();
      const dis=ended?" disabled":"";"""
NEW2 = """      const endLeft=Math.round((p.end-Date.now()/1000)/3600);
      const ended=(Number(p.end)*1000)<=Date.now();
      const dis=(ended||off)?" disabled":"";"""

OLD3 = """      d.innerHTML=`<h3>#${p.id} ${esc(p.title)} <span class="mut">[${p.ptype}]</span>${ended?' <span class="err">已结束</span>':""}</h3>"""
NEW3 = """      d.innerHTML=`<h3>#${p.id} ${esc(p.title)} <span class="mut">[${p.ptype}]</span>${off?' <span class="err">已作废/已过期</span>':(ended?' <span class="err">已结束</span>':"")}</h3>"""

OLD4 = """        <button class="btn sm" data-v="yes" data-id="${p.id}"${dis}>赞成</button><button class="btn ghost sm" data-v="no" data-id="${p.id}"${dis}>反对</button><button class="btn ghost sm" data-v="abstain" data-id="${p.id}"${dis}>弃权</button><button class="btn ghost sm" data-e="1" data-id="${p.id}">执行</button>`;
      el.appendChild(d);
    });"""
NEW4 = """        <button class="btn sm" data-v="yes" data-id="${p.id}"${dis}>赞成</button><button class="btn ghost sm" data-v="no" data-id="${p.id}"${dis}>反对</button><button class="btn ghost sm" data-v="abstain" data-id="${p.id}"${dis}>弃权</button><button class="btn ghost sm" data-e="1" data-id="${p.id}"${dis}>执行</button>`;
      if(off){ d.style.opacity=".55"; }
      el.appendChild(d);
    }
    if(!ps.length){ el.innerHTML='<span class="mut">暂无可投票的进行中提案</span>'; }
    ps.forEach(p=>renderCard(p,false));
    if(dead.length){
      const tip=document.createElement("p"); tip.className="mut"; tip.style.marginTop="10px";
      tip.textContent="以下 "+dead.length+" 个提案已作废或已过期，不计入进行中，也不可再操作：";
      el.appendChild(tip);
      dead.forEach(x=>renderCard(x.p,true));
    }"""

for a, b, tag in ((OLD, NEW, "取状态+分组"), (OLD2, NEW2, "按钮禁用"),
                  (OLD3, NEW3, "标题标注"), (OLD4, NEW4, "渲染与分组输出")):
    if t.count(a) != 1:
        print("FAIL 锚点「%s」命中 %d 次" % (tag, t.count(a))); sys.exit(2)
    t = t.replace(a, b, 1)
    print("  ok %s" % tag)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
r = subprocess.run(["node", "--check", P], capture_output=True, timeout=90)
if r.returncode:
    print("FAIL 语法:", r.stderr.decode("utf-8", "replace")[:400]); sys.exit(3)
print("GOV_CLASSIFY_OK")
