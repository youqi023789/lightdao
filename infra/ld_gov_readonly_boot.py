#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""治理页：让未连钱包的访客也能看到提案列表（公开信息不该被连接门槛挡住）。
做法：加一个只读 CosmWasmClient 做首屏；签名路径（execute/vote）完全不动。
失败时给出明确文案，不再无限"加载中…"。"""
import io
import os
import subprocess
import sys

CAND = sys.argv[1]
P = os.path.join(CAND, "js", "governance_2.js")
t = io.open(P, encoding="utf-8").read()
SENT = "LD-GOV-READONLY-BOOT-20261016"
if SENT in t:
    print("已应用，跳过"); sys.exit(0)

fails = []

# 1) 只读客户端变量
a = "let client=null,addr=null;"
if t.count(a) != 1:
    fails.append("锚点1 命中 %d" % t.count(a))
else:
    t = t.replace(a, "let client=null,addr=null,ro=null;   /* ro = 只读客户端，未连钱包也能查链上 */", 1)

# 2) 查询走 client||ro（只影响查询，不影响签名）
n = t.count("client.queryContractSmart(")
t = t.replace("client.queryContractSmart(", "(client||ro).queryContractSmart(")
print("  ok 查询改走 client||ro（%d 处）" % n)

# 3) 首屏只读加载
anchor = "async function refreshBal(){"
if t.count(anchor) != 1:
    fails.append("锚点3 命中 %d" % t.count(anchor))
else:
    boot = """/* %s 首屏用只读客户端加载公开治理信息；连钱包后才启用签名能力。
   之前 refreshProps 只在 connect() 里调用，未连钱包的访客永远停在"加载中…"。 */
async function initReadOnly(){
  const el=document.getElementById("props");
  try{
    const c=await loadCosmjs();
    if(!c){ if(el) el.innerHTML='<span class="err">链上查询组件加载失败（网络受限），提案列表暂不可读</span>'; return; }
    ro=await c.cs.CosmWasmClient.connect(location.origin+"/rpc/");
    await refreshProps();
    try{ await refreshTreas(); }catch(e){}
  }catch(e){
    if(el) el.innerHTML='<span class="err">读取链上提案失败：'+String((e&&e.message)||e).slice(0,80)+'</span>';
  }
}
if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",initReadOnly);
else initReadOnly();

""" % SENT
    t = t.replace(anchor, boot + anchor, 1)
    print("  ok 注入只读首屏")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
r = subprocess.run(["node", "--check", P], capture_output=True, timeout=90)
if r.returncode:
    print("FAIL 语法:", r.stderr.decode("utf-8", "replace")[:400]); sys.exit(3)

# 自检：签名相关调用不能被误改
t2 = io.open(P, encoding="utf-8").read()
for must in ("client.execute(", "client.getBalance("):
    if must not in t2:
        fails.append("签名/余额调用丢失: " + must)
if "(ro).queryContractSmart" in t2 and "(client||ro).queryContractSmart" not in t2:
    fails.append("替换不完整")
if fails:
    print("!!! 失败:", fails); sys.exit(4)
print("READONLY_BOOT_OK")
