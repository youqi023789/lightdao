#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 CRON_MANIFEST.json 里残留的 purpose=TODO 逐条补成一句人话。
清单只登记"有什么命令"是不够的：机器重建时，没人知道某条任务为什么必须存在、
删掉会怎样——那才是它最容易被顺手砍掉的时候。"""
import json
import re
import sys

MAN = "/home/ubuntu/repo/docs/CRON_MANIFEST.json"
FILL = {
    "ld_sign_root.sh": "每日奖励根多签签发：站点结算与链上发分的源头，缺它当天没有奖励根",
    "ld_sri.sh": "重算并校验脚本 SRI（子资源完整性哈希），防线上 js 被改动而页面仍照常加载",
    "ld_validator_watch.py": "验证者在线/落后巡检（脱敏后的 ld-node-01..10），掉线或落后即告警",
    "ld_vesting_watch.sh": "vesting 计划看门狗：解锁/领取窗口与链上实际是否一致",
    "ld_watchdog.sh": "监控自身的看门狗：status.json 必须 <15 分钟新鲜，否则说明 monitor 死了或被致盲",
    "qa_cross_cron.sh": "跨层契约巡检 C1-C7（页面显示值 ↔ 网关 ↔ 链上三方是否互相自洽）",
    "wp_reconcile.py": "白皮书口径与链上真实数值对账（发行量/释放/质押参数变了要说出来）",
    "withdraw-all-rewards": "每周提取验证者佣金到运营账户（不提取=收益躺在分配池里不动）",
    "ld_gov_fail_watch.py": "治理提案执行失败看门狗：提案通过但执行失败=规则没改成功",
    "rebuild_search": "重建站内搜索索引，新页面/新文档要能被搜到",
    "lightdao_oracle_feeder.sh": "TWAP 预言机喂价，喂不动则依赖价格的页面与合约拿旧值",
    "ld_backup.sh": "每日备份（配置+台账+清单），是异地恢复的唯一来源",
    "ld_voters_backup.sh": "投票人数据备份",
    "ld_monitor.py": "主监控：链高/出块/错误率/客户端报错，status.json 由它产出",
    "mig_autopilot.sh": "节点健康自动驾驶：HTTP RPC 高度与落后检测，空清单必须响亮失败",
    "ld_grant_watch.py": "免 Gas 代付看门狗：签发失败会让用户领取静默失败",
    "ld_render_watch.py": "钱相关三页深度渲染断言（导航/返回按钮/出块实测/链上取数跑通/提案分组禁用）",
    "ld_render_all.py": "全站 18 页真机渲染巡检 + 语种棘轮",
    "ld_migrate_gate.py": "迁移门禁：敏感合约迁到无源/不可复现 code 时非零退出并告警",
    "ld_miner_watch.py": "矿工留存看门狗：整天掉人>=2 或连续>=3 天零新增即告警",
    "ld_ops_reconcile.py": "运维脚本对账：cron 在用的脚本与仓库不一致或未入库即非零退出",
    "ld_gw_expose_watch.py": "网关暴露面哨兵 E1-E4（8080 只绑本机、单元无明文口令、口令文件权限、/gw 200）",
    "ld_gate_watch.py": "门禁自身完整性：线上门禁脚本哈希必须等于仓库清单记录",
    "ld_treasury_keywatch.sh": "金库密钥不变量：磁盘不得出现签名私钥明文、钥匙环签名人数必须为 0",
    "repo_leak_check.py": "公开仓库泄露扫描门禁（IP/密钥/助记词/webhook/桌面路径）",
    "ld_cron_reconcile2.py": "本门禁：线上 cron 与清单双向对账",
    "ld_epoch_audit.py": "挖矿纪元/日界审计：日界与提案 #11 对齐后要复核领取窗口",
    "ld_claim_gas_watch.py": "领取免 Gas 通道看门狗",
    "ld_daily_telegram.sh": "每日 Telegram 播报（对外发布，脚本化自动发）",
    "ld_alerts_and_hosts.sh": "告警汇聚与侧车地址读取",
    "discord_bot.py": "告警投递到 Discord",
}

d = json.load(open(MAN, encoding="utf-8"))
n = 0
for j in d.get("jobs") or []:
    if not str(j.get("purpose", "")).startswith("TODO"):
        continue
    c = j.get("cmd") or ""
    for k, v in FILL.items():
        if k in c:
            j["purpose"] = v
            n += 1
            break
left = [j["cmd"][:70] for j in (d.get("jobs") or [])
        if str(j.get("purpose", "")).startswith("TODO")]
with open(MAN, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("补全 %d 条；仍剩 TODO %d 条" % (n, len(left)))
for x in left:
    print("   还差: %s" % x)
