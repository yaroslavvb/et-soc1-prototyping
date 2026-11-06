#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, ../KIT.md.dated-note-1.md section 6), step 11, v2: E180's card session on aifoundry3, launched detached
# on the box (it returns at once), ONLY after the day's post names aifoundry3 and steps 7-10 (v2) read clean. s11_a3_session_e180.sh (v1,
# which stays as committed) with v2's session, session_e180_v2.sh, and v2's jobs: it refuses unless a3-dry-e180-v2 and a3-build-e180-v2
# (steps 10 and 8, v2) ended rc 0 today. The command is:
#   E180_T0=$(date +%s) E180_PLAN=FULL|TWO E180_LATEST_START=<the round's last start> E180_DEADLINE=<the round's last end>
#     setsid nohup bash tools/claims-v3/e180/session_e180_v2.sh > build/e180/session.out 2>&1 < /dev/null &
# The session runs its own checks, the stop-path test and the smoke with its gate before any pass; its gates refuse with exit 8.
# Refused (10) before any launch: no window, past the last start, fewer seconds left than the plan's budget (FULL 3,000, TWO 1,200:
# E180.md section 7), the v2 dry job or the v2 build job not ended rc 0 today, a dry pass of the runbook still running there, or a card
# session of ours (k6's ours_live counts session_e180_v2.sh and queue_e180_v2.sh by the lab's naming rule).
#
#   bash tools/claims-v3/e180/rb/s11_a3_session_e180_v2.sh [FULL|TWO]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s11_a3_session_v2
plan=${1:-FULL}
need=$(e180_budget "$plan") || rb_die $RB_E_USAGE "E180's plan is FULL or TWO"
rb_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e180)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan"
  rb_guard_text
  cat <<'EOF2'
job_ok_today a3-dry-e180-v2 || { echo "REFUSED: E180's v2 dry pass (s10_a3_dry_e180_v2.sh) has not ended rc 0 today"; exit 3; }
job_ok_today a3-build-e180-v2 || { echo "REFUSED: E180's v2 build and preflight (s08_a3_build_e180_v2.sh) have not ended rc 0 today"; exit 3; }
mkdir -p build/e180 build/q141k
if [ -f build/e180/session.log ]; then wc -l < build/e180/session.log; else echo 0; fi > build/q141k/e180.log-offset
E180_T0=$(date +%s) E180_PLAN="$PLAN" E180_LATEST_START="$LAST_START" E180_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e180/session_e180_v2.sh > build/e180/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e180 (kit v2) $(date '+%F %T %Z') (plan $PLAN; gates: latest start $LAST_START, deadline $LAST_END)"
tail -n +"$(( $(cat build/q141k/e180.log-offset) + 1 ))" build/e180/session.log | tail -n 6 | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e180, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e180
rb_say "e180 (kit v2) launched on aifoundry3; wait with s20_wait_e180_v2.sh (bounded), and read its smoke gate before counting it as started"
