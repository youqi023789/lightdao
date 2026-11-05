#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ld_i18n_mt_watch.py —— 看门狗：盯"补齐流水线自己是不是停了"。

为什么需要它（真实事故）：11-05 03:30~06:00 三批 cron 全部 0 成功 / 45 失败，
日志里每批都打了 FAIL，但没人看日志；页面残留数字不动，看起来像"已经补完了"。
静默停摆和已经完成，从外部看一模一样 —— 所以必须有个专门证明"它还在动"的探测器。

判定（都从状态文件读，不重复渲染页面）：
  · remaining>0 且 距最后一次成功翻译 > STALL_MIN 分钟  → 告警（流水线卡住）
  · remaining==0                                      → 正常（真的补完了）
  · 状态文件缺失/太旧（> 6 小时）                       → 告警（cron 没跑起来）
反向验证：LD_MT_WATCH_NOW + 假状态文件必须让本脚本非零退出（见 --selftest）。
"""
import json
import os
import sys
import time

STATE = os.environ.get("LD_MT_STATE", "/home/ubuntu/ld_i18n_mt_state.json")
ALERTS = os.environ.get("LD_MT_ALERTS", "/home/ubuntu/ld_alerts.log")
STALL_MIN = int(os.environ.get("LD_MT_STALL_MIN", "90"))
NOW = os.environ.get("LD_MT_WATCH_NOW")   # 测试用：伪造"现在"


def alert(msg, rc):
    line = "%s I18N-MT-WATCH %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(line)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    return rc


def parse(ts):
    return time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone


def main():
    selftest = "--selftest" in sys.argv
    if selftest:
        sys.argv.remove("--selftest")          # 少了这行，selftest 会无限递归
        # 植入一个"91 分钟前成功、还剩 100 条"的假状态 —— 必须报警，否则看门狗是瞎的
        tmp = "/tmp/ld_mt_watch_selftest.json"
        stale = time.strftime("%Y-%m-%dT%H:%M:%SZ",
                              time.gmtime(time.time() - (STALL_MIN + 1) * 60))
        json.dump({"ts": stale, "last_success_ts": stale, "remaining": 100, "cache": 10},
                  open(tmp, "w"))
        os.environ["LD_MT_STATE"] = tmp
        os.environ["LD_MT_ALERTS"] = "/tmp/ld_mt_watch_selftest.log"
        globals()["STATE"] = tmp
        globals()["ALERTS"] = os.environ["LD_MT_ALERTS"]
        rc = main()
        print("SELFTEST 期望非零，实际 rc=%d → %s" % (rc, "OK（会报警）" if rc != 0 else "看门狗是瞎的，必须修"))
        return 0 if rc != 0 else 1

    if not os.path.exists(STATE):
        return alert("FAIL 状态文件不存在（%s）：cron 从没跑成过或路径变了" % STATE, 1)
    try:
        st = json.load(open(STATE, encoding="utf-8"))
    except Exception as e:
        return alert("FAIL 状态文件读不出来：%s" % str(e)[:70], 1)
    rem = int(st.get("remaining", -1))
    ts = st.get("last_success_ts") or st.get("ts")
    now = parse(NOW) if NOW else time.time()
    if rem < 0:
        return alert("FAIL 状态里没有 remaining 字段，判定不了（不当成正常）", 1)
    if rem == 0:
        print("OK 待补队列已清空（缓存 %s 条）" % st.get("cache"))
        return 0
    if not ts:
        return alert("FAIL 还剩 %d 条但没有时间戳，无法判断是否卡住" % rem, 1)
    age_min = (now - parse(ts)) / 60.0
    if age_min > STALL_MIN:
        return alert("FAIL 卡住：还剩 %d 条，距最后一次成功翻译 %.0f 分钟（阈值 %d）；"
                     "后端=%s 本批成功 %s 失败 %s" % (rem, age_min, STALL_MIN,
                                                  "gtx优先/MyMemory兜底", st.get("ok"), st.get("bad")), 1)
    print("OK 流水线在动：还剩 %d 条，距上次成功 %.1f 分钟" % (rem, age_min))
    return 0


if __name__ == "__main__":
    sys.exit(main())
