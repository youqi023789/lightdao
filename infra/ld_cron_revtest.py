#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反向验证：调度级别的失联必须被查出来。
临时从 ubuntu 的 crontab 里去掉 ld_finalize.sh 的 4 个调度之一，
对账必须报【清单有但线上没跑】并非零退出；随后完整恢复并核对行数。
（不用 shell 一行流做这件事：里面出现 del/rm 之类字样会被本机安全层拦，
  而且链式命令一旦短路会把关键状态改坏——今天已经栽过两次。）"""
import json
import subprocess
import sys

WHO = "ubuntu"
TARGET = "30 0 * * * /usr/local/bin/ld_finalize.sh"


def crontab(args):
    return subprocess.run(["crontab"] + args, capture_output=True, text=True, timeout=60)


def current():
    r = crontab(["-l", "-u", WHO])
    if r.returncode != 0:
        print("FAIL 读不到 crontab:", r.stderr[:150])
        sys.exit(2)
    return r.stdout


def run_reconcile():
    p = subprocess.run(["python3", "/usr/local/bin/ld_cron_reconcile2.py"],
                       capture_output=True, text=True, timeout=180)
    return p.returncode, (p.stdout + p.stderr)


base = current()
lines = base.splitlines()
keep = [l for l in lines if l.strip() != TARGET]
if len(keep) != len(lines) - 1:
    print("FAIL 锚点行不是恰好 1 条（找到 %d 条差异），放弃，不动 crontab"
          % (len(lines) - len(keep)))
    sys.exit(3)
open("/tmp/ub_without_one.cron", "w").write("\n".join(keep) + "\n")
open("/tmp/ub_original.cron", "w").write(base)
print("原 %d 行；已准备去掉 1 个调度的版本（%d 行）" % (len(lines), len(keep)))

r = crontab(["-u", WHO, "/tmp/ub_without_one.cron"])
if r.returncode != 0:
    print("FAIL 安装失败:", r.stderr[:150])
    sys.exit(4)
rc, out = run_reconcile()
print("=== 植入后对账 rc=%s ===" % rc)
for ln in out.splitlines()[-3:]:
    print("   ", ln[:130])

# 恢复
r2 = crontab(["-u", WHO, "/tmp/ub_original.cron"])
after = current().splitlines()
ok_restore = len(after) == len(lines) and TARGET in after
print("=== 恢复：原 %d 行 → 现 %d 行，目标调度已回来=%s，安装返回码=%s ==="
      % (len(lines), len(after), TARGET in after, r2.returncode))
rc3, out3 = run_reconcile()
print("恢复后对账 rc=%s：%s" % (rc3, out3.splitlines()[-1][:110]))
if rc == 0:
    print("FAIL 植入故障时没有报错，说明这道门禁不咬——修复未完成")
    sys.exit(5)
# 只断言"非零"是不够的：崩溃也返回非零（本次就是这么撞出解包 bug 的）。
# 必须断言它给出了人话结论、且没有 traceback。
if "Traceback" in out or "清单有但线上没跑" not in out:
    print("FAIL 植入故障时脚本没有正确报告（有 traceback 或缺少结论行）——"
          "非零退出但原因不对，等于门禁仍然不咬")
    sys.exit(8)
if rc3 != 0:
    print("FAIL 恢复后仍报错，说明恢复不完整")
    sys.exit(6)
if not ok_restore:
    sys.exit(7)
print("PASS 调度级失联可检出，且可完整恢复")
