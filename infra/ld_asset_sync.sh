#!/bin/bash
# LD-ASSET-SYNC-20261104  把"promote 不负责的静态资产"从仓库同步到线上（白名单，逐文件按内容比对）。
#
# 为什么需要（今天实测出来的双源漂移）：promote.py 只复制 *.html 与 js/*.js，
# 白皮书 whitepaper.md 一直是手工 cp——结果 11-04 加了勘误后，线上还是旧版，
# 仓库与线上两份表达不一致，而且没有任何东西会响。这类问题不能靠"我记得复制"。
#
# 口径：
#  · 白名单而不是通配全目录：线上目录里还有 SRI 注入过的 html/js，那些必须走 promote 的门禁，
#    不能让这个脚本绕过门禁覆盖（绕过门禁的"方便"就是下一次事故的入口）。
#  · 只在内容不同才复制；复制后立刻回读比对，不一致就报警退出。
#  · 读不到源文件 = 失败，绝不当成"没变化所以通过"。
set -u
SRC=${LD_ASSET_SRC:-/home/ubuntu/repo/client}
DST=${LD_ASSET_DST:-/var/www/lightdao}
ALERTS=${LD_ALERTS:-/home/ubuntu/ld_alerts.log}
FILES="whitepaper.md"
changed=0
fail=0
for f in $FILES; do
  s="$SRC/$f"; d="$DST/$f"
  if [ ! -r "$s" ]; then
    echo "$(date -u +%FT%TZ) ASSET-SYNC-FAIL 源文件读不到：$s" >> "$ALERTS"
    echo "ASSET-SYNC-FAIL 源文件读不到：$s"; fail=1; continue
  fi
  hs=$(md5sum "$s" | cut -d" " -f1)
  hd=$(md5sum "$d" 2>/dev/null | cut -d" " -f1)
  if [ "$hs" = "$hd" ]; then
    echo "OK $f 已一致"
    continue
  fi
  cp "$s" "$d"
  hd2=$(md5sum "$d" 2>/dev/null | cut -d" " -f1)
  if [ "$hs" != "$hd2" ]; then
    echo "$(date -u +%FT%TZ) ASSET-SYNC-FAIL $f 复制后回读不一致（src=$hs dst=$hd2）" >> "$ALERTS"
    echo "ASSET-SYNC-FAIL $f 回读不一致"; fail=1; continue
  fi
  echo "SYNCED $f（$hd→$hd2）"; changed=1
done
[ "$fail" = "1" ] && exit 5
echo "asset-sync 完成（有变更=$changed）"
exit 0
