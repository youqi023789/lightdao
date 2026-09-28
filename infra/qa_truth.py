#!/usr/bin/env python3
"""qa_truth.py — 真相不变量 × 退化态 门(单读者 CDP, 无并发抢ws)。
浏览器态: S0 新鲜不变量(徽章/状态/倒计时/无console错) · S5 断网优雅 · S6 时钟漂移+6h倒计时仍准。
静态态(读线上JS/HTML源码断言): 缓存击穿 / 回前台重取 / 按版本自愈哨兵 / 徽章由LDBUILD驱动 / gasPrice=0.2 / status徽章id存在。
任一 FAIL 退出非0。"""
import asyncio, json, sys, urllib.request, re
import websockets

CDP="http://127.0.0.1:9222"; BASE="https://lightdao.net/app.html"
R=[]
def rec(n,ok,d=""):
    R.append((n,ok)); print(("PASS " if ok else "FAIL ")+n+(" | "+d if d else ""))
def get(u):
    return urllib.request.urlopen(u, timeout=15).read().decode("utf-8","replace")

class Page:
    def __init__(s,ws,sid): s.ws=ws; s.sid=sid; s.mid=0; s.errors=[]
    async def send(s,m,p=None):
        s.mid+=1; msg={"id":s.mid,"method":m,"params":p or {}}
        if s.sid: msg["sessionId"]=s.sid
        await s.ws.send(json.dumps(msg))
        while True:
            r=json.loads(await asyncio.wait_for(s.ws.recv(),timeout=30))
            if r.get("method")=="Runtime.exceptionThrown": s.errors.append("exc")
            if r.get("id")==s.mid and (s.sid is None or r.get("sessionId")==s.sid):
                if "error" in r: raise RuntimeError(m)
                return r.get("result",{})
    async def ev(s,e,aw=False):
        r=await s.send("Runtime.evaluate",{"expression":e,"returnByValue":True,"awaitPromise":aw})
        return r.get("result",{}).get("value")

async def new_page(ws,ua=None):
    t=await Page(ws,None).send("Target.createTarget",{"url":"about:blank"})
    a=await Page(ws,None).send("Target.attachToTarget",{"targetId":t["targetId"],"flatten":True})
    pg=Page(ws,a["sessionId"])
    await pg.send("Page.enable"); await pg.send("Runtime.enable"); await pg.send("Network.enable")
    if ua: await pg.send("Emulation.setUserAgentOverride",{"userAgent":ua})
    return pg,t["targetId"]

def static_checks():
    a2=get("https://127.0.0.1/js/app_2.js") if False else None
    import ssl
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    def g(u): return urllib.request.urlopen(urllib.request.Request(u,headers={"Host":"lightdao.net"}),context=ctx,timeout=15).read().decode("utf-8","replace")
    a1=g("https://127.0.0.1/js/app_1.js"); a2=g("https://127.0.0.1/js/app_2.js"); a3=g("https://127.0.0.1/js/app_3.js"); ah=g("https://127.0.0.1/app.html")
    rec("static status fetch cache-busted", ('/status.json?ts=' in a2 and 'no-store' in a2))
    rec("static resume listeners", all(k in a2 for k in ("visibilitychange","pageshow","focus")))
    rec("static per-version self-heal sentinel", ("done!==String(j.v)" in a1))
    rec("static badge driven by LDBUILD", ('ld-build' in a1 and 'textContent=window.LDBUILD' in a1))
    rec("static gasPrice=0.2", ('GasPrice.fromString("0.2"' in a3))
    rec("static status element present", ('id="sysStatusApp"' in ah))
    rec("static dayBnd element present", ('id="dayBnd"' in ah))
    # badge/LDBUILD/ver consistency
    ver=json.loads(g("https://127.0.0.1/js/ver.json"))["v"]
    m=re.search(r'window\.LDBUILD="v(\d+)"',a1)
    rec("static LDBUILD==ver.json", m and int(m.group(1))==ver, f"ldb={m.group(1) if m else None} ver={ver}")

async def browser_checks():
    health=json.load(urllib.request.urlopen("http://127.0.0.1:8080/v1/health"))
    ver=json.load(urllib.request.urlopen("http://127.0.0.1:9222/json/version"))
    async with websockets.connect(ver["webSocketDebuggerUrl"], max_size=20*1024*1024) as ws:
        # S0 fresh
        pg,tid=await new_page(ws,"Mozilla/5.0 (Linux; Android 13; Pixel 7) Chrome/120 Mobile Safari/537.36")
        await pg.send("Page.navigate",{"url":BASE}); await asyncio.sleep(6)
        badge=await pg.ev("document.getElementById('ld-build')&&document.getElementById('ld-build').textContent")
        ldb=await pg.ev("window.LDBUILD")
        rec("S0 badge==LDBUILD", badge==ldb, f"{badge}/{ldb}")
        st=await pg.ev("document.getElementById('sysStatusApp')&&document.getElementById('sysStatusApp').textContent")
        rec("S0 status badge==server", (st in ("正常","—")) and (st=="正常")==bool(health["ok"]) or st=="—", f"{st}/{health['ok']}")
        bnd=await pg.ev("document.getElementById('dayBnd')&&document.getElementById('dayBnd').textContent")
        rec("S0 countdown present", bool(bnd) and "倒计时" in (bnd or ""), str(bnd)[:50])
        rec("S0 no exceptions", len(pg.errors)==0)
        await pg.send("Target.closeTarget",{"targetId":tid})
        # S5 offline
        pg,tid=await new_page(ws)
        await pg.send("Page.navigate",{"url":BASE}); await asyncio.sleep(4)
        await pg.send("Network.emulateNetworkConditions",{"offline":True,"latency":0,"downloadThroughput":0,"uploadThroughput":0})
        await asyncio.sleep(2)
        stt=await pg.ev("document.getElementById('sysStatusApp')&&document.getElementById('sysStatusApp').textContent")
        rec("S5 offline graceful", stt in ("—","正常","异常"), f"{stt}")
        await pg.send("Network.emulateNetworkConditions",{"offline":False,"latency":0,"downloadThroughput":10000000,"uploadThroughput":10000000})
        await pg.send("Target.closeTarget",{"targetId":tid})
        # S6 clock-skew +6h
        pg,tid=await new_page(ws)
        await pg.send("Page.addScriptToEvaluateOnNewDocument",{"source":"(function(){var off=6*3600*1000;var R=Date.now;Date.now=function(){return R()+off;};var G=Date.prototype.getTime;Date.prototype.getTime=function(){return G.call(this)+off;};})();"})
        await pg.send("Page.navigate",{"url":BASE}); await asyncio.sleep(6)
        bnd=await pg.ev("document.getElementById('dayBnd')&&document.getElementById('dayBnd').textContent")
        m=re.search(r"倒计时 (\d+):(\d+):(\d+)", bnd or ""); ok=False; d=str(bnd)[:50]
        if m:
            left=int(m.group(1))*3600+int(m.group(2))*60+int(m.group(3))
            srv=health["next_boundary_ts"]-health["now_ts"]
            ok=abs(left-srv)<=120; d+=f" left={left} srv={srv}"
        rec("S6 clock-skew countdown correct", ok, d)
        await pg.send("Target.closeTarget",{"targetId":tid})

static_checks()
asyncio.run(browser_checks())
fails=[r for r in R if not r[1]]
print("TRUTH-MATRIX FAILS: %d"%len(fails))
sys.exit(1 if fails else 0)
