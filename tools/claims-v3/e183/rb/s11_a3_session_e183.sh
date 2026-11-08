#!/usr/bin/env bash
# E183 (Q155, the kit), KIT.md box step 9: the session, launched detached on aifoundry3 (E180's step 9 v2 with E184 v2's T0 rule): the
# window's gates (no session after the last start; the plan's cap before the last end), k6's guard (never during a runbook job, never beside
# a session of ours), today's good build and dry pass; then T0 = the launch's epoch second, written on the box (build/q141k/e183.t0) and in
# RB_OUT (t0-e183.txt), and every file the session writes carries it.
#   bash tools/claims-v3/e183/rb/s11_a3_session_e183.sh FULL|SHORT
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s11_a3_session
plan=${1:-FULL}
need=$(e183_budget "$plan") || rb_die $RB_E_USAGE "E183's plan is FULL or SHORT"
rb_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e183)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan"
  rb_guard_text
  cat <<'EOF2'
job_ok_today a3-dry-e183 || { echo "REFUSED: E183's dry pass (s10_a3_dry_e183.sh) has not ended rc 0 today"; exit 3; }
{ job_ok_today a3-build-e183 && grep -q '^TRAIN-HOST-BUILT rc=0' build/q141k/jobs/a3-build-e183.out 2>/dev/null; } ||
  { echo "REFUSED: E183's train host (s08_a3_build_e183.sh) was not built today"; exit 3; }
mkdir -p build/e183 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e183.t0
E183_T0=$T0 E183_PLAN="$PLAN" E183_LATEST_START="$LAST_START" E183_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e183/session_e183.sh > "build/e183/session-t$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e183 T0=$T0 $(date '+%F %T %Z') (plan $PLAN; gates: latest start $LAST_START, deadline $LAST_END)"
head -n 6 "build/e183/session-t$T0.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e183, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e183
t0=$(rb_val '^LAUNCHED e183 T0=([0-9]+) .*$')
case "$t0" in ''|*[!0-9]*) rb_die $RB_E_FAIL "the launch printed no T0 (read '$t0'): read the output above" ;; esac
echo "$t0" > "$RB_OUT/t0-e183.txt"
rb_say "e183 launched on aifoundry3, T0 $t0 (plan $plan); wait with s20_wait_e183.sh (bounded), and read its smoke gate before counting it as started"
