#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站 18 页巡检（先测量、后定判据，不凭想象写断言）。
两层：
  L1 HTTP 层（不需要浏览器，很便宜）：页面本身 200、页面里引用的每个本地
     js/css/图片 都 200、HTML 里没有未替换的模板占位。
     —— 这一层能抓到"发布后资源 404"：浏览器里表现为脚本静默不执行，
        所有 JS 级门禁全绿（本项目真出过同类事故）。
  L2 渲染层（无头 chrome，贵）：脚本真的跑起来了 —— <title> 存在、
     可见文本里没有 undefined/NaN/[object Object]、导航条在、
     没有停在"加载中/首次同步中"这类占位。
用法：
  python3 ld_render_all.py probe      # 只测量打印，不做判定（建基线用）
  python3 ld_render_all.py check      # 按基线判定 + 告警（cron 用）
  python3 ld_render_all.py check --pages /a.html,/b.html   # 只查子集
  python3 ld_render_all.py check --no-render               # 只跑 L1（便宜档）
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE = "https://lightdao.net"
ROOT = "/var/www/lightdao"
STATE = os.environ.get("LD_RSTATE", "/home/ubuntu/ld_render_all_state.json")
ALERTS = os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log")
CHROME = next((c for c in ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                           "/usr/bin/chromium-browser"] if os.path.exists(c)), None)
BAD_TOKENS = ["[object Object]", "undefined is not", "NaN%", "Infinity LIGHT"]
PLACEHOLDER = ["{{", "TODO:", "FIXME", "占位待填"]
# 允许停在占位的页面（本来就没有异步取数）
RENDER_STALL_OK = ("/privacy.html", "/terms.html", "/blog.html", "/quiz.html",
                   "/search.html", "/audit_logic.html",
                   # app.html 的 加载中… 是 #airFirst(空投中心) 与 #myBadges(我的徽章)，
                   # 两个面板都要连钱包才有数据，无头浏览器没钱包必然停在这儿（2026-10-16 实测）。
                   # 记一笔真实缺口：未连钱包时更该写"连接钱包后查看"而不是永远"加载中…"，
                   # 与治理页已修的"只读首屏"是同一类问题，等排期改，不在这里当误报刷。
                   "/app.html")


def pages():
    return sorted("/" + f for f in os.listdir(ROOT) if f.endswith(".html"))


def http_get(path, timeout=25):
    req = urllib.request.Request(BASE + path,
                                 headers={"User-Agent": "LDRenderAll/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return -1, "ERR:%s" % type(e).__name__


def assets_of(html):
    """页面引用的本站资源（跳过外链、data:、模板变量）。"""
    out = []
    for m in re.finditer(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', html):
        u = m.group(1)
        if u.startswith(("http://", "https://", "data:", "mailto:", "#", "//")):
            continue
        if "${" in u or "{{" in u:
            continue
        out.append(u)
    return sorted(set(out))


def render(path, budget=45000, timeout=90):
    if not CHROME:
        return None, "no-chrome"
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--ignore-certificate-errors", "--virtual-time-budget=%d" % budget,
           "--user-agent=LDRenderAll/1.0", "--dump-dom", BASE + path]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        h = p.stdout.decode("utf-8", "replace")
        return (h, "") if h else (None, "empty-dom rc=%s" % p.returncode)
    except subprocess.TimeoutExpired:
        return None, "chrome-timeout"
    except Exception as e:
        return None, "chrome-%s" % type(e).__name__


def visible(html):
    b = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    t = re.sub(r"(?s)<[^>]+>", " ", b)
    return re.sub(r"\s+", " ", t)


def note(kind, msg):
    """告警统一出口：打印 + 落盘；落盘失败必须喊出来。
    （ld_alerts.log 由 root cron 创建、ubuntu 不可写——非 root 跑时若静默 pass，
      就等于"检测到了但永远没人知道"，这正是本项目反复挨打的静默失败模式。）"""
    line = "%s %s [render-all] %s" % (
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), kind, msg)
    print(line)
    try:
        with open(ALERTS, "a") as f:
            f.write(line + "\n")
        return True
    except Exception as e:
        print("WARN 告警没写进 %s: %s —— 请用 root 跑或设 LD_ALERTS 指到可写文件"
              % (ALERTS, e))
        return False


def fallback_signature():
    """本站 nginx 对不存在的 .html 会回 200 + 首页内容（SPA 兜底），
    所以"页面 200"根本不能证明页面存在。用一个必然不存在的探针 URL 学出
    兜底响应的哈希，运行时判定，不写死首页内容。"""
    st, body = http_get("/__ld_404_canary__.html", timeout=20)
    return hashlib.sha256(body.encode("utf-8", "replace")).hexdigest() if body else None


def internal_links(html):
    out = []
    for m in re.finditer(r'href=["\'](/[^"\'#?]+\.(?:html))[?\'"]', html):
        out.append(m.group(1))
    return sorted(set(out))


def probe_page(path, do_render=True, fsig=None):
    st, html = http_get(path)
    rec = {"page": path, "http": st, "bytes": len(html), "bad_assets": [],
           "render": None, "flags": []}
    if st != 200:
        rec["flags"].append("页面 HTTP %s" % st)
        return rec
    if fsig and hashlib.sha256(html.encode("utf-8", "replace")).hexdigest() == fsig \
            and path not in ("/index.html", "/landing.html"):
        # 200 但内容其实是兜底首页 = 这个页面根本不存在（改链接名/删文件都会这样）
        rec["flags"].append("页面由 SPA 兜底返回（文件不存在）")
        return rec
    for u in assets_of(html):
        a, ab = http_get(u.split("?")[0] if u.startswith("/") else u, timeout=15)
        if a != 200:
            rec["bad_assets"].append("%s→%s" % (u, a))
        elif u.endswith(".js") and "<!DOCTYPE" in ab[:200]:
            rec["bad_assets"].append("%s→200 但返回的是 HTML(被兜底冒充)" % u)
    # 站内链接完整性：兜底机制让 HTTP 层查不出坏链接，只能直接看磁盘
    for l in internal_links(html):
        if not os.path.exists(ROOT + l):
            rec["flags"].append("站内链接指向不存在的页面 %s" % l)
    for tok in PLACEHOLDER:
        if tok in html:
            rec["flags"].append("模板占位 %s" % tok)
    if do_render:
        h, err = render(path)
        if h is None:
            rec["render"] = "FAIL:" + err
            rec["flags"].append("渲染失败 " + err)
        else:
            rec["render"] = "dom=%dB" % len(h)
            txt = visible(h)
            if not re.search(r"<title[^>]*>\s*\S", h):
                rec["flags"].append("无 title")
            if 'class="ldnav"' not in h:
                rec["flags"].append("无 .ldnav 导航")
            for tok in BAD_TOKENS:
                if tok in txt:
                    rec["flags"].append("可见文本含 %s" % tok)
            if path not in RENDER_STALL_OK and re.search(r"加载中…|加载中\.\.\.|首次同步中", txt):
                rec["flags"].append("停在加载占位")
    return rec


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "probe"
    only = []
    for a in args:
        if a.startswith("--pages="):
            only = [p for p in a.split("=", 1)[1].split(",") if p]
    do_render = "--no-render" not in args
    plist = only or pages()
    fsig = fallback_signature()
    if not fsig:
        print("WARN 取不到 SPA 兜底探针（canary 请求失败）——"
              "\"页面被兜底冒充\"这一判据本轮不生效，其余判据照跑")
    recs = [probe_page(p, do_render, fsig) for p in plist]
    if mode == "probe":
        print("%-22s %-6s %-9s %-12s %s" % ("页面", "HTTP", "字节", "渲染", "问题"))
        for r in recs:
            print("%-22s %-6s %-9s %-12s %s"
                  % (r["page"], r["http"], r["bytes"], (r["render"] or "-")[:12],
                     "; ".join(r["flags"] + (["坏资源 " + ",".join(r["bad_assets"])]
                                             if r["bad_assets"] else [])) or "干净"))
        json.dump({"ts": int(time.time()), "recs": recs},
                  open(STATE + ".probe", "w"), ensure_ascii=False, indent=1)
        print("\n探测结果已写 %s（供人工核对后落成基线）" % (STATE + ".probe"))
        return 0
    bad = [r for r in recs if r["flags"] or r["bad_assets"]]
    for r in bad:
        print("FAIL %s :: %s" % (r["page"], "; ".join(r["flags"] +
              (["坏资源 " + ",".join(r["bad_assets"])] if r["bad_assets"] else []))))
    prev = {"fail": 0, "msg": ""}
    if os.path.exists(STATE):
        try:
            prev = json.load(open(STATE))
        except Exception:
            pass
    sig = json.dumps([r["page"] for r in bad], sort_keys=True)
    if bad:
        n = int(prev.get("fail", 0)) + 1 if prev.get("sig") == sig else 1
        json.dump({"fail": n, "sig": sig, "msg": bad[0]["page"], "ts": int(time.time())},
                  open(STATE, "w"))
        line = "%d 页有问题（连续第 %d 轮同签名）: %s" % (len(bad), n, sig[:180])
        print(line)
        if n >= 2:      # 连续两轮才告警，躲开 chrome/网络瞬时抖动
            note("ALERT", line)
        return 1
    if int(prev.get("fail", 0)) >= 2:
        note("NOTE", "全站渲染恢复正常（上一轮故障页 %s）" % prev.get("msg", "")[:80])
    json.dump({"fail": 0, "sig": "[]", "ts": int(time.time())}, open(STATE, "w"))
    print("全站 %d 页通过（L1%s）" % (len(recs), "+L2" if do_render else " 仅"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
