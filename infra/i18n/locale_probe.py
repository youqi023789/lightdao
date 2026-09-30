#!/usr/bin/env python3
"""locale_probe.py — render live homepage in each locale via CDP, detect literal <br> bug.
Single-reader CDP. Reports per-lang: documentElement.lang, [data-i=ht].innerHTML,
whether textContent contains a literal '<br>' (BUG), and title."""
import asyncio, json, sys, urllib.request
import websockets

CDP = "http://127.0.0.1:9222"
URL = "https://lightdao.net/?ts=" + str(__import__("time").time())
LANGS = ["zh", "en", "ja", "ar", "vi", "de", "ko", "es", "fr", "pt", "ru", "hi", "tr", "id"]


class Page:
    def __init__(s, ws, sid): s.ws = ws; s.sid = sid; s.mid = 0
    async def send(s, m, p=None):
        s.mid += 1; msg = {"id": s.mid, "method": m, "params": p or {}}
        if s.sid: msg["sessionId"] = s.sid
        await s.ws.send(json.dumps(msg))
        while True:
            r = json.loads(await asyncio.wait_for(s.ws.recv(), timeout=30))
            if r.get("id") == s.mid and (s.sid is None or r.get("sessionId") == s.sid):
                if "error" in r: raise RuntimeError(m + ": " + str(r["error"]))
                return r.get("result", {})
    async def ev(s, e, aw=False):
        r = await s.send("Runtime.evaluate", {"expression": e, "returnByValue": True, "awaitPromise": aw})
        return r.get("result", {}).get("value")


async def new_page(ws):
    t = await Page(ws, None).send("Target.createTarget", {"url": "about:blank"})
    a = await Page(ws, None).send("Target.attachToTarget", {"targetId": t["targetId"], "flatten": True})
    pg = Page(ws, a["sessionId"])
    await pg.send("Page.enable"); await pg.send("Runtime.enable")
    return pg, t["targetId"]


async def main():
    ver = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json/version"))
    bug_langs = []
    async with websockets.connect(ver["webSocketDebuggerUrl"], max_size=20 * 1024 * 1024) as ws:
        pg, tid = await new_page(ws)
        try:
            await pg.send("Page.navigate", {"url": URL}); await asyncio.sleep(6)
            for lang in LANGS:
                await pg.ev("localStorage.setItem('ld_lang','%s')" % lang)
                await pg.send("Page.navigate", {"url": URL}); await asyncio.sleep(3)
                info = await pg.ev("""(function(){
                    var el=document.querySelector('[data-i="ht"]');
                    var fin=document.querySelector('[data-i="finH"]');
                    return {
                      hlang: document.documentElement.lang,
                      ht_html: el?el.innerHTML:null,
                      ht_text: el?el.textContent:null,
                      fin_text: fin?fin.textContent:null,
                      title: document.title
                    };
                })()""")
                ht_text = (info or {}).get("ht_text") or ""
                fin_text = (info or {}).get("fin_text") or ""
                has_bug = ("<br>" in ht_text) or ("<br>" in fin_text)
                if has_bug: bug_langs.append(lang)
                print("[%s] hlang=%s BUG=%s" % (lang, (info or {}).get("hlang"), has_bug))
                print("     ht_html=%r" % ((info or {}).get("ht_html")))
                print("     ht_text=%r" % (ht_text[:120]))
        finally:
            await Page(ws, None).send("Target.closeTarget", {"targetId": tid})
    print("=== LANGS WITH LITERAL <br> BUG: %s ===" % (bug_langs or "none"))
    sys.exit(1 if bug_langs else 0)


asyncio.run(main())
