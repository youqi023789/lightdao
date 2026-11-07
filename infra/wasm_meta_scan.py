#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只读扫描 contracts/wasm/*.wasm：从字节码里取出构建期留下的自描述段，用来给 B6
形式化验证的两条阻断项（缺源 crate / toolchain unknown）提供第一手客观证据。

为什么要读二进制里的元数据：
  cosmwasm-opt / cw-build 会把一段 JSON 写进 WASM 的 custom section（段名 cosmwasm），
  带 contract_name / contract_version；rustc、wasm-opt 这类工具又会往 producers 段里
  留下自己的名字和版本。这些字节跟着产物一起上链，所以只要归档字节码与链上 checksum
  一致，段里的东西就是链上那份代码自报的出身。对 code 16/17 这种有字节匹配产物、
  仓库里没有源 crate 的情况，这是最省事的定位线索；producers 段也是 BUILDLOG.tsv 的
  toolchain 列目前唯一拿得到的客观依据。

口径与边界：
  · 只读：不写主网、不改文件（除显式 --out JSON）。
  · 判定分档，避免把"猜得像"当成"能复现"：
      SOURCE-MATCH   cosmwasm 段自报的 name 与仓库某 crate 一致且 version 一致
      SOURCE-NEAR    name 一致但 version 不一致（找回源码后要对齐版本号）
      NAME-HINT      产物根本没写 cosmwasm 段，只能按文件名猜 crate —— 只算线索
      NO-METADATA    既无自描述段，文件名也对不上任何 crate（code 17 这类）
  · 实测本仓 30 份归档产物里"没有一份带 cosmwasm 段"，所以真正的可用证据是
    producers 段（rustc / wasm-opt / clang 等自报版本）与 target_features：
    这正是 BUILDLOG.tsv 里 toolchain 列长期写 unknown 的替代来源，先把事实钉下来，
    再谈用 CI 逐字节比对（infra/ci_wasm_compare.py）把 reproducible 升成 yes。
  · 不做反编译，也不把"名字对上了"表述成"可复现"——可复现只有"确定性构建产物
    逐字节比对"那一条口径能证明。
"""
import argparse
import hashlib
import json
import os
import re
import sys

WASM_DIR = "contracts/wasm"
CRATE_DIR = "contracts/contracts"
SUMS_FILE = os.path.join(WASM_DIR, "SHA256SUMS")


def uleb128(buf, pos):
    """LEB128 无符号整数解码，返回 (value, next_pos)。"""
    val = 0
    shift = 0
    while True:
        if pos >= len(buf):
            raise ValueError("LEB128 越界")
        b = buf[pos]
        pos += 1
        val |= (b & 0x7F) << shift
        if not (b & 0x80):
            return val, pos
        shift += 7
        if shift > 63:
            raise ValueError("LEB128 过长")


def custom_sections(buf):
    """遍历顶层 section，返回 [(section_name, payload_bytes)] 里的 custom 段。"""
    if buf[:4] != b"\x00asm":
        raise ValueError("不是 WASM 文件（magic 不匹配）")
    pos = 8
    out = []
    n = len(buf)
    while pos < n:
        sid, pos = uleb128(buf, pos)
        size, pos = uleb128(buf, pos)
        end = pos + size
        if end > n:
            raise ValueError("section 长度越界")
        if sid == 0:
            ln, p2 = uleb128(buf, pos)
            name = buf[p2:p2 + ln].decode("utf-8", "replace")
            out.append((name, buf[p2 + ln:end]))
        pos = end
    return out


def read_str(buf, pos):
    ln, pos = uleb128(buf, pos)
    return buf[pos:pos + ln].decode("utf-8", "replace"), pos + ln


def parse_producers(payload):
    """producers 段：{字段名: [(实体名, 版本), ...]}。rustc / clang / wasm-opt / cw-*
    都会往这里写自己那份签名，是"产物到底是谁编出来的"唯一还留在字节码里的线索。"""
    out = {}
    try:
        nfields, pos = uleb128(payload, 0)
        for _ in range(nfields):
            fname, pos = read_str(payload, pos)
            nents, pos = uleb128(payload, pos)
            ents = []
            for _ in range(nents):
                ename, pos = read_str(payload, pos)
                ever, pos = read_str(payload, pos)
                ents.append((ename, ever))
            out[fname] = ents
    except Exception as e:
        out["_parse_error"] = str(e)
    return out


def parse_target_features(payload):
    try:
        n, pos = uleb128(payload, 0)
        feats = []
        for _ in range(n):
            s, pos = read_str(payload, pos)
            feats.append(s)
        return feats
    except Exception:
        return []


def cosmwasm_meta(path):
    with open(path, "rb") as f:
        buf = f.read()
    meta = {}
    producers = {}
    features = []
    names = []
    for name, payload in custom_sections(buf):
        names.append(name)
        if name == "cosmwasm":
            try:
                meta = json.loads(payload.decode("utf-8", "replace"))
            except Exception as e:  # 段存在但解析不了，如实记录
                meta = {"_parse_error": str(e), "_raw_head": payload[:64].decode("utf-8", "replace")}
        elif name == "producers":
            producers = parse_producers(payload)
        elif name == "target_features":
            features = parse_target_features(payload)
    return meta, names, buf, producers, features


def crates_index():
    """仓库里现有 crate：目录名 -> (Cargo.toml 的 name, version)。"""
    idx = {}
    if not os.path.isdir(CRATE_DIR):
        return idx
    for d in sorted(os.listdir(CRATE_DIR)):
        cto = os.path.join(CRATE_DIR, d, "Cargo.toml")
        if not os.path.isfile(cto):
            continue
        txt = open(cto, encoding="utf-8", errors="replace").read()
        m = re.search(r'(?m)^\s*name\s*=\s*["\']([^"\']+)["\']', txt)
        v = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']', txt)
        idx[d] = (m.group(1) if m else d, v.group(1) if v else "?")
    return idx


def norm(s):
    """crate 名与 contract_name 常常一个用下划线一个用连字符，归一后再比。"""
    return (s or "").strip().lower().replace("-", "_")


def sums_index():
    """SHA256SUMS 里路径写作 contracts/wasm/xxx.wasm，统一按 basename 建索引。"""
    out = {}
    if not os.path.isfile(SUMS_FILE):
        return out
    for line in open(SUMS_FILE, encoding="utf-8", errors="replace"):
        parts = line.split()
        if len(parts) >= 2 and re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
            out[os.path.basename(parts[1].lstrip("*"))] = parts[0].lower()
    return out


def fmt_producers(producers):
    """把 producers 压成一行紧凑文本，优先显示与构建相关的字段。"""
    if not producers:
        return "-"
    bits = []
    for field, ents in sorted(producers.items()):
        for en, ev in ents:
            bits.append("%s=%s" % (en, ev) if ev else en)
    return "; ".join(bits) if bits else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="把结果写成 JSON（默认只打印，不落盘）")
    ap.add_argument("--dir", default=WASM_DIR)
    ap.add_argument("--md", action="store_true", help="按 markdown 表格输出（默认为制表符文本，便于管道）")
    args = ap.parse_args()

    crates = crates_index()
    sums = sums_index()
    rows = []
    for fn in sorted(os.listdir(args.dir)):
        if not fn.endswith(".wasm"):
            continue
        p = os.path.join(args.dir, fn)
        try:
            meta, secnames, buf, producers, features = cosmwasm_meta(p)
        except Exception as e:
            rows.append({"artifact": fn, "error": str(e)})
            continue
        sha = hashlib.sha256(buf).hexdigest()
        cname = meta.get("contract_name", "")
        cver = meta.get("contract_version", "")
        match_dir, verdict = "", "NO-SOURCE"
        if cname:
            for d, (tn, tv) in crates.items():
                if norm(tn) == norm(cname) or norm(d) == norm(cname):
                    match_dir = d
                    verdict = "SOURCE-MATCH" if norm(tv) == norm(cver) else "SOURCE-NEAR"
                    break
        else:
            # 字节码里没有 cosmwasm 自描述段时，用文件名里的合约名去猜 crate，
            # 但只能给 NAME-HINT，不能当作源码可复现的证据。
            stem = re.sub(r"^code\d+_", "", fn[:-5])
            for d in crates:
                if norm(d) == norm(stem):
                    match_dir = d
                    verdict = "NAME-HINT"
                    break
            else:
                verdict = "NO-METADATA"
        rows.append({
            "artifact": fn,
            "bytes": len(buf),
            "sha256": sha,
            "in_SHA256SUMS": (fn in sums and sums[fn] == sha),
            "contract_name": cname,
            "contract_version": cver,
            "build": meta.get("build", ""),
            "custom_sections": secnames,
            "producers": producers,
            "target_features": features,
            "crate_dir": match_dir,
            "crate_verdict": verdict,
        })

    hdr = ["artifact", "bytes", "sha256_12", "in_SUMS", "contract_name", "version", "crate_dir", "verdict", "producers"]
    if args.md:
        print("| " + " | ".join(hdr) + " |")
        print("|" + "|".join(["---"] * len(hdr)) + "|")
    for r in rows:
        if "error" in r:
            print("%s\tPARSE-ERROR: %s" % (r["artifact"], r["error"]))
            continue
        vals = [r["artifact"], str(r["bytes"]), r["sha256"][:12], str(r["in_SHA256SUMS"]),
                r["contract_name"] or "-", r["contract_version"] or "-",
                r["crate_dir"] or "-", r["crate_verdict"], fmt_producers(r["producers"])]
        print(("| %s |\n" % " | ".join(vals)) if args.md else "\t".join(vals))

    tally = {}
    for r in rows:
        tally[r.get("crate_verdict", "ERR")] = tally.get(r.get("crate_verdict", "ERR"), 0) + 1
    print("\n判定统计：%s" % json.dumps(tally, ensure_ascii=False, sort_keys=True))
    nometa = [r["artifact"] for r in rows if r.get("contract_name") == "" and "error" not in r]
    print("缺 cosmwasm 自描述段的产物数：%d%s" % (len(nometa), "（" + ", ".join(nometa) + "）" if nometa and len(nometa) <= 4 else ""))
    noprod = [r["artifact"] for r in rows if not r.get("producers") and "error" not in r]
    print("缺 producers 段的产物数：%d%s" % (len(noprod), "（" + ", ".join(noprod) + "）" if noprod and len(noprod) <= 4 else ""))
    bad = [r["artifact"] for r in rows if r.get("in_SHA256SUMS") is False and "error" not in r]
    print("与 SHA256SUMS 不一致或不在册：%d 个" % len(bad))
    if bad:
        print("  " + ", ".join(bad[:8]) + (" ..." if len(bad) > 8 else ""))
    # producers 去重汇总：这就是 BUILDLOG 里 toolchain 一列目前能给到的最好证据
    prodset = {}
    for r in rows:
        if "error" in r:
            continue
        key = fmt_producers(r["producers"])
        prodset.setdefault(key, []).append(r["artifact"])
    print("\nproducers 组合（%d 种）：" % len(prodset))
    for k, v in sorted(prodset.items(), key=lambda x: -len(x[1])):
        print("  [%d] %s   例：%s" % (len(v), k, v[0]))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        print("已写出 %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
