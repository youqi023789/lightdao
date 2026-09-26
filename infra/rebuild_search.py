#!/usr/bin/env python3
import json, os, re
WWW="/var/www/lightdao"
def strip(h):
    h=re.sub(r"<script[\s\S]*?</script>"," ",h); h=re.sub(r"<style[\s\S]*?</style>"," ",h); return h
pages=["index.html","app.html","explorer.html","governance.html","whitepaper.html","season.html","blog.html","privacy.html","terms.html","nodes.html","invest.html"]
idx=[]
for p in pages:
    path=os.path.join(WWW,p)
    if not os.path.exists(path): continue
    raw=open(path,encoding="utf-8").read()
    url="/" if p=="index.html" else "/"+p
    tm=re.search(r"<title>(.*?)</title>",raw,re.S); title=tm.group(1).strip() if tm else url
    secs=[]
    for m in re.finditer(r"<(h1|h2|h3)[^>]*>(.*?)</\1>",raw,re.S):
        head=re.sub(r"<[^>]+>","",m.group(2)).strip()
        if not head: continue
        pre=raw[:m.start()]; idm=None
        for sm in re.finditer(r'id="([A-Za-z0-9_-]+)"',pre): idm=sm
        nxt=re.search(r"<(h1|h2|h3)\b",raw[m.end():])
        chunk=raw[m.end():m.end()+(nxt.start() if nxt else 600)]
        text=re.sub(r"<[^>]+>"," ",chunk); text=re.sub(r"\s+"," ",text).strip()[:400]
        secs.append({"head":head,"id":idm.group(1) if idm else "","text":text or head})
    if not secs:
        b=re.sub(r"<[^>]+>"," ",strip(raw)); b=re.sub(r"\s+"," ",b).strip()[:400]
        secs.append({"head":"","id":"","text":b})
    idx.append({"url":url,"title":title,"sections":secs})
json.dump(idx,open(WWW+"/search-index.json","w",encoding="utf-8"),ensure_ascii=False)
print("search index rebuilt:",len(idx),"pages")
