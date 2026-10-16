#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把构建产物登记进两份台账，让"store/migrate 无源可查"这种事在源头就闭上：
  contracts/wasm/SHA256SUMS   —— sha256 + 路径（迁移门禁按这个判有没有源）
  contracts/wasm/BUILDLOG.tsv —— 这份字节码是哪个提交、哪套工具链编的、能不能复现
用法：
  python3 register_artifacts.py <wasm 文件> [<wasm 文件> ...] [--code-id 19 ...]
不带 --code-id 时按文件名里的 code<N>_ 前缀推断；推不出就留空（只登记产物）。
构建记录会写当前 git 提交号与 rustc 版本，reproducible 先写 yes（
因为这次是"从工作树当场编出来的"，事后只要提交不丢就能复现）。
"""
import datetime
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WDIR = os.path.join(ROOT, "contracts/wasm")
SUMS = os.path.join(WDIR, "SHA256SUMS")
LOG = os.path.join(WDIR, "BUILDLOG.tsv")
HEAD = ["code_id", "sha256_16", "artifact", "source_commit", "toolchain",
        "reproducible", "until", "note"]


def git(*a):
    p = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, timeout=60)
    return (p.stdout.decode("utf-8", "replace").strip()
            or p.stderr.decode("utf-8", "replace").strip()[:60])


def toolchain():
    for cmd in (["rustc", "--version"], [os.path.expanduser("~/.cargo/bin/rustc"),
                                         "--version"]):
        try:
            return subprocess.run(cmd, capture_output=True, timeout=30
                                  ).stdout.decode().strip()[:40]
        except Exception:
            continue
    return "unknown"


def read_log():
    rows, head = {}, None
    if not os.path.exists(LOG):
        return rows
    for ln in open(LOG, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        ps = ln.split("\t")
        if head is None:
            head = ps
            continue
        d = dict(zip(head, ps))
        if d.get("sha256_16"):
            rows[d["sha256_16"].lower()] = d
    return rows


def write_log(rows):
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("# LD 合约字节码构建台账（门禁 infra/ld_migrate_gate.py 读取本文件）\n")
        f.write("# reproducible=yes 必须同时给出 source_commit 与 toolchain；"
                "no 的条目按跟踪例外处理，解除日前只提示不阻断。\n")
        f.write("\t".join(HEAD) + "\n")
        for k in sorted(rows, key=lambda x: (rows[x].get("code_id") or "999").zfill(4)):
            r = rows[k]
            f.write("\t".join([str(r.get(c, "")) for c in HEAD]) + "\n")


args = [a for a in sys.argv[1:] if not a.startswith("--")]
want_code = dict(re.findall(r"--code-id=(\S+)", " ".join(sys.argv[1:])))
if not args and not want_code:
    print(__doc__)
    sys.exit(2)
if not os.path.isdir(WDIR):
    print("找不到 %s（要在仓库里跑）" % WDIR)
    sys.exit(2)

commit = git("rev-parse", "--short", "HEAD")
dirty = git("status", "--porcelain", "--", "contracts")
tc = toolchain()
rows = read_log()
n = 0
for path in args:
    if not os.path.exists(path):
        print("跳过（文件不存在）: %s" % path)
        continue
    raw = open(path, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    base = os.path.basename(path)
    if not base.startswith("code"):
        dst = os.path.join(WDIR, base)
        if os.path.abspath(path) != os.path.abspath(dst):
            open(dst, "wb").write(raw)
        rel = "contracts/wasm/" + base
    else:
        rel = "contracts/wasm/" + base
    cid = want_code.get(base) or (re.match(r"code(\d+)_", base).group(1)
                                  if re.match(r"code(\d+)_", base) else "")
    # SHA256SUMS：同一 sha 只留一条，同一产物文件只留一条
    lines = []
    if os.path.exists(SUMS):
        lines = [l.rstrip("\n") for l in open(SUMS, encoding="utf-8") if l.strip()]
    lines = [l for l in lines if not l.endswith(" " + rel)
             and (l.split()[0].lower() != sha or l.split()[-1] != rel)]
    lines.append("%s  %s" % (sha, rel))
    with open(SUMS, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(lines)) + "\n")
    rows[sha[:16].lower()] = {
        "code_id": cid, "sha256_16": sha[:16], "artifact": rel,
        "source_commit": commit + ("+dirty" if dirty else ""),
        "toolchain": tc, "reproducible": "yes", "until": "",
        "note": "现场登记 %s；工作树%s（register_artifacts.py 写入）"
                % (datetime.date.today().isoformat(),
                   "有未提交改动" if dirty else "干净"),
    }
    print("登记 %s  sha256=%s…  code=%s  提交=%s  工具链=%s"
          % (rel, sha[:16], cid or "?", commit, tc))
    n += 1
if n:
    write_log(rows)
    print("BUILDLOG.tsv 现有 %d 行；SHA256SUMS 现有 %d 行"
          % (len(rows), sum(1 for _ in open(SUMS, encoding="utf-8"))))
    print("下一步：git add contracts/wasm && git commit（把产物与台账一起进版本库）")
