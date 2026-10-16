#!/bin/bash
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
# LD-GW-HARDEN 管理员口令只有一个来源，避免"单元里一份、文件里一份"迟早对不上
S=$(grep -m1 "^GW_ADMIN_SECRET=" /etc/lightdao/gw_admin.env | cut -d= -f2-)
D=$(/usr/local/bin/ld_day.sh prev)
echo "$(date -u +%FT%TZ) finalizing day $D" >> /home/ubuntu/ld_finalize.log
curl -s -X POST http://localhost:8080/v1/finalize -H "X-Admin: $S" -d "{\"day\":$D}" >> /home/ubuntu/ld_finalize.log 2>&1
echo >> /home/ubuntu/ld_finalize.log
