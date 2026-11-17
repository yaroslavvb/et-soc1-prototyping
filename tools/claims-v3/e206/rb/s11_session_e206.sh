#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum), the box step "the session" (this file is s11; step 9), for one arm:
# E190's step 9 v2 (rb/s11_session_e190_v2.sh) launching session_e206.sh (run_e206.py), detached on the arm's box (it returns at once), ONLY
# after steps 4-8 read clean for that arm: the window rule, the last start, the session's cap before the last end (E206_BUDGET_S: 7,500 s),
# k6's guard (no dry pass running, no card session of ours on the box: rb_guard_text, which also reads aifoundry1's identity by continuity),
# THE REST RULE (rb/rest_rule_e206.sh), THE HUNG MARKER (E202's: any "<time> HUNG: ..." line in a session log of ours under build/ refuses:
# a device process of ours did not end after its timeout's TERM, so the card may hold a hung hart; only the owner's word and a dated kit
# amendment lift it), THE SAME-DAY RULE (E202's: a session of this arm that opened the card earlier today refuses; after sessions that opened
# no device, a third try the same day refuses), today's dry pass (the arm's job a?-dry-e206 ended rc 0 today) and today's build
# (RB_OUT/e206-built-<arm>.txt; the box's job a?-build-e206 read RGM-BUILT today); then session_e206.sh detached with the T0 written on the box
# (build/q141k/e206<arm>.T0) and in RB_OUT (e206-T0-<arm>.txt), which steps 10 and 11 read.
#   bash tools/claims-v3/e206/rb/s11_session_e206.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e206.sh"
rb_init s11_session
e206_arm "${1:-}"
e206_jobs "$ARM"
e206_window
rb_need_start
rb_need_end "$E206_BUDGET_S"
b=$(e206_built "$ARM")
[ -n "${RB_DRY:-}" ] && b=${b:-rgm}
[ "$b" = rgm ] || rb_die $RB_E_USAGE "rgm136 was not built today for arm $ARM (RB_OUT/e206-built-$ARM.txt, step 6's wait): run step 6 first"
f=$(rb_file e206)
{ rb_prelude "$BOX"
  echo "ARM=$ARM; JD=$JOB_DRY; JB=$JOB_BUILD; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E206_DIR/rest_rule_e206.sh"
  e206_hung_text
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
opened=0; nodev=0
for L in build/e206/T*-"$ARM"/session.log; do
  [ -f "$L" ] || continue
  [ "$(TZ=America/Los_Angeles date -r "$L" +%F 2>/dev/null)" = "$TODAY" ] || continue
  if grep -q 'the first card command' "$L"; then opened=$((opened + 1)); else nodev=$((nodev + 1)); fi
done
[ "$opened" -eq 0 ] || { echo "REFUSED: the same-day rule: a session of arm $ARM opened the card earlier today ($opened): not again today"; exit 3; }
[ "$nodev" -lt 2 ] || { echo "REFUSED: the same-day rule: $nodev sessions of arm $ARM that opened no device ran today: a third try is not made"; exit 3; }
echo "same-day: arm $ARM sessions today: $opened that opened the card, $nodev that opened no device"
job_ok_today "$JD" || { echo "REFUSED: E206's dry pass (step 8's job $JD) has not ended rc 0 today"; exit 3; }
echo "dry pass: $JD ended rc 0 today"
fresh "build/q141k/jobs/$JB.out" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JB.out" ||
  { echo "REFUSED: rgm136 was not built today (step 6's job $JB)"; exit 3; }
mkdir -p build/e206 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e206$ARM.T0"
E206_T0=$T0 E206_ARM=$ARM E206_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e206/session_e206.sh > "build/e206/session-$ARM.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e206 arm $ARM T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; session_e206.sh)"
tail -n 6 "build/e206/T$T0-$ARM/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$BOX"
rb_remote launch "$BOX" "launch e206 arm $ARM, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e206 arm $ARM"
for k in rest note hung same-day; do rb_has "^$k: " && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 "^$k: " "$RB_CAP")" >> "$RB_LOG"; done
t0=$(rb_val '^LAUNCHED e206 arm [AB] T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e206-T0-$ARM.txt"
rb_say "e206 arm $ARM launched on $BOX (T0 $t0); wait with s20_wait_e206.sh $ARM (bounded), and read its identity gate, identity read, smoke and stop-path test"
