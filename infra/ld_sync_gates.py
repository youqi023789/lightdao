#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把"看门狗盯的门禁"三处对齐：
  主机部署文件  →  仓库 infra/<basename>  →  infra/gate_manifest.txt 里的哈希
顺序说明：这次以主机为准（2026-10-16 实测 promote.py 与 qa_truth.py 的线上版本
比仓库新，仓库里是旧的；若按仓库重建机器，g11 脚本结构门禁与 status 缓存失效不变量
会静默消失）。所以是把线上真相回填进仓库，而不是反过来。
每条 manifest 只增/改对应行，不动别的行；结尾打印变更清单。"""
import ast
import hashlib
import os
import re
import shutil

REPO = "/home/ubuntu/repo"
INFRA = os.path.join(REPO, "infra")
MAN = os.path.join(INFRA, "gate_manifest.txt")
DEPLOYED = "/usr/local/bin/ld_gate_watch.py"

# 不 import 看门狗：它结尾是无条件的 sys.exit(main())，import 会真的跑一遍检查
src = open(DEPLOYED, encoding="utf-8").read()
m = re.search(r"^PATHS\s*=\s*(\{.*?^\})", src, re.S | re.M)
if not m:
    print("!! 在 %s 里找不到 PATHS 定义，拒绝猜测" % DEPLOYED)
    raise SystemExit(2)
PATHS = ast.literal_eval(m.group(1))
print("从部署版看门狗读到 %d 个受监控门禁" % len(PATHS))
lines = open(MAN, encoding="utf-8").read().splitlines() if os.path.exists(MAN) else []
head = [l for l in lines if l.startswith("#")]
body = {}
for l in lines:
    if l.startswith("#") or not l.strip():
        continue
    ps = l.split()
    if len(ps) >= 2:
        body[ps[-1]] = ps[0]

copied, added, changed, missing = [], [], [], []
for name, host in PATHS.items():
    if not os.path.exists(host):
        missing.append(name)
        continue
    data = open(host, "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    dst = os.path.join(INFRA, name)
    old = open(dst, "rb").read() if os.path.exists(dst) else b""
    if old != data:
        shutil.copyfile(host, dst)
        copied.append(name)
    if name not in body:
        added.append(name)
        body[name] = digest
    elif body[name] != digest:
        changed.append(name)
        body[name] = digest

with open(MAN, "w", encoding="utf-8") as f:
    for h in head:
        f.write(h + "\n")
    for name in sorted(body):
        f.write("%s %s\n" % (body[name], name))

print("回填进仓库的文件 %d 个: %s" % (len(copied), ", ".join(copied) or "无"))
print("清单新增 %d 项: %s" % (len(added), ", ".join(added) or "无"))
print("清单更新哈希 %d 项: %s" % (len(changed), ", ".join(changed) or "无"))
if missing:
    print("!! 主机上找不到的门禁 %d 项: %s" % (len(missing), ", ".join(missing)))
print("清单现有 %d 行，PATHS 共 %d 项" % (sum(1 for l in open(MAN) if not l.startswith("#")),
                                     len(PATHS)))
