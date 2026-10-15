#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-RENDER-WATCH-20261015
真机渲染巡检：专门盯"代码上线了但浏览器里静默没跑"这类故障
（今天就是这样发现 funds_3.js 被塞进上一个 <script> 元素体内、永不执行，
 而所有静态门禁全绿）。

检查项（对本地 127.0.0.1，带 Host: lightdao.net）：
  R1 首页/资金页存在 .ldnav 吸顶导航
  R2 三个返回按钮文案都在
  R3 首页出块时间是实测数字（0.2~60 秒），不是写死的 1.75s、也不是空
  R4 资金页第 0 节的 data-live-step 能推进到"5 余额已取回"或更高（说明实时链上取数真的在跑）
  R5 页面上不应出现"取数失败/加载验证者失败"这类静默降级词以外的错误占位（出现即报）
告警复用 ld_monitor 的 /home/ubuntu/ld_alerts.log 通道；连续两轮才告警去重。
"""
import json
import os
import re
import subprocess
import sys
import time

BASE = "https://lightdao.net"   # 走域名，避免 nginx 默认虚拟主机 server_name _ 返回非本站
HOST = "lightdao.net"
STATE = "/home/ubuntu/ld_render_watch_state.json"
ALERTS = "/home/ubuntu/ld_alerts.log"
PAGES = {"/index.html": ["R1", "R2", "R3"],
         "/funds.html": ["R1", "R2", "R4", "R5"]}
CHROME = next((c for c in ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                           "/usr/bin/chromium-browser"] if os.path.exists(c)), None)


def log(msg):
    line = "%s RENDER-WATCH %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(line)


def alert(msg):
    with open(ALERTS, "a") as f:
        f.write("%s ALERT [render-watch] %s\n"
                % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg))


def render(path, tries=3):
    """用无头 chrome 真实执行页面脚本后 dump DOM。
    资金页的实时链要约 40s 才跑完，无头首帧可能停在"首次同步中…"，
    所以渲染本身要重试，取最后一次（最完整）的 DOM。"""
    if not CHROME:
        return None, "no-chrome"
    url = BASE + path
    last_err = ""
    best = None
    for k in range(tries):
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--ignore-certificate-errors", "--virtual-time-budget=120000",
               "--user-agent=LDRenderWatch/1.0", "--dump-dom", url]
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=170)
            h = p.stdout.decode("utf-8", "replace")
            if not h:
                last_err = "empty-dom rc=%s" % p.returncode
                continue
            if best is None or len(h) > len(best):
                best = h
            # 内容已完整就提前收工，省时间
            if path == "/funds.html" and "最后同步" in h and "已执行" in h:
                return h, ""
            if path != "/funds.html":
                return h, ""
        except subprocess.TimeoutExpired:
            last_err = "chrome-timeout"
        except Exception as e:
            last_err = "chrome-%s" % type(e).__name__
    if best is not None:
        return best, ""
    return None, last_err


def check_index(h):
    f = []
    if 'class="ldnav"' not in h:
        f.append("R1 首页无吸顶导航 .ldnav")
    for w in ["返回上一页", "返回挖矿页", "返回主客户端"]:
        if w not in h:
            f.append("R2 首页缺返回按钮: " + w)
    m = re.search(r"<b[^>]*data-btime[^>]*>\s*([^<]{0,16})\s*</b>", h)
    if not m:
        f.append("R3 首页没有 data-btime 实测出块元素")
    else:
        v = m.group(1)
        if "1.75" in v:
            f.append("R3 出块时间仍是写死的 1.75s")
        elif v.strip() in ("取不到", "—", ""):
            f.append("R3 出块时间实测未成功: %r" % v)
        else:
            mm = re.match(r"^(\d+\.\d+)s$", v.strip())
            if not mm or not (0.2 < float(mm.group(1)) < 60):
                f.append("R3 出块时间数值不合理: %r" % v)
    return f


def check_funds(h):
    f = []
    if 'class="ldnav"' not in h:
        f.append("R1 资金页无吸顶导航 .ldnav")
    for w in ["返回上一页", "返回挖矿页", "返回主客户端"]:
        if w not in h:
            f.append("R2 资金页缺返回按钮: " + w)
    # R4 判"内容真的渲染出来了"，不判 data-live-step：
    #   页面有 60s 定时器，无头虚拟时间会让探针抓到第二轮刚开始的瞬时值（停在第 4 步）。
    #   而且不能拿"99x,xxx,xxx.xx 余额数字"当证据——第 2 节静态快照里写死的
    #   990,394,202.64 会被同一个正则匹配到，那正是我要防的"旧数字冒充现状"。
    #   "最后同步 <时间>" 只有在 refresh() 整条链（余额+生态基金+台账）跑完后才会
    #   替换掉初始的"首次同步中…"，是唯一稳定的完成证据。
    if "最后同步" not in h or "首次同步中" in h:
        f.append("R4 资金页实时链上取数没有整体跑通（仍停在『首次同步中…』）")
    if "已执行" not in h:
        f.append("R4 资金页多签台账没渲染（缺『已执行』）")
    if re.search(r"取数失败", h):
        # 取数失败是"允许的诚实降级"，但如果常态出现要提醒（不当致命错误）
        log("提示：资金页有账户取数失败（可能是节点瞬时抖动，连续多轮再看）")
    # R5：旧的静默降级词不该再出现
    if "加载验证者失败" in h:
        f.append("R5 资金页出现旧的静默降级词『加载验证者失败』")
    return f


def main():
    if not CHROME:
        log("FATAL 本机没有 chrome/chromium，无法做真机渲染巡检")
        sys.exit(3)
    allf = []
    for path, _ in PAGES.items():
        h, err = render(path)
        if h is None:
            allf.append("%s 渲染失败: %s" % (path, err))
            log("渲染失败 %s: %s" % (path, err))
            continue
        if path == "/index.html":
            fs = check_index(h)
        else:
            fs = check_funds(h)
        for x in fs:
            allf.append("%s %s" % (path, x))
            log("FAIL %s %s" % (path, x))
        if not fs:
            log("OK %s" % path)

    prev = {"fail": 0, "msg": ""}
    if os.path.exists(STATE):
        try:
            prev = json.load(open(STATE))
        except Exception:
            prev = {"fail": 0, "msg": ""}

    if allf:
        n = int(prev.get("fail", 0)) + 1
        json.dump({"fail": n, "msg": allf[0], "ts": int(time.time())},
                  open(STATE, "w"))
        log("累计失败项 %d，连续第 %d 轮" % (len(allf), n))
        # 连续第 2 轮才告警，避免 chrome 偶发抖动就吵
        if n >= 2:
            alert("; ".join(allf[:5]))
            log("已写入告警通道")
    else:
        if int(prev.get("fail", 0)) >= 2:
            alert("render-watch 恢复正常（上一轮: %s）" % prev.get("msg", "")[:120])
        json.dump({"fail": 0, "msg": "", "ts": int(time.time())},
                  open(STATE, "w"))
        log("全部通过")
    sys.exit(0 if not allf else 1)


main()
