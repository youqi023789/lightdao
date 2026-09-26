#!/usr/bin/env python3
"""Headless-Chrome mobile E2E matrix via CDP.
Profiles: modern android, wechat, qq, ios safari, ios-private(storage throws), old-webview-UA.
Flow per profile: load app -> console/pageerror capture -> import test mnemonic -> main view ->
reload -> auto-login persists -> ld_ref default founder -> landing CTA ref + lang count + theme toggle + live stats.
"""
import asyncio, json, sys, urllib.request

import websockets

CDP_HTTP = "http://127.0.0.1:9222"
MNEM = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
FOUNDER = "wasm19g2hgc28u9c0xxkeyf0fu2dg9k9d8wh8m3fc9v"

PROFILES = {
    "modern_android": ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36", True),
    "wechat": ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.44(0x28002c33) WeChat/arm64", True),
    "qq": ("Mozilla/5.0 (Linux; Android 12; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.58 Mobile Safari/537.36 MQQBrowser/14.2", True),
    "ios_safari": ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1", True),
    "ios_private_storage_throw": ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", True),
    "old_webview_ua": ("Mozilla/5.0 (Linux; Android 7.0; SM-G9300) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.132 Mobile Safari/537.36", False),
}
STORAGE_THROW = ("Object.defineProperty(window,'localStorage',{configurable:true,get:function(){return {getItem:function(){return null;},setItem:function(){throw new DOMException('quota','QuotaExceededError');},removeItem:function(){},clear:function(){}};}});"
 "Object.defineProperty(window,'sessionStorage',{configurable:true,get:function(){return {getItem:function(){return null;},setItem:function(){throw new DOMException('quota','QuotaExceededError');},removeItem:function(){},clear:function(){}};}});")


class Page:
    def __init__(self, ws, sid): self.ws = ws; self.sid = sid; self.mid = 0; self.errors = []
    async def send(self, method, params=None):
        self.mid += 1
        msg = {"id": self.mid, "method": method, "params": params or {}}
        if self.sid: msg["sessionId"] = self.sid
        await self.ws.send(json.dumps(msg))
        while True:
            r = json.loads(await asyncio.wait_for(self.ws.recv(), timeout=30))
            if r.get("method") == "Log.entryAdded" and r["params"]["entry"]["level"] in ("error",):
                self.errors.append("console: " + r["params"]["entry"]["text"][:120])
            if r.get("method") == "Runtime.exceptionThrown":
                d = r["params"]["exceptionDetails"]
                self.errors.append("exception: " + (d.get("exception", {}) or {}).get("description", d.get("text", ""))[:160])
            if r.get("id") == self.mid:
                if "error" in r: raise RuntimeError(method + " -> " + json.dumps(r["error"])[:200])
                return r.get("result", {})
    async def evaljs(self, expr, awaitp=False):
        r = await self.send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": awaitp})
        return r.get("result", {}).get("value")


async def main():
    ver = json.load(urllib.request.urlopen(CDP_HTTP + "/json/version"))
    bws = ver["webSocketDebuggerUrl"]
    results = {}
    async with websockets.connect(bws, max_size=10 * 1024 * 1024) as ws:
        for name, (ua, mobile) in PROFILES.items():
            t = await (Page(ws, None)).send("Target.createTarget", {"url": "about:blank"}) if False else None
            # create target
            mid = [0]
            async def cmd(method, params=None, sid=None):
                mid[0] += 1
                m = {"id": mid[0], "method": method, "params": params or {}}
                if sid: m["sessionId"] = sid
                await ws.send(json.dumps(m))
                while True:
                    r = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
                    if r.get("id") == mid[0]:
                        return r
            r = await cmd("Target.createTarget", {"url": "about:blank"})
            tid = r["result"]["targetId"]
            a = await cmd("Target.attachToTarget", {"targetId": tid, "flatten": True})
            sid = a["result"]["sessionId"]
            pg = Page(ws, sid)
            await pg.send("Page.enable"); await pg.send("Runtime.enable"); await pg.send("Log.enable")
            await pg.send("Emulation.setUserAgentOverride", {"userAgent": ua, "platform": "Android" if "Android" in ua else "iPhone"})
            if mobile:
                await pg.send("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True})
            if name == "ios_private_storage_throw":
                await pg.send("Page.addScriptToEvaluateOnNewDocument", {"source": STORAGE_THROW})
            res = {"errors": [], "steps": {}}
            try:
                await pg.send("Page.navigate", {"url": "https://lightdao.net/app.html"})
                await asyncio.sleep(4)
                ld = await pg.evaljs("!!window.LD")
                res["steps"]["wallet_lib_loaded"] = bool(ld)
                # import mnemonic
                await pg.evaljs('document.getElementById("mnem").value=%s; document.getElementById("btnImport").click();' % json.dumps(MNEM))
                await asyncio.sleep(4)
                main_visible = await pg.evaljs('!document.getElementById("sec-main").classList.contains("hide")')
                res["steps"]["import_then_main_view"] = bool(main_visible)
                # reload -> auto login
                await pg.send("Page.navigate", {"url": "https://lightdao.net/app.html"})
                await asyncio.sleep(4)
                auto = await pg.evaljs('!document.getElementById("sec-main").classList.contains("hide")')
                res["steps"]["reload_auto_login"] = bool(auto) if name != "ios_private_storage_throw" else True  # storage disabled: persistence impossible by design
                ref = await pg.evaljs("(function(){try{return localStorage.getItem('ld_ref');}catch(e){return 'throw';}})()")
                res["steps"]["ld_ref_default_founder"] = (ref == FOUNDER) or (name == "ios_private_storage_throw")
                # landing checks
                await pg.send("Page.navigate", {"url": "https://lightdao.net/"})
                await asyncio.sleep(3)
                cta = await pg.evaljs('(function(){var e=document.querySelector(\'a[href^="/app.html?ref="],[data-go^="/app.html?ref="]\');return e?(e.getAttribute("href")||e.getAttribute("data-go")):null;})()')
                res["steps"]["landing_cta_has_ref"] = bool(cta and FOUNDER in cta)
                langs = await pg.evaljs('document.getElementById("lang").options.length')
                res["steps"]["lang_options_14"] = (langs == 14)
                await pg.evaljs('document.getElementById("themeT").click()')
                th = await pg.evaljs('document.documentElement.getAttribute("data-theme")')
                res["steps"]["theme_toggle_works"] = th in ("light", "dark")
                await asyncio.sleep(3)
                sh = await pg.evaljs('(document.getElementById("sH")||{}).textContent')
                res["steps"]["landing_live_stats"] = bool(sh and sh != "—" and sh != "")
                res["errors"] = pg.errors
            except Exception as e:
                res["fatal"] = str(e)[:200]
                res["errors"] = pg.errors
            results[name] = res
            await cmd("Target.closeTarget", {"targetId": tid})
    ok = True
    for name, r in results.items():
        steps = r.get("steps", {})
        bad = [k for k, v in steps.items() if v is False]
        errs = [e for e in r.get("errors", []) if "QuotaExceeded" not in e]
        status = "PASS" if not bad and not errs and "fatal" not in r else "FAIL"
        if status == "FAIL": ok = False
        print("%-28s %s  bad=%s  errors=%d %s" % (name, status, bad or "-", len(errs), r.get("fatal", "")))
        for e in errs[:3]:
            print("      ", e)
    print("MATRIX", "ALL-PASS" if ok else "HAS-FAILURES")
    sys.exit(0 if ok else 1)

asyncio.run(main())
