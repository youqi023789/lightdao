#!/bin/bash
mkdir -p /home/ubuntu/backups
tar czf /home/ubuntu/backups/gw-$(date +%F).tgz -C /home/ubuntu lightdao_gateway/data lightdao_gateway/granted.json 2>/dev/null
find /home/ubuntu/backups -name "gw-*.tgz" -mtime +7 -delete
echo "backup done $(date -u)"
