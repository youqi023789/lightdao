#!/bin/bash
# LD-G10-DAILY-20261104  每天把"G10 独立重算 Merkle 根/总分"跑一遍（原来只在发布时当门禁跑）。
#
# 为什么现在加：站内首页写着"持续自审 + 每日独立对账"，而真正每天重算根/分数的那件事，
# 之前挂在 QwenWork 定时任务（每日经济对账）里，用的是会消耗额度的智能体——
# 10-30 之后它连续失败（runlog 原因：The usage limit has been reached），
# 于是"每日独立对账"这句声明事实上断了 5 天，而服务器的告警面一声不响。
# 修法不是再养一个智能体，而是把已有量具挪进 cron：零成本、确定性、失败必响。
#
# 口径：非零退出 → 写 G10-PARITY-FAIL 告警（同一签名只在变化时刷屏一次），恢复时写一条 OK；
#       拿不到结果（脚本自身崩了/超时）同样算 FAIL，绝不把"没量到"当成"没问题"。
# 可测性：LD_G10_CHECKER 可换成桩脚本，用于反向验证（默认是真门）。
set -u
CHECKER=${LD_G10_CHECKER:-/usr/local/bin/g10_root_parity_check.py}
ALERTS=/home/ubuntu/ld_alerts.log
STATE=/home/ubuntu/.ld_g10_daily_state
ts=$(date -u +%FT%TZ)

OUT=$(timeout 600 python3 "$CHECKER" 2>&1); RC=$?
SIG=$(printf '%s' "$OUT" | md5sum | cut -c1-16)
PREV=$(cat "$STATE" 2>/dev/null || echo "")

if [ "$RC" -ne 0 ]; then
  echo "G10-PARITY-FAIL rc=$RC"
  printf '%s\n' "$OUT" | tail -6 | sed 's/^/  /'
  if [ "$PREV" != "F:$SIG" ]; then
    echo "$ts G10-PARITY-FAIL rc=$RC $(printf '%s' "$OUT" | tr '\n' ' ' | tail -c 300)" >> "$ALERTS"
    echo "F:$SIG" > "$STATE"
  fi
  exit 1
fi
echo "G10-PARITY-OK $(printf '%s' "$OUT" | tr '\n' ' ' | tail -c 120)"
if printf '%s' "$PREV" | grep -q '^F:'; then
  echo "$ts G10-PARITY-OK（此前 $PREV 的告警已恢复）" >> "$ALERTS"
fi
echo "OK" > "$STATE"
exit 0
