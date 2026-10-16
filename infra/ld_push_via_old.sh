#!/bin/bash
# 从 HK 仓库经 sg-old（唯一持有 GitHub 凭据的机器）做"仅快进"推送。
# 绝不强推；有分歧就停下报告。令牌值全程脱敏。
set -e
BR=${1:-main}
TS=$(date +%Y%m%dT%H%M%SZ)
BUNDLE=/home/ubuntu/backup/push-$TS.bundle
mkdir -p /home/ubuntu/backup
cd /home/ubuntu/repo
git bundle create "$BUNDLE" "$BR" >/dev/null 2>&1
scp -q "$BUNDLE" sg-old:~/hk_push.bundle
ssh sg-old "set -e; cd ~/repo-push
  timeout 60 git fetch -q origin $BR 2>&1 | sed -E 's#(://)[^@/]*@#\1***@#g' || true
  git fetch -q ~/hk_push.bundle $BR:refs/remotes/hkmain
  if git merge-base --is-ancestor origin/$BR refs/remotes/hkmain; then
    N=\$(git rev-list --count origin/$BR..refs/remotes/hkmain)
    echo \"快进可行，待推 \$N 个提交\"
    timeout 90 git push origin refs/remotes/hkmain:$BR 2>&1 | sed -E 's#(://)[^@/]*@#\1***@#g' | tail -4
  else
    echo 'DIVERGED：远端有本地没有的提交，拒绝推送（不强推）'
    git log --oneline origin/$BR -3
    exit 9
  fi
  rm -f ~/hk_push.bundle"
echo "--- 远端 HEAD 复核 ---"
ssh sg-old "timeout 30 git -C ~/repo-push ls-remote origin -h refs/heads/$BR 2>/dev/null | cut -c1-45"
ssh sg "cd /home/ubuntu/repo; timeout 40 git fetch -q origin $BR || true; echo \"HK 认为 origin/$BR = \$(git rev-parse origin/$BR | cut -c1-12)；本地领先 \$(git rev-list --count origin/$BR..HEAD)\"; rm -f $BUNDLE"
echo PUSH_FLOW_DONE
