#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum), the box step "the session" v2 (this file is
# s11 v2), for one arm: rb/s11_session_e190.sh (the kit, unchanged beside it) launching session_e190_v2.sh (run_e190_v2.py: the identity
# gate, the identity read, the host watch, the sampler's freshness), detached on the arm's box (it returns at once), ONLY after steps 4-8
# v2 read clean for that arm: the window rule, the last start, the session's cap before the last end (E190_BUDGET_S: 2,700 s), k6's guard
# (no dry pass running, no card session of ours on the box: rb_guard_text, which also reads the box's identity by continuity), THE REST
# RULE (rb/rest_rule_e190.sh, unchanged), today's dry pass v2 (the arm's job a?-dry-e190v2 ended rc 0 today) and today's build v2
# (RB_OUT/e190-built-v2-<arm>.txt; the box's job a?-build-e190v2 read RGM-BUILT today), then session_e190_v2.sh detached with the T0 written
# on the box (build/q141k/e190<arm>.T0) and in RB_OUT (e190-T0-<arm>.txt), which steps 10 v2 and 11 v2 read.
#   bash tools/claims-v3/e190/rb/s11_session_e190_v2.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190_v2.sh"
rb_init s11_session_v2
e190_arm "${1:-}"
e190_jobs_v2 "$ARM"
e190_window
rb_need_start
rb_need_end "$E190_BUDGET_S"
b=$(e190_built_v2 "$ARM")
[ -n "${RB_DRY:-}" ] && b=${b:-rgm-v2}
[ "$b" = rgm-v2 ] || rb_die $RB_E_USAGE "rgm136 was not built today by the build v2 for arm $ARM (RB_OUT/e190-built-v2-$ARM.txt, step 6 v2's wait): run step 6 v2 first"
f=$(rb_file e190)
{ rb_prelude "$BOX"
  echo "ARM=$ARM; JD=$JOB_DRY; JB=$JOB_BUILD; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E190_DIR/rest_rule_e190.sh"
  cat <<'EOF2'
job_ok_today "$JD" || { echo "REFUSED: E190's dry pass v2 (step 8 v2's job $JD) has not ended rc 0 today"; exit 3; }
echo "dry pass v2: $JD ended rc 0 today"
fresh "build/q141k/jobs/$JB.out" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JB.out" ||
  { echo "REFUSED: rgm136 was not built today by the build v2 (step 6 v2's job $JB)"; exit 3; }
mkdir -p build/e190 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e190$ARM.T0"
E190_T0=$T0 E190_ARM=$ARM E190_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e190/session_e190_v2.sh > "build/e190/session-$ARM.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e190 arm $ARM T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; session_e190_v2.sh)"
tail -n 6 "build/e190/T$T0-$ARM/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$BOX"
rb_remote launch "$BOX" "launch e190 arm $ARM (v2), detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e190 arm $ARM"
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e190 arm [AB] T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e190-T0-$ARM.txt"
rb_say "e190 arm $ARM (v2) launched on $BOX (T0 $t0); wait with s20_wait_e190_v2.sh $ARM (bounded), and read its identity gate, identity read, stop-path test and smoke gate"
