#!/usr/bin/env bash
# E116 (Q133, tools/claims-v3/e116/E116.md): read the accumulators back once per E88 tile, as a lib.sh block on aifoundry3
# card 0, under the card lock. E104's block_readback_e104.sh with the binary, the plan and the card changed: one launch per
# read, each under `timeout 10` (readback_e116.py); the card's static configuration read at both ends, read only; no
# sampler, because nothing here is a power measurement. No knob is written: no governor, TDP, threshold or clock set, no
# reset, no --reset-ms, no PMIC command.
#
#   bash tools/claims-v3/e116/block_readback_e116.sh <pass> [--first-only]
#   V3_DRY=1 bash tools/claims-v3/e116/block_readback_e116.sh <pass>      # print every read, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1 (hl/README.md, kept by E60-E113), as block_e88.sh reads it on aifoundry3: a user who is only logged in does
# not block; another user's device process, or a holder of this card's node or lock, does. Fails closed when et-holders is
# unreadable.
case "$CARD" in aifoundry3)
  if [ -z "${V3_DRY:-}" ]; then
  others_present() {
    local procs= holders= out
    procs=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {print $1":"$2":"$3}' | tr '\n' ' ')
    out=$(sudo -n /usr/local/sbin/et-holders 9>&- 8>&- 2>&1) || { log "others present: et-holders unreadable: ${out:0:120}"; return 0; }
    holders=$(printf '%s\n' "$out" | grep -v 'et-holders' |
              awk -v me="$USER" -v d="/dev/et0_" -v l="lock:etsoc-shire0.lock" \
                  'index($1, d) == 1 || $1 == l { if ($2 != me && $2 != "") print $2":"$3 }' | tr '\n' ' ')
    if [ -n "${procs// /}${holders// /}" ]; then log "others present: procs=[$procs] holders=[$holders]"; return 0; fi
    return 1
  }
  fi ;;
*) echo "E116's read-back runs on aifoundry3 only" >&2; exit 2 ;;
esac
others_present && exit 3
PASS=${1:?usage: block_readback_e116.sh <pass> [--first-only]}
FIRST=; [ "${2:-}" = --first-only ] && FIRST=--first-only
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e116
[ -x build/e116/b/host/sparsity_host ] || { echo "no build/e116/b/host/sparsity_host: run build_host_e116.sh first" >&2; exit 2; }
[ -f build/sparsity/kernel/sparsity.elf ] || { echo "no kernel ELF" >&2; exit 2; }
if [ -n "${V3_DRY:-}" ]; then
  python3 "$HERE/readback_e116.py" "$V3_ROOT/build/e116-dry-readback" --dry | sed 's/^/  /'
  exit 0
fi
EXPN=rpath-readback
D=$DATA_ROOT/$EXPN/p$PASS
if [ -d "$D" ] && ! grep -q '"status":"ok"' "$D/block.json" 2>/dev/null; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
sha256sum build/e116/b/host/sparsity_host build/sparsity/kernel/sparsity.elf build/sparsity/host/sparsity_host build/e116/src/host/main.cpp "$HERE/readback_e116.py" "$HERE/expect-e116.json" > "$OUT/binaries.sha256" 2>/dev/null
card_config() { timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true; }
card_config > "$OUT/config_start.json"
python3 "$HERE/readback_e116.py" "$OUT" $FIRST; rc=$?
card_config > "$OUT/config_end.json"
case $rc in
  0) block_end ok "read-back${FIRST:+ first only}" ;;
  *) block_end failed "readback_e116 exit $rc"; exit 1 ;;
esac
