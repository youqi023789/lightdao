#!/usr/bin/env python3
"""Production monitor: chain liveness, gateway, finalize/sign pipeline, miners, http.
Writes /var/www/lightdao/status.json; appends failures to /home/ubuntu/ld_alerts.log."""
import json, os, subprocess, time, urllib.request

STATE = "/home/ubuntu/ld_last_height"
ALERTS = "/home/ubuntu/ld_alerts.log"
STATUS = "/var/www/lightdao/status.json"

def curl(url, timeout=10):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)

def alert(msg):
    with open(ALERTS, "a") as f:
        f.write("%s ALERT %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg))

def main():
    now = int(time.time())
    st = {"ts": now, "ok": True, "checks": {}}
    # chain
    code, body = curl("http://127.0.0.1:26657/status")
    h = None
    try:
        h = int(json.loads(body)["result"]["sync_info"]["latest_block_height"])
    except Exception:
        pass
    prev = None
    if os.path.exists(STATE):
        try:
            d = json.load(open(STATE)); prev = d.get("h"); pts = d.get("t")
        except Exception:
            prev = None; pts = None
    advancing = True
    if h is None:
        advancing = False; st["ok"] = False; alert("chain status unreachable")
    else:
        if prev is not None and h <= prev and (now - (pts or now)) > 360:
            advancing = False; st["ok"] = False; alert("chain stalled at %s" % h)
        json.dump({"h": h, "t": now}, open(STATE, "w"))
    st["checks"]["chain"] = {"height": h, "advancing": advancing}
    # gateway
    code, body = curl("http://127.0.0.1:8080/v1/health")
    gok = code == 200
    if not gok: st["ok"] = False; alert("gateway unhealthy %s" % code)
    day = None
    try: day = json.loads(body).get("current_day")
    except Exception: pass
    st["checks"]["gateway"] = {"ok": gok, "day": day}
    # finalize for day-1
    fok = None  # None = not required (no miners that day)
    try:
        log = open("/home/ubuntu/ld_finalize.log").read().strip().split("\n")
        for ln in reversed(log[-12:]):
            if ('"day": %s' % (day - 1)) in ln or ('"day":%s' % (day - 1)) in ln:
                fok = ("no miners" not in ln) and ("error" not in ln.lower()); break
    except Exception:
        pass
    if fok is None:
        # day had no miners -> nothing to finalize; check day file miners count
        try:
            dj = json.load(open("/home/ubuntu/lightdao_gateway/data/day_%d.json" % (day - 1)))
            fok = not bool(dj.get("miners"))
        except Exception:
            fok = True
    if day and fok is False:
        st["ok"] = False; alert("finalize failed for day %s" % (day - 1))
    st["checks"]["finalize"] = {"ok": bool(fok), "day": (day - 1) if day else None}
    # sign root for day-1
    sok = False
    try:
        slog = open("/home/ubuntu/ld_sign.log").read()
        sok = ("submitted root for day %s" % (day - 1)) in slog
    except Exception:
        pass
    required = bool(fok) and bool(day)
    if required and not sok:
        import datetime
        if datetime.datetime.utcnow().hour >= 6:
            st["ok"] = False; alert("root not signed for day %s" % (day - 1))
        st["checks"]["sign_root"] = {"ok": False}
    else:
        st["checks"]["sign_root"] = {"ok": True}
    # miners today
    code, body = curl("http://127.0.0.1:8080/v1/scores?day=%s" % day)
    mn = 0
    try: mn = len(json.loads(body).get("scores", {}))
    except Exception: pass
    st["checks"]["miners_today"] = mn
    # http
    import ssl as _ssl
    _ctx = _ssl.create_default_context(); _ctx.check_hostname = False; _ctx.verify_mode = _ssl.CERT_NONE
    _req = urllib.request.Request("https://127.0.0.1/", headers={"Host": "lightdao.net"})
    try:
        with urllib.request.urlopen(_req, timeout=10, context=_ctx) as r: code = r.status
    except Exception as e: code = 0
    if code != 200: st["ok"] = False; alert("http %s" % code)
    st["checks"]["http"] = code
    json.dump(st, open(STATUS, "w"))
    print("monitor ok=%s height=%s miners=%s" % (st["ok"], h, mn))

if __name__ == "__main__":
    main()
