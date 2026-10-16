#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 CRON_MANIFEST.json 按线上真实任务重建一次，并把老条目里的 purpose 带过来。
匹配用"命令的前两个词"（解释器 + 脚本路径），因为旧 --gen 生成的条目尾部有被截断的
`2`、重定向写法也不统一，整串比对永远对不上——这正是它长期失真的原因。
重建后：清单 = 线上事实 + 人工说明；此后新增任务若没登记，对账会立刻报"未登记"。"""
import json
import os
import re
import subprocess
import sys
import time

MAN = "/home/ubuntu/repo/docs/CRON_MANIFEST.json"
TODAY = time.strftime("%Y-%m-%d")

# 今天新装的 5 条：purpose 直接写好，免得留 TODO 变成没人补的坑
PURPOSE = {
    "ld_migrate_gate.py": "迁移门禁：敏感合约要迁到无源/不可复现的 code 时非零退出并告警（提案 #14/#15 真出过事）",
    "ld_miner_watch.py": "矿工留存看门狗：已完成整天掉人>=2 或连续>=3 天零新增即告警；查不到网关数据判 QUERY-FAIL",
    "ld_render_all.py": "全站 18 页真机渲染巡检（L1 每小时查资源/链接/兜底冒充，L2 每 6 小时查脚本真跑起来 + 语种棘轮）",
    "ld_ops_reconcile.py": "运维脚本对账：cron 在用的脚本只要与仓库不一致或未入库就非零退出（机器重建不会静默丢防护）",
    "ld_gw_expose_watch.py": "网关暴露面哨兵：8080 只绑本机、单元里无明文口令、口令文件权限正确、/gw 入口 200",
    "ld_cron_reconcile2.py": "本门禁自己：线上 cron 与清单双向对账（未登记=漂移，清单有而线上无=静默死亡）",
    "repo_leak_check.py": "公开仓库泄露扫描门禁（基础设施 IP/密钥/助记词/webhook/桌面路径）",
    "ld_render_watch.py": "钱相关三页的深度渲染断言（导航/返回按钮/出块实测/链上取数跑通/提案分组禁用）",
    "ld_treasury_keywatch.sh": "金库密钥不变量：磁盘不得出现签名私钥明文、钥匙环签名人数必须为 0、密文备份必须在位",
    "ld_gov_fail_watch.py": "治理提案执行失败看门狗（提案通过但执行失败=资金规则没改成功）",
    "ld_gate_watch.py": "门禁自身完整性：线上部署的门禁脚本哈希必须等于仓库清单记录（防被改/被删/仓库与线上不一致）",
    "ld_grant_watch.py": "免 Gas 代付看门狗：签发失败会让用户领取静默失败",
    "ld_monitor.py": "主监控（链高/出块/错误率/客户端报错等）",
    "ld_backup.sh": "每日备份",
    "ld_voters_backup.sh": "投票人数据备份",
    "lightdao_oracle_feeder.sh": "TWAP 预言机喂价",
    "rebuild_search.sh": "站内搜索索引重建",
    "ld_finalize.sh": "每日奖励根 finalize（站点结算与发分的源头）",
    "mig_autopilot.sh": "迁移/节点健康自动驾驶（HTTP RPC 高度与落后检测）",
}


def norm(line):
    s = re.sub(r"\s#.*$", "", line.strip())
    s = re.sub(r">>?\s*\S+(\s+2>&1)?", "", s)
    s = re.sub(r"2>&1", "", s)
    parts = s.split()
    while parts and re.match(r"^[A-Z_][A-Z0-9_]*=", parts[0]):
        parts = parts[1:]
    if parts and parts[0].startswith("@"):
        parts = parts[1:]
    else:
        parts = parts[5:]
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def sched(line):
    s = re.sub(r"\s#.*$", "", line.strip()).split()
    return s[0] if s and s[0].startswith("@") else " ".join(s[:5])


def purpose_of(cmd):
    for k, v in PURPOSE.items():
        if k in cmd:
            return v
    return "TODO 补一句为什么需要它"


def norm_cmd(cmd):
    """清单里的 cmd 只有命令，绝不能按 crontab 行砍前 5 个字段（那是上一版对账器
    把 45 条任务全砍成空串/半截的原因）。"""
    s = re.sub(r">>?\s*\S+(\s+2>&1)?", "", (cmd or "").strip())
    s = re.sub(r"2>&1", "", s)
    s = re.sub(r"\s2$", "", s)
    return re.sub(r"\s+", " ", s).strip()


old = {}
old_exact = {}
if os.path.exists(MAN):
    try:
        for j in (json.load(open(MAN, encoding="utf-8")).get("jobs") or []):
            c = norm_cmd(j.get("cmd") or "")
            sig = " ".join(c.split()[:2])
            if j.get("purpose") and sig not in old:
                old[sig] = j["purpose"]
            if j.get("purpose") and not str(j["purpose"]).startswith("TODO"):
                old_exact[(j.get("user"), c)] = j["purpose"]
    except Exception as e:
        print("旧清单读取失败（不影响重建）:", e)

live = []
for u in ("root", "ubuntu"):
    args = ["crontab", "-l"] if u == "root" else ["crontab", "-l", "-u", u]
    r = subprocess.run(args, capture_output=True, text=True, timeout=60)
    for ln in (r.stdout or "").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        c = norm(ln)
        if not c:
            continue
        c = re.sub(r"\s2$", "", c)
        sig = " ".join(c.split()[:2])
        live.append({"user": u, "schedule": sched(ln), "cmd": c,
                     # 先按 (用户, 命令) 精确继承旧清单里已写好的 purpose，
                     # 再退到内置表。上一版这里写成 `purpose_of(c) or old.get(...)`，
                     # 而 purpose_of 找不到时返回的是 "TODO …"（真值），
                     # 于是旧说明永远继承不到——每次重建都把人工补的中文说明清空。
                     "purpose": (old_exact.get((u, c)) or old.get(sig)
                                 or purpose_of(c) or ""),
                     "added": TODAY})

seen = set()
jobs = []
for j in sorted(live, key=lambda x: (x["user"], x["cmd"])):
    k = (j["user"], j["cmd"])
    if k in seen:
        continue
    seen.add(k)
    if not j["purpose"]:
        j["purpose"] = "TODO 补一句为什么需要它"
    jobs.append(j)

out = {"_comment": "Canonical cron manifest for the gateway. Reconciled daily by "
                   "ld_cron_reconcile2.py (G24). Regenerate: ld_cron_reconcile2.py --gen, "
                   "review, commit. 2026-10-16 rebuilt from live crontabs because the old "
                   "file's commands carried '--gen' truncation artifacts (trailing 2) and "
                   "the reconciler itself was never scheduled.",
       "generated": TODAY, "jobs": jobs}
tmp = MAN + ".new"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write("\n")
os.replace(tmp, MAN)
todo = sum(1 for j in jobs if j["purpose"].startswith("TODO"))
print("清单重建完成：%d 条（root %d / ubuntu %d），其中待补 purpose %d 条"
      % (len(jobs), sum(1 for j in jobs if j["user"] == "root"),
         sum(1 for j in jobs if j["user"] == "ubuntu"), todo))
for j in jobs:
    if j["purpose"].startswith("TODO"):
        print("   TODO: [%s] %s" % (j["user"], j["cmd"][:80]))
