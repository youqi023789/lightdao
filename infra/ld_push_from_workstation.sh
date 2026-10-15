#!/bin/bash
# ld_push_from_workstation.sh — 从【本机/工作站】把 HK 网关上的仓库仅快进推到 GitHub。
#
# 为什么必须在本机跑：HK 网关机器上没有 GitHub 凭据，且 HK→sg-old 无互信密钥
# （实测从 HK 直接 scp 到 sg-old 被拒）。只有本机能同时 ssh 到两台。
# （我先前提交的 ld_push_via_old.sh 假设可以在 HK 上跑，是错的，已废弃。）
#
# 安全：绝不 --force；远端若领先本地，停下报告。令牌全程脱敏。
set -e
BR=${1:-main}
TS=$(date +%Y%m%dT%H%M%SZ)
TMPB="$(dirname "$0")/.push-$TS.bundle"

echo "[1/4] HK 打 bundle"
ssh sg "mkdir -p /home/ubuntu/backup && cd /home/ubuntu/repo && git bundle create /home/ubuntu/backup/push-$TS.bundle $BR >/dev/null 2>&1 && git rev-parse --short HEAD"

echo "[2/4] HK -> 本机 -> sg-old 中转"
scp -q "sg:/home/ubuntu/backup/push-$TS.bundle" "$TMPB"
scp -q "$TMPB" "sg-old:~/hk_push.bundle"

echo "[3/4] sg-old 校验并仅快进推送"
ssh sg-old "set -e; cd ~/repo-push
  timeout 60 git fetch -q origin $BR
  git fetch -q ~/hk_push.bundle $BR:refs/remotes/hkmain
  if git merge-base --is-ancestor origin/$BR refs/remotes/hkmain; then
    N=\$(git rev-list --count origin/$BR..refs/remotes/hkmain)
    echo \"  快进可行：\$N 个提交\"
    timeout 90 git push origin refs/remotes/hkmain:$BR 2>&1 | sed -E 's#(://)[^@/]*@#\1***@#g' | tail -3
  else
    echo '  DIVERGED：远端有本地没有的提交，拒绝推送（不使用 --force）'
    git log --oneline origin/$BR -3
    exit 9
  fi"

echo "[4/4] 复核 + 清理远端临时 bundle"
ssh sg-old "timeout 30 git -C ~/repo-push ls-remote origin -h refs/heads/$BR 2>/dev/null | cut -c1-45; rm -f ~/hk_push.bundle"
ssh sg "cd /home/ubuntu/repo && timeout 40 git fetch -q origin $BR || true; echo \"  HK 认为 origin/$BR = \$(git rev-parse origin/$BR | cut -c1-12)，本地领先 \$(git rev-list --count origin/$BR..HEAD)\"; rm -f /home/ubuntu/backup/push-$TS.bundle"
echo "PUSH_DONE"

# 本机临时 bundle 由调用方按文件保护策略回收（不用 rm）
echo "TEMP_BUNDLE=$TMPB"
