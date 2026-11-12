#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): KIT.md box step 9 v2, the session's launch.
# It is rb/s11_a3_session_e183.sh (cc597bf2, which stays as committed) with two changes, each marked "note 4":
#   - THE REST RULE (rb/rest_rule_e183.sh, sent to the box after k6's guard and before the launch): no E183 session starts within 40 minutes
#     of the end of our last real session on aifoundry3, read from every session log of ours there in every form (E184's session-<arm>-t<T0>,
#     E185's and E186's T<T0>/session.log, E183's own session-t<T0>, and the plain session.log); under 40 minutes it is REFUSED (10). v1 had
#     no rest rule (k6's guard refuses only beside a live session of ours), so it read no session log at all;
#   - it launches session_e183_v2.sh (block v2 and queue v2), whose files are named as v1's by T0, so step 10 (s20_wait_e183.sh) and step
#     11 v2 (s22_collect_e183_v2.sh) read it unchanged; its name in the runbook's log is s11_a3_session_v2_e183.
# Today's good build (a3-build-e183 with TRAIN-HOST-BUILT) and dry pass (a3-dry-e183) are read as v1 reads them: run them by step 6 v2 and
# step 8 v2.
#   bash tools/claims-v3/e183/rb/s11_a3_session_e183_v2.sh FULL|SHORT
# v1's words follow:
# E183 (Q155, the kit), KIT.md box step 9: the session, launched detached on aifoundry3 (E180's step 9 v2 with E184 v2's T0 rule): the
# window's gates (no session after the last start; the plan's cap before the last end), k6's guard (never during a runbook job, never beside
# a session of ours), today's good build and dry pass; then T0 = the launch's epoch second, written on the box (build/q141k/e183.t0) and in
# RB_OUT (t0-e183.txt), and every file the session writes carries it.
#   bash tools/claims-v3/e183/rb/s11_a3_session_e183.sh FULL|SHORT
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s11_a3_session_v2
plan=${1:-FULL}
need=$(e183_budget "$plan") || rb_die $RB_E_USAGE "E183's plan is FULL or SHORT"
rb_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e183)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan"
  rb_guard_text
  cat "$RB_E183_DIR/rest_rule_e183.sh"     # note 4: the rest rule, before the launch
  cat <<'EOF2'
job_ok_today a3-dry-e183 || { echo "REFUSED: E183's dry pass (s10_a3_dry_e183.sh) has not ended rc 0 today"; exit 3; }
{ job_ok_today a3-build-e183 && grep -q '^TRAIN-HOST-BUILT rc=0' build/q141k/jobs/a3-build-e183.out 2>/dev/null; } ||
  { echo "REFUSED: E183's train host (s08_a3_build_e183.sh) was not built today"; exit 3; }
mkdir -p build/e183 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e183.t0
E183_T0=$T0 E183_PLAN="$PLAN" E183_LATEST_START="$LAST_START" E183_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e183/session_e183_v2.sh > "build/e183/session-t$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e183 T0=$T0 $(date '+%F %T %Z') (plan $PLAN; gates: latest start $LAST_START, deadline $LAST_END)"
head -n 6 "build/e183/session-t$T0.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e183, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e183
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"     # note 4
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e183 T0=([0-9]+) .*$')
case "$t0" in ''|*[!0-9]*) rb_die $RB_E_FAIL "the launch printed no T0 (read '$t0'): read the output above" ;; esac
echo "$t0" > "$RB_OUT/t0-e183.txt"
rb_say "e183 launched on aifoundry3, T0 $t0 (plan $plan); wait with s20_wait_e183.sh (bounded), and read its smoke gate before counting it as started"
