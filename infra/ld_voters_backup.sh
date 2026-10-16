#!/bin/bash
# ld_voters_backup.sh — encrypted backup of the recovered root-voter keyrings (/home/ubuntu/voters).
# These 6 keyrings are the only copies left after the Tencent hosts retire (10-18); without them the
# N-of-M daily root can never reach threshold again, which would silently break ALL reward claims.
# Plaintext NEVER touches disk: tar streams straight through gzip into AES256 gpg.
set -u
SRC=/home/ubuntu/voters
[ -d "$SRC" ] || { echo "$(date -u +%FT%TZ) no voters dir - skip"; exit 0; }
DEST=${VB_DEST:-/home/ubuntu/backups}
PASS=${VB_PASS:-/root/.ld_backup_pass}
[ -s "$PASS" ] || { echo "$(date -u +%FT%TZ) FATAL: passphrase $PASS missing - NOT writing plaintext"; exit 1; }
mkdir -p "$DEST"; chmod 700 "$DEST"
STAMP=$(date -u +%F)
ARCH="$DEST/voters-$STAMP.tar.gz.gpg"
if tar cf - -C /home/ubuntu voters 2>/dev/null | gzip -c | gpg --batch --yes --pinentry-mode loopback \
     --passphrase-file "$PASS" --symmetric --cipher-algo AES256 -o "$ARCH"; then
  chmod 600 "$ARCH"
  echo "$(date -u +%FT%TZ) voters backup $ARCH ($(stat -c%s "$ARCH") bytes)"
  find "$DEST" -name "voters-*.tar.gz.gpg" -mtime +30 -delete 2>/dev/null
else
  echo "$(date -u +%FT%TZ) voters backup FAILED"; exit 1
fi
