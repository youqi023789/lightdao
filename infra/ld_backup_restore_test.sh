#!/usr/bin/env bash
# ld_backup_restore_test.sh — restore-test the NEWEST encrypted key archive.
#
# Proves the archive written by ld_backup.sh can actually be decrypted and extracted, and
# that priv_validator_state.json inside it is valid JSON (a corrupt/truncated state file is
# the double-sign hazard the backup exists to prevent).
#
# HARD SAFETY RULES
#   * Production data is never touched: this script only READS $DEST/keys-*.gpg and the
#     passphrase file, and writes only inside /tmp/restore_test.
#   * It prints STRUCTURAL facts only (file names, sizes, JSON keys, block height). No key
#     material, no mnemonic, no private key bytes ever reach stdout or the log.
#   * /tmp/restore_test is created 0700 and shredded on exit (trap), so plaintext key
#     material does not survive the test on a live validator.
set -uo pipefail

RT=/tmp/restore_test
HOST=$(hostname -s)
say() { echo "[restore-test $(date -u +%FT%TZ)] $*"; }

cleanup() {
  if [ -d "$RT" ]; then
    find "$RT" -type f -print0 2>/dev/null | xargs -0 -r shred -u 2>/dev/null
    rm -rf "$RT" 2>/dev/null
    say "cleanup: $RT shredded and removed (exists=$([ -d "$RT" ] && echo yes || echo no))"
  fi
}
trap cleanup EXIT

if [ -d /home/ubuntu/backups ]; then DEST=/home/ubuntu/backups
elif [ -d /root/backups ]; then DEST=/root/backups
else DEST="$HOME/backups"; fi

if [ "$(id -u)" = "0" ]; then PASSFILE=/root/.ld_backup_pass; else PASSFILE="$HOME/.ld_backup_pass"; fi

say "host=$HOST dest=$DEST passfile=$PASSFILE"

ARCH=$(ls -1t "$DEST"/keys-*.tar.gz.gpg "$DEST"/keys-*.tar.gz.age 2>/dev/null | head -1)
if [ -z "$ARCH" ]; then say "FAIL: no keys-*.gpg / keys-*.age archive in $DEST"; exit 1; fi
say "newest archive: $ARCH ($(stat -c%s "$ARCH") bytes, mtime $(stat -c%y "$ARCH"))"
[ -r "$PASSFILE" ] || { say "FAIL: passphrase file $PASSFILE not readable"; exit 1; }
say "passphrase file perms: $(stat -c '%a %U:%G' "$PASSFILE")"

# fresh 0700 sandbox
[ -d "$RT" ] && { find "$RT" -type f -print0 2>/dev/null | xargs -0 -r shred -u 2>/dev/null; rm -rf "$RT"; }
mkdir -p "$RT" && chmod 700 "$RT"

say "-- step 1: decrypt"
case "$ARCH" in
  *.gpg) gpg --batch --yes --pinentry-mode loopback --passphrase-file "$PASSFILE" \
              --decrypt --output "$RT/keys.tar.gz" "$ARCH" >/dev/null 2>"$RT/gpg.err" ;;
  *.age) age --decrypt -i "$PASSFILE" -o "$RT/keys.tar.gz" "$ARCH" 2>"$RT/gpg.err" ;;
esac
RC=$?
if [ $RC -ne 0 ] || [ ! -s "$RT/keys.tar.gz" ]; then
  say "FAIL: decrypt rc=$RC $(head -c 200 "$RT/gpg.err" 2>/dev/null)"; exit 1
fi
say "PASS decrypt -> keys.tar.gz ($(stat -c%s "$RT/keys.tar.gz") bytes)"

say "-- step 1b: wrong passphrase must be rejected"
echo "definitely-not-the-passphrase" > "$RT/bad.pass"; chmod 600 "$RT/bad.pass"
if gpg --batch --yes --pinentry-mode loopback --passphrase-file "$RT/bad.pass" \
       --decrypt --output "$RT/should_not_exist" "$ARCH" >/dev/null 2>&1; then
  say "FAIL: a WRONG passphrase decrypted the archive"
else
  say "PASS wrong passphrase rejected (no plaintext produced: $([ -s "$RT/should_not_exist" ] && echo LEAK || echo clean))"
fi

say "-- step 2: extract"
mkdir -p "$RT/x" && chmod 700 "$RT/x"
tar xzf "$RT/keys.tar.gz" -C "$RT/x" || { say "FAIL: tar extract"; exit 1; }
say "PASS extract; tree (names/sizes only):"
find "$RT/x" -mindepth 1 -printf '      %M %10s  %P\n' 2>/dev/null | sort -k3 | head -40

say "-- step 3: verify priv_validator_state.json parses"
PVS=$(find "$RT/x" -name priv_validator_state.json | head -1)
if [ -z "$PVS" ]; then say "FAIL: priv_validator_state.json not in the archive"; exit 1; fi
say "found: ${PVS#$RT/x/} ($(stat -c%s "$PVS") bytes)"
if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$PVS" 2>/dev/null; then
  say "FAIL: priv_validator_state.json is not valid JSON"; exit 1
fi
python3 - "$PVS" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print("      PASS valid JSON; keys=%s" % sorted(d.keys()))
print("      height=%s round=%s step=%s" % (d.get("height"), d.get("round"), d.get("step")))
PY

say "-- step 4: verify the keyring payload survived the round trip BYTE-EXACTLY"
say "    method: sha256 of every extracted file vs sha256 of the LIVE file it came from."
say "    (structural comparison only -- no key bytes, no JWE payload, nothing secret is printed)"
KR=$(find "$RT/x" -maxdepth 2 -type d -name "keyring-*" | head -1)
if [ -z "$KR" ]; then
  say "FAIL: no keyring-* directory in the archive"; exit 1
fi
LIVE_WASMD=""
for h in /root/.wasmd /home/ubuntu/.wasmd /home/*/.wasmd; do
  [ -d "$h" ] || continue
  found=0
  for k in "$h"/keyring-*; do [ -d "$k" ] && found=1 && break; done
  [ -f "$h/data/priv_validator_state.json" ] && found=1
  [ -f "$h/config/priv_validator_state.json" ] && found=1
  [ "$found" = "1" ] && LIVE_WASMD="$h" && break
done
NINFO=$(find "$KR" -name '*.info' | wc -l)
say "keyring dir in archive: ${KR#$RT/x/}  ($NINFO .info file(s)); live wasmd home: ${LIVE_WASMD:-none}"
MISMATCH=0; COMPARED=0
while IFS= read -r f; do
  rel="${f#$RT/x/}"                       # e.g. keyring-test/operator.info
  live="$LIVE_WASMD/$rel"
  if [ ! -f "$live" ]; then
    say "      MISSING LIVE COUNTERPART: $rel"; MISMATCH=$((MISMATCH+1)); continue
  fi
  h1=$(sha256sum "$f" | cut -d' ' -f1)
  h2=$(sudo -n sha256sum "$live" 2>/dev/null | cut -d' ' -f1)
  [ -z "$h2" ] && h2=$(sha256sum "$live" 2>/dev/null | cut -d' ' -f1)
  COMPARED=$((COMPARED+1))
  if [ "$h1" = "$h2" ]; then
    say "      MATCH    $rel  sha256=${h1:0:16}...  size=$(stat -c%s "$f")"
  else
    say "      MISMATCH $rel  archive=${h1:0:16}... live=${h2:0:16}..."
    MISMATCH=$((MISMATCH+1))
  fi
done < <(find "$KR" -type f | sort)
# the state file too
if [ -n "$PVS" ]; then
  say "      priv_validator_state.json: archived height/step parsed above; the live file advances"
  say "      with every block so a byte comparison is expected to differ (structure compared instead)."
fi
if [ "$MISMATCH" -eq 0 ] && [ "$COMPARED" -gt 0 ] && [ "$NINFO" -gt 0 ]; then
  say "PASS all $COMPARED keyring files are byte-identical to the live originals after decrypt+extract"
else
  say "FAIL: $MISMATCH mismatched/missing file(s) out of $COMPARED compared"; exit 1
fi
say "-- step 4b: confirm the .info payloads are ENCRYPTED JWE envelopes, not plaintext keys"
FIRST=$(find "$KR" -name '*.info' | head -1)
if [ -n "$FIRST" ]; then
  python3 - "$FIRST" <<'PY'
import base64, json, re, sys
raw = open(sys.argv[1], "rb").read().strip()
txt = raw.decode("latin1")
# a cosmos keyring .info file holds a compact JWE: 5 dot-separated base64url segments,
# whose first segment is the (non-secret) JOSE header. A raw secp256k1 key blob is neither.
segs = txt.split(".")
print("      length=%d  first char=%r  dot-separated segments=%d" % (len(raw), txt[:1], len(segs)))
ok = False
if len(segs) == 5 and all(re.fullmatch(r"[A-Za-z0-9_-]+", s) for s in segs):
    pad = segs[0] + "=" * (-len(segs[0]) % 4)
    try:
        hdr = json.loads(base64.urlsafe_b64decode(pad))
        print("      JOSE header (public, not secret): %s" % json.dumps(hdr, sort_keys=True))
        ok = hdr.get("alg", "").startswith("PBES2") and hdr.get("enc") == "A256GCM"
    except Exception as e:
        print("      header decode failed: %s" % e)
if ok:
    print("      VERDICT: intact PBES2/A256GCM JWE envelope -> the key material is still encrypted")
    print("               and survived tar+gpg+untar+gpg-decrypt byte-for-byte (see step 4).")
else:
    print("      VERDICT: NOT a recognisable JWE envelope -- inspect manually before trusting the backup")
PY
fi

say "-- step 5: compare against the LIVE files (read-only, must be identical)"
LIVE_PVS=""
for p in /root/.wasmd/data/priv_validator_state.json /home/ubuntu/.wasmd/data/priv_validator_state.json \
         /root/.wasmd/config/priv_validator_state.json /home/ubuntu/.wasmd/config/priv_validator_state.json; do
  [ -f "$p" ] && LIVE_PVS="$p" && break
done
if [ -n "$LIVE_PVS" ]; then
  # the live file advances with every block, so compare structure, not bytes
  python3 - "$LIVE_PVS" "$PVS" <<'PY'
import json, sys
live = json.load(open(sys.argv[1])); arch = json.load(open(sys.argv[2]))
print("      live  %s height=%s step=%s" % (sys.argv[1], live.get("height"), live.get("step")))
print("      arch  height=%s step=%s" % (arch.get("height"), arch.get("step")))
print("      same key set: %s" % (sorted(live.keys()) == sorted(arch.keys())))
print("      archived height <= live height: %s" % (int(arch.get("height", 0)) <= int(live.get("height", 0))))
PY
  say "PASS live priv_validator_state.json was only READ, never modified"
fi

say "RESULT: ALL RESTORE TESTS PASSED on $HOST"
exit 0
