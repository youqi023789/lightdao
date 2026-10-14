#!/usr/bin/env python3
"""ld_gateway_trace_watch.py — gateway worker-exception watch.
The 2026-10-10 /v1/proof 502 outage was invisible to the watchdog because
/v1/health stayed 200 while every proof request crashed its worker thread.
This monitor scans the lightdao-gateway journal for NEW Tracebacks and alerts.
State: /home/ubuntu/ld_gwtrace.state. Cron every 5 min."""
import json, subprocess, sys, time

STATE = "/home/ubuntu/ld_gwtrace.state"

def alert(msg):
    try:
        subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "[gw-trace-watch] " + msg],
                       timeout=30, capture_output=True)
    except Exception:
        pass

try:
    st = json.load(open(STATE))
except Exception:
    st = {"count": 0, "first_bad": 0}

r = subprocess.run(["journalctl", "-u", "lightdao-gateway", "--since", "-10 min", "--no-pager"],
                   capture_output=True, text=True, timeout=60)
tb = r.stdout.count("Traceback (most recent call last)")
now = time.time()

if tb > 0:
    # dedup: alert at most once per 30 min while errors continue
    if now - st.get("last_alert", 0) > 1800:
        # extract a representative exception line
        lines = [l for l in r.stdout.splitlines() if "Error" in l or "error" in l]
        alert("gateway worker exceptions in last 10min: %d (e.g. %s)" %
              (tb, lines[-1][:150] if lines else "?"))
        st["last_alert"] = now
    st["count"] += tb
    st["first_bad"] = st.get("first_bad") or now
    json.dump(st, open(STATE, "w"))
    print("GW-TRACE FAILS: %d tracebacks in 10min" % tb)
    sys.exit(1)
else:
    if st.get("count"):
        alert("RECOVERED: gateway tracebacks stopped (%d total during incident)" % st["count"])
    json.dump({"count": 0, "first_bad": 0, "last_alert": 0}, open(STATE, "w"))
    print("GW-TRACE OK")
