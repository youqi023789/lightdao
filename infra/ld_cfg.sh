#!/bin/bash
# ld_cfg.sh — 配置漂移门(G17)。snap=建基线; check=对比, 未ack的漂移即告警; ack=接受当前为基线。
# 覆盖: ubuntu/root crontab, nginx 配置树, 关键 systemd 单元, /etc/hosts, 时区, snippets。
#
# [N2 fix 2026-10-01 月度审计] 判定必须与"调用身份"无关。
#   旧版 gen() 首行用 `crontab -l`(= 调用者的 crontab):root-cron 跑时取 root 表、
#   ubuntu 手动跑时取 ubuntu 表 → 同一时刻两种身份给出相反判定(ubuntu=DRIFT / root=clean),
#   门不可信(与已修的 qa_cross C4 同类 bug,commit 72e776e)。
#   修法:(1) 始终以 root 运行(非 root 自动 sudo 重入,带防循环 guard);
#        (2) gen() 显式按用户名采 ubuntu 与 root 两张 crontab(`crontab -l -u <user>`),
#            不再依赖调用者上下文。=> 任何身份调用得到同一基线/同一判定。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
if [ "$(id -u)" != "0" ] && [ -z "${LD_CFG_ROOTED:-}" ]; then
  export LD_CFG_ROOTED=1
  exec sudo -E "$0" "$@"
fi
B=/home/ubuntu/cfg_baseline.txt; S=/home/ubuntu/cfg_baseline.sha; ACK=/home/ubuntu/cfg_ack
gen() {
  { echo "--UBUNTUCRON--"; crontab -l -u ubuntu 2>/dev/null | grep -v "^CRON_TZ" | sort
    echo "--ROOTCRON--";   crontab -l -u root   2>/dev/null | grep -v "^CRON_TZ" | sort
    echo "--NGINX--"; cat /etc/nginx/sites-available/lightdao /etc/nginx/conf.d/*.conf /etc/nginx/snippets/* 2>/dev/null | grep -vE "^\s*#" | tr -s " "
    echo "--UNITS--"; for u in lightd lightdao-gateway lightd-upgrader headless-chrome; do systemctl cat $u 2>/dev/null | md5sum; done
    echo "--HOSTS--"; grep -v "^#" /etc/hosts | sort
    echo "--TZ--"; timedatectl show -p Timezone --value
  } 2>/dev/null
}
case "$1" in
  snap) gen > $B; sha256sum $B | cut -d" " -f1 > $S; echo "baseline $(cat $S)";;
  ack)  gen > $B; sha256sum $B | cut -d" " -f1 > $S; rm -f $ACK; echo "acked new baseline";;
  check)
    T=$(mktemp); gen > $T; CUR=$(sha256sum $T | cut -d" " -f1); OLD=$(cat $S 2>/dev/null)
    if [ "$CUR" != "$OLD" ]; then
      if [ -f $ACK ] && [ $ACK -nt $S ]; then mv $T $B; echo "$CUR" > $S; rm -f $ACK; echo "rebaselined (acked)"; exit 0; fi
      echo "$(date -u +%FT%TZ) CFG-DRIFT" >> /home/ubuntu/ld_alerts.log
      diff $B $T | head -40 >> /home/ubuntu/ld_cfg_diff.log 2>/dev/null
      /usr/bin/python3 /usr/local/bin/discord_bot.py send "⚠️ CONFIG DRIFT on $(hostname): see ld_cfg_diff.log (ack with ld_cfg.sh ack after review)" >/dev/null 2>&1
      echo "DRIFT detected"; rm -f $T; exit 4
    fi
    rm -f $T; echo "config clean";;
  *) echo "usage: ld_cfg.sh snap|check|ack";;
esac
