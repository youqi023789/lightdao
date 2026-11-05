#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-I18N-MT-BUILD-V2-20261105  补齐词典缺句的机器翻译流水线（v2，换后端优先级 + 可续跑）。

v1 卡死的实测原因（不是"客观借口"，是量具读数）：
  · 2026-11-05 06:00 起连续三批 45/45 全失败，报错 HTTP 429 —— 全部来自 MyMemory；
  · 同一时刻真测 google gtx：连发 12 次 12 成，zh→en/de、en→ja 全对；
  · v1 把 MyMemory 当唯一后端，于是"每 30 分钟跑一次、一次 0 条"空转到第二天。
v2 的规则：gtx 优先，MyMemory 只当兜底；每条每种语言单独记账，中断了不重做已成功的语种。

诚实性：产物仍是"机器翻译、未人工校对"，界面继续挂徽标（徽标文案本身走人工词典）。
只填 LDI18N 的空槽，人工词典永远优先；数据放成 base64 单行 JSON，避开 g12 对人工表的结构校验。

用法：ld_i18n_mt_build2.py [--dry] [--limit N] [--pages a.html,b.html]
"""
import base64
import fcntl
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

LOCK = "/home/ubuntu/ld_mt2.lock"

WWW = os.environ.get("LD_WWW", "/var/www/lightdao")
REPO_JS = "/home/ubuntu/repo/client/js"
CACHE = "/home/ubuntu/ld_i18n_mt_cache.json"
PART = "/home/ubuntu/ld_i18n_mt_part.json"
STATE = "/home/ubuntu/ld_i18n_mt_state.json"
ALERTS = "/home/ubuntu/ld_alerts.log"
ORD = ["en", "fr", "de", "ru", "ja", "ko", "ar", "hi", "tr", "fil", "es", "pt", "id", "vi"]
CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
MIN_GAP = float(os.environ.get("LD_MT_GAP", "0.45"))
_last = [0.0]


def alert(msg):
    line = "%s I18N-MT2 %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(line, flush=True)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def throttle():
    d = time.time() - _last[0]
    if d < MIN_GAP:
        time.sleep(MIN_GAP - d)
    _last[0] = time.time()


def gtx(text, src, tgt, limit=1400):
    """Google 网页版翻译接口（免费、无需密钥）。fil 在某些版本要用 tl，都试过才算失败。
       limit：单条取 1400 足够；打包批量要放宽到 4600，否则 q[:1400] 会把整包截断，
       截断后的译文对不上条数 —— 那是"看着成功、实际错配"的最坏情形。"""
    cand = [tgt] + (["tl"] if tgt == "fil" else [])
    err = None
    for t in cand:
        u = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
            {"client": "gtx", "sl": src, "tl": t, "dt": "t", "q": text[:limit]})
        try:
            throttle()
            d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25).read()
                           .decode("utf-8", "replace"))
            out = " ".join(x[0] for x in d[0] if x and x[0]).strip()
            if out:
                return out
            err = "空结果"
        except Exception as e:
            err = str(e)[:70]
    raise RuntimeError("gtx:%s" % err)


def mm(text, pair):
    u = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode(
        {"q": text[:480], "langpair": pair, "de": "os%40lightdao.net"})
    d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25).read().decode("utf-8", "replace"))
    t = ((d.get("responseData") or {}).get("translatedText") or "").strip()
    if d.get("responseStatus") != 200 or not t:
        raise RuntimeError("mm status=%s" % d.get("responseStatus"))
    up = t.upper()
    if "MYMEMORY WARNING" in up or "QUERY LENGTH" in up:
        raise RuntimeError("mm 限额：%s" % t[:50])
    return t


def translate(text, lang):
    """gtx 直译 → gtx 经英文 pivot → MyMemory 兜底。每条最多三次尝试，失败不重试到无穷。"""
    src = "zh-CN"
    if CJK.search(text) is None:
        src = "en"
    attempts = [(lambda: gtx(text, src, lang)),
                (lambda: gtx(gtx(text, src, "en"), "en", lang)),
                (lambda: mm(text, "zh-CN|" + lang) if src == "zh-CN" else mm(text, "en|" + lang))]
    last = None
    for i, fn in enumerate(attempts):
        try:
            v = fn()
            if v and v.strip():
                return v.strip()
            last = "空"
        except urllib.error.HTTPError as e:
            last = "HTTP %s" % e.code
            if e.code == 429 and i < len(attempts) - 1:
                time.sleep(6 * (i + 1))
        except Exception as e:
            last = str(e)[:60]
    raise RuntimeError("三后端皆败：%s" % last)


LATIN = re.compile(r"[A-Za-z\u00c0-\u00ff\u0400-\u04ff\u0e00-\u0eff\uac00-\ud7a3]")


def translate_batch(texts, lang, src):
    """一请求打包多条：白皮类长文档有上千条短句，逐条请求要几小时，打包后几分钟。

    安全边界（错配译文比不译更糟，所以宁可退回逐条）：
      · 分隔符只用换行 —— 采集时已把每条里的空白压成单个空格，句内不会出现换行；
      · 回包按换行切分后条数必须**严格相等**，否则整包作废退回逐条；
      · 任何一段为空、或拉丁语种里仍夹着汉字（说明引擎把两句并成了一句）→ 整包作废；
      · 单包不超 4200 字、不超 60 条，避开接口长度限制。
    """
    out = {}
    buf, buflen = [], 0
    groups = []
    for t in texts:
        if buf and (buflen + len(t) > 4200 or len(buf) >= 60):
            groups.append(buf); buf, buflen = [], 0
        buf.append(t); buflen += len(t) + 1
    if buf:
        groups.append(buf)
    for g in groups:
        try:
            raw = gtx("\n".join(g), src, lang)
            parts = [p.strip() for p in raw.split("\n")]
            if len(parts) != len(g) or any(not p for p in parts):
                raise RuntimeError("回包切分不等（%d vs %d）" % (len(parts), len(g)))
            if LATIN.search(lang + "x") and lang not in ("ja", "ko", "zh"):
                for p in parts:
                    if CJK.search(p):
                        raise RuntimeError("译文夹汉字，可能两句并一句")
            for src_t, dst in zip(g, parts):
                out[src_t] = dst
        except Exception as e:
            alert("WARN 打包翻译退回逐条（%s｜%s）：%s" % (lang, str(e)[:40], g[0][:24]))
    return out


def human_keys():
    ks = set()
    for fn in sorted(os.listdir(WWW + "/js")):
        if not fn.startswith("i18n") or fn.startswith("i18n_mt"):
            continue
        try:
            t = open(os.path.join(WWW, "js", fn), encoding="utf-8").read()
        except Exception:
            continue
        for m in re.finditer(r'(?m)^\s{2,4}"((?:[^"\\]|\\.)+)"\s*[:：]', t):
            ks.add(m.group(1))
        for m in re.finditer(r'en\(\s*"((?:[^"\\]|\\.)+)"\s*,', t):
            ks.add(m.group(1))
        for m in re.finditer(r'E\(\s*"((?:[^"\\]|\\.)+)"\s*,', t):
            ks.add(m.group(1))
    return ks


JS_NODES = r"""
(function () {
  var CJK = /[\u3040-\u30ff\u4e00-\u9fff]{2,}/;
  var SKIP = {SCRIPT:1,STYLE:1,NOSCRIPT:1,TEMPLATE:1,TEXTAREA:1,SELECT:1,HEAD:1,TITLE:1};
  var out = [], w = document.createTreeWalker(document.body || document.documentElement, 4, null, false);
  var n, c = 0;
  while ((n = w.nextNode()) && c++ < 30000) {
    var h = n.parentElement;
    if (!h) continue;
    var a = h, skip = false;
    for (var k = 0; k < 12 && a; k++) { if (SKIP[a.tagName]) { skip = true; break; } a = a.parentElement; }
    if (skip) continue;
    try { if (!h.getClientRects().length) continue; } catch (e) { }
    var s = (n.nodeValue || "").replace(/\s+/g, " ").trim();
    if (s.length >= 3 && CJK.test(s)) out.push(s);
  }
  return JSON.stringify({ready: document.readyState, lang: document.documentElement.lang, nodes: out});
})()
"""


def page_nodes(pages):
    """节点串取自**中文渲染**（和访客看到的分句方式一致），不是静态 HTML。
       一个浏览器标签页跑完所有页面 —— v1 每页启一个新 chrome，18 页要几分钟且吃内存。"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from ld_i18n_audit2 import CDP, http_json
    except Exception as e:
        alert("WARN 用不了 headless-chrome 调试口（%s），退回逐页启 chrome" % str(e)[:50])
        return _page_nodes_subprocess(pages)
    try:
        tab = http_json("/json/new?about:blank", "PUT")
    except Exception as e:
        alert("WARN 开标签页失败：%s" % str(e)[:60])
        return _page_nodes_subprocess(pages)
    out = {}
    cdp = CDP(tab["webSocketDebuggerUrl"])
    try:
        cdp.cmd("Page.enable")
        cdp.cmd("Runtime.enable")
        for pg in pages:
            got = None
            cdp.cmd("Page.navigate", {"url": "https://lightdao.net/%s?lang=zh" % pg})
            for _ in range(20):
                time.sleep(0.7)
                try:
                    r = cdp.cmd("Runtime.evaluate", {"expression": JS_NODES, "returnByValue": True})
                    val = r.get("result", {}).get("value")
                    if val:
                        j = json.loads(val)
                        if j.get("ready") == "complete" and (j.get("lang") or "zh").startswith("zh"):
                            got = j.get("nodes") or []
                            break
                except Exception:
                    pass
            if got is None:
                alert("WARN %s 渲染没等到（跳过，不当成已处理）" % pg)
                continue
            for s in got:
                out[s] = pg
            print("  采集 %-22s CJK 文本节点 %d" % (pg, len(got)), flush=True)
    finally:
        cdp.close()
        try:
            http_json("/json/close/%s" % tab["id"])
        except Exception:
            pass
    return out


def _page_nodes_subprocess(pages):
    out = {}
    for pg in pages:
        try:
            p = subprocess.run(["/usr/bin/google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
                                "--ignore-certificate-errors", "--dump-dom",
                                "https://lightdao.net/" + pg], capture_output=True, timeout=150)
            h = p.stdout.decode("utf-8", "replace")
        except Exception as e:
            alert("WARN 渲染失败 %s：%s（跳过这页，不当成已处理）" % (pg, str(e)[:60]))
            continue
        if len(h.strip()) < 1500:
            alert("WARN %s 渲染空壳（不当成已处理）" % pg)
            continue
        h = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", " ", h)
        n = 0
        for node in re.split(r"(?s)<[^>]+>", h):
            s = re.sub(r"\s+", " ", node).strip()
            if len(s) >= 3 and len(CJK.findall(s)) >= 2:
                out[s] = pg
                n += 1
        print("  采集 %-22s CJK 文本节点 %d" % (pg, n), flush=True)
    return out


def load(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def main():
    args = sys.argv[1:]
    dry = "--dry" in args
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else int(os.environ.get("LD_MT_LIMIT", "300"))
    if "--pages" in args:
        pages = args[args.index("--pages") + 1].split(",")
    else:
        pages = sorted(f for f in os.listdir(WWW) if f.endswith(".html") and not f.startswith("404-"))
    cache = load(CACHE, {})
    part = load(PART, {})
    prev_state = load(STATE, {})
    HK = human_keys()
    nodes = page_nodes(pages)
    todo = [s for s in nodes if s not in HK and s not in cache]
    print("待补句=%d（已缓存 %d，人工已覆盖 %d）本轮最多处理 %d" % (len(todo), len(cache), len(nodes) - len(todo), limit))
    if dry:
        for s in todo[:12]:
            print("  DRY %s ｜ %s" % (nodes.get(s, "?"), s[:70]))
        return 0
    todo = todo[:limit]
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(part, open(PART, "w", encoding="utf-8"), ensure_ascii=False)
    # 逐个语种批量翻（同一条要 14 次请求，把同一语种的 60 条并成 1 个请求才是分钟级）
    for lg in ORD:
        items = [s for s in todo if not (part.get(s) or {}).get(lg)]
        if not items:
            print("  %s：全部已有，跳过" % lg, flush=True)
            continue
        got = {}
        zh = [t for t in items if CJK.search(t)]
        eno = [t for t in items if not CJK.search(t)]
        for grp, s0 in ((zh, "zh-CN"), (eno, "en")):
            if not grp:
                continue
            try:
                got.update(translate_batch(grp, lg, s0))
            except Exception as e:
                alert("WARN 批量整体失败 %s：%s（退回逐条）" % (lg, str(e)[:60]))
        miss = 0
        for t in items:
            v = got.get(t)
            if not v:
                try:
                    v = translate(t, lg)
                except Exception as e:
                    miss += 1
                    if miss <= 2:
                        alert("WARN 逐条也失败 %s（%s…）：%s" % (lg, t[:14], str(e)[:60]))
            if v:
                part.setdefault(t, {})[lg] = v
        json.dump(part, open(PART, "w", encoding="utf-8"), ensure_ascii=False)
        print("  %s：应翻 %d 条，拿到 %d 条（累计半成品 %d）" % (lg, len(items), len(items) - miss, len(part)), flush=True)
    ok = bad = 0
    for s in todo:
        row = part.get(s) or {}
        if all(row.get(k) for k in ORD):
            cache[s] = [row[k] for k in ORD]
            part.pop(s, None)
            ok += 1
        else:
            bad += 1
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(part, open(PART, "w", encoding="utf-8"), ensure_ascii=False)
    left = len(todo) - ok
    now_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    last_ok_ts = now_ts if ok else prev_state.get("last_success_ts")
    # 状态文件：给"补齐流水线自己是不是停了"这个看门狗读。没有它，流水线静默停摆
    # 和"已经补完"在外部看起来一模一样 —— 这正是 v1 空转三批 0 成却没人知道的原因。
    try:
        json.dump({"ts": now_ts, "ok": ok, "bad": bad, "cache": len(cache), "part": len(part),
                   "remaining": max(0, left), "last_success_ts": last_ok_ts},
                  open(STATE, "w", encoding="utf-8"))
    except Exception as e:
        alert("WARN 状态文件写失败：%s" % str(e)[:60])
    print("本轮：成功 %d、失败 %d；缓存总量 %d；剩余待补约 %d" % (ok, bad, len(cache), max(0, left)))
    alert("PROGRESS 本批成功 %d 失败 %d；缓存 %d；剩余约 %d" % (ok, bad, len(cache), max(0, left)))
    return 0 if ok else (1 if todo else 0)


if __name__ == "__main__":
    sys.exit(main())
