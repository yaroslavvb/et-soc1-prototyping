#!/usr/bin/env bash
# E181, step 11: E181's card session on aifoundry3, launched detached on the box (it returns at once), ONLY after the day's post names
# aifoundry3 and steps 7-10 read clean. The command is E181's README box step 5:
#   E181_T0=$(date +%s) E181_LATEST_START=<the last start> E181_END_GATE=<the last end>
#     setsid nohup bash tools/claims-v3/e181/session_e181.sh > build/e181/session.out 2>&1 < /dev/null &
# The session runs its own checks, A6-1's floor, the smoke with its five stop tests and its gate before the measured pass; its gates refuse
# with exit 8. ../../q143k-runbook/s11_a3_session_q143k.sh (92a1b27f) ported, with E176's runbook note 2 section 1 fixed and A7-4 carried:
#   - THE REST RULE reads every session log of ours on this card (build/e171, e176, e178, e180, e181/session.log), any day, and takes the
#     last session end of a REAL session: a session block (from its "session start" line to its "session end") whose lines carry "DRY" or
#     "DESK:" is a dry session and is skipped (E176's log holds one, its lines 1-78); E181's own dry sessions write session-dry.log instead,
#     so they never reach it. Under 40 minutes since that end: refused (the runbook's gate, kept by A6 and A7).
#   - A7-4's plan: under an hour since that end, refused unless --under-an-hour is given (logged as a departure from the plan).
#   - A6's and A7's cool-hour plan: at or after 12:00 PST (the Intel's clock, Pacific), refused unless --after-noon is given (logged).
# Refused (10) before any launch also on: no window, past the last start, fewer than 76 minutes left (session_e181.sh's budget, no subset),
# the dry job not ended rc 0 today, a dry pass of the runbook or a card session of ours on the box, or an earlier E181 smoke on the box
# without --later-try (its later-try rule kept: the smoke moved aside once, p18101 -> p18101.try1).
#
#   bash tools/claims-v3/e181/rb/s11_a3_launch_e181.sh [--later-try] [--under-an-hour] [--after-noon]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
rb_init s11_a3_launch
LATER=""; HOUR=""; NOON=""
for x in "$@"; do
  case "$x" in --later-try) LATER=$x ;; --under-an-hour) HOUR=$x ;; --after-noon) NOON=$x ;;
    *) rb_die $RB_E_USAGE "usage: s11_a3_launch_e181.sh [--later-try] [--under-an-hour] [--after-noon]" ;; esac
done
rb_window
rb_need_start
rb_need_end 4560        # 76 card-minutes from T0, no subset (session_e181.sh's BUDGET_S)
hm=$(TZ=America/Los_Angeles date +%H%M)
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${RB_NOW_HM:-}" ] && hm=$RB_NOW_HM            # the desk test's clock, read only with RB_DESKTEST=1
if [ -z "${RB_DRY:-}" ] && [ "$((10#$hm))" -ge 1200 ]; then
  [ -n "$NOON" ] || rb_die $RB_E_USAGE "it is $hm PST: A6's and A7's cool-hour plan asks for a launch before 12:00 PST; to launch anyway, run again with --after-noon (a stated departure from the plan)"
  echo "$(date '+%F %T %Z') step=$RB_STEP departure: --after-noon at $hm PST (A6/A7's cool-hour plan asks for a launch before 12:00 PST)" >> "$RB_LOG"
fi
f=$(rb_file e181)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); LATER=$(printf '%q' "$LATER"); HOUR=$(printf '%q' "$HOUR")"
  rb_guard_text
  cat <<'EOF2'
job_ok_today a3-dry-e181 || { echo "REFUSED: E181's dry pass (s10_a3_dry_e181.sh) has not ended rc 0 today"; exit 3; }
SM=build/claims-v3/aifoundry3/e181-smoke
if [ "$LATER" != --later-try ]; then
  [ -e "$SM/p18101" ] && { echo "REFUSED: an earlier E181 smoke is on the box ($SM/p18101): this is a later try: run s11_a3_launch_e181.sh --later-try"; exit 3; }
  [ -e "$SM/p18101.try1" ] && { echo "REFUSED: an earlier try's smoke was moved aside ($SM/p18101.try1): a further try needs its own amendment"; exit 3; }
fi
# the card rested: the last session end of a REAL session of ours on this card, any day (dry sessions skipped)
last=""; lastw=""
for w in e171 e176 e178 e180 e181; do
  l=$(awk '/session start/ {dry = 0} /DRY|DESK:/ {dry = 1} /session end$/ && !dry && $0 !~ /DRY session end/ {e = $1 " " $2 " " $3} END {print e}' build/$w/session.log 2>/dev/null)
  [ -n "$l" ] || continue
  t=$(date -d "$l" +%s 2>/dev/null) || continue
  if [ -z "$last" ] || [ "$t" -gt "$(date -d "$last" +%s)" ]; then last=$l; lastw=E${w#e}; fi
done
if [ -n "$last" ]; then
  rest=$(( ($(date +%s) - $(date -d "$last" +%s)) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's session end ($last): E181 needs a rested card, at least 40 (the runbook's gate)"; exit 3; }
  if [ "$rest" -lt 60 ]; then
    [ "$HOUR" = --under-an-hour ] || { echo "REFUSED: $rest minutes since $lastw's session end ($last): A7-4's plan asks for an hour; to launch anyway, run again with --under-an-hour"; exit 3; }
    echo "departure: --under-an-hour: $rest minutes since $lastw's session end (A7-4's plan asks for an hour; the gate's 40 holds)"
  fi
  echo "rest: $rest minutes since $lastw's session end ($last; dry sessions skipped)"
else
  echo "rest: no real session end of ours in build/e171, e176, e178, e180 or e181/session.log"
fi
if [ "$LATER" = --later-try ] && [ -e "$SM/p18101" ]; then
  [ -e "$SM/p18101.try1" ] && { echo "REFUSED: p18101.try1 exists already: a third try needs its own amendment"; exit 3; }
  mv "$SM/p18101" "$SM/p18101.try1" && echo "moved the earlier smoke aside: p18101 -> p18101.try1"
fi
mkdir -p build/e181 build/q141k
if [ -f build/e181/session.log ]; then wc -l < build/e181/session.log; else echo 0; fi > build/q141k/e181.log-offset
E181_T0=$(date +%s) E181_LATEST_START="$LAST_START" E181_END_GATE="$LAST_END" setsid nohup bash tools/claims-v3/e181/session_e181.sh > build/e181/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e181 $(date '+%F %T %Z') (gates: latest start $LAST_START, end gate $LAST_END)"
tail -n +"$(( $(cat build/q141k/e181.log-offset) + 1 ))" build/e181/session.log 2>/dev/null | tail -n 6 | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e181, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e181
rb_has '^departure: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^departure: ' "$RB_CAP")" >> "$RB_LOG"
rb_say "e181 launched on aifoundry3; wait with s20_wait_e181.sh (bounded), and read its smoke gate before counting it as started"
