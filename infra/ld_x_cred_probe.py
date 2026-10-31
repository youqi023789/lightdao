#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-X-CRED-PROBE-20261031  X 发帖凭据的**只读**预检（每天在两条定时帖之前跑一次）。

为什么需要：
  · 每日发帖从 2026-10-24 起一直在 DRY（预演）分支里空转，直到 10-31 才发现；
    那几天如果凭据也有问题，症状同样是"日志里安静躺着一条错误"。
  · 发帖脚本现在会在真失败时写 X-POST-FAIL（已加，已反向验证），但那是"事后响"；
    本预检是"事前响"：不发帖、不花额度，只把 OAuth1.0a user context 打一次
    GET https://api.x.com/2/users/me，200 就算身份可用。

只打印状态码、用户名、限额头；任何密钥都不打印（本项目硬规矩）。
反向验证：LD_X_CRED_FAKE=1 走同一条代码路径但用一把坏 token → 必须 FAIL 且落告警。
"""
import hashlib, json, os, subprocess, sys, datetime

ENVF = "/etc/lightdao/x_api.env"
ALERTS = "/home/ubuntu/ld_alerts.log"
STATE = "/home/ubuntu/.ld_x_cred_state"
URL = "https://api.x.com/2/users/me"
sys.path.insert(0, "/home/ubuntu")   # post_tweet_media.py 住在 /home/ubuntu（生产发帖用的就是它）

kv = {}
for line in open(ENVF, encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        kv[k.strip()] = v.strip().strip('"').strip("'")
for k, v in kv.items():
    os.environ[k] = v            # 复用生产 sign()：它按 os.environ 取值，与发帖时完全一致

try:
    import post_tweet_media as P
except Exception as e:
    print("X-CRED-QUERY-FAIL 无法导入生产发帖模块（%s）" % e)
    detail = "import-error"
    hdr = None
else:
    if os.environ.get("LD_X_CRED_FAKE") == "1":
        os.environ["X_ACCESS_TOKEN"] = "BAD" + os.environ.get("X_ACCESS_TOKEN", "")[:12]
        os.environ["X_ACCESS_SECRET"] = "BADSECRET"
    hdr = P.sign("GET", URL, {})
    r = subprocess.run(["curl", "-sS", "-m", "25", "-o", "/tmp/ld_x_cred_body_%d" % os.getpid(),
                        "-w", "%{http_code}", "-H", "Authorization: " + hdr, URL],
                       capture_output=True, text=True, timeout=40)
    code = r.stdout.strip()
    body = ""
    try:
        body = open("/tmp/ld_x_cred_body_%d" % os.getpid(), encoding="utf-8", errors="replace").read()
    except Exception:
        pass

def emit(status, msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sig = hashlib.sha256((status + "|" + msg).encode("utf-8")).hexdigest()[:16]
    prev = ""
    try:
        prev = open(STATE, encoding="utf-8").read().strip()
    except Exception:
        pass
    if status == "OK":
        print("X-CRED-OK %s" % msg)
        if prev.startswith("F"):
            try:
                with open(ALERTS, "a", encoding="utf-8") as f:
                    f.write("%s X-CRED-OK（此前凭据预检失败的告警已恢复）\n" % ts)
            except Exception:
                pass
            try:
                open(STATE, "w", encoding="utf-8").write("OK")
            except Exception:
                pass
        else:
            try:
                open(STATE, "w", encoding="utf-8").write("OK")
            except Exception:
                pass
        sys.exit(0)
    print("X-CRED-FAIL %s" % msg)
    if prev != "F:" + sig:
        try:
            with open(ALERTS, "a", encoding="utf-8") as f:
                f.write("%s X-CRED-FAIL %s\n" % (ts, msg))
        except Exception as e:
            print("WARN 告警写不下去：%s" % e)
        try:
            open(STATE, "w", encoding="utf-8").write("F:" + sig)
        except Exception:
            pass
    sys.exit(1)


if hdr is None:
    emit("FAIL", detail)
try:
    d = json.loads(body)
except Exception as e:
    emit("FAIL", "HTTP=%s 响应不是 JSON（%s）：%s" % (code, e, body[:120]))
if code == "200":
    u = d.get("data", {}).get("username")
    emit("OK", "handle=@%s id=%s（user context 可用，未发帖）" % (u, d.get("data", {}).get("id")))
emit("FAIL", "HTTP=%s %s" % (code, json.dumps(d, ensure_ascii=False)[:200]))
