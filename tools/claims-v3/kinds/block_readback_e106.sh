#!/usr/bin/env bash
# E106 (Q132, tools/claims-v3/kinds/E106.md): read the accumulators back, as a lib.sh block on aifoundry1 card 1, under the card lock. One launch per read, each under `timeout 10`
# (readback_e106.py); the card's static configuration read at both ends, read only; no sampler, because nothing here is a power measurement. The binary is E106's own, build/e104/b/host/sparsity_host
# (build_host_e104.sh, one flag added: --dump-c), with the existing build's kernel. No knob is written: no governor, TDP, threshold or clock set, no reset, no --reset-ms.
#
#   V3_DEVICE=1 bash tools/claims-v3/kinds/block_readback_e106.sh <pass> [--first-only]
#   V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/kinds/block_readback_e106.sh <pass>      # print every read, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1, as block_e106.sh's: another user who is only logged in does not block; another user on THIS card does. Fails closed when et-holders is unreadable.
case "$CARD" in aifoundry1-c*)
  if [ -z "${V3_DRY:-}" ]; then
  others_present() {
    local holders= out n=${V3_DEVICE:-0}
    out=$(sudo -n /usr/local/sbin/et-holders 9>&- 8>&- 2>&1) || { log "others present: et-holders unreadable: ${out:0:120}"; return 0; }
    holders=$(printf '%s\n' "$out" | grep -v 'et-holders' |
              awk -v me="$USER" -v d="/dev/et${n}_" -v l="lock:etsoc-shire${n}.lock" \
                  'index($1, d) == 1 || $1 == l { if ($2 != me && $2 != "") print $2":"$3 }' | tr '\n' ' ')
    if [ -n "${holders// /}" ]; then log "others present: holders=[$holders]"; return 0; fi
    return 1
  }
  fi ;;
*) echo "E106's read-back runs on aifoundry1's cards only" >&2; exit 2 ;;
esac
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE
PASS=${1:?usage: block_readback_e106.sh <pass> [--first-only]}
FIRST=; [ "${2:-}" = --first-only ] && FIRST=--first-only
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
[ -x build/e104/b/host/sparsity_host ] || { echo "no build/e104/b/host/sparsity_host: run build_host_e104.sh first" >&2; exit 2; }
[ -f build/sparsity/kernel/sparsity.elf ] || { echo "no kernel ELF" >&2; exit 2; }
if [ -n "${V3_DRY:-}" ]; then
  python3 "$HERE/readback_e106.py" "$V3_ROOT/build/e106-dry-readback" --dry | sed 's/^/  /'
  exit 0
fi
EXPN=kinds-readback
D=$DATA_ROOT/$EXPN/p$PASS
if [ -d "$D" ] && ! grep -q '"status":"ok"' "$D/block.json" 2>/dev/null; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
sha256sum build/e104/b/host/sparsity_host build/sparsity/kernel/sparsity.elf build/sparsity/host/sparsity_host build/e104/src/host/main.cpp "$HERE/readback_e106.py" "$HERE/e106/e106.json" > "$OUT/binaries.sha256" 2>/dev/null
card_config() { timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true; }
card_config > "$OUT/config_start.json"
python3 "$HERE/readback_e106.py" "$OUT" $FIRST; rc=$?
card_config > "$OUT/config_end.json"
case $rc in
  0) block_end ok "read-back${FIRST:+ first only}" ;;
  *) block_end failed "readback_e106 exit $rc"; exit 1 ;;
esac
