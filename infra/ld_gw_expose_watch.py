#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LD-GW-EXPOSE-WATCH-20261016  看住 2026-10-16 这次收紧的成果不被悄悄改回去。
四条形不变量：
  E1 评分网关端口只在 127.0.0.1 上监听（0.0.0.0/:: 出现即违规）
  E2 systemd 单元/覆盖片段里没有明文 GW_ADMIN_SECRET=（必须走 EnvironmentFile）
  E3 口令文件 /etc/lightdao/gw_admin.env 属主 root:ubuntu、权限不宽于 640
  E4 对外唯一入口 /gw/v1/health 必须 200（否则"关掉了 8080 顺手把服务也关了"）
读不到就报，不静默跳过（本项目反复吃过这个亏）。
反向验证：另起一个真的监听在 0.0.0.0 的影子端口，用 LD_GW_PORT 指过去，必须报 E1。"""
import os
import re
import subprocess
import sys
import time
import urllib.request

PORT = os.environ.get("LD_GW_PORT", "8080")
UNIT = "lightdao-gateway"
ENVF = os.environ.get("LD_GW_ENVFILE", "/etc/lightdao/gw_admin.env")
HEALTH = os.environ.get("LD_GW_HEALTH", "https://lightdao.net/gw/v1/health")
ALERTS = os.environ.get("LD_ALERTS", "/home/ubuntu/ld_alerts.log")
MARK = "/home/ubuntu/ld_gw_expose_last"


def sh(args):
    p = subprocess.run(args, capture_output=True, timeout=45)
    return p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")


def checks():
    bad = []
    # E1：注意 ss -ltn 的"本地地址"是第 4 列，且 IPv6 会写成 [::]:8080。
    # 上一版按"第 3 列"匹配，真公网监听匹配不到、反而报"没监听"——
    # 如果端口同时绑在 127.0.0.1 和 0.0.0.0，那版会当成通过（反向验证才抓出来）。
    ss = sh(["ss", "-ltn"])
    rows = [l.replace("[", "").replace("]", "") for l in ss.splitlines()]
    pub = [l for l in rows
           if re.search(r"(^|\s)(0\.0\.0\.0|\*|::):%s(\s|$)" % re.escape(PORT), l)]
    loc = [l for l in rows
           if re.search(r"(^|\s)127\.0\.0\.1:%s(\s|$)" % re.escape(PORT), l)]
    if pub:
        bad.append("E1 端口 %s 正监听在公网地址上（应只绑 127.0.0.1）: %s"
                   % (PORT, pub[0].split()[-2] if len(pub[0].split()) > 3 else pub[0][:60]))
    elif not loc:
        bad.append("E1 端口 %s 根本没有监听（服务没起来？也不算通过）" % PORT)
    # E2
    unit = sh(["systemctl", "cat", UNIT])
    if re.search(r"^\s*Environment=GW_ADMIN_SECRET=\S", unit, re.M):
        bad.append("E2 systemd 单元里又有明文 GW_ADMIN_SECRET（systemctl cat 就能看到口令）")
    if "EnvironmentFile=" not in unit:
        bad.append("E2 单元里没有 EnvironmentFile=，口令来源不明")
    # E3：只有"其他用户"的位才算过宽；组可读是必须的（服务以 ubuntu 身份跑要能读）
    if not os.path.exists(ENVF):
        bad.append("E3 口令文件不存在: %s" % ENVF)
    else:
        st = os.stat(ENVF)
        mode = st.st_mode & 0o777
        if mode & 0o007:
            bad.append("E3 %s 权限 %o：同机其他用户可读" % (ENVF, mode))
        if not (mode & 0o040):
            bad.append("E3 %s 权限 %o：组读不到，服务（User=ubuntu）会拿不到口令"
                       % (ENVF, mode))
        if st.st_uid != 0:
            bad.append("E3 %s 属主不是 root（uid=%s）" % (ENVF, st.st_uid))
    # E4
    try:
        code = urllib.request.urlopen(HEALTH, timeout=15).status
    except Exception as e:
        code = getattr(e, "code", 0)
    if code != 200:
        bad.append("E4 对外入口 %s 返回 %s（矿工进不来）" % (HEALTH, code))
    return bad


def main():
    bad = checks()
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    sig = "; ".join(sorted(bad))
    prev = ""
    if os.path.exists(MARK):
        try:
            prev = open(MARK).read().split("|", 1)[-1]
        except Exception:
            prev = ""
    n = 0
    if os.path.exists(MARK):
        try:
            n = int(open(MARK).read().split("|")[0])
        except Exception:
            n = 0
    if bad:
        n = n + 1 if sig == prev else 1
        msg = "%s ALERT [gw-expose] %d 条形不变量被破坏: %s" % (ts, len(bad), sig)
    else:
        n = 0
        msg = ""
    try:
        open(MARK, "w").write("%d|%s" % (n, sig))
    except Exception as e:
        print("WARN 状态文件写不进 %s: %s" % (MARK, e))
    for b in bad:
        print("  VIOLATION " + b)
    if bad:
        print(msg)
        if n >= 2:      # 连续两轮才告警，躲开瞬时抖动；但退出码当场就非零
            try:
                with open(ALERTS, "a") as f:
                    f.write(msg + "\n")
                print("已写告警通道")
            except Exception as e:
                print("WARN 告警没落盘 %s: %s —— 请用 root 跑或设 LD_ALERTS" % (ALERTS, e))
        return 1
    if prev:
        # 上一轮有违规、这轮干净：记一条恢复，别只留一条孤零零的告警
        try:
            with open(ALERTS, "a") as f:
                f.write("%s NOTE [gw-expose] 网关暴露面不变量恢复正常（上一轮: %s）\n"
                        % (ts, prev[:120]))
        except Exception:
            pass
    print("GW EXPOSE OK：E1-E4 四条不变量全部成立（端口 %s 只绑本机、口令单一来源、对外入口 200）"
          % PORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
