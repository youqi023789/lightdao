#!/usr/bin/env python3
"""ld_gov_guard.py — governance-migration watch + premature-execution guard (S7/S15, 2026-10 audit).

READ-ONLY (never broadcasts). Runs every 15 min. Two jobs:

(A) PREMATURE-EXECUTION GUARD (the ~48h exposure window until native id=7 auto-executes at
    2026-10-04T06:05:40Z): on the live code-11 governance contract exec() has NO sender auth and
    NO expiry, so contract proposal id=5 (add_schedule minting 75,000,000 LIGHT to wasm182d06...)
    can be fired by ANYONE until the code-13 migration voids it. qa_cross C7 SKIPS the void list,
    so this guard is the only thing watching it. If any void-list proposal flips executed==True
    -> immediate Discord alarm.

(B) MIGRATION PROGRESS: native x/gov id=7 (MsgMigrateContract governance->code13,
    void_ids=[2,5,6,7,9], 100% yes) auto-executes at voting_end. This guard tracks the state
    machine and alerts ONLY on transitions (to avoid */15 spam):
      - governance code_id 11 -> 13  == migration landed; then verify id=5 is voided (not executed)
      - native id=7 -> REJECTED/VETOED/FAILED == migration will NOT happen -> id=5 stays live (alarm)
      - contract id=10 (v4 mining->code12) executed == v4 done (info)

State is persisted in /home/ubuntu/.ld_gov_guard_state so alerts fire once per change.
Exit codes: 0 normal, 3 premature-execution/void-failure alarm, 4 migration-failed alarm.
"""
import base64, json, subprocess, sys, datetime, os

NODE = "tcp://127.0.0.1:26657"
GOV = "wasm14axmz74pppxqxs3qhxaaf2qzl6x53pvvzm7c6p52qrycwnyh8ktsfukapt"
VOID_IDS = [2, 5, 6, 7, 9]
ID5 = 5
ID5_BENEFICIARY = "wasm182d06dcj2upp9hkxqsxzp5ngws6kqdnq5yvu2g"
NATIVE_MIGRATION_PROPOSAL = 7
V4_CONTRACT_PROPOSAL = 10
ALERTS = "/home/ubuntu/ld_alerts.log"
STATE = "/home/ubuntu/.ld_gov_guard_state"


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def alert(msg):
    try:
        open(ALERTS, "a").write("%s GOV-GUARD %s\n" % (now(), msg))
    except Exception:
        pass
    subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "🚨 GOV-GUARD: %s" % msg],
                   capture_output=True, text=True)


def info(msg):
    subprocess.run(["python3", "/usr/local/bin/discord_bot.py", "send", "✅ GOV-GUARD: %s" % msg],
                   capture_output=True, text=True)


def wasmd(args):
    r = subprocess.run(["wasmd"] + args + ["--node", NODE, "-o", "json"],
                       capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)


def raw_map(ns, key_int):
    b = ns.encode()
    key = (len(b).to_bytes(2, "big") + b + key_int.to_bytes(8, "big")).hex()
    d = wasmd(["q", "wasm", "contract-state", "raw", GOV, key])
    data = d.get("data")
    return json.loads(base64.b64decode(data)) if data else None


def gov_code_id():
    d = wasmd(["q", "wasm", "contract", GOV])
    return int(d["contract_info"]["code_id"])


def native_status(pid):
    d = wasmd(["q", "gov", "proposal", str(pid)])
    return d.get("proposal", d).get("status")


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save_state(s):
    try:
        json.dump(s, open(STATE, "w"))
    except Exception:
        pass


def main():
    st = load_state()
    rc = 0

    # ---- (A) premature-execution guard on the void list ----
    fired = []
    for pid in VOID_IDS:
        try:
            p = raw_map("proposals", pid)
        except Exception as e:
            print("%s gov-guard: proposal %d read error (%s) fail-soft" % (now(), pid, e))
            continue
        if p and p.get("executed") is True:
            fired.append(pid)
    if fired:
        alert("void-list proposal(s) %s EXECUTED before migration void (code-11 exec has no "
              "auth/expiry). id=5 => 75M LIGHT schedule to %s may now exist. INVESTIGATE NOW."
              % (fired, ID5_BENEFICIARY))
        print("%s ALARM premature execution: %s" % (now(), fired))
        sys.exit(3)

    # ---- (B) migration progress (alert on transition only) ----
    try:
        code = gov_code_id()
    except Exception as e:
        print("%s gov-guard: code_id read error (%s)" % (now(), e)); code = st.get("code")
    try:
        nat = native_status(NATIVE_MIGRATION_PROPOSAL)
    except Exception as e:
        nat = st.get("native7", "UNKNOWN"); print("%s gov-guard: native7 read error (%s)" % (now(), e))

    # migration-failed alarm (once)
    if nat in ("PROPOSAL_STATUS_REJECTED", "PROPOSAL_STATUS_VETOED", "PROPOSAL_STATUS_FAILED") \
       and st.get("native7") != nat:
        alert("native x/gov id=%d (governance->code13 migration) is %s — migration will NOT "
              "execute; id=5 (mint 75M) stays live-executable on code11. RE-PLAN REQUIRED."
              % (NATIVE_MIGRATION_PROPOSAL, nat))
        rc = 4

    # code 11 -> 13 transition: verify void took effect
    if st.get("code") not in (None, code) and code == 13 and st.get("code") == 11:
        try:
            voided5 = raw_map("voided", ID5)
        except Exception:
            voided5 = None
        if voided5 is True:
            info("governance migrated code 11->13; id=5 voided=%s. TOP1 risk (mint 75M) "
                 "NEUTRALIZED. Verify staked balances + new stake/vote per MIGRATION doc §12."
                 % voided5)
        else:
            alert("governance migrated to code13 BUT id=5 voided flag=%s (expected True). "
                  "void_ids may not have applied — INVESTIGATE." % voided5)
            rc = 3

    # v4 (contract id=10) executed transition
    try:
        v4 = raw_map("proposals", V4_CONTRACT_PROPOSAL)
        v4x = bool(v4 and v4.get("executed"))
    except Exception:
        v4x = st.get("v4_executed", False)
    if v4x and not st.get("v4_executed"):
        info("v4 executed: contract proposal id=%d (mining_reward->code12) executed==True."
             % V4_CONTRACT_PROPOSAL)

    save_state({"code": code, "native7": nat, "v4_executed": v4x, "ts": now()})
    print("%s gov-guard OK: gov_code=%s native_id7=%s void-list executed=[] v4_executed=%s%s"
          % (now(), code, nat, v4x, " (rc=%d)" % rc if rc else ""))
    sys.exit(rc)


if __name__ == "__main__":
    main()
