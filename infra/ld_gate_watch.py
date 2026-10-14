#!/usr/bin/env python3
"""ld_gate_watch.py — 发布门禁完整性看门狗。

比对「本机部署的门禁脚本哈希」与「仓库 gate_manifest.txt 记录的哈希」，任一不符即告警。
动机：2026-10-14 发现 5 个门禁脚本从未进版本库（g1/g2/g3/g4/g9），而 promote 依赖它们；
保护发布的那套东西本身不在保护之下。此看门狗让"门禁被改/被删/仓库与线上不一致"当天暴露。

用法: ld_gate_watch.py [manifest_url]
退出码: 0 一致 / 1 有漂移或缺文件
"""
import hashlib, json, os, subprocess, sys, time, urllib.request


def UTC():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

MANIFEST = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "GW_MANIFEST_URL",
    "https://raw.githubusercontent.com/youqi023789/lightdao/main/infra/gate_manifest.txt")
ALERTS = "/home/ubuntu/ld_alerts.log"
LASTFLAG = "/home/ubuntu/ld_gate_watch_last"

# 部署位置：/usr/local/bin 与 /home/ubuntu 两处
PATHS = {
    "promote.py": "/usr/local/bin/promote.py",
    "sri_integrity.py": "/usr/local/bin/sri_integrity.py",
    "g1_i18n_lint.py": "/usr/local/bin/g1_i18n_lint.py",
    "g2_a11y_check.py": "/usr/local/bin/g2_a11y_check.py",
    "g3_weight_check.py": "/usr/local/bin/g3_weight_check.py",
    "g4_sw_check.py": "/usr/local/bin/g4_sw_check.py",
    "g7_fuzz_check.py": "/usr/local/bin/g7_fuzz_check.py",
    "g9_day_atomic_check.py": "/usr/local/bin/g9_day_atomic_check.py",
    "qa_site.py": "/home/ubuntu/qa_site.py",
    "qa_extra.py": "/home/ubuntu/qa_extra.py",
    "site_audit.py": "/home/ubuntu/site_audit.py",
    "qa_truth.py": "/home/ubuntu/qa_truth.py",
}


def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except Exception:
        return None


def main():
    try:
        raw = urllib.request.urlopen(MANIFEST, timeout=25).read().decode()
    except Exception as e:
        # 拉不到清单只连续失败多次才告警（避免网络抖动刷屏）
        n = 0
        if os.path.exists(LASTFLAG):
            try: n = int(open(LASTFLAG).read().split("|")[0])
            except Exception: n = 0
        n += 1
        open(LASTFLAG, "w").write("%d|manifest-unreachable" % n)
        if n == 6:
            with open(ALERTS, "a") as f:
                f.write("%s ALERT gate-watch cannot fetch manifest 6x: %s\n"
                        % (UTC(), e))
        print("gate-watch: manifest fetch failed (%d): %s" % (n, e))
        return 0

    want = {}
    for ln in raw.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"): continue
        h, name = ln.split()[0], ln.split()[-1]
        want[name] = h

    drift, missing = [], []
    for name, path in PATHS.items():
        got = sha(path)
        if got is None:
            missing.append(name); continue
        if name in want and want[name] != got:
            drift.append("%s (repo %s… vs host %s…)" % (name, want[name][:12], got[:12]))
        if name not in want:
            drift.append("%s not listed in manifest" % name)

    unversioned = [n for n in PATHS if n not in want]
    msg = "gate-watch: checked=%d drift=%d missing_on_host=%d unversioned=%d" % (
        len(PATHS), len(drift), len(missing), len(unversioned))
    print(msg)
    for d in drift: print("  DRIFT", d)
    for m in missing: print("  MISSING", m)
    for u in unversioned: print("  NOT-IN-MANIFEST", u)

    bad = bool(drift or missing or unversioned)
    prev = ""
    if os.path.exists(LASTFLAG):
        prev = open(LASTFLAG).read().split("|", 1)[-1]
    sig = json.dumps({"d": sorted(drift), "m": sorted(missing), "u": sorted(unversioned)}, sort_keys=True)
    open(LASTFLAG, "w").write("0|" + sig)
    if bad and sig != prev:                      # 只在状态变化时告警，避免每 6 小时刷屏
        with open(ALERTS, "a") as f:
            f.write("%s ALERT deploy gates drifted from repo: %d drift, %d missing, %d unversioned\n"
                    % (UTC(), len(drift), len(missing), len(unversioned)))
        subprocess.run(["/usr/local/bin/discord_bot.py", "send",
                        "⚠️ 发布门禁与仓库不一致（漂移%d/缺失%d/未入库%d）：门禁本身可能被改动，见 ld_gate_watch.log"
                        % (len(drift), len(missing), len(unversioned))], capture_output=True)
    return 1 if bad else 0


sys.exit(main())
