#!/usr/bin/env bash
# V3-X5 (PLAN3 §2, suggested E40): is the 0.92-0.95 card scale the card or its temperature? Two launch temperatures.
# One pass p = the plan's pair hi<b>, lo<b> with b = p-1: two one-block invocations of the shared patched runner
# (tools/claims-v3/abla/ablrun.sh) on x5.cfg, 7 s runs, SEED_OFFSET = b (seed b+1 in both arms, so hot and cool
# of a pass run the same tiles and passes differ), each with its own 10 Hz sampler:
#   aifoundry2 hot 83 C launch / 86 C preheat, then cool 76 / 79;  aifoundry3 hot 65 / 68, then cool 55 / 60.
#   bash tools/claims-v3/x5/block.sh <pass 1..3> [--smoke]
# Data: $OUT/hi<b>/ and $OUT/lo<b>/ (session directories as abla's pass directory).
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
. "$V3_ROOT/tools/claims-v3/abla/ablrun.sh"
pass=${1:?usage: block.sh <pass> [--smoke]}; mode=${2:-}
case $pass in ''|*[!0-9]*|0) echo "pass must be 1, 2, ..." >&2; exit 2 ;; esac
others_present && exit 3

HERE=$V3_ROOT/tools/claims-v3/x5
case $CARD in
  aifoundry2) HOT=83; HOT_PRE=86; COOL=76; COOL_PRE=79; LEAK=0.81; HOT_CAP=1200; COOL_CAP=1200 ;;
  aifoundry3) HOT=65; HOT_PRE=68; COOL=55; COOL_PRE=60; LEAK=0.55; HOT_CAP=1500; COOL_CAP=900 ;;
esac
b=$(( pass - 1 ))

arm() {  # arm <name> <target> <preheat> <cap_s> [secs] [cfg]: one invocation; sets ARM_RC and appends to NOTE
  local name=$1 target=$2 pre=$3 cap=$4 secs=${5:-7} cfg=${6:-$HERE/x5.cfg} n crc
  ABL_CAP_S=$cap abl_session "$OUT/$name" "$cfg" 0 "$secs" "$target" "$pre" "$b"; ARM_RC=$?
  n=$(python3 "$V3_ROOT/tools/claims-v3/abla/ablcheck.py" "$OUT/$name" --leak "$LEAK" \
      --launch-temp "$(python3 -c "print($target + 0.9)")" $ARM_CHECK_ARGS); crc=$?
  NOTE="$NOTE $name: $n;"
  [ -z "${V3_DRY:-}" ] && [ $ARM_RC -eq 0 ] && [ $crc -ne 0 ] && ARM_RC=5
  return 0
}

finish() {
  [ -n "${V3_DRY:-}" ] && { block_end ok "dry run:$NOTE"; exit 0; }
  case $ARM_RC in
    0) block_end ok "$NOTE"; exit 0 ;;
    3) block_end fail "someone else held the card mid-block:$NOTE"; exit 3 ;;
    5) block_end fail "check failed:$NOTE"; exit 1 ;;
    *) block_end fail "session stopped (rc $ARM_RC: 2 sampler lost, 4 time cap):$NOTE"; exit 1 ;;
  esac
}

NOTE=
if [ "$mode" = --smoke ]; then
  # Smallest real check (~12 s of card time): both arms' session paths (sampler stop and restart between them),
  # one heater burst each, 3 s of fp32 uniform (hot arm) and fp16 randn (cool arm); then the per-run metrics.
  block_begin x5-smoke "$pass"
  abl_hash_code x5 docs/reports/data/2026-09-25-claims-v3/PLAN3.md
  grep -E '^fp32_uniform ' "$HERE/x5.cfg" > "$OUT/smoke-hi.cfg"; grep -E '^fp16_randn ' "$HERE/x5.cfg" > "$OUT/smoke-lo.cfg"
  ARM_CHECK_ARGS=--smoke
  # aifoundry2: start on a warm die (lib rule, heat_to 76, before the sampler opens the management node); no-op on a3
  heat_to 76 "$OUT/heat.jsonl" || log "smoke: heat_to 76 gave up; runs below 600 MHz will be marked"
  ABL_NO_APPROACH=1 arm hi$b "$HOT" "$HOT_PRE" 120 3 "$OUT/smoke-hi.cfg"
  if [ $ARM_RC -eq 0 ]; then nap 2; ABL_NO_APPROACH=1 arm lo$b "$COOL" "$COOL_PRE" 120 3 "$OUT/smoke-lo.cfg"; fi
  finish
fi

block_begin x5 "$pass"
abl_hash_code x5 docs/reports/data/2026-09-25-claims-v3/PLAN3.md
ARM_CHECK_ARGS=
arm hi$b "$HOT" "$HOT_PRE" "$HOT_CAP"
if [ $ARM_RC -eq 0 ]; then nap 2; arm lo$b "$COOL" "$COOL_PRE" "$COOL_CAP"; fi
finish
