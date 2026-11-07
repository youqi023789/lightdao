#!/usr/bin/env python3
"""LightDAO code-id provenance verifier (read-only).

Answers the audit question: does every wasm code-id live on lightdao-mainnet-1
correspond to a bytecode artifact we actually hold in contracts/wasm/, and is
that artifact byte-identical (sha256) to the on-chain checksum?

It also reports the reverse direction: repo artifacts that no longer map to any
on-chain code-id, artifacts whose filename carries no code-id, and (with
--instances) how many contracts each code-id has instantiated.

Hard guarantees: issues only `q` (query) subcommands, never a tx; opens repo
files read-only; writes nothing unless --out is given.
"""
import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys

RPC = "http://127.0.0.1:26657"
WASM_DIR = "contracts/wasm"
PREFIX = "code"


def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(" ".join(args) + " failed: " + p.stderr.strip()[:200])
    return json.loads(p.stdout)


def list_codes():
    d = run(["wasmd", "q", "wasm", "list-code", "--node", RPC, "-o", "json"])
    out = {}
    for c in d.get("code_infos", []):
        out[int(c["code_id"])] = {"sha256": c["data_hash"].upper(),
                                  "creator": c.get("creator", "")}
    return out


def instances(code_id):
    d = run(["wasmd", "q", "wasm", "list-contract-by-code", str(code_id),
             "--node", RPC, "-o", "json"])
    return d.get("contracts") or []


def repo_artifacts(root):
    by_id, orphans = {}, []
    for path in sorted(glob.glob(os.path.join(root, WASM_DIR, "*.wasm"))):
        rel = os.path.relpath(path, root)
        base = os.path.basename(path)
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest().upper()
        size = os.path.getsize(path)
        head = base.split("_")[0]
        if head.startswith(PREFIX) and head[len(PREFIX):].isdigit():
            by_id.setdefault(int(head[len(PREFIX):]), []).append((rel, digest, size))
        else:
            orphans.append((rel, digest, size))
    return by_id, orphans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root containing contracts/wasm/")
    ap.add_argument("--out", help="also write the JSON report here")
    ap.add_argument("--instances", action="store_true", help="query instance counts (slower)")
    a = ap.parse_args()

    chain = list_codes()
    by_id, orphans = repo_artifacts(a.root)

    rows, problems, notes = [], [], []
    for cid in sorted(set(chain) | set(by_id)):
        c = chain.get(cid)
        arts = by_id.get(cid, [])
        match = [x for x in arts if c and x[1] == c["sha256"]]
        if c and match:
            status = "MATCH"
            if len(arts) > 1:
                notes.append("code %d has %d numbered artifacts, %d of them match" % (cid, len(arts), len(match)))
        elif c and arts:
            status = "SHA_MISMATCH"
            problems.append("code %d: on-chain %s != repo %s" % (cid, c["sha256"][:16], arts[0][1][:16]))
        elif c:
            status = "NO_ARTIFACT"
            problems.append("code %d is live on chain with no artifact in %s/" % (cid, WASM_DIR))
        else:
            status = "ARTIFACT_NOT_ON_CHAIN"
            notes.append("code %d artifact is not registered on chain (stale or not yet uploaded)" % cid)
        row = {"code_id": cid, "status": status,
               "chain_sha256": c["sha256"] if c else None,
               "creator": c["creator"] if c else None,
               "artifacts": [x[0] for x in (match or arts)]}
        if a.instances and c:
            row["instances"] = instances(cid)
        rows.append(row)

    by_hash = {}
    for cid, c in chain.items():
        by_hash.setdefault(c["sha256"], []).append(cid)
    for rel, digest, size in orphans:
        hits = by_hash.get(digest, [])
        if hits:
            notes.append("unnumbered artifact %s is byte-identical to live code-id(s) %s"
                         % (rel, ",".join(str(h) for h in sorted(hits))))
        else:
            notes.append("unnumbered artifact %s (sha256 %s, %d B) matches no live code-id"
                         % (rel, digest[:16], size))

    print("%-4s %-24s %-34s %s" % ("id", "status", "artifact", "chain_sha12"))
    for r in rows:
        art = os.path.basename(r["artifacts"][0]) if r["artifacts"] else "-"
        print("%-4s %-24s %-34s %s" % (r["code_id"], r["status"], art,
                                       (r["chain_sha256"] or "-")[:12]))

    n_match = sum(1 for r in rows if r["status"] == "MATCH")
    print("\nsummary: %d/%d on-chain code-ids byte-match a repo artifact; %d problem(s), %d note(s)"
          % (n_match, len(chain), len(problems), len(notes)))
    for p in problems:
        print("  PROBLEM " + p)
    for n in notes:
        print("  note    " + n)

    if a.out:
        with open(a.out, "w") as f:
            json.dump({"rpc": RPC, "codes": rows, "problems": problems, "notes": notes},
                      f, indent=2, sort_keys=True)
        print("wrote " + a.out)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
