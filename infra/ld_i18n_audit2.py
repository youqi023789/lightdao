#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_i18n_audit2.py —— 分语种"真机渲染 + 出处定位"多语言普查（量具，不改任何东西）。

为什么换量具（三条都是踩过的坑，不是追求完美）：
 1) 旧量具只报"还剩几条中文"，不报"这条中文挂在 DOM 的哪一层"，于是只能靠猜。这里给每个
    片段打路径签名（最近 6 层祖先的 tag#id.class），直接点名"是 nav.js 生成的导航、还是页面正文"。
 2) 口径混算：funds/institutions 等页**刻意**中英并列（旁边就挂着一个 <span class="en">英文），
    那不是漏翻；算进残留会虚高上百条。这里拆成"真漏翻"与"中英并列(设计如此)"两栏分开报。
 3) 旧量具语种表漏了 ja（14 语种只测 13 个），日语坏了没人发现。这里 14 个语种全跑。
 4) 只统计**看得见**的文字（getClientRects 为空 = 被 CSS 藏起来 = 用户看不到，不计）。
    此前 nav.js 会隐藏页内旧的返回行，把它当残留算过。
 5) 日语/韩语的译文本身就含汉字 —— 早期量具把「白書」「オンチェーン実測」这类**正常译文**
    当成漏翻，于是日语页面永远修不完（假故障）。现在先渲染一份中文版拿到"源串清单"，
    只有和源串一模一样的才算真漏翻；译文里夹带的汉字另列"夹生"栏，参考但不算漏翻。

实现：连本机已有的 headless-chrome（127.0.0.1:9222，qa_truth 用的那个），在页面里真跑
JS 遍历渲染后的 DOM —— 而不是拿静态 HTML 猜，也不是另起一个 chrome 进程（省内存）。
连不上就明确退出码 2，绝不静默降级成"静态测量"冒充"真机测量"。

用法：
  ld_i18n_audit2.py                                  # 全站 × 14 语种汇总
  ld_i18n_audit2.py --pages app.html --locale de --show 12
退出码：0=真漏翻 0 条；1=有真漏翻（可挂 cron 告警）；2=渲染/连接失败。
"""
import json
import os
import re
import socket
import base64
import struct
import sys
import time
import urllib.request

CDP_HOST, CDP_PORT = "127.0.0.1", int(os.environ.get("LD_AUDIT_CDP", "9222"))
# 默认量**线上**（用户真正看到的那份）；要看预发布用 --base http://127.0.0.1:8093
BASE = os.environ.get("LD_AUDIT_BASE", "https://lightdao.net")
DEFAULT_PAGES = ["index.html", "app.html", "institutions.html", "funds.html", "governance.html",
                 "nodes.html", "contracts.html", "whitepaper.html", "audit_logic.html", "landing.html"]
LOCALES = ["en", "de", "fr", "ru", "ja", "ko", "ar", "hi", "tr", "fil", "es", "pt", "id", "vi"]

JS = r"""
(function () {
  var CJK = /[\u3040-\u30ff\u4e00-\u9fff]{2,}/g;
  var NATIVE = {"中文":1,"日本語":1,"한국어":1,"العربية":1,"हिन्दी":1,"繁體":1,"Русский":1,
    "Deutsch":1,"Français":1,"Português":1,"Español":1,"Tiếng":1,"Bahasa":1,"Türkçe":1,
    "Filipino":1,"简体中文":1,"繁體中文":1};
  var SKIP = {SCRIPT:1,STYLE:1,NOSCRIPT:1,TEMPLATE:1,TEXTAREA:1,HEAD:1,TITLE:1,SELECT:1};
  var BI = /(^|[\s_\-])(en|dual|bilingual|gloss)(?=$|[\s_\-])/i;
  function cls(n){ try { return (typeof n.className === "string" ? n.className : "") || ""; } catch (e) { return ""; } }
  function sig(el){
    var out = [], n = el, i = 0;
    while (n && n.nodeType === 1 && i++ < 6) {
      var t = n.tagName.toLowerCase();
      var s = t;
      if (n.id) s += "#" + String(n.id).slice(0, 18);
      else { var c = cls(n).trim().split(/\s+/)[0]; if (c) s += "." + c.slice(0, 18); }
      out.unshift(s); n = n.parentElement;
    }
    return out.join(">");
  }
  function visible(n){ try { return !!(n.getClientRects && n.getClientRects().length); } catch (e) { return true; } }
  function biPartner(el){
    /* 同一父/祖先生级里挂着一个"对照"块（class 含 en/dual/gloss）且其中是纯拉丁文 → 判为设计如此 */
    var p = el;
    for (var up = 0; up < 4 && p; up++) {
      var par = p.parentElement;
      if (par) {
        var kids = par.children || [];
        for (var j = 0; j < kids.length; j++) {
          if (!BI.test(cls(kids[j]))) continue;
          var tx = kids[j].textContent || "";
          if (/[A-Za-z\u00c0-\u00ff]{8,}/.test(tx) && !/[\u3040-\u30ff\u4e00-\u9fff]/.test(tx)) return 1;
        }
      }
      if (BI.test(cls(p))) return 1;
      p = par;
    }
    return 0;
  }
  var real = [], bi = [], seen = {}, fbenList = [], nativeSkipped = 0;
  /* 静默显英文检测：某条文字在词典里**有**本语种译文，页面上却显示着英文 —— 这是最隐蔽的一类
     （德语页面 = 德语正文 + 英语导航）。它不含汉字，所以"找中文"的量具永远看不见。
     判据：节点文本等于某个键的 en 值，而该键在本语种有**不同**的译文。 */
  var EN2KEY = {};
  try {
    for (var kk in window.LDI18N) {
      var ev = (window.LDI18N[kk] || {}).en;
      if (typeof ev === "string" && ev.length > 2) { (EN2KEY[ev] = EN2KEY[ev] || []).push(kk); }
    }
  } catch (e0) { }
  var curlang = (document.documentElement.getAttribute("lang") || "zh").toLowerCase().split("-")[0];
  var root = document.body || document.documentElement;
  var w = document.createTreeWalker(root, 4 /* TEXT */, null, false);
  var node, count = 0;
  while ((node = w.nextNode()) && count++ < 20000) {
    var host = node.parentElement;
    if (!host) continue;
    var anc = host, skip = false;
    for (var k = 0; k < 12 && anc; k++) { if (SKIP[anc.tagName]) { skip = true; break; } anc = anc.parentElement; }
    if (skip) continue;
    if (!visible(host)) continue;
    var m = (node.nodeValue || "").match(CJK);
    if (!m) continue;
    var txt = (node.nodeValue || "").replace(/\s+/g, " ").trim();
    var isBi = biPartner(host);
    /* 日语/韩语的**正常译文本身就用汉字/混排**：「資金とリリース」里切出来的「資金」正好等于
       某个中文源串，就会被当成漏翻（实测 governance.html?lang=ja 报的 40 个"残留"全是
       ホーム/採掘/クライアント 这类正常日语）。判据：节点里出现假名/谚文就说明它已是日/韩文，
       不再按汉字片段判漏翻，但单独计数，不悄悄吞掉。
       另一个假缺口来源：翻译器二次重扫时拿**已经是日语**的文本去问中文键词典
       （ja|採掘、ja|検索…），那是"重复提问"不是"漏翻"，所以这里同样跳过。 */
    var nativeScript = (curlang === "ja" && /[\u3040-\u30ff]/.test(txt))
                    || (curlang === "ko" && /[\uac00-\ud7a3]/.test(txt));
    if (nativeScript) { nativeSkipped++; continue; }
    /* 站内有一批刻意写成「中文 / English」的对照标签（页脚、返回行、卡片小标题）：
       中文侧是本意，英文侧由 i18n 换成本语种 —— 不算漏翻，但单列数量看得见。 */
    if (!isBi && /[一-鿿]{2,}\s*\/\s*[A-Za-zÀ-ÿ]/.test(txt)) isBi = 1;
    var fben = null;
    if (curlang !== "zh" && curlang !== "en" && !CJK.test(txt) && /[A-Za-z\u00c0-\u00ff]{3,}/.test(txt)
        && EN2KEY[txt]) {
      for (var z = 0; z < EN2KEY[txt].length; z++) {
        var e2 = window.LDI18N[EN2KEY[txt][z]] || {};
        if (e2[curlang] && e2[curlang] !== txt) { fben = [txt, EN2KEY[txt][z], e2[curlang]]; break; }
      }
    }
    for (var q = 0; q < m.length; q++) {
      var f = m[q];
      if (NATIVE[f]) continue;
      var key = f + "\u0001" + sig(host) + "\u0001" + isBi;
      if (seen[key]) continue;
      seen[key] = 1;
      (isBi ? bi : real).push([f, sig(host)]);
    }
    if (fben) {
      var k2 = "FB\u0001" + fben[0] + "\u0001" + sig(host);
      if (!seen[k2]) { seen[k2] = 1; fbenList.push([fben[0], sig(host), fben[1], fben[2]]); }
    }
  }
  var de = document.documentElement, bd = document.body;
  function ds(k){ try { return (de && de.dataset && de.dataset[k]) || (bd && bd.dataset && bd.dataset[k]) || null; } catch (e) { return null; } }
  return JSON.stringify({
    ready: document.readyState,
    lang: (de && de.lang) || null,
    href: location.href.slice(0, 120),
    tgaps: ds("ldTgaps"), tgapfb: ds("ldTgapFb"), i18n: ds("ldI18n"),
    hasT: typeof window.__ldT,
    navFallback: (window.__ldNavFallback === undefined ? null : window.__ldNavFallback),
    real: real, bi: bi, fben: fbenList, nativeSkipped: nativeSkipped
  });
})()
"""


class CDP:
    def __init__(self, ws_url, timeout=40):
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)", ws_url)
        if not m:
            raise RuntimeError("bad ws url " + ws_url)
        host, port, path = m.group(1), int(m.group(2)), m.group(3)
        self.s = socket.create_connection((host, port), timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ("GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n" % (path, host, port, key))
        self.s.sendall(req.encode())
        self.buf = b""
        resp = self._read_until(b"\r\n\r\n")
        if b" 101 " not in resp.split(b"\r\n")[0]:
            raise RuntimeError("ws handshake failed: " + resp[:80].decode("utf-8", "replace"))
        self.id = 0
        self.timeout = timeout

    def _recv(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(65536)
            if not chunk:
                raise RuntimeError("ws closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _read_until(self, delim):
        while delim not in self.buf:
            chunk = self.s.recv(65536)
            if not chunk:
                raise RuntimeError("ws closed during handshake")
            self.buf += chunk
        i = self.buf.index(delim) + len(delim)
        out, self.buf = self.buf[:i], self.buf[i:]
        return out

    def _frame(self):
        hdr = self._recv(2)
        fin = hdr[0] >> 7
        op = hdr[0] & 0x0F
        ln = hdr[1] & 0x7F
        if ln == 126:
            ln = struct.unpack(">H", self._recv(2))[0]
        elif ln == 127:
            ln = struct.unpack(">Q", self._recv(8))[0]
        pl = self._recv(ln) if ln else b""
        return fin, op, pl

    def cmd(self, method, params=None, session=None):
        self.id += 1
        m = {"id": self.id, "method": method, "params": params or {}}
        if session:
            m["sessionId"] = session
        self._send(json.dumps(m))
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            data = b""
            while True:
                fin, op, pl = self._frame()
                if op == 8:
                    raise RuntimeError("ws close from peer")
                if op in (1, 2):
                    data += pl
                if fin:
                    break
            try:
                j = json.loads(data.decode("utf-8", "replace"))
            except Exception:
                continue
            if j.get("id") == self.id:
                if "error" in j:
                    raise RuntimeError("%s -> %s" % (method, j["error"].get("message", "?")))
                return j.get("result", {})
        raise RuntimeError("timeout waiting for " + method)

    def _send(self, s):
        b = s.encode("utf-8")
        hdr = bytearray([0x81])
        n = len(b)
        mask = os.urandom(4)
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr.append(0x80 | 126); hdr += struct.pack(">H", n)
        else:
            hdr.append(0x80 | 127); hdr += struct.pack(">Q", n)
        hdr += mask
        hdr += bytes(x ^ mask[i % 4] for i, x in enumerate(b))
        self.s.sendall(bytes(hdr))

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


def http_json(path, method="GET"):
    req = urllib.request.Request("http://%s:%d%s" % (CDP_HOST, CDP_PORT, path), method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def run_audit(pages, locales, show, base):
    """自己开一个标签页跑，跑完关掉 —— 不去占用 headless-chrome 里已有的页面。"""
    try:
        tab = http_json("/json/new?about:blank", "PUT")
    except Exception as e:
        # 绝不退回去"借用别人的标签页"：两个量者共用一个页面时会互相导航，
        # 结果就是一边读数正常、另一边满屏 ERR（实测这样误判过 3 页"渲染失败"）。
        raise RuntimeError("开不了自己的标签页（%s）——拒绝借用别人的页面，避免互相导航污染" % str(e)[:60])
    if "webSocketDebuggerUrl" not in (tab or {}):
        raise RuntimeError("新标签页没有调试地址，拒跑")
    own = True
    cdp = CDP(tab["webSocketDebuggerUrl"])
    try:
        cdp.cmd("Page.enable")
        cdp.cmd("Runtime.enable")
        out = {}
        for pg in pages:
            for loc in locales:
                url = "%s/%s?lang=%s" % (base, pg, loc)
                cdp.cmd("Page.navigate", {"url": url})
                res = None
                for _ in range(24):
                    time.sleep(0.75)
                    try:
                        r = cdp.cmd("Runtime.evaluate", {"expression": JS, "returnByValue": True,
                                                         "awaitPromise": True})
                        val = r.get("result", {}).get("value")
                        if not val:
                            continue
                        got = json.loads(val)
                        # 只有"页面真的切到目标语种并且词典已应用"才算测完了这一格；
                        # 否则继续等 —— 拿中文渲染结果冒充德语残留是量具级错误。
                        applied = (got.get("lang") or "").lower().replace("_", "-")
                        if (got.get("ready") == "complete" and applied.startswith(loc)
                                and got.get("i18n")):
                            res = got
                            break
                    except Exception:
                        time.sleep(0.4)
                if res is None:
                    print("  !! %s?lang=%s 渲染/语种未生效（不当成 0 残留）" % (pg, loc))
                    out[(pg, loc)] = None
                else:
                    out[(pg, loc)] = res
    finally:
        cdp.close()
        if own:
            try:
                http_json("/json/close/%s" % tab["id"])
            except Exception:
                pass
    return out


def classify(res, base, pages, locales):
    """把命中拆成三类，避免量具自欺：
       真漏翻   = 这段中文在该页中文版里也出现（就是没翻的源串）
       夹生     = 目标语种页面上出现的 CJK，但不在中文源串里 —— 多为日/韩译文里合法汉字，
                  或机翻把中文留在句子里；单独报数，不计入漏翻（否则日语页面永远"没修好"）。
       中英并列 = 旁边挂着对照英文块，设计如此。"""
    out = {}
    for pg in pages:
        zset = set()
        b = base.get((pg, "zh"))
        if b:
            zset = set(f for f, _ in b["real"]) | set(f for f, _ in b["bi"])
        for loc in locales:
            r = res.get((pg, loc))
            if r is None:
                out[(pg, loc)] = None
                continue
            miss = [h for h in r["real"] if h[0] in zset]
            mix = [h for h in r["real"] if h[0] not in zset]
            out[(pg, loc)] = {"miss": miss, "mix": mix, "bi": r["bi"], "fben": r.get("fben") or [],
                              "nsk": r.get("nativeSkipped") or 0,
                              "tgaps": r.get("tgaps"), "tgapfb": r.get("tgapfb"),
                              "lang": r.get("lang"), "navFallback": r.get("navFallback")}
    return out


def main():
    args = sys.argv[1:]
    pages = DEFAULT_PAGES
    locales = LOCALES
    show = 8
    if "--pages" in args:
        pages = [p for p in args[args.index("--pages") + 1].split(",") if p]
    if "--locale" in args:
        locales = [args[args.index("--locale") + 1]]
    if "--show" in args:
        show = int(args[args.index("--show") + 1])
    if "--base" in args:
        globals()["BASE"] = args[args.index("--base") + 1]
    try:
        base = run_audit(pages, ["zh"], show, BASE)
        res = run_audit(pages, locales, show, BASE)
    except Exception as e:
        print("量具故障（不冒充测量结果）：%s" % str(e)[:160])
        return 2
    cells = classify(res, base, pages, locales)
    tot_real = tot_bi = tot_mix = tot_fben = fails = 0
    sig_tally = {}
    mix_tally = {}
    fben_tally = {}
    gaps_t = {}
    for pg in pages:
        pr = pb = pm = page_fb = page_nsk = 0
        per = []
        for loc in locales:
            r = cells.get((pg, loc))
            if r is None:
                fails += 1
                per.append("%s:ERR" % loc)
                continue
            n = len(set(f for f, _ in r["miss"]))
            pr += n
            pb += len(set(f for f, _ in r["bi"]))
            pm += len(set(f for f, _ in r["mix"]))
            page_fb += len(set(x[0] for x in r["fben"]))
            page_nsk += int(r.get("nsk") or 0)
            per.append("%s:%d" % (loc, n))
            if r.get("tgaps") not in (None, "0") or r.get("tgapfb") not in (None, "0"):
                gaps_t[(pg, loc)] = "tgaps=%s fb=%s" % (r.get("tgaps"), r.get("tgapfb"))
            for f, s in r["miss"]:
                t = sig_tally.setdefault(s, {"n": 0, "ex": set(), "pg": set()})
                t["n"] += 1
                t["ex"].add(f)
                t["pg"].add(pg)
            for x in r["fben"]:
                t = fben_tally.setdefault(x[1], {"n": 0, "ex": set(), "pg": set(), "want": set()})
                t["n"] += 1
                t["ex"].add(x[0])
                t["pg"].add(pg)
                t["want"].add("%s→%s" % (x[2][:14], x[3][:22]))
            for f, s in r["mix"]:
                t = mix_tally.setdefault(s, {"n": 0, "ex": set(), "pg": set()})
                t["n"] += 1
                t["ex"].add(f)
                t["pg"].add(pg)
        tot_real += pr
        tot_bi += pb
        tot_mix += pm
        tot_fben += page_fb
        print("%-20s 真漏翻=%-5d 静默显英文=%-5d 译文夹生CJK=%-5d 中英并列=%-5d 日韩正常译文节点=%-5d %s"
              % (pg, pr, page_fb, pm, pb, page_nsk, " ".join(per)))
    print("\n合计：真漏翻=%d ｜ 静默显英文=%d ｜ 译文夹生CJK(多为日韩合法汉字)=%d ｜ 中英并列(不计)=%d ｜ 渲染失败=%d"
          % (tot_real, tot_fben, tot_mix, tot_bi, fails))
    if gaps_t:
        print("运行时取词缺口非零：%s" % "; ".join("%s?%s=%s" % (p, l, v) for (p, l), v in list(gaps_t.items())[:6]))
    nf = [(k, cells[k].get("navFallback")) for k in cells if cells[k] and cells[k].get("navFallback")]
    if nf:
        print("导航退回旧小表(NAVEN)计数：%s" % "; ".join("%s?%s=%s" % (p, l, v) for (p, l), v in nf[:6]))
    print("\n—— 静默显英文出处榜（词典里其实有本语种译文，页面却显示英文；前 %d）——" % show)
    for s, v in sorted(fben_tally.items(), key=lambda x: -x[1]["n"])[:show]:
        print("  %5d 次  %s\n          页面=%s ｜ 显示：%s ｜ 应显示：%s" % (
            v["n"], s[:88], ",".join(sorted(v["pg"]))[:44],
            " / ".join(sorted(v["ex"])[:2])[:58], " / ".join(sorted(v["want"])[:2])[:70]))
    print("\n—— 真漏翻出处榜（片段×语种命中次数，前 %d）——" % show)
    for s, v in sorted(sig_tally.items(), key=lambda x: -x[1]["n"])[:show]:
        print("  %5d 次  %s\n          页面=%s ｜ 例：%s" % (
            v["n"], s[:96], ",".join(sorted(v["pg"]))[:52], " / ".join(sorted(v["ex"])[:3])[:96]))
    print("\n—— 夹生 CJK 出处榜（前 %d，仅供参考，不算漏翻）——" % max(3, show // 2))
    for s, v in sorted(mix_tally.items(), key=lambda x: -x[1]["n"])[:max(3, show // 2)]:
        print("  %5d 次  %s\n          页面=%s ｜ 例：%s" % (
            v["n"], s[:80], ",".join(sorted(v["pg"]))[:40], " / ".join(sorted(v["ex"])[:3])[:80]))
    if fails:
        return 2
    return 1 if tot_real else 0


if __name__ == "__main__":
    sys.exit(main())
