#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day), the box step "the session" (this file is s11; step 9): E215 arm A's step 9
# (tools/claims-v3/e215/rb/s11_session_e215.sh, landed in 8bde0182, run on aifoundry3 on Thu 19 Nov 2026) for E222: the last start (k6's rb_need_start), the
# cap before the last end (rb_need_end with E222_BUDGET_S), today's build of both trees (step 6), today's never-run report (step 6n), then in ONE
# launch on the box: k6's guard, THE REST RULE (rb/rest_rule_e222.sh), THE HUNG MARKER, THE SAME-DAY RULE (an E222 session that opened the card
# earlier today refuses another; after two that opened no device, a third try refuses), today's dry pass and build, then session_e222.sh detached
# (setsid nohup; ET_DEVICES unset, which the wrapper makes sure of), its T0 written on the box and in RB_OUT/e222-T0-A.txt.
#   bash tools/claims-v3/e222/rb/s11_session_e222.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e222.sh"
rb_init s11_session
e222_arm "${1:-}"
e222_jobs "$ARM"
e222_window
rb_need_start
rb_need_end "$E222_BUDGET_S"
b=$(e222_built "$ARM")
[ -n "${RB_DRY:-}" ] && b=${b:-rgm}
[ "$b" = rgm ] || rb_die $RB_E_USAGE "rgm136 and rgm211 were not built today (RB_OUT/e222-built-$ARM.txt, step 6's wait): run step 6 first"
if [ -z "${RB_DRY:-}" ]; then      # step 6n's report written today (step 7 needed it under 30 minutes old before the day's first card command)
  [ -s "$RB_OUT/e222-neverrun-$ARM.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e222-neverrun-$ARM.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "no never-run report from today in RB_OUT (step 6n, then step 7, come before the session)"
else
  echo "--- gate: RB_OUT/e222-neverrun-$ARM.txt (step 6n's) written today"
fi
f=$(rb_file e222)
{ rb_prelude "$BOX"
  echo "ARM=$ARM; JD=$JOB_DRY; JB=$JOB_BUILD; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E222_DIR/rest_rule_e222.sh"
  e222_hung_text
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
opened=0; nodev=0
for L in build/e222/T*-"$ARM"/session.log; do
  [ -f "$L" ] || continue
  [ "$(TZ=America/Los_Angeles date -r "$L" +%F 2>/dev/null)" = "$TODAY" ] || continue
  if grep -q 'the first card command' "$L"; then opened=$((opened + 1)); else nodev=$((nodev + 1)); fi
done
[ "$opened" -eq 0 ] || { echo "REFUSED: the same-day rule: an E222 session opened the card earlier today ($opened): not again today"; exit 3; }
[ "$nodev" -lt 2 ] || { echo "REFUSED: the same-day rule: $nodev E222 sessions that opened no device ran today: a third try is not made"; exit 3; }
echo "same-day: E222 sessions today: $opened that opened the card, $nodev that opened no device"
job_ok_today "$JD" || { echo "REFUSED: E222's dry pass (step 8's job $JD) has not ended rc 0 today"; exit 3; }
echo "dry pass: $JD ended rc 0 today"
fresh "build/q141k/jobs/$JB.out" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JB.out" ||
  { echo "REFUSED: rgm136 and rgm211 were not built today (step 6's job $JB)"; exit 3; }
mkdir -p build/e222 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e222$ARM.T0"
E222_T0=$T0 E222_ARM=$ARM E222_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e222/session_e222.sh > "build/e222/session-$ARM.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e222 arm $ARM T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; session_e222.sh)"
tail -n 6 "build/e222/T$T0-$ARM/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$BOX"
rb_remote launch "$BOX" "launch e222 arm $ARM, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e222 arm $ARM"
for k in rest note hung same-day; do rb_has "^$k: " && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 "^$k: " "$RB_CAP")" >> "$RB_LOG"; done
t0=$(rb_val "^LAUNCHED e222 arm $ARM T0 ([0-9]+) .*\$")
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e222-T0-$ARM.txt"
rb_say "e222 arm $ARM launched on $BOX (T0 $t0); wait with s20_wait_e222.sh $ARM (bounded), and read its identity gate, identity read, smoke and stop-path test"
