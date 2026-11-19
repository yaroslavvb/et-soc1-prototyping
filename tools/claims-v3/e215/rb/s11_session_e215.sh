#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum), the box step "the session" (this file is s11; step 9): E211's step 9
# (tools/claims-v3/e211/rb/s11_session_e211.sh, landed in 2b7f261f) for E215's arm: the last start (k6's rb_need_start), the cap before the last
# end (rb_need_end with the arm's E215_BUDGET_S), today's build of both kernels (step 6), today's never-run report for this arm (step 6n), then
# in ONE launch on the box: k6's guard, THE REST RULE (rb/rest_rule_e215.sh), THE HUNG MARKER, THE SAME-DAY RULE (an E215 session of this arm that
# opened the card earlier today refuses another; after two that opened no device, a third try refuses), today's dry pass and build, then
# session_e215.sh detached (setsid nohup; arm B with ET_DEVICES=1, which the wrapper sets), its T0 written on the box and in
# RB_OUT/e215-T0-<arm>.txt.
#   bash tools/claims-v3/e215/rb/s11_session_e215.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e215.sh"
rb_init s11_session
e215_arm "${1:-}"
e215_jobs "$ARM"
e215_window
rb_need_start
rb_need_end "$E215_BUDGET_S"
b=$(e215_built "$ARM")
[ -n "${RB_DRY:-}" ] && b=${b:-rgm}
[ "$b" = rgm ] || rb_die $RB_E_USAGE "rgm136 and rgm211 were not built today (RB_OUT/e215-built-$ARM.txt, step 6's wait): run step 6 first"
if [ -z "${RB_DRY:-}" ]; then      # step 6n's report written today (step 7 needed it under 30 minutes old before the day's first card command)
  [ -s "$RB_OUT/e215-neverrun-$ARM.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e215-neverrun-$ARM.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "no never-run report from today in RB_OUT (step 6n, then step 7, come before the session)"
else
  echo "--- gate: RB_OUT/e215-neverrun-$ARM.txt (step 6n's) written today"
fi
f=$(rb_file e215)
{ rb_prelude "$BOX"
  echo "ARM=$ARM; JD=$JOB_DRY; JB=$JOB_BUILD; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E215_DIR/rest_rule_e215.sh"
  e215_hung_text
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
opened=0; nodev=0
for L in build/e215/T*-"$ARM"/session.log; do
  [ -f "$L" ] || continue
  [ "$(TZ=America/Los_Angeles date -r "$L" +%F 2>/dev/null)" = "$TODAY" ] || continue
  if grep -q 'the first card command' "$L"; then opened=$((opened + 1)); else nodev=$((nodev + 1)); fi
done
[ "$opened" -eq 0 ] || { echo "REFUSED: the same-day rule: an E215 session opened the card earlier today ($opened): not again today"; exit 3; }
[ "$nodev" -lt 2 ] || { echo "REFUSED: the same-day rule: $nodev E215 sessions that opened no device ran today: a third try is not made"; exit 3; }
echo "same-day: E215 sessions today: $opened that opened the card, $nodev that opened no device"
job_ok_today "$JD" || { echo "REFUSED: E215's dry pass (step 8's job $JD) has not ended rc 0 today"; exit 3; }
echo "dry pass: $JD ended rc 0 today"
fresh "build/q141k/jobs/$JB.out" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JB.out" ||
  { echo "REFUSED: rgm136 and rgm211 were not built today (step 6's job $JB)"; exit 3; }
mkdir -p build/e215 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e215$ARM.T0"
E215_T0=$T0 E215_ARM=$ARM E215_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e215/session_e215.sh > "build/e215/session-$ARM.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e215 arm $ARM T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; session_e215.sh)"
tail -n 6 "build/e215/T$T0-$ARM/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$BOX"
rb_remote launch "$BOX" "launch e215 arm $ARM, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e215 arm $ARM"
for k in rest note hung same-day; do rb_has "^$k: " && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 "^$k: " "$RB_CAP")" >> "$RB_LOG"; done
t0=$(rb_val "^LAUNCHED e215 arm $ARM T0 ([0-9]+) .*\$")
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e215-T0-$ARM.txt"
rb_say "e215 arm $ARM launched on $BOX (T0 $t0); wait with s20_wait_e215.sh $ARM (bounded), and read its identity gate, identity read, smoke and stop-path test"
