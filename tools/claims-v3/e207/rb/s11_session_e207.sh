#!/usr/bin/env bash
# E207 (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum), the box step "the session" (this file is s11; step 9): E206's step 9
# (tools/claims-v3/e206/rb/s11_session_e206.sh, landed in 906699ea) launching session_e207.sh (run_e207.py), detached on aifoundry3 (it returns
# at once), ONLY after steps 4-8 read clean: the window rule, THE LAST START (k6's rb_need_start: the registered G + 1:30), the session's cap
# before the last end (E207_BUDGET_S: 4,500 s, the 70-minute cap and 5 minutes), k6's guard (no dry pass running, no card session of ours on the
# box: rb_guard_text), THE REST RULE (rb/rest_rule_e207.sh), THE HUNG MARKER (E202's: any "<time> HUNG: ..." line in a session log of ours under
# build/ refuses: a device process of ours did not end after its timeout's TERM, so the card may hold a hung hart; only the owner's word and a
# dated kit amendment lift it), THE SAME-DAY RULE (E202's: an E207 session that opened the card earlier today refuses; after sessions that opened
# no device, a third try the same day refuses), step 6n's never-run report written today (RB_OUT/e207-neverrun.txt), today's dry pass (the job
# a3-dry-e207 ended rc 0 today) and today's build (RB_OUT/
# e207-built-A.txt; the box's job a3-build-e207 read RGM-BUILT today); then session_e207.sh detached with the T0 written on the box (build/q141k/
# e207A.T0) and in RB_OUT (e207-T0-A.txt), which steps 10 and 11 read.
#   bash tools/claims-v3/e207/rb/s11_session_e207.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e207.sh"
rb_init s11_session
e207_arm "${1:-}"
e207_jobs "$ARM"
e207_window
rb_need_start
rb_need_end "$E207_BUDGET_S"
b=$(e207_built "$ARM")
[ -n "${RB_DRY:-}" ] && b=${b:-rgm}
[ "$b" = rgm ] || rb_die $RB_E_USAGE "rgm136 was not built today (RB_OUT/e207-built-$ARM.txt, step 6's wait): run step 6 first"
if [ -z "${RB_DRY:-}" ]; then      # step 6n's report written today (step 7 needed it under 30 minutes old before the day's first card command)
  [ -s "$RB_OUT/e207-neverrun.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e207-neverrun.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "no never-run report from today in RB_OUT (step 6n, then step 7, come before the session)"
else
  echo "--- gate: RB_OUT/e207-neverrun.txt (step 6n's) written today"
fi
f=$(rb_file e207)
{ rb_prelude "$BOX"
  echo "ARM=$ARM; JD=$JOB_DRY; JB=$JOB_BUILD; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E207_DIR/rest_rule_e207.sh"
  e207_hung_text
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
opened=0; nodev=0
for L in build/e207/T*-"$ARM"/session.log; do
  [ -f "$L" ] || continue
  [ "$(TZ=America/Los_Angeles date -r "$L" +%F 2>/dev/null)" = "$TODAY" ] || continue
  if grep -q 'the first card command' "$L"; then opened=$((opened + 1)); else nodev=$((nodev + 1)); fi
done
[ "$opened" -eq 0 ] || { echo "REFUSED: the same-day rule: an E207 session opened the card earlier today ($opened): not again today"; exit 3; }
[ "$nodev" -lt 2 ] || { echo "REFUSED: the same-day rule: $nodev E207 sessions that opened no device ran today: a third try is not made"; exit 3; }
echo "same-day: E207 sessions today: $opened that opened the card, $nodev that opened no device"
job_ok_today "$JD" || { echo "REFUSED: E207's dry pass (step 8's job $JD) has not ended rc 0 today"; exit 3; }
echo "dry pass: $JD ended rc 0 today"
fresh "build/q141k/jobs/$JB.out" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JB.out" ||
  { echo "REFUSED: rgm136 was not built today (step 6's job $JB)"; exit 3; }
mkdir -p build/e207 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e207$ARM.T0"
E207_T0=$T0 E207_ARM=$ARM E207_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e207/session_e207.sh > "build/e207/session-$ARM.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e207 arm $ARM T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; session_e207.sh)"
tail -n 6 "build/e207/T$T0-$ARM/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$BOX"
rb_remote launch "$BOX" "launch e207 arm $ARM, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e207 arm $ARM"
for k in rest note hung same-day; do rb_has "^$k: " && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 "^$k: " "$RB_CAP")" >> "$RB_LOG"; done
t0=$(rb_val '^LAUNCHED e207 arm A T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e207-T0-$ARM.txt"
rb_say "e207 arm $ARM launched on $BOX (T0 $t0); wait with s20_wait_e207.sh $ARM (bounded), and read its identity gate, identity read, smoke and stop-path test"
