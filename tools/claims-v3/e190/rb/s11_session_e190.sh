#!/usr/bin/env bash
# E190 (Q169, the kit), the box step "the session" (this file is s11), for one arm: E190's card session on the arm's box, launched detached
# there (it returns at once), ONLY after steps 4-8 read clean for that arm. E189's step 9's form: the window rule (written today for E190),
# the last start, the session's cap before the last end (E190_BUDGET_S: 2,700 s), k6's guard (no dry pass running, no card session of ours
# on the box: rb_guard_text, which also reads the box's identity by continuity: booted before its firmware read of record), THE REST RULE
# (rb/rest_rule_e190.sh: 40 minutes after our last real session on the box, every session-log form of ours), today's dry pass (the arm's
# job ended rc 0 today) and today's build (RB_OUT/e190-built-<arm>.txt; the box's job read RGM-BUILT today), then session_e190.sh detached
# with the T0 written on the box (build/q141k/e190<arm>.T0) and in RB_OUT (e190-T0-<arm>.txt), which steps 10 and 11 read.
#   bash tools/claims-v3/e190/rb/s11_session_e190.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190.sh"
rb_init s11_session
e190_arm "${1:-}"
J=$([ "$ARM" = A ] && echo a2 || echo a1)
e190_window
rb_need_start
rb_need_end "$E190_BUDGET_S"
b=$(e190_built "$ARM")
[ -n "${RB_DRY:-}" ] && b=${b:-rgm}
[ "$b" = rgm ] || rb_die $RB_E_USAGE "rgm136 was not built today for arm $ARM (RB_OUT/e190-built-$ARM.txt, step 6's wait): run step 6 first"
f=$(rb_file e190)
{ rb_prelude "$BOX"
  echo "ARM=$ARM; J=$J; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E190_DIR/rest_rule_e190.sh"
  cat <<'EOF2'
job_ok_today "$J-dry-e190" || { echo "REFUSED: E190's dry pass (step 8's job $J-dry-e190) has not ended rc 0 today"; exit 3; }
echo "dry pass: $J-dry-e190 ended rc 0 today"
fresh "build/q141k/jobs/$J-build-e190.out" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$J-build-e190.out" ||
  { echo "REFUSED: rgm136 was not built today (step 6's job $J-build-e190)"; exit 3; }
mkdir -p build/e190 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e190$ARM.T0"
E190_T0=$T0 E190_ARM=$ARM E190_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e190/session_e190.sh > "build/e190/session-$ARM.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e190 arm $ARM T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END)"
tail -n 6 "build/e190/T$T0-$ARM/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$BOX"
rb_remote launch "$BOX" "launch e190 arm $ARM, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e190 arm $ARM"
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e190 arm [AB] T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e190-T0-$ARM.txt"
rb_say "e190 arm $ARM launched on $BOX (T0 $t0); wait with s20_wait_e190.sh $ARM (bounded), and read its stop-path test and smoke gate"
