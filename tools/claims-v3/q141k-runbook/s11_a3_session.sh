#!/usr/bin/env bash
# Q141(k), go checklist step 11: an aifoundry3 card session, launched detached on the box (it returns at once), ONLY after the day's
# post names aifoundry3 (the main session's step 6) and steps 7-10 read clean. The commands are the kits':
#   E166 (README box step 5): E166_T0=$(date +%s) E166_LATEST_START=<the round's last start> E166_END_GATE=<the round's last end>
#     setsid nohup bash tools/claims-v3/e166/session_e166.sh > build/e166/session.out 2>&1 < /dev/null &
#   E163 (README step 10): E163_T0=$(date +%s) E163_PLAN=FULL|TWO|SHORT E163_LATEST_START=<last start> E163_DEADLINE=<last end>
#     setsid nohup bash tools/claims-v3/e163/session_e163.sh > build/e163/session.out 2>&1 < /dev/null &
# Each session runs its own checks, the stop-path tests and the smoke with its gate before any pass; its gates refuse with exit 8
# and open no device. The order (Q141(f)): E166 first, on a rested card; E163 after it, with no rest. If E166's G0 refuses (the room
# above 53.0 C: s20_wait.sh e166 prints G0-REFUSED), E163 goes first, and a later E166 needs at least 40 minutes of rest after
# E163's session end and the earlier smoke moved aside (README.md.dated-note.md: p16601 -> p16601.try1): --later-try does both.
#
#   bash tools/claims-v3/q141k-runbook/s11_a3_session.sh e166 [--later-try]
#   bash tools/claims-v3/q141k-runbook/s11_a3_session.sh e163 [FULL|TWO|SHORT]
#
# Refused (10) before any launch: no window, past the last start, E166 with fewer than 76 minutes left, E163 before E166's session
# end (unless the plan is a, E163 instead of E166), a dry pass of the runbook still running there, or a card session of ours there.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s11_a3_session
run=${1:-}; opt=${2:-}
rb_window
rb_need_start
f=$(rb_file "$run")
case "$run" in
  e166)
    case "$opt" in ""|--later-try) ;; *) rb_die $RB_E_USAGE "e166 takes only --later-try" ;; esac
    [ "$RB_PLAN" = a ] && rb_die $RB_E_USAGE "plan a runs E163 instead of E166 on aifoundry3"
    rb_need_end 4560        # 76 card-minutes from T0, no subset (session_e166.sh's BUDGET_S)
    { rb_prelude aifoundry3
      echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); LATER=$(printf '%q' "$opt")"
      rb_guard_text
      cat <<'EOF'
if [ "$LATER" = --later-try ]; then
  # E166 README.md.dated-note.md: at least 40 minutes of rest after E163's session end, and the earlier smoke moved aside
  last=$(grep 'session end' build/e163/session.log 2>/dev/null | tail -n 1 | cut -d' ' -f1-3)
  [ -n "$last" ] || { echo "REFUSED: no E163 session end in build/e163/session.log to rest from"; exit 3; }
  rest=$(( ($(date +%s) - $(date -d "$last" +%s)) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since E163's session end ($last): E166 needs at least 40"; exit 3; }
  if [ -e build/claims-v3/aifoundry3/e166-smoke/p16601 ]; then
    [ -e build/claims-v3/aifoundry3/e166-smoke/p16601.try1 ] && { echo "REFUSED: p16601.try1 exists already: a third try needs its own amendment"; exit 3; }
    mv build/claims-v3/aifoundry3/e166-smoke/p16601 build/claims-v3/aifoundry3/e166-smoke/p16601.try1 && echo "moved the earlier smoke aside: p16601 -> p16601.try1"
  fi
fi
mkdir -p build/e166
if [ -f build/e166/session.log ]; then wc -l < build/e166/session.log; else echo 0; fi > build/q141k/e166.log-offset
E166_T0=$(date +%s) E166_LATEST_START="$LAST_START" E166_END_GATE="$LAST_END" setsid nohup bash tools/claims-v3/e166/session_e166.sh > build/e166/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e166 $(date '+%F %T %Z') (gates: latest start $LAST_START, end gate $LAST_END)"
tail -n +"$(( $(cat build/q141k/e166.log-offset) + 1 ))" build/e166/session.log | tail -n 6 | cut -c1-300
EOF
    } > "$f"
    ;;
  e163)
    plan=${opt:-FULL}
    case "$plan" in FULL|TWO|SHORT) ;; *) rb_die $RB_E_USAGE "E163's plan is FULL, TWO or SHORT" ;; esac
    { rb_prelude aifoundry3
      echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan; DAYPLAN=$RB_PLAN"
      rb_guard_text
      cat <<'EOF'
if [ "$DAYPLAN" != a ]; then
  # Q141(f)'s order: E166 first on a rested card, then E163 (if E166's G0 refused, its session still ended: E163 goes next)
  off=$(cat build/q141k/e166.log-offset 2>/dev/null) || { echo "REFUSED: E166 has not run today: it goes first on aifoundry3 (plan $DAYPLAN)"; exit 3; }
  tail -n +"$((off + 1))" build/e166/session.log 2>/dev/null | grep -q 'session end' || { echo "REFUSED: E166's session has not ended"; exit 3; }
fi
mkdir -p build/e163
if [ -f build/e163/session.log ]; then wc -l < build/e163/session.log; else echo 0; fi > build/q141k/e163.log-offset
E163_T0=$(date +%s) E163_PLAN="$PLAN" E163_LATEST_START="$LAST_START" E163_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e163/session_e163.sh > build/e163/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e163 $(date '+%F %T %Z') (plan $PLAN; gates: latest start $LAST_START, deadline $LAST_END)"
tail -n +"$(( $(cat build/q141k/e163.log-offset) + 1 ))" build/e163/session.log | tail -n 6 | cut -c1-300
EOF
    } > "$f"
    ;;
  *) rb_die $RB_E_USAGE "usage: s11_a3_session.sh e166 [--later-try] | e163 [FULL|TWO|SHORT]" ;;
esac
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch $run, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "$run"
rb_say "$run launched on aifoundry3; wait with s20_wait.sh $run (bounded), and read its smoke gate before counting it as started"
