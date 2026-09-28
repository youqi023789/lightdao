#!/bin/bash
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
S=$(cat /home/ubuntu/lightdao_gateway/admin_secret)
D=$(/usr/local/bin/ld_day.sh prev)
echo "$(date -u +%FT%TZ) finalizing day $D" >> /home/ubuntu/ld_finalize.log
curl -s -X POST http://localhost:8080/v1/finalize -H "X-Admin: $S" -d "{\"day\":$D}" >> /home/ubuntu/ld_finalize.log 2>&1
echo >> /home/ubuntu/ld_finalize.log
