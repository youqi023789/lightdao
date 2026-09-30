#!/usr/bin/env python3
"""dump_locale_seo.py — for each of the 14 locales, load the LIVE new homepage with
?lang=LOC (cleared localStorage) via CDP and capture the rendered localized hero title
(data-i=ht, <br> -> ' ') and hero body (data-i=hb) for use as SEO <title>/og:title/description.
Writes /home/ubuntu/locale_seo.json = {loc: {"title":..., "desc":...}}."""
import asyncio, json, urllib.request, re, html
import websockets

CDP = "http://127.0.0.1:9222"
LOCS = ["zh", "en", "es", "fr", "de", "pt", "ru", "ja", "ko", "ar", "hi", "tr", "vi", "id"]


class Page:
    def __init__(s, ws, sid): s.ws = ws; s.sid = sid; s.mid = 0
    async def send(s, m, p=None):
        s.mid += 1; msg = {"id": s.mid, "method": m, "params": p or {}}
        if s.sid: msg["sessionId"] = s.sid
        await s.ws.send(json.dumps(msg))
        while True:
            r = json.loads(await asyncio.wait_for(s.ws.recv(), timeout=30))
            if r.get("id") == s.mid and (s.sid is None or r.get("sessionId") == s.sid):
                if "error" in r: raise RuntimeError(m)
                return r.get("result", {})
    async def ev(s, e):
        r = await s.send("Runtime.evaluate", {"expression": e, "returnByValue": True})
        return r.get("result", {}).get("value")


async def new_page(ws):
    t = await Page(ws, None).send("Target.createTarget", {"url": "about:blank"})
    a = await Page(ws, None).send("Target.attachToTarget", {"targetId": t["targetId"], "flatten": True})
    pg = Page(ws, a["sessionId"]); await pg.send("Page.enable"); await pg.send("Runtime.enable")
    return pg, t["targetId"]


async def main():
    ver = json.load(urllib.request.urlopen(CDP + "/json/version"))
    out = {}
    async with websockets.connect(ver["webSocketDebuggerUrl"], max_size=20 * 1024 * 1024) as ws:
        pg, tid = await new_page(ws)
        try:
            for loc in LOCS:
                await pg.send("Page.navigate", {"url": "https://lightdao.net/?ts=0"}); await asyncio.sleep(3)
                await pg.ev("localStorage.removeItem('ld_lang')")
                await pg.send("Page.navigate", {"url": "https://lightdao.net/?lang=%s&ts=%d" % (loc, hash(loc) % 9999)}); await asyncio.sleep(4)
                d = await pg.ev("""(function(){
                    var ht=document.querySelector('[data-i="ht"]');
                    var hb=document.querySelector('[data-i="hb"]');
                    var sub=document.querySelector('[data-i="sub"]');
                    return {
                      hlang: document.documentElement.lang,
                      ht_html: ht?ht.innerHTML:'',
                      hb_text: hb?hb.textContent:'',
                      sub_text: sub?sub.textContent:''
                    };
                })()""") or {}
                ht = re.sub(r"<br\s*/?>", " ", d.get("ht_html", "") or "")
                ht = html.unescape(re.sub(r"<[^>]+>", "", ht)).strip()
                desc = (d.get("hb_text") or d.get("sub_text") or "").strip()
                out[loc] = {"title": "LightDAO — " + ht, "desc": desc, "hlang": d.get("hlang")}
                print("[%s] hlang=%s title=%r" % (loc, d.get("hlang"), out[loc]["title"]))
        finally:
            await Page(ws, None).send("Target.closeTarget", {"targetId": tid})
    json.dump(out, open("/home/ubuntu/locale_seo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE /home/ubuntu/locale_seo.json (%d locales)" % len(out))


asyncio.run(main())
