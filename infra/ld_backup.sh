#!/bin/bash
# ld_backup.sh — LightDAO validator backup.
#
# v2 (2026-09-29, OPS_ROADMAP S1/P6 + audit finding "no backup of ANY key material exists"):
#   1. UNCHANGED: gateway data tarball  -> $DEST/gw-<date>.tgz          (keep 7)
#   2. NEW      : encrypted key material -> $DEST/keys-<host>-<date>.tar.gz.gpg (keep 7)
#                 contents: the wasmd keyring directory + priv_validator_state.json
#
# Safety properties (this script runs on live mainnet validators):
#   * READ-ONLY on production data. It never writes to, moves, chmods or deletes anything
#     under the wasmd home; it only reads files into a tar.
#   * The plaintext tar is written to a 0700 mktemp dir and shredded immediately after
#     encryption, so plaintext key material never persists.
#   * No service, config, cron or chain state is touched. The script path is unchanged so
#     any existing cron entry keeps working as-is.
#   * Fails soft: if a step cannot run it logs and continues, so the gateway backup is
#     never lost because of the new key step (and vice versa).
#
# Encryption: `age` if installed, else `gpg -c --batch --passphrase-file`. The passphrase
# file is created once, 0600 root, from 32 random bytes.
#
# NOTE (deliberate limitation): the archive and its passphrase both live on the same host,
# so this protects against accidental deletion / disk replacement, NOT against a root
# compromise. KEYRING_MIGRATION_RUNBOOK PHASE 3 still requires an OFFSITE copy (age +
# 2-of-3 Shamir). Copy $DEST/keys-*.gpg offsite and delete the on-host passphrase there.

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
STAMP=$(date -u +%F)
HOST=$(hostname -s)
RUNUSER=$(id -un)

log() { echo "[ld_backup $(date -u +%FT%TZ)] $*"; }

# ---- locate the wasmd home. It must ACTUALLY hold key material: on the ubuntu nodes an
#      empty /root/.wasmd also exists and picking it would silently back up nothing.
has_keymat() {
  local h="$1" k
  for k in "$h"/keyring-*; do [ -d "$k" ] && return 0; done
  [ -f "$h/data/priv_validator_state.json" ] && return 0
  [ -f "$h/config/priv_validator_state.json" ] && return 0
  return 1
}
WASMD_HOME=""
CANDIDATES=""
SEEN=""
for h in /root/.wasmd /home/ubuntu/.wasmd /home/*/.wasmd; do
  [ -d "$h" ] || continue
  case " $SEEN " in *" $h "*) continue ;; esac   # /home/*/.wasmd can repeat /home/ubuntu/.wasmd
  SEEN="$SEEN $h"
  if has_keymat "$h"; then
    CANDIDATES="$CANDIDATES $h"
    [ -z "$WASMD_HOME" ] && WASMD_HOME="$h"
  fi
done
if [ "$(echo $CANDIDATES | wc -w)" -gt 1 ]; then
  log "WARNING: more than one wasmd home holds key material:$CANDIDATES - archiving $WASMD_HOME only"
fi

# ---- backup destination: reuse the existing one, else create $HOME/backups
if [ -d /home/ubuntu/backups ]; then
  DEST=/home/ubuntu/backups
elif [ -d /root/backups ]; then
  DEST=/root/backups
else
  DEST="$HOME/backups"
fi
mkdir -p "$DEST" 2>/dev/null
chmod 700 "$DEST" 2>/dev/null

log "start host=$HOST user=$RUNUSER dest=$DEST wasmd_home=${WASMD_HOME:-none}"

# =========================================================================
# 1. gateway data (original behaviour, unchanged)
# =========================================================================
if [ -d /home/ubuntu/lightdao_gateway/data ]; then
  if tar czf "$DEST/gw-$STAMP.tgz" -C /home/ubuntu lightdao_gateway/data lightdao_gateway/granted.json 2>/dev/null; then
    log "gateway archive  $DEST/gw-$STAMP.tgz ($(stat -c%s "$DEST/gw-$STAMP.tgz" 2>/dev/null) bytes)"
  else
    log "gateway archive FAILED (tar rc=$?)"
  fi
  find "$DEST" -name "gw-*.tgz" -mtime +7 -delete 2>/dev/null
else
  log "no lightdao_gateway on this host - gateway step skipped"
fi

# =========================================================================
# 2. encrypted key material (NEW)
# =========================================================================
if [ -z "$WASMD_HOME" ]; then
  log "no wasmd home found - key backup SKIPPED"
else
  # --- passphrase file: 0600, 32 random bytes, created once and never rewritten
  if [ "$(id -u)" = "0" ]; then PASSFILE=/root/.ld_backup_pass; else PASSFILE="$HOME/.ld_backup_pass"; fi
  if [ ! -s "$PASSFILE" ]; then
    ( umask 077
      if command -v openssl >/dev/null 2>&1; then openssl rand -base64 32 > "$PASSFILE"
      else head -c 32 /dev/urandom | base64 | tr -d '\n' > "$PASSFILE"; echo >> "$PASSFILE"; fi
      chmod 600 "$PASSFILE"
      chown root:root "$PASSFILE" 2>/dev/null )
    log "created passphrase file $PASSFILE (0600, 32 random bytes)"
  fi
  if [ ! -r "$PASSFILE" ]; then
    log "FATAL: cannot read $PASSFILE - key backup SKIPPED (no plaintext left behind)"
  else
    # --- collect the inputs
    KEYRING=""
    for k in "$WASMD_HOME"/keyring-*; do [ -d "$k" ] && KEYRING="$k" && break; done
    PVS=""
    for p in "$WASMD_HOME/data/priv_validator_state.json" "$WASMD_HOME/config/priv_validator_state.json"; do
      [ -f "$p" ] && PVS="$p" && break
    done
    if [ -z "$KEYRING" ] && [ -z "$PVS" ]; then
      log "neither a keyring dir nor priv_validator_state.json found under $WASMD_HOME - SKIPPED"
    else
      log "inputs: keyring=${KEYRING:-none} priv_validator_state=${PVS:-none}"
      TMPD=$(mktemp -d /tmp/ld_keys.XXXXXX) || TMPD=""
      if [ -z "$TMPD" ]; then
        log "FATAL: mktemp failed - key backup SKIPPED"
      else
        chmod 700 "$TMPD"
        PLAIN="$TMPD/keys-$HOST-$STAMP.tar"
        # tar with paths relative to the wasmd home so a restore lands in the right place
        ITEMS=""
        [ -n "$KEYRING" ] && ITEMS="$ITEMS $(basename "$KEYRING")"
        [ -n "$PVS" ]     && ITEMS="$ITEMS ${PVS#$WASMD_HOME/}"
        # shellcheck disable=SC2086
        if tar cf "$PLAIN" -C "$WASMD_HOME" $ITEMS 2>/dev/null; then
          NKEYS=$(tar tf "$PLAIN" 2>/dev/null | grep -c '\.info$' || true)
          ARCH="$DEST/keys-$HOST-$STAMP.tar.gz.gpg"
          ENC_OK=0
          if command -v age >/dev/null 2>&1 && [ -n "${AGE_RECIPIENT:-}" ]; then
            gzip -c "$PLAIN" | age -r "$AGE_RECIPIENT" -o "$ARCH" && ENC_OK=1 && log "encrypted with age"
          elif command -v gpg >/dev/null 2>&1; then
            gzip -c "$PLAIN" | gpg --batch --yes --pinentry-mode loopback \
                 --passphrase-file "$PASSFILE" --symmetric --cipher-algo AES256 \
                 -o "$ARCH" && ENC_OK=1 && log "encrypted with gpg (AES256 symmetric)"
          else
            log "FATAL: neither age nor gpg available - NOT writing a plaintext archive"
          fi
          # shred the plaintext no matter what happened
          if command -v shred >/dev/null 2>&1; then shred -u "$PLAIN" 2>/dev/null; else rm -f "$PLAIN"; fi
          rm -rf "$TMPD" 2>/dev/null
          if [ "$ENC_OK" = "1" ] && [ -s "$ARCH" ]; then
            chmod 600 "$ARCH" 2>/dev/null
            log "key archive      $ARCH ($(stat -c%s "$ARCH" 2>/dev/null) bytes, $NKEYS keyring .info entries)"
            find "$DEST" -name "keys-*.tar.gz.gpg" -mtime +7 -delete 2>/dev/null
            find "$DEST" -name "keys-*.tar.gz.age" -mtime +7 -delete 2>/dev/null
          else
            log "key archive FAILED - nothing written to $DEST"
          fi
        else
          log "tar of the key material FAILED - SKIPPED"
          rm -rf "$TMPD" 2>/dev/null
        fi
      fi
    fi
  fi
fi

log "retention: $(ls -1 "$DEST" 2>/dev/null | wc -l) file(s) in $DEST"
log "backup done $(date -u)"
