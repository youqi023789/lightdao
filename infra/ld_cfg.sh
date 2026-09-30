#!/bin/bash
# ld_cfg.sh — 配置漂移门(G17)。snap=建基线; check=对比, 未ack的漂移即告警; ack=接受当前为基线。
# 覆盖: ubuntu/root crontab, nginx 配置树, 关键 systemd 单元, /etc/hosts, 时区, snippets。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
B=/home/ubuntu/cfg_baseline.txt; S=/home/ubuntu/cfg_baseline.sha; ACK=/home/ubuntu/cfg_ack
gen() {
  { crontab -l 2>/dev/null | grep -v "^CRON_TZ" | sort
    echo "--ROOTCRON--"; sudo crontab -l 2>/dev/null | sort
    echo "--NGINX--"; sudo cat /etc/nginx/sites-available/lightdao /etc/nginx/conf.d/*.conf /etc/nginx/snippets/* 2>/dev/null | grep -vE "^\s*#" | tr -s " "
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
