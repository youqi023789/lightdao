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
ALERTS = os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log")
LASTFLAG = os.environ.get("LD_LASTFLAG", "/home/ubuntu/ld_gate_watch_last")

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
    "g11_script_lint.py": "/usr/local/bin/g11_script_lint.py",
    "qa_site.py": "/home/ubuntu/qa_site.py",
    "qa_extra.py": "/home/ubuntu/qa_extra.py",
    "site_audit.py": "/home/ubuntu/site_audit.py",
    "qa_truth.py": "/home/ubuntu/qa_truth.py",
    # LD-GATE-COVERAGE-20261016：这一批是"钱与共识"侧的门禁，之前完全没人盯它们本身。
    # 2026-10-14 那次发现的正是同类问题（5 个发布门禁不在版本库），当时只补了发布侧。
    # 事实核对：promote.py 与 qa_truth.py 的线上版本比仓库新（g11 挂进流水线、
    # status 缓存失效不变量），也就是说一旦按仓库重建机器，这两处防护会静默消失。
    "repo_leak_check.py": "/usr/local/bin/repo_leak_check.py",
    "ld_migrate_gate.py": "/usr/local/bin/ld_migrate_gate.py",
    "ld_cfg.sh": "/usr/local/bin/ld_cfg.sh",
    "ld_chain_params.sh": "/usr/local/bin/ld_chain_params.sh",
    "ld_treasury_keywatch.sh": "/usr/local/bin/ld_treasury_keywatch.sh",
    "ld_gov_fail_watch.py": "/usr/local/bin/ld_gov_fail_watch.py",
    # ld_code_audit.py 只在仓库里（一次性对账工具，没部署到主机），不进监控清单：
    # 2026-10-16 同步时发现 PATHS 里有它会导致"MISSING"噪声。
    # 看门狗自己也进清单：改它本身就会表现为哈希漂移（清单在仓库里，改仓库要走 commit）
    "ld_gate_watch.py": "/usr/local/bin/ld_gate_watch.py",
}


def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except Exception:
        return None


def main():
    try:
        if MANIFEST.startswith(("http://", "https://")):
            raw = urllib.request.urlopen(MANIFEST, timeout=25).read().decode()
        else:
            raw = open(MANIFEST).read()
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
        try:
            prev = open(LASTFLAG).read().split("|", 1)[-1]
        except Exception:
            prev = ""
    sig = json.dumps({"d": sorted(drift), "m": sorted(missing), "u": sorted(unversioned)}, sort_keys=True)
    # LD-GATEWATCH-WRITEGUARD-20261016：LASTFLAG 与 ld_alerts.log 都是 root cron 建的
    # root 属主文件，非 root 手工跑时 open(...,"w"/"a") 会抛 PermissionError，
    # 崩溃点正好在"已经发现漂移"之后——结果是漂移只打在屏幕上、退出码被 traceback 吞掉。
    # 反向验证（植入改动）时暴露出来。持久化失败必须喊出来，但绝不影响判定与退出码。
    for path, content in ((LASTFLAG, "0|" + sig),):
        try:
            open(path, "w").write(content)
        except Exception as e:
            print("  WARN 状态文件写不进去 %s: %s（不影响判定）" % (path, e))
    if bad and sig != prev:                      # 只在状态变化时告警，避免每 6 小时刷屏
        try:
            with open(ALERTS, "a") as f:
                f.write("%s ALERT deploy gates drifted from repo: %d drift, %d missing, %d unversioned\n"
                        % (UTC(), len(drift), len(missing), len(unversioned)))
        except Exception as e:
            print("  WARN 告警落盘失败 %s: %s —— 漂移未通知出去，请用 root 跑或改 LD_ALERTS"
                  % (ALERTS, e))
        else:
            subprocess.run(["/usr/local/bin/discord_bot.py", "send",
                            "⚠️ 发布门禁与仓库不一致（漂移%d/缺失%d/未入库%d）：门禁本身可能被改动，见 ld_gate_watch.log"
                            % (len(drift), len(missing), len(unversioned))], capture_output=True)
    return 1 if bad else 0


sys.exit(main())
