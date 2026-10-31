#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-RENDER-TRUTH-20261031  站内"事实类文案"的看门狗。

为什么需要（今天实测出来的两类真问题，之前都没有执行点）：
  1) 过期数字：链上 `wasmd q staking validators` 实测 BONDED=10，
     但 index/landing/nodes/institutions 还写着"7 验证者 / 7/7 BONDED"——
     页面上那一段的小标题恰恰是"不承诺,只展示已验证的"。
  2) 不可自证的说法：多签"分母 7"在链上查不到（mining_reward 只有 4 种查询、
     treasury_multisig 只有 tx/signers；本节点交易索引里 MsgInstantiateContract 命中 0 笔），
     能自证的只有每笔 submit_root 事件里的 threshold=5 与实际签名账户数=5。
  3) 位置泄露：index/landing 的 lv1 曾把验证者所在国家缩写
     （JP/KR/SG/US/HK/FR/UK）印在公开页面上。

两种模式：
  static  便宜、可高频：只查线上文件文本（残留禁用串）+ 链上 BONDED 数与站内数字是否一致。
  render  贵、每天一次：无头 chrome 跑完 JS 之后，按**可见文本**核对 7 条多语言说法。

告警口径（沿用本项目硬规矩）：
  · "查不到"绝不等于"没问题" → 读不到链上数据/渲染失败都算 FAIL 并非零退出；
  · 同一问题只在状态变化时刷屏一次（STATE 签名去重），恢复时打一条 CROSS-OK。

用法：
  python3 ld_render_truth.py static
  python3 ld_render_truth.py render
  LD_FAKE_BONDED=3 python3 ld_render_truth.py static   # 反向验证：必须 FAIL
"""
import json, os, re, subprocess, sys, hashlib, datetime

WWW = os.environ.get("LD_WWW", "/var/www/lightdao")
NODE = os.environ.get("LD_NODE", "http://127.0.0.1:26657")
ALERTS = "/home/ubuntu/ld_alerts.log"
STATE = "/home/ubuntu/.ld_render_truth_state"
BASE = os.environ.get("LD_BASE", "https://lightdao.net")
CHROME = next((c for c in ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                          "/usr/bin/chromium", "/usr/bin/chromium-browser"] if os.path.exists(c)), None)

# 禁用串：出现即说明"不可自证/已过期/泄露"的说法回流到线上（含各语种写法）
FORBIDDEN = ["5/7", "JP/KR", "SG/US/HK", "7/7 BONDED", "7 验证者", "7 validators",
             "5 of 7 authorised", "sur 7 comptes autorisés", "von 7 autorisierten",
             "из 7 авторизованных", "7개 중 5", "認可 7 アカウント", "سبعة حسابات",
             "7 अधिकृत खातों", "7 yetkili hesaptan", "sa 7 na pinahintulutang"]
# 站内可能出现"验证者数量"的写法（用于与链上实测值对齐）
# 收紧：数字必须 1–3 位、前面不能是 - 或数字（否则 LD-XXXX-20261015 这类改动标记会被当成"20261015 个验证者"，
# 我第一版就中了这个招）；数字与词之间最多两个空白（不让跨行的注释尾数混进来）。
NUM = r"(?<![\dA-Za-z.-])(\d{1,3})"
COUNT_PAT = re.compile(NUM + r"[ \t]{0,2}/[ \t]{0,2}\d{1,3}[ \t]{0,2}BONDED|"
                      + NUM + r"[ \t]{0,2}验证者|"
                      + NUM + r"[ \t]{0,2}validators(?:[ \t]{0,4}all)?[ \t]{0,4}BONDED", re.I)


def strip_comments(t):
    """去掉 JS/C 注释与 HTML 注释：只对"数字对不对"这类面向用户的判定生效；
    禁用串检查仍然查原文（注释里出现机房位置也一样是泄露）。"""
    t = re.sub(r"(?is)/\*.*?\*/", " ", t)
    t = re.sub(r"(?m)^\s*//.*$", " ", t)
    t = re.sub(r"(?s)<!--.*?-->", " ", t)
    return t

CASES = [
    ("/index.html?lang=en", ["10 validators all BONDED"], ["JP/KR", "7 validators", "5/7"]),
    ("/index.html", ["10 验证者全部 BONDED"], ["JP/KR", "7 验证者", "5/7"]),
    ("/nodes.html?lang=de", ["10/10 BONDED"], ["7/7 BONDED", "5/7"]),
    ("/season.html?lang=ja", ["（認可アカウント署名 5 件）"], ["5/7", "7/7"]),
    ("/contracts.html?lang=ru", ["5 подписей авторизованных счетов"], ["5/7", "из 7"]),
    ("/contracts.html?lang=fr", ["5 signatures de comptes autorisés"], ["5/7", "sur 7"]),
    ("/season.html?lang=fr", ["multisig de 5 comptes autorisés"], ["5/7", "sur 7"]),
]


def sh(args, timeout=90):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def chain_bonded():
    r = sh(["wasmd", "q", "staking", "validators", "--node", NODE, "-o", "json"])
    if r.returncode != 0:
        return None, "链上查询失败 rc=%s" % r.returncode
    try:
        d = json.loads(r.stdout)
    except Exception as e:
        return None, "链上返回不是 JSON：%s" % e
    vs = d.get("validators") or d.get("result", {}).get("validators") or []
    if not vs:
        return None, "validator 列表为空（不确定是链的问题还是量具的问题 → 报 FAIL）"
    n = sum(1 for v in vs if v.get("status") == "BOND_STATUS_BONDED")
    return n, ""


def site_numbers():
    """从线上 HTML/JS/搜索索引里抓"验证者数量"类数字（多个来源各自记录，便于定位）。"""
    out = []
    files = []
    for root, dirs, fns in os.walk(WWW):
        dirs[:] = [x for x in dirs if x not in (".git", "vendor")]
        for fn in fns:
            if fn.endswith((".html", ".js")) and "vendor" not in fn:
                files.append(os.path.join(root, fn))
    files.append(os.path.join(WWW, "search-index.json"))
    for p in files:
        try:
            t = open(p, encoding="utf-8").read()
        except Exception as e:
            return None, "读不到 %s（%s）→ 不算通过" % (p, e)
        for m in COUNT_PAT.finditer(strip_comments(t)):
            num = next(g for g in m.groups() if g)
            out.append((os.path.relpath(p, WWW), int(num)))
    return out, ""


def static_mode():
    fails = []
    # 1) 禁用串残留
    for root, dirs, fns in os.walk(WWW):
        dirs[:] = [x for x in dirs if x not in (".git", "vendor")]
        for fn in sorted(fns):
            if not fn.endswith((".html", ".js", ".json")) or "vendor" in fn:
                continue
            p = os.path.join(root, fn)
            try:
                t = open(p, encoding="utf-8").read()
            except Exception as e:
                fails.append("读取失败 %s：%s" % (p, e)); continue
            for bad in FORBIDDEN:
                if bad in t:
                    fails.append("禁用串 %r 回流：%s" % (bad, os.path.relpath(p, WWW)))
    # 2) 数字与链上一致
    fake = os.environ.get("LD_FAKE_BONDED")
    if fake is not None:                      # 反向验证用的"假链上读数"
        bonded, err = int(fake), ""
    else:
        bonded, err = chain_bonded()
    if bonded is None:
        fails.append("链上 BONDED 数取不到：%s" % err)
    else:
        nums, err = site_numbers()
        if nums is None:
            fails.append("站内数字提取失败：%s" % err)
        else:
            for rel, n in nums:
                if n != bonded:
                    fails.append("站内 %s 写 %s 个，链上 BONDED=%s" % (rel, n, bonded))
    return fails, ("bonded=%s" % bonded if bonded is not None else "bonded=UNKNOWN")


def render_mode():
    if not CHROME:
        return ["没有 chrome，渲染层无法执行（不算通过）"], "no-chrome"
    fails = []
    for path, musts, mustnots in CASES:
        try:
            p = sh([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--ignore-certificate-errors", "--virtual-time-budget=45000",
                    "--user-agent=LDRenderTruth/1.0", "--dump-dom", BASE + path], timeout=120)
        except Exception as e:
            fails.append("%s 渲染异常 %s" % (path, e)); continue
        html = p.stdout
        if not html.strip():
            fails.append("%s 渲染输出为空 rc=%s" % (path, p.returncode)); continue
        vis = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", " ", html)
        vis = re.sub(r"(?s)<[^>]+>", " ", vis)
        miss = [m for m in musts if m not in vis]
        leak = [n for n in mustnots if n in vis]
        if miss or leak:
            fails.append("%s 缺=%s 漏=%s" % (path, miss, leak))
    return fails, "%d 条渲染用例" % len(CASES)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "static"
    if mode == "render":
        fails, detail = render_mode()
    else:
        fails, detail = static_mode()
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sig = hashlib.sha256(("\n".join(sorted(fails)) + "|" + mode).encode("utf-8")).hexdigest()[:16]
    try:
        prev = open(STATE, encoding="utf-8").read().strip() if os.path.exists(STATE) else ""
    except Exception:
        prev = ""
    if fails:
        print("RENDER-TRUTH-FAIL [%s] %s | %s" % (mode, detail, " ; ".join(fails[:8])))
        if prev != "F:" + sig:
            try:
                with open(ALERTS, "a", encoding="utf-8") as f:
                    f.write("%s RENDER-TRUTH-FAIL mode=%s %s\n" % (ts, mode, " ; ".join(fails[:6])))
            except Exception as e:
                print("WARN 告警写不下去：%s" % e)
            try:
                open(STATE, "w", encoding="utf-8").write("F:" + sig)
            except Exception:
                pass
        sys.exit(1)
    print("RENDER-TRUTH-OK [%s] %s" % (mode, detail))
    if prev.startswith("F:"):
        try:
            with open(ALERTS, "a", encoding="utf-8") as f:
                f.write("%s RENDER-TRUTH-OK mode=%s（此前 %s 的告警已恢复）\n" % (ts, mode, prev[2:10]))
        except Exception:
            pass
        try:
            open(STATE, "w", encoding="utf-8").write("OK")
        except Exception:
            pass
    sys.exit(0)


if __name__ == "__main__":
    main()
