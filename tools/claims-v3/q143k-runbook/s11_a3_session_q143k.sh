#!/usr/bin/env bash
# Q143(k), step 11: E176's card session on aifoundry3, launched detached on the box (it returns at once), ONLY after the day's post names
# aifoundry3 and steps 7-10 read clean. The command is E176's README box step 5:
#   E176_T0=$(date +%s) E176_LATEST_START=<the last start> E176_END_GATE=<the last end>
#     setsid nohup bash tools/claims-v3/e176/session_e176.sh > build/e176/session.out 2>&1 < /dev/null &
# The session runs its own checks, the smoke with its five stop tests and its gate before the measured pass; its gates refuse with exit 8.
# v3.1's s11_a3_session.sh e166 route, ported (its later-try rule kept): refused (10) before any launch on: no window, past the last start,
# fewer than 76 minutes left (session_e176.sh's budget, no subset), the dry job not ended rc 0 today, a dry pass of the runbook or a card
# session of ours on the box (E171's among them), an earlier E176 smoke on the box without --later-try, or less than 40 minutes since the
# card's last session end of ours today (E171's or E176's; E176's README: a rested card after E171).
#
#   bash tools/claims-v3/q143k-runbook/s11_a3_session_q143k.sh [--later-try]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s11_a3_session
opt=${1:-}
case "$opt" in ""|--later-try) ;; *) rb_die $RB_E_USAGE "usage: s11_a3_session_q143k.sh [--later-try]" ;; esac
rb_window
rb_need_start
rb_need_end 4560        # 76 card-minutes from T0, no subset (session_e176.sh's BUDGET_S)
f=$(rb_file e176)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); LATER=$(printf '%q' "$opt")"
  rb_guard_text
  cat <<'EOF2'
job_ok_today a3-dry-e176 || { echo "REFUSED: E176's dry pass (s10_a3_dry_q143k.sh) has not ended rc 0 today"; exit 3; }
SM=build/claims-v3/aifoundry3/e176-smoke
if [ "$LATER" != --later-try ]; then
  [ -e "$SM/p17601" ] && { echo "REFUSED: an earlier E176 smoke is on the box ($SM/p17601): this is a later try: run s11_a3_session_q143k.sh --later-try"; exit 3; }
  [ -e "$SM/p17601.try1" ] && { echo "REFUSED: an earlier try's smoke was moved aside ($SM/p17601.try1): a further try needs its own amendment"; exit 3; }
fi
# the card rested: at least 40 minutes since the last session end of ours on this card today (E171's or E176's own)
last=""; lastw=""
for w in e171 e176; do
  l=$(grep 'session end' build/$w/session.log 2>/dev/null | tail -n 1 | cut -d' ' -f1-3)
  [ -n "$l" ] || continue
  [ "$(TZ=America/Los_Angeles date -d "$l" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] || continue
  if [ -z "$last" ] || [ "$(date -d "$l" +%s)" -gt "$(date -d "$last" +%s)" ]; then last=$l; lastw=E${w#e}; fi
done
if [ -n "$last" ]; then
  rest=$(( ($(date +%s) - $(date -d "$last" +%s)) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's session end ($last): E176 needs a rested card, at least 40"; exit 3; }
  echo "rest: $rest minutes since $lastw's session end"
fi
if [ "$LATER" = --later-try ] && [ -e "$SM/p17601" ]; then
  [ -e "$SM/p17601.try1" ] && { echo "REFUSED: p17601.try1 exists already: a third try needs its own amendment"; exit 3; }
  mv "$SM/p17601" "$SM/p17601.try1" && echo "moved the earlier smoke aside: p17601 -> p17601.try1"
fi
mkdir -p build/e176
if [ -f build/e176/session.log ]; then wc -l < build/e176/session.log; else echo 0; fi > build/q141k/e176.log-offset
E176_T0=$(date +%s) E176_LATEST_START="$LAST_START" E176_END_GATE="$LAST_END" setsid nohup bash tools/claims-v3/e176/session_e176.sh > build/e176/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e176 $(date '+%F %T %Z') (gates: latest start $LAST_START, end gate $LAST_END)"
tail -n +"$(( $(cat build/q141k/e176.log-offset) + 1 ))" build/e176/session.log | tail -n 6 | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e176, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e176
rb_say "e176 launched on aifoundry3; wait with s20_wait_q143k.sh (bounded), and read its smoke gate before counting it as started"
