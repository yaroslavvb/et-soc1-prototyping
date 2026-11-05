#!/usr/bin/env bash
# Q142(k6), step 11: E171's card session on aifoundry3, launched detached on the box (it returns at once), ONLY after the day's post
# names aifoundry3 and steps 7-10 read clean. The command is E171's README step 10:
#   E171_T0=$(date +%s) E171_PLAN=FULL|TWO|SHORT E171_LATEST_START=<the round's last start> E171_DEADLINE=<the round's last end>
#     setsid nohup bash tools/claims-v3/e171/session_e171.sh > build/e171/session.out 2>&1 < /dev/null &
# The session runs its own checks, the stop-path test and the smoke with its gate before any pass; its gates refuse with exit 8.
# Refused (10) before any launch: no window, past the last start, fewer seconds left than the plan's budget (FULL 4,200, TWO 2,280,
# SHORT 1,800: E171.md), the dry job not ended rc 0 today, a dry pass of the runbook still running there, or a card session of ours.
#
#   bash tools/claims-v3/q141k-runbook/k6/s11_a3_session_k6.sh [FULL|TWO|SHORT]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s11_a3_session
plan=${1:-FULL}
case "$plan" in FULL) need=4200 ;; TWO) need=2280 ;; SHORT) need=1800 ;; *) rb_die $RB_E_USAGE "E171's plan is FULL, TWO or SHORT" ;; esac
rb_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e171)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan"
  rb_guard_text
  cat <<'EOF'
job_ok_today a3-dry-e171 || { echo "REFUSED: E171's dry pass (s10_a3_dry_k6.sh) has not ended rc 0 today"; exit 3; }
mkdir -p build/e171
if [ -f build/e171/session.log ]; then wc -l < build/e171/session.log; else echo 0; fi > build/q141k/e171.log-offset
E171_T0=$(date +%s) E171_PLAN="$PLAN" E171_LATEST_START="$LAST_START" E171_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e171/session_e171.sh > build/e171/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e171 $(date '+%F %T %Z') (plan $PLAN; gates: latest start $LAST_START, deadline $LAST_END)"
tail -n +"$(( $(cat build/q141k/e171.log-offset) + 1 ))" build/e171/session.log | tail -n 6 | cut -c1-300
EOF
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e171, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e171
rb_say "e171 launched on aifoundry3; wait with s20_wait_k6.sh e171 (bounded), and read its smoke gate before counting it as started"
