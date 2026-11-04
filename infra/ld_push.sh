#!/bin/bash
# LD-PUSH-RETRY-20261104  推送到 origin 带重试与"卡住必须响"。
#
# 为什么需要（今天实测）：同一台机器、同一把 ed25519 部署密钥，
# `ssh -T git@github.com` 在 6 秒内出现 2 次成功 + 1 次 Permission denied (publickey)；
# git push 也连续 4 次失败、第 5 次成功。也就是说 GitHub 侧鉴权是**偶发**抖动，
# 单次失败既不说明密钥被撤销，也不说明该改配置——真正的危险是"重试没人做、仓库悄悄落后"，
# 而站内承诺是"合约开源、可自验"，访客是照着仓库核对的。
#
# 做法：重试最多 LD_PUSH_TRIES 次（退避 15/30/45…），每次失败打印真实末行（不吞错误）；
# 结束后用 `rev-list --count @{u}..HEAD` 客观核对是否真的追平；
# 没追平就写 REPO-PUSH-STUCK 告警并非零退出（查不到 gap 也当失败，绝不当成通过）。
#
# 用法：ld_push.sh                    # 正常推送
#       LD_PUSH_REPO=/tmp/x ld_push.sh # 反向验证（不存在的仓库 → 必须 REPO-PUSH-STUCK）
set -u
REPO=${LD_PUSH_REPO:-/home/ubuntu/repo}
TRIES=${LD_PUSH_TRIES:-5}
ALERTS=${LD_ALERTS:-/home/ubuntu/ld_alerts.log}

if [ ! -d "$REPO/.git" ]; then
  echo "$(date -u +%FT%TZ) REPO-PUSH-STUCK repo=$REPO 不是 git 仓库（反向验证路径）" >> "$ALERTS"
  echo "REPO-PUSH-STUCK repo=$REPO 不存在或不是 git 仓库"; exit 5
fi

ok=0
for i in $(seq 1 "$TRIES"); do
  out=$(cd "$REPO" && timeout 90 git push 2>&1); rc=$?
  if [ "$rc" -eq 0 ]; then echo "push ok（第 $i 次）"; ok=1; break; fi
  echo "第 $i 次失败: $(printf '%s' "$out" | tail -1 | cut -c1-90)"
  sleep $((i * 15))
done

gap=$(cd "$REPO" && git rev-list --count '@{u}..HEAD' 2>/dev/null)
case "$gap" in
  ''|*[!0-9]*) gap=unknown ;;
esac
if [ "$ok" = "1" ] && [ "$gap" = "0" ]; then
  echo "OK 本地与 origin 一致（gap=0）"
  exit 0
fi
echo "$(date -u +%FT%TZ) REPO-PUSH-STUCK ok=$ok gap=${gap}（重试 $TRIES 次仍未追平 origin；站内'开源可自验'暂时名不副实，需人工处理）" >> "$ALERTS"
echo "REPO-PUSH-STUCK ok=$ok gap=${gap}"; exit 5
