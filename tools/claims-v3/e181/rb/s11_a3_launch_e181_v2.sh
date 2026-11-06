#!/usr/bin/env bash
# E181, step 11 v2: E181's card session on aifoundry3, launched detached on the box (it returns at once), ONLY after the day's post names
# aifoundry3, steps 7-10 read clean and step 12 has read the host's start window. It is s11_a3_launch_e181.sh (33cdccf6, which stays as
# committed) with ONE change, the rest rule (the E181 kit verifier's fault 7, Fri 6 Nov 2026; the kit's README.md.dated-note-1.md):
#   - v1 counted only a block's "session end" line, so a real session killed before its last line was invisible to it, and a later try
#     counted its rest from an earlier end. v2 reads every session log of ours on this card (build/e171, e176, e178, e180, e181/session.log),
#     any day, block by block (a block runs from a "session start" line to the next):
#       a block whose lines carry "DRY" or "DESK:" is a dry session: skipped (v1's rule);
#       a block that says "no device opened" ended at a session gate before any device opened: skipped (it never touched the card);
#       any other block is a real session: it ended at its "session end" line; WITHOUT one, at its last timestamped line, or, for the log's
#       final block, at the later of that line and the log's last write (its mtime): "counted as ended at its last line".
#     The rest is counted from the latest such end over every log. Under 40 minutes: refused (the runbook's gate, kept by A6 and A7). Under
#     an hour: refused unless --under-an-hour (A7-4's plan; a logged departure). A block counted without its end is named in the output.
# Everything else is v1's, line for line: the command is E181's README box step 5,
#   E181_T0=$(date +%s) E181_LATEST_START=<the last start> E181_END_GATE=<the last end>
#     setsid nohup bash tools/claims-v3/e181/session_e181.sh > build/e181/session.out 2>&1 < /dev/null &
# A6's and A7's cool-hour plan (at or after 12:00 PST refused unless --after-noon, logged); refused (10) before any launch also on: no
# window, past the last start, fewer than 76 minutes left (session_e181.sh's budget, no subset), the dry job not ended rc 0 today, a dry pass
# of the runbook or a card session of ours on the box, or an earlier E181 smoke on the box without --later-try (the smoke moved aside once,
# p18101 -> p18101.try1).
#
#   bash tools/claims-v3/e181/rb/s11_a3_launch_e181_v2.sh [--later-try] [--under-an-hour] [--after-noon]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
rb_init s11_a3_launch_v2
LATER=""; HOUR=""; NOON=""
for x in "$@"; do
  case "$x" in --later-try) LATER=$x ;; --under-an-hour) HOUR=$x ;; --after-noon) NOON=$x ;;
    *) rb_die $RB_E_USAGE "usage: s11_a3_launch_e181_v2.sh [--later-try] [--under-an-hour] [--after-noon]" ;; esac
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
  [ -e "$SM/p18101" ] && { echo "REFUSED: an earlier E181 smoke is on the box ($SM/p18101): this is a later try: run s11_a3_launch_e181_v2.sh --later-try"; exit 3; }
  [ -e "$SM/p18101.try1" ] && { echo "REFUSED: an earlier try's smoke was moved aside ($SM/p18101.try1): a further try needs its own amendment"; exit 3; }
fi
# the card rested (v2): the latest end of a REAL session of ours on this card, any day; dry blocks and blocks that opened no device skipped;
# a real block without its "session end" counted as ended at its last timestamped line (the log's final block: or its last write, the later)
last=""; lastw=""; lastt=0; lastkind=""
for w in e171 e176 e178 e180 e181; do
  L=build/$w/session.log
  [ -f "$L" ] || continue
  mt=$(date -r "$L" +%s 2>/dev/null || echo 0)
  ends=$(awk '
    function flush(final) {
      if (inblk && !dry && !nodev) {
        if (endts != "") print "END 0 " endts
        else if (lastts != "") print "NOEND " final " " lastts
      }
    }
    /session start/ { flush(0); inblk = 1; dry = 0; nodev = 0; endts = ""; lastts = "" }
    inblk && /DRY|DESK:/ { dry = 1 }
    inblk && /no device opened/ { nodev = 1 }
    inblk && /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [A-Z][A-Z]* / { lastts = $1 " " $2 " " $3 }
    inblk && /session end$/ && $0 !~ /DRY session end/ { endts = $1 " " $2 " " $3 }
    END { flush(1) }' "$L" 2>/dev/null)
  while read -r kind fin d1 d2 d3; do
    [ -n "$kind" ] || continue
    t=$(date -d "$d1 $d2 $d3" +%s 2>/dev/null) || continue
    ts="$d1 $d2 $d3"
    if [ "$kind" = NOEND ] && [ "$fin" = 1 ] && [ "$mt" -gt "$t" ]; then t=$mt; ts="$(date -d @"$mt" '+%F %T %Z') (the log's last write)"; fi
    if [ -z "$last" ] || [ "$t" -gt "$lastt" ]; then last=$ts; lastt=$t; lastw=E${w#e}; lastkind=$kind; fi
  done <<< "$ends"
done
if [ -n "$last" ]; then
  what="session end"; [ "$lastkind" = NOEND ] && what="last real session line (its block has no session end: counted as ended at its last line)"
  [ "$lastkind" = NOEND ] && echo "note: $lastw's last real session block has no 'session end': counted as ended at $last"
  rest=$(( ($(date +%s) - lastt) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E181 needs a rested card, at least 40 (the runbook's gate)"; exit 3; }
  if [ "$rest" -lt 60 ]; then
    [ "$HOUR" = --under-an-hour ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): A7-4's plan asks for an hour; to launch anyway, run again with --under-an-hour"; exit 3; }
    echo "departure: --under-an-hour: $rest minutes since $lastw's $what (A7-4's plan asks for an hour; the gate's 40 holds)"
  fi
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped)"
else
  echo "rest: no real session of ours in build/e171, e176, e178, e180 or e181/session.log"
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
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
rb_say "e181 launched on aifoundry3; wait with s20_wait_e181.sh (bounded), then step 12's end window (s12_a3_host_e181.sh end), then collect with s22_collect_e181_v2.sh"
