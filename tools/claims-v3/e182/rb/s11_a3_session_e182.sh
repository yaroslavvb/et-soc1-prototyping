#!/usr/bin/env bash
# E182 (Q153, the kit), step 11: E182's card session on aifoundry3, launched detached on the box (it returns at once), ONLY after the day's
# post names aifoundry3 and steps 7-10 read clean. A port of E178's step 11. The command is KIT.md's box step 9:
#   E182_T0=$(date +%s) E182_PLAN=FULL|PASSES E182_TRAINS=yes|no E182_LATEST_START=<the round's last start> E182_DEADLINE=<the last end>
#     setsid nohup bash tools/claims-v3/e182/session_e182.sh > build/e182/session.out 2>&1 < /dev/null &
# The session runs its own checks, the stop-path test and the smoke with its gate before any block; its gates refuse with exit 8. A
# failed train smoke turns FULL into PASSES inside the session (E182.md section 7). Refused (10) before any launch: no window, past the
# last start, fewer seconds left than the plan's budget (FULL 6,000, PASSES 2,400), the dry job not ended rc 0 today, a dry pass of the
# runbook still running there, or a card session of ours.
#
#   bash tools/claims-v3/e182/rb/s11_a3_session_e182.sh [FULL|PASSES] [yes|no]       (the second: the trains; "no" after step 8's build failed)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s11_a3_session
plan=${1:-FULL}
trains=${2:-yes}
need=$(e182_budget "$plan") || rb_die $RB_E_USAGE "E182's plan is FULL or PASSES"
case "$trains" in yes|no) ;; *) rb_die $RB_E_USAGE "the trains are yes or no" ;; esac
rb_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e182)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan; TRAINS=$trains"
  rb_guard_text
  cat <<'EOF2'
job_ok_today a3-dry-e182 || { echo "REFUSED: E182's dry pass (s10_a3_dry_e182.sh) has not ended rc 0 today"; exit 3; }
mkdir -p build/e182 build/q141k
if [ -f build/e182/session.log ]; then wc -l < build/e182/session.log; else echo 0; fi > build/q141k/e182.log-offset
E182_T0=$(date +%s) E182_PLAN="$PLAN" E182_TRAINS="$TRAINS" E182_LATEST_START="$LAST_START" E182_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e182/session_e182.sh > build/e182/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e182 $(date '+%F %T %Z') (plan $PLAN, trains $TRAINS; gates: latest start $LAST_START, deadline $LAST_END)"
tail -n +"$(( $(cat build/q141k/e182.log-offset) + 1 ))" build/e182/session.log | tail -n 6 | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e182, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e182
rb_say "e182 launched on aifoundry3; wait with s20_wait_e182.sh (bounded), and read its smoke gate before counting it as started"
