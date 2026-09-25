#!/usr/bin/env bash
# V3-ABL-A (PLAN3 §2, suggested E38): tensor-unit energy by operands, precision, structure and active minions.
# One pass = one shuffled block (block index pass-1) of the 23 configurations in abl_a.cfg, 7 s runs, strict start
# (aifoundry2: heat to 84 C, launch when the die reads 80 C; aifoundry3: 60 / 55 C), 10 Hz sampler for the block.
#   bash tools/claims-v3/abla/block.sh <pass 1..4> [--smoke]
# The plan's one invocation of 4 blocks is split into passes 1-4 (blocks 0-3: the same shuffles, seeds 1-4 and
# structured-tile seeds 1,2,1,2 as the original runner's loop). A pass 5+ replaces runs dropped from passes 1-4.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
. "$V3_ROOT/tools/claims-v3/abla/ablrun.sh"
pass=${1:?usage: block.sh <pass> [--smoke]}; mode=${2:-}
case $pass in ''|*[!0-9]*|0) echo "pass must be 1, 2, ..." >&2; exit 2 ;; esac
others_present && exit 3

HERE=$V3_ROOT/tools/claims-v3/abla
case $CARD in
  aifoundry2) TARGET=80; PREHEAT=84; LEAK=0.81; LAUNCH=80.9; export ABL_CAP_S=2700 ;;
  aifoundry3) TARGET=55; PREHEAT=60; LEAK=0.55; LAUNCH=55.8; export ABL_CAP_S=1800 ;;
esac

finish() {  # finish <session-rc> <check-args...>
  local rc=$1 note crc; shift
  note=$(python3 "$HERE/ablcheck.py" "$OUT" --leak "$LEAK" --launch-temp "$LAUNCH" "$@"); crc=$?
  [ -n "${V3_DRY:-}" ] && { block_end ok "dry run: $note"; exit 0; }
  case $rc in
    0) if [ $crc -eq 0 ]; then block_end ok "$note"; exit 0; else block_end fail "check failed: $note"; exit 1; fi ;;
    3) block_end fail "someone else held the card mid-block: $note"; exit 3 ;;
    *) block_end fail "session stopped (rc $rc: 2 sampler lost, 4 time cap): $note"; exit 1 ;;
  esac
}

if [ "$mode" = --smoke ]; then
  # Smallest real check (~20 s of card time; up to ~35 s on a cool aifoundry2, which first runs heat_to 76): sampler
  # start, one heater burst, 3 s runs of a structured-tile file
  # (reads the committed tiles on this host), int8, fp16 and the integer loop; then the reducer's per-run metrics.
  block_begin abla-smoke "$pass"
  abl_hash_code abla docs/reports/data/2026-09-25-claims-v3/PLAN3.md
  abl_check_tiles || { block_end fail "structured tiles missing or changed (see tiles.check)"; exit 1; }
  grep -E '^(m_negzero|int8_ones|fp16_zeros|spin) ' "$HERE/abl_a.cfg" > "$OUT/smoke.cfg"
  # aifoundry2: start on a warm die (lib rule, heat_to 76, before the sampler opens the management node); no-op on a3
  heat_to 76 "$OUT/heat.jsonl" || log "smoke: heat_to 76 gave up; runs below 600 MHz will be marked"
  ABL_NO_APPROACH=1 ABL_CAP_S=120 abl_session "$OUT" "$OUT/smoke.cfg" 0 3 "$TARGET" "$PREHEAT" 0
  finish $? --smoke
fi

block_begin abla "$pass"
abl_hash_code abla docs/reports/data/2026-09-25-claims-v3/PLAN3.md
abl_check_tiles || { block_end fail "structured tiles missing or changed (see tiles.check)"; exit 1; }
abl_session "$OUT" "$HERE/abl_a.cfg" $(( pass - 1 )) 7 "$TARGET" "$PREHEAT" 0
finish $?
