#!/usr/bin/env python3
"""ld_leak_proof.py — reverse-direction proof for repo_leak_check.py.

An allowlist gate is only trustworthy if it still fires on a real leak. This copies the working
tree into a scratch dir, plants one synthetic finding per detector class, runs the gate and
asserts every class is reported. Values are assembled at runtime from fragments so this file
itself never contains anything a secret scanner would (rightly) block.
"""
import base64
import os
import shutil
import subprocess
import sys
import tempfile

REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/repo"
GATE = "/usr/local/bin/repo_leak_check.py"
IP_FILE = "/etc/lightdao/leak_ips.txt"
_HOME = "Use" + "rs"          # assembled so this fixture never trips its own scanner on review
_DESK = "Desk" + "top"

first_ip = None
for ln in open(IP_FILE, encoding="utf-8"):
    ln = ln.split("#")[0].strip()
    if ln:
        first_ip = ln
        break
assert first_ip, "no IPs in %s" % IP_FILE

decoy = "\n".join([
    "# synthetic operator notes (proof fixture, not real)",
    "node a: " + ".".join(first_ip.split(".")[:-1]) + "." + first_ip.split(".")[-1],
    "pem: " + "BE" + "GIN RSA PRI" + "VATE KEY",
    "auth: " + "Be" + "arer " + "Zm9vYmFy" + "dG9rZW5zdHJpbmctaGVyZS0xMjM0NTY3ODkw",
    "hook: h" + "ttps://discord.com/api/webh" + "ooks/123456789012345678/" + "AbCdEf-" + "gHiJkLmNoPqRsTuV",
    # both spellings matter: a single separator is what an editor actually writes into a path,
    # and the doubled form is what shows up in escaped strings/logs.
    "open " + "C:" + chr(92) + _HOME + chr(92) + "33635" + chr(92) + _DESK + chr(92) + "keys.txt",
    "open " + "C:" + chr(92) * 2 + _HOME + chr(92) * 2 + "33635" + chr(92) * 2 + _DESK,
    "see /" + _HOME + "/33635/" + _DESK + "/notes.txt and also ~/" + _DESK + "/old.png",
    "seed: " + " ".join(["abandon"] * 11 + ["about"]) + " zebra monkey",   # 13-word shape
    "admin = " + chr(34) + "sup3r-s3cret-admin-value-42" + chr(34),
]) + "\n"

# per-user scratch root (a root-run pass and an ubuntu-run pass must not fight over ownership),
# re-used so repeated proof runs do not pile up 17 MB copies
SCRATCH = "/tmp/ld-leakproof-%s" % os.getuid()
if os.path.isdir(SCRATCH):
    try:
        shutil.rmtree(SCRATCH)
    except OSError as e:
        print("cannot reuse %s (%s) - rerun as the user who created it" % (SCRATCH, e))
        sys.exit(2)
os.makedirs(SCRATCH)
tree = os.path.join(SCRATCH, "repo")
shutil.copytree(REPO, tree, symlinks=True, ignore=shutil.ignore_patterns(".git"))
with open(os.path.join(tree, "PROOF_DECOY.md"), "w", encoding="utf-8") as fh:
    fh.write(decoy)

# the planted findings are a self-test, not an incident: never let them reach the alert log
r = subprocess.run([sys.executable, GATE, tree], capture_output=True, text=True,
                   env=dict(os.environ, LD_LEAK_NO_ALERT="1"))
print(r.stdout[-2600:])
if r.stderr.strip():
    print("stderr:", r.stderr[-400:])
print("exit code:", r.returncode)

want = ["infra-ip", "private-key", "bearer-token", "discord-webhook",
        "local-desktop-path", "mnemonic-phrase", "inline-secret"]
missing = [w for w in want if w not in r.stdout]
print("classes expected:", len(want), " missing:", missing or "none")
if r.returncode == 0:
    print("PROOF FAILED: gate passed a tree that contains every leak shape")
    sys.exit(1)
if missing:
    print("PROOF INCOMPLETE: %d class(es) not detected: %s" % (len(missing), ", ".join(missing)))
    sys.exit(3)
print("PROOF OK: planted leaks in all %d classes were caught (scratch tree left at %s)" % (len(want), tree))
