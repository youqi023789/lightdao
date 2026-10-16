#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI 里跑：把本次确定性构建的产物，与仓库里归档的"链上真实字节码"逐字节比对。
结论既写进 job summary（人在界面上看），也写成 annotations（机器可查，公开仓库
不带凭据也能用 /check-runs/{id}/annotations 读到），避免"CI 跑过了但没人知道结论"。

判定口径：
  · 一致        → 这份链上代码确实能从仓库源码重跑出来（可复现）
  · 不一致      → 只能核对"是不是这一份"，不能证明"源码编得出这一份"
  · 构建缺产物  → 判"未产出"，不当成一致
退出码：只有当 BUILDLOG 里某行已经声明 reproducible=yes 却比对不一致时才非零
（那是"声称可复现却复现不出来"，必须红）；其余情况只报告不阻断，因为当前状态
本来就是"已知不可复现的跟踪例外"，不该让每次提交都变红变成噪声。"""
import hashlib
import io
import os
import re
import sys

LOG = "contracts/wasm/BUILDLOG.tsv"
CI_DIR = "ci_out"
HEAD = ["code_id", "sha256_16", "artifact", "source_commit", "toolchain",
        "reproducible", "until", "note"]


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def read_log():
    if not os.path.exists(LOG):
        return []
    rows = []
    head = None
    for ln in io.open(LOG, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        ps = ln.split("\t")
        if head is None:
            head = ps
            continue
        rows.append(dict(zip(head, ps)))
    return rows


def main():
    rows = read_log()
    if not rows:
        print("::warning title=构建台账缺失::读不到 %s，无法判定可复现性" % LOG)
        return 0
    lines = ["# 合约字节码可复现性实测（CI 确定性构建 vs 链上归档产物）", ""]
    lines.append("| code | crate | 链上归档 sha256 | 本次构建 sha256 | 判定 |")
    lines.append("|---|---|---|---|---|")
    hard_fail = 0
    n_match = n_diff = n_missing = 0
    for r in rows:
        cid = (r.get("code_id") or "").strip()
        art = (r.get("artifact") or "").strip()
        if not cid or not art or not os.path.exists(art):
            continue
        m = re.match(r"contracts/wasm/code\d+_(.+)\.wasm$", art)
        if not m:
            continue                       # 非"链上回捞"命名的归档（源码自带产物）不参与本比对
        crate = m.group(1)
        want = sha(art)
        built = os.path.join(CI_DIR, crate + ".wasm")
        claim = (r.get("reproducible") or "").strip().lower()
        if not os.path.exists(built):
            verdict = "本次未产出该 crate"
            got = "—"
            n_missing += 1
            if claim == "yes":
                hard_fail += 1
        else:
            got = sha(built)
            if got == want:
                verdict = "**一致（可复现）**"
                n_match += 1
            else:
                verdict = "不一致（不可复现）"
                n_diff += 1
                if claim == "yes":
                    hard_fail += 1
        lines.append("| %s | %s | `%s…` | `%s…` | %s |"
                     % (cid, crate, want[:16], got[:16] if got != "—" else "—", verdict))
        if want[:16] != (got[:16] if got != "—" else ""):
            print("::warning title=code %s 不可复现::crate %s：链上 %s… 本次构建 %s…"
                  % (cid, crate, want[:16], got[:16]))
    lines += ["", "统计：一致 %d、不一致 %d、未产出 %d；其中"
                    "声称可复现却复现不出的 %d 项" % (n_match, n_diff, n_missing, hard_fail),
              "",
              "读法：`不一致` 意味着第三方只能核对【链上跑的是这一份字节码】，"
              "无法从仓库源码重跑出同样的 sha256 —— 依赖未锁定（仓库无 Cargo.lock，"
              "本次 CI 生成的已作为构件上传）、工具链版本与当年构建机不一致都会导致字节差异。"]
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with io.open(summary, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if hard_fail:
        print("::error title=可复现性声明不成立::%d 项在 BUILDLOG 里标 reproducible=yes "
              "但本次构建复现不出来" % hard_fail)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
