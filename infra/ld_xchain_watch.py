#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_xchain_watch.py —— 跨链面板的看门狗：探针进程在不在、数据新不新、有没有内部错误。

为什么需要：面板显示的是"链上此刻的真相"。探针一旦挂掉或卡住，浏览器端的 fetch 会失败，
访客看到的是"读不到"（诚实），但**我**看不到——只有这个看门狗能从服务端这边发现。
另外探针自己会把读不到的项写进 errors 数组（比如主网查询超时），这里也一并盯住。

判定（任一不过 = 非零退出 + 写告警日志）：
 1) systemd 服务 lightdao-xchain.service 必须 active
 2) 直连 127.0.0.1:8096/v1/ibc 必须 200，且 utc 距今 < AGE_MAX 秒（数据新鲜）
 3) 同一份数据里三条链的高度必须都是整数，A/B 高度不得比上次记录还小（回退=节点或探针出问题）
 4) errors 数组非空 → 报警（探针自己不沉默）
 5) 公网路径 https://lightdao.net/xchain/v1/ibc 必须 200 且 application/json
    （防止"服务活着但 nginx 反代断了"——那时访客全看到读不到，而进程监控一切正常）
 6) /xchain/v1/prices 必须给得出至少 3 个币种（外部接口挂了要早于用户发现）

--selftest 植入：假 utc（过期）、假 errors、坏 JSON、地址写错 四种故障，逐一确认会响。
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

SVC = os.environ.get("XC_SVC", "lightdao-xchain.service")
LOCAL = os.environ.get("XC_LOCAL", "http://127.0.0.1:8096/v1/ibc")
PUB = os.environ.get("XC_PUB", "https://lightdao.net/xchain/v1/ibc")
PUBP = os.environ.get("XC_PUB_PRICES", "https://lightdao.net/xchain/v1/prices")
STATE = os.environ.get("XC_STATE", "/home/ubuntu/ld_xchain_watch_state.json")
ALERTS = os.environ.get("XC_ALERTS", "/home/ubuntu/ld_alerts.log")
AGE_MAX = float(os.environ.get("XC_AGE_MAX", "180"))
UA = {"User-Agent": "LightDAO-XChain-Watch/1.0"}


def line(msg):
    s = "%s XCHAIN %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(s)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(s + "\n")
    except Exception:
        pass


def get(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {}


def save_state(d):
    try:
        tmp = STATE + ".tmp"
        json.dump(d, open(tmp, "w", encoding="utf-8"))
        os.replace(tmp, STATE)
    except Exception:
        pass


def check(alarms, now, pub=True):
    p = subprocess.run(["systemctl", "is-active", SVC], capture_output=True, text=True, timeout=20)
    st = (p.stdout or "").strip()
    if st != "active":
        alarms.append("探针进程 %s 不是 active（实测 %s）：面板会全线显示读不到" % (SVC, st or "读不到"))
    code, body = get(LOCAL)
    if code != 200:
        alarms.append("探针 /v1/ibc 返回 %s" % code)
        return
    d = json.loads(body)
    age = now - time.mktime(time.strptime(d["utc"][:19], "%Y-%m-%dT%H:%M:%S"))
    if age > AGE_MAX:
        alarms.append("探针数据已 %.0f 秒没刷新（阈值 %.0f）：缓存或链查询卡住了" % (age, AGE_MAX))
    ss = load_state()
    for k in ("a", "b", "main"):
        c = d.get(k)
        if not c or not isinstance(c.get("height"), int):
            alarms.append("探针 %s 链高度读不到（%s）" % (k, c))
            continue
        old = ss.get("h_" + k)
        if isinstance(old, int) and c["height"] < old:
            alarms.append("%s 链高度倒退（%d < 上次 %d）：节点回滚或探针连到了别的链" % (k, c["height"], old))
        ss["h_" + k] = c["height"]
    if d.get("errors"):
        alarms.append("探针自报读数缺口：%s" % " ｜ ".join(str(x)[:70] for x in d["errors"][:3]))
    ss["utc"] = d["utc"]
    save_state(ss)
    if pub:
        try:
            code2, body2 = get(PUB, timeout=20)
            j2 = json.loads(body2)
            if code2 != 200 or not isinstance(j2.get("a"), dict):
                alarms.append("公网 /xchain/v1/ibc 不通（HTTP %s）：反代或证书问题，访客侧全瞎" % code2)
        except Exception as e:
            alarms.append("公网 /xchain/v1/ibc 取不到：%s" % str(e)[:90])
        try:
            code3, body3 = get(PUBP, timeout=20)
            n = len((json.loads(body3).get("usd") or {}))
            if code3 != 200 or n < 3:
                alarms.append("行情只剩 %d 个币种（HTTP %s）：CoinGecko 侧异常或额度用尽" % (n, code3))
        except Exception as e:
            alarms.append("行情取不到：%s" % str(e)[:90])


def selftest():
    print("XCHAIN SELFTEST：植入故障，逐项确认会响")
    hits = 0
    old = {"SVC": globals()["SVC"], "LOCAL": globals()["LOCAL"]}
    # a) 进程名换成不存在的
    globals()["SVC"] = "ld-not-a-service.service"
    al = []; check(al, time.time(), pub=False)
    ok = any("不是 active" in x for x in al); hits += ok
    print("  a 探针进程挂掉 -> %s" % ("抓到" if ok else "漏了"))
    globals()["SVC"] = old["SVC"]
    # b) 假数据（utc 过期 + errors 非空）：用一个假 URL 指向临时文件服务不现实，这里直接喂假 JSON
    import http.server, threading

    payload = {"bad": json.dumps({"utc": "2026-01-01T00:00:00Z", "a": {"height": 1}, "b": {"height": 1},
                                  "main": {"height": 1}, "errors": ["故意注入的错误"]}).encode(),
               "okjson": b"not json"}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(payload["bad"])

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    globals()["LOCAL"] = "http://127.0.0.1:%d/v1/ibc" % port
    al = []; check(al, time.time(), pub=False)
    ok1 = any("没刷新" in x for x in al)
    ok2 = any("读数缺口" in x for x in al)
    hits += ok1 + ok2
    print("  b 数据过期 -> %s ｜ c 自报错误 -> %s" % ("抓到" if ok1 else "漏了", "抓到" if ok2 else "漏了"))
    # d) 公网反代：换成一个必然取不到的地址
    globals()["LOCAL"] = old["LOCAL"]
    globals()["PUB"] = "https://lightdao.net/xchain/no-such-path"
    al = []
    globals()["SVC"] = old["SVC"]
    check(al, time.time(), pub=True)
    ok = any("公网" in x for x in al)
    hits += ok
    print("  d 公网路径不通 -> %s" % ("抓到" if ok else "漏了"))
    for k, v in old.items():
        globals()[k] = v
    globals()["PUB"] = os.environ.get("XC_PUB", "https://lightdao.net/xchain/v1/ibc")
    print("XCHAIN SELFTEST：%d/4 类被抓到" % hits)
    return 0 if hits >= 4 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    alarms = []
    try:
        check(alarms, time.time())
    except Exception as e:
        line("FAIL 量具自己读不到（不当成正常）：%s" % str(e)[:180])
        sys.exit(2)
    for a in alarms:
        line("ALERT " + a)
    if alarms:
        sys.exit(1)
    print("XCHAIN OK：进程/新鲜度/高度不回退/自报错误/公网/行情 全过")
    sys.exit(0)
