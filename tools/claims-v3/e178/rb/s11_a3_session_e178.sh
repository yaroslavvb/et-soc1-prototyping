#!/usr/bin/env bash
# E178 (Q146, the kit), step 11: E178's card session on aifoundry3, launched detached on the box (it returns at once), ONLY after the day's
# post names aifoundry3 and steps 7-10 read clean. The command is KIT.md's box step 10:
#   E178_T0=$(date +%s) E178_PLAN=FULL|TWO E178_LATEST_START=<the round's last start> E178_DEADLINE=<the round's last end>
#     setsid nohup bash tools/claims-v3/e178/session_e178.sh > build/e178/session.out 2>&1 < /dev/null &
# The session runs its own checks, the stop-path test and the smoke with its gate before any pass; its gates refuse with exit 8.
# Refused (10) before any launch: no window, past the last start, fewer seconds left than the plan's budget (FULL 3,600, TWO 1,920:
# E178.md section 7), the dry job not ended rc 0 today, a dry pass of the runbook still running there, or a card session of ours.
# A port of ../../q141k-runbook/k6/s11_a3_session_k6.sh.
#
#   bash tools/claims-v3/e178/rb/s11_a3_session_e178.sh [FULL|TWO]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e178.sh"
rb_init s11_a3_session
plan=${1:-FULL}
need=$(e178_budget "$plan") || rb_die $RB_E_USAGE "E178's plan is FULL or TWO"
rb_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e178)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan"
  rb_guard_text
  cat <<'EOF2'
job_ok_today a3-dry-e178 || { echo "REFUSED: E178's dry pass (s10_a3_dry_e178.sh) has not ended rc 0 today"; exit 3; }
mkdir -p build/e178 build/q141k
if [ -f build/e178/session.log ]; then wc -l < build/e178/session.log; else echo 0; fi > build/q141k/e178.log-offset
E178_T0=$(date +%s) E178_PLAN="$PLAN" E178_LATEST_START="$LAST_START" E178_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e178/session_e178.sh > build/e178/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e178 $(date '+%F %T %Z') (plan $PLAN; gates: latest start $LAST_START, deadline $LAST_END)"
tail -n +"$(( $(cat build/q141k/e178.log-offset) + 1 ))" build/e178/session.log | tail -n 6 | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e178, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e178
rb_say "e178 launched on aifoundry3; wait with s20_wait_e178.sh (bounded), and read its smoke gate before counting it as started"
