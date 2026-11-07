#!/usr/bin/env python3
"""Read-only re-verification of audit code-id provenance.

Compares live lightdao-mainnet-1 CosmWasm code ids (checksum + instance count)
against the wasm artifacts tracked in the repo, and reports whether the
AUDIT_CODEID_PROVENANCE claim (20/20 sha256 MATCH) still holds today.
Performs no writes of any kind.
"""
import base64
import hashlib
import json
import os
import subprocess
import sys

NODE = "tcp://127.0.0.1:26657"
REPO = os.environ.get("LD_REPO", "/home/ubuntu/repo")
WASM_DIR = os.path.join(REPO, "contracts", "wasm")


def sh(args):
    return subprocess.run(args, capture_output=True, text=True, timeout=120)


def bq(b32):
    """cosmwasm checksum is lowercase base32 (no padding) of sha256; some
    wasmd builds expose a plain hex data_hash instead."""
    s = str(b32).strip()
    if len(s) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in s):
        return s.lower()
    pad = "=" * ((8 - len(s) % 8) % 8)
    return base64.b32decode(s.upper() + pad).hex()


def load_json(stdout):
    i = stdout.find("{")
    if i < 0:
        return None
    try:
        return json.loads(stdout[i:])
    except Exception:
        return None


def main():
    r = sh(["wasmd", "q", "wasm", "list-code", "--node", NODE, "-o", "json", "--limit", "200"])
    d = load_json(r.stdout)
    if not d or "code_infos" not in d:
        print("QUERY-FAIL list-code rc=%s err=%s" % (r.returncode, r.stderr[:200]))
        return 2
    codes = {}
    for c in d["code_infos"]:
        ck = c.get("checksum") or c.get("data_hash") or ""
        codes[int(c["code_id"])] = ck

    inst = {}
    addr_of = {}
    for cid in sorted(codes):
        ri = sh(["wasmd", "q", "wasm", "list-contract-by-code", str(cid), "--node", NODE,
                 "-o", "json", "--limit", "100"])
        di = load_json(ri.stdout)
        addrs = (di or {}).get("contracts", [])
        addrs = [a if isinstance(a, str) else a.get("address", "?") for a in addrs]
        inst[cid] = len(addrs)
        addr_of[cid] = addrs

    # repo artifacts: codeN_xxx.wasm
    local = {}
    if os.path.isdir(WASM_DIR):
        for fn in sorted(os.listdir(WASM_DIR)):
            if not fn.endswith(".wasm"):
                continue
            p = os.path.join(WASM_DIR, fn)
            try:
                with open(p, "rb") as f:
                    local[fn] = hashlib.sha256(f.read()).hexdigest()
            except Exception as e:
                local[fn] = "READ-ERR:%s" % e

    def guess(cid):
        pref = "code%d_" % cid
        for fn, h in local.items():
            if fn.startswith(pref):
                return fn, h
        return None, None

    print("# live code ids: %d (max id %s) | instances total: %d | repo .wasm files: %d"
          % (len(codes), max(codes) if codes else "-", sum(inst.values()), len(local)))
    print("%-6s %-10s %-8s %-34s %-6s %s" % ("code", "instances", "sha-match", "repo artifact", "size", "note"))
    mismatch, orphan_art = [], []
    for cid in sorted(codes):
        live_hex = bq(codes[cid])
        fn, lh = guess(cid)
        n = inst.get(cid, 0)
        if fn is None:
            print("%-6s %-10s %-8s %-34s %-6s %s" % (cid, n, "-", "NONE", "-", "no artifact in contracts/wasm"))
            mismatch.append((cid, "artifact missing"))
            continue
        try:
            size = os.path.getsize(os.path.join(WASM_DIR, fn))
        except Exception:
            size = -1
        ok = (lh == live_hex)
        if not ok:
            mismatch.append((cid, "sha differs"))
        print("%-6s %-10s %-8s %-34s %-6s %s"
              % (cid, n, "MATCH" if ok else "DIFFER", fn, size,
                 "" if ok else "live=%s local=%s" % (live_hex[:16], str(lh)[:16])))
    # artifacts with no matching live code id
    live_ids = set(codes)
    for fn in sorted(local):
        try:
            cid = int(fn.split("_", 1)[0].replace("code", ""))
        except Exception:
            continue
        if cid not in live_ids:
            orphan_art.append(fn)

    # sensitive-contract instance addresses (for the RFQ appendix)
    MR = "wasm173y0pgdh6ensz4gpgglz40a260www6qse4dswshc87za9du6h4fsm5r9wx"
    print("\n# contract addresses by code id (up to 3 each)")
    for cid in sorted(addr_of):
        print("code %-4d %s" % (cid, ", ".join(addr_of[cid][:3]) + ("" if len(addr_of[cid]) <= 3 else " ...")))
    mining_addr = [a for cid, aa in addr_of.items() for a in aa if a == MR]
    print("\nmining_reward instance seen in list-contracts: %s" % (bool(mining_addr)))

    print("\nVERDICT")
    if not mismatch and not orphan_art:
        print("CLEAN: every live code id byte-matches a repo artifact; no orphan artifacts")
    else:
        for cid, why in mismatch:
            print("PROBLEM code %s: %s" % (cid, why))
        for fn in orphan_art:
            print("ORPHAN artifact %s (no such live code id)" % fn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
