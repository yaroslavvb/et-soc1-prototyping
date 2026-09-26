#!/usr/bin/env bash
# V3-ABL-B (PLAN3 §2, suggested E39): sparse-compute energy configurations (E3) and TenB streaming (E2).
# One pass = one shuffled block (block index pass-1) of the 18 configurations in v3-energy.cfg, 5 s runs, strict
# start (governor-free cards, aifoundry2 and aifoundry1-c0/-c1: heat to 84 C, launch at 80 C; the pinned aifoundry3:
# 57 / 55 C), 10 Hz sampler for the block.
#   bash tools/claims-v3/ablb/block.sh <pass 1..3> [--smoke]        (aifoundry1: V3_DEVICE=0 or 1 selects the card)
# The plan's one invocation of 3 blocks is split into passes 1-3 (blocks 0-2, seeds 1-3). Pass 4+ replaces dropped runs.
# Runner: the shared patched run_ablation (tools/claims-v3/abla/ablrun.sh).
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
. "$V3_ROOT/tools/claims-v3/abla/ablrun.sh"
pass=${1:?usage: block.sh <pass> [--smoke]}; mode=${2:-}
case $pass in ''|*[!0-9]*|0) echo "pass must be 1, 2, ..." >&2; exit 2 ;; esac
others_present && exit 3

HERE=$V3_ROOT/tools/claims-v3/ablb
# Launch temperatures follow the governor (as abla): governor-free cards 80 / 84 C, the pinned card 55 / 57 C.
if [ -n "$GOV_FREE" ]; then TARGET=80; PREHEAT=84; LAUNCH=80.9; export ABL_CAP_S=2100
else                        TARGET=55; PREHEAT=57; LAUNCH=55.8; export ABL_CAP_S=1500; fi
# Leakage slope per card; aifoundry1's cards take aifoundry2's (their own are unmeasured; see ../abla/README.md).
case $CARD in
  aifoundry3) LEAK=0.55 ;;
  aifoundry2|aifoundry1-c0|aifoundry1-c1) LEAK=0.81 ;;
  *) echo "ablb: no leakage slope for card $CARD" >&2; exit 2 ;;
esac

finish() {  # finish <session-rc> <check-args...>
  local rc=$1 note crc; shift
  note=$(python3 "$V3_ROOT/tools/claims-v3/abla/ablcheck.py" "$OUT" --leak "$LEAK" --launch-temp "$LAUNCH" "$@"); crc=$?
  [ -n "${V3_DRY:-}" ] && { block_end ok "dry run: $note"; exit 0; }
  case $rc in
    0) if [ $crc -eq 0 ]; then block_end ok "$note"; exit 0; else block_end fail "check failed: $note"; exit 1; fi ;;
    3) block_end fail "someone else held the card mid-block: $note"; exit 3 ;;
    *) block_end fail "session stopped (rc $rc: 2 sampler lost, 4 time cap): $note"; exit 1 ;;
  esac
}

if [ "$mode" = --smoke ]; then
  # Smallest real check (~30 s of card time, ~45 s on a cool governor-free card with heat_to 76): one heater burst; 3 s
  # runs of the gemv kernel, the tensor_mask row mask, int8 and fp16 with B streamed through TenB (random operands,
  # as the block), and the same two TenB types on the host's default small-integer operands, whose results the host
  # checks (--b-stream had only run on silicon with fp32): ablcheck.py --smoke fails the smoke unless each *_chk_*
  # run has a launch the host checked ("both", "math" or "prm-literal"; the long timed fp16 launches pass 2^24 and
  # print "unchecked", the 20,000-iteration calibration launch does not) and none "wrong". Then the per-run metrics.
  block_begin ablb-smoke "$pass"
  abl_hash_code ablb docs/reports/data/2026-09-25-claims-v3/PLAN3.md
  { grep -E '^(gemv-dense-0|fma-rowmask|int8_randn_tenb|fp16_randn_tenb) ' "$HERE/v3-energy.cfg"
    echo "int8_chk_tenb   --test fma --type int8 --pattern none --b-stream --shires 0xffffffff --per-shire 32"
    echo "fp16_chk_tenb   --test fma --type fp16 --pattern none --b-stream --shires 0xffffffff --per-shire 32"
  } > "$OUT/smoke.cfg"
  # governor-free cards: start on a warm die (lib rule, heat_to 76, before the sampler opens the management node);
  # a no-op on the pinned aifoundry3
  heat_to 76 "$OUT/heat.jsonl" || log "smoke: heat_to 76 gave up; runs below 600 MHz will be marked"
  ABL_NO_APPROACH=1 ABL_CAP_S=120 abl_session "$OUT" "$OUT/smoke.cfg" 0 3 "$TARGET" "$PREHEAT" 0
  finish $? --smoke
fi

block_begin ablb "$pass"
abl_hash_code ablb docs/reports/data/2026-09-25-claims-v3/PLAN3.md
abl_session "$OUT" "$HERE/v3-energy.cfg" $(( pass - 1 )) 5 "$TARGET" "$PREHEAT" 0
finish $?
