#!/usr/bin/env bash
# G24 修订版的反向验证：两个方向都必须真的会咬。
# 全程用文件备份 + 行数校验恢复，不用链式 &&/||（今天就是被它坑过一次）。
set -u
WHO=ubuntu
BKP=/tmp/cronrecon_test_$(date +%s)
sudo cp /home/ubuntu/repo/docs/CRON_MANIFEST.json $BKP.man
crontab -l -u $WHO > $BKP.cron 2>/dev/null || sudo crontab -l -u $WHO > $BKP.cron
BEFORE=$(grep -c . $BKP.cron)
echo "起点：ubuntu crontab $BEFORE 条；清单 $(sudo python3 -c "import json;print(len(json.load(open('/home/ubuntu/repo/docs/CRON_MANIFEST.json'))['jobs']))") 条"

echo
echo "=== 方向一：线上多一条未登记的任务，必须报 rc=1 ==="
sudo python3 /usr/local/bin/ld_cron_add_safe.py $WHO \
  "*/59 * * * * /bin/true  # LD-RECON-SELFTEST" | tail -1
sudo python3 /usr/local/bin/ld_cron_reconcile2.py > $BKP.r1 2>&1; RC=$?
echo "rc=$RC（应为 1）"; grep -E "未登记|ALERT" $BKP.r1 | head -2 | cut -c1-110

echo
echo "=== 恢复 crontab 并核对行数 ==="
sudo crontab -u $WHO $BKP.cron
AFTER=$(sudo crontab -l -u $WHO | grep -c .)
echo "恢复后 $AFTER 条（应为 $BEFORE）；自检标记残留 $(sudo crontab -l -u $WHO | grep -c LD-RECON-SELFTEST) 条"

echo
echo "=== 方向二：清单里删掉一条（线上还在跑），必须报【清单有但线上没跑】 rc=1 ==="
sudo python3 - <<PY
import json
p="/home/ubuntu/repo/docs/CRON_MANIFEST.json"
d=json.load(open(p,encoding="utf-8"))
drop=[j for j in d["jobs"] if "ld_monitor.py" in j["cmd"]][0]
d["jobs"]=[j for j in d["jobs"] if j is not drop]
json.dump(d,open(p,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("已从清单临时删除:",drop["cmd"][:60])
PY
sudo python3 /usr/local/bin/ld_cron_reconcile2.py > $BKP.r2 2>&1; RC2=$?
echo "rc=$RC2（应为 1）"; grep -E "清单有但线上没跑|ALERT" $BKP.r2 | head -2 | cut -c1-110

echo
echo "=== 恢复清单并复核全绿 ==="
sudo cp $BKP.man /home/ubuntu/repo/docs/CRON_MANIFEST.json
sudo python3 /usr/local/bin/ld_cron_reconcile2.py | tail -1; echo "rc=${PIPESTATUS[0]}"
echo "=== 告警日志确实各写了一条 ==="
sudo grep -c "cron-reconcile" /home/ubuntu/ld_alerts.log
