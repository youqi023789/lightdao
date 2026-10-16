#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补完 CRON_MANIFEST 里剩下的 purpose=TODO 条目（第二批）。"""
import json

MAN = "/home/ubuntu/repo/docs/CRON_MANIFEST.json"
FILL = {
    "gas_grant.py": "每日为矿工签发免 Gas 代付额度（缺它新用户领取会因没有 gas 静默失败）",
    "canary_claim.py beat": "金丝雀账户心跳场景自检：验证【节点在线】这条链路真能被观测到",
    "canary_claim.py claim": "金丝雀账户真实领取自检：每天真的领一次，确保领取链路没坏",
    "canary_claim.py degraded": "金丝雀账户降级场景自检：故意走异常路径，确认降级会被报出来",
    "ld_gov_guard.py": "治理守卫：盯异常提案/参数变更（提案通过但内容危险时先喊）",
    "ld_cfg.sh check": "配置漂移门禁：crontab/关键配置与基线不一致即告警（缺基线时响亮失败）",
    "ld_chain_params.sh check": "链上参数漂移门禁：gov/wasm/staking/mint/slashing/共识参数/min-gas 逐项对基线",
    "ld_cron_reconcile.py": "旧版 cron 对账（清单路径写死在已消失目录，被 ld_cron_reconcile2.py 取代，待停用）",
    "ld_cve_watch.py": "依赖与安全公告巡检（CometBFT/SDK/cosmwasm 相关 CVE）",
    "ld_daily_discord.sh": "每日 Discord 播报",
    "ld_daily_x_marketing.sh": "每日 X（推特）自动发布（对外发言，按规矩需逐次授权，改文案要走人工）",
    "ld_gateway_trace_watch.py": "网关请求追踪看门狗：异常比例/慢请求/5xx 抬头即告警",
    "ld_observer_watch.sh": "观察者节点（对外 RPC）健康：落后或拒绝服务时页面数据会假死",
    "ld_secret_scan.py": "密钥/助记词二次扫描（与 repo_leak_check 不同层，扫主机文件与产物）",
}

d = json.load(open(MAN, encoding="utf-8"))
n = 0
for j in d.get("jobs") or []:
    p = str(j.get("purpose", ""))
    if not p.startswith("TODO"):
        continue
    c = j.get("cmd") or ""
    for k, v in FILL.items():
        if k in c:
            j["purpose"] = v
            n += 1
            break
left = [j["cmd"][:80] for j in d["jobs"] if str(j.get("purpose", "")).startswith("TODO")]
with open(MAN, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("补全 %d 条；仍剩 %d 条" % (n, len(left)))
for x in left:
    print("   还差:", x)
