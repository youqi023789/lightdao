#!/usr/bin/env bash
# 统计 /gw/v1/heartbeat 每分钟请求数，用来证明"收紧 8080 之后矿工没断"。
# 用法：bash ld_gw_rate.sh [日志文件]
LOG=${1:-/var/log/nginx/access.log}
sudo awk '
  /POST \/gw\/v1\/heartbeat/ {
    # nginx combined 日志时间形如 [16/Oct/2026:11:07:43 +0000]
    i = index($4, "[")
    ts = substr($4, i+1, 20)
    hm = substr(ts, 13, 5)
    cnt[hm]++
  }
  END { for (k in cnt) printf "%s %6d\n", k, cnt[k] }
' "$LOG" | sort | tail -18
