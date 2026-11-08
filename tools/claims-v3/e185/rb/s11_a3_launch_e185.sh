#!/usr/bin/env bash
# E185, step 11 v2: E185's card session on aifoundry3, launched detached on the box (it returns at once), ONLY after the day's post names
# aifoundry3, steps 7-10 read clean and step 12 has read the host's start window. It is s11_a3_launch_e185.sh (33cdccf6, which stays as
# committed) with ONE change, the rest rule (the E185 kit verifier's fault 7, Fri 6 Nov 2026; the kit's README.md.dated-note-1.md):
#   - v1 counted only a block's "session end" line, so a real session killed before its last line was invisible to it, and a later try
#     counted its rest from an earlier end. It reads every session log of ours on this card (e185: build/e17x and e18x/session.log,
#     E184's build/e184/session-*.log and E185's T0-named build/e185/T*/session.log; dry logs skipped by name),
#     any day, block by block (a block runs from a "session start" line to the next):
#       a block whose lines carry "DRY" or "DESK:" is a dry session: skipped (v1's rule);
#       a block that says "no device opened" ended at a session gate before any device opened: skipped (it never touched the card);
#       any other block is a real session: it ended at its "session end" line; WITHOUT one, at its last timestamped line, or, for the log's
#       final block, at the later of that line and the log's last write (its mtime): "counted as ended at its last line".
#     The rest is counted from the latest such end over every log. Under 40 minutes: refused (the runbook's gate, kept by A6 and A7). Under
#     an hour: refused unless --under-an-hour (A7-4's plan; a logged departure). A block counted without its end is named in the output.
# Everything else is v1's, line for line: the command is E185's README box step 5,
#   E185_T0=$(date +%s) E185_LATEST_START=<the last start> E185_END_GATE=<the last end>
#     setsid nohup bash tools/claims-v3/e185/session_e185.sh > build/e185/session-$T0.out 2>&1 < /dev/null &
# A6's and A7's cool-hour plan (at or after 12:00 PST refused unless --after-noon, logged); refused (10) before any launch also on: no
# window, past the last start, fewer than 105 minutes left (session_e185.sh's budget, no subset), the dry job not ended rc 0 today, a dry pass
# of the runbook or a card session of ours on the box, or an earlier E185 smoke on the box without --later-try (the smoke moved aside once,
# p18501 -> p18501.try1).
#
#   bash tools/claims-v3/e185/rb/s11_a3_launch_e185.sh [--later-try] [--under-an-hour] [--after-noon]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e185.sh"
rb_init s11_a3_launch
LATER=""; HOUR=""; NOON=""
for x in "$@"; do
  case "$x" in --later-try) LATER=$x ;; --under-an-hour) HOUR=$x ;; --after-noon) NOON=$x ;;
    *) rb_die $RB_E_USAGE "usage: s11_a3_launch_e185.sh [--later-try] [--under-an-hour] [--after-noon]" ;; esac
done
rb_window
rb_need_start
rb_need_end 6300        # 105 card-minutes from T0, no subset (session_e185.sh's BUDGET_S)
hm=$(TZ=America/Los_Angeles date +%H%M)
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${RB_NOW_HM:-}" ] && hm=$RB_NOW_HM            # the desk test's clock, read only with RB_DESKTEST=1
if [ -z "${RB_DRY:-}" ] && [ "$((10#$hm))" -ge 1200 ]; then
  [ -n "$NOON" ] || rb_die $RB_E_USAGE "it is $hm PST: A6's and A7's cool-hour plan asks for a launch before 12:00 PST; to launch anyway, run again with --after-noon (a stated departure from the plan)"
  echo "$(date '+%F %T %Z') step=$RB_STEP departure: --after-noon at $hm PST (A6/A7's cool-hour plan asks for a launch before 12:00 PST)" >> "$RB_LOG"
fi
f=$(rb_file e185)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); LATER=$(printf '%q' "$LATER"); HOUR=$(printf '%q' "$HOUR")"
  rb_guard_text
  cat <<'EOF2'
job_ok_today a3-dry-e185 || { echo "REFUSED: E185's dry pass (s10_a3_dry_e185.sh) has not ended rc 0 today"; exit 3; }
SM=build/claims-v3/aifoundry3/e185-smoke
if [ "$LATER" != --later-try ]; then
  [ -e "$SM/p18501" ] && { echo "REFUSED: an earlier E185 smoke is on the box ($SM/p18501): this is a later try: run s11_a3_launch_e185.sh --later-try"; exit 3; }
  [ -e "$SM/p18501.try1" ] && { echo "REFUSED: an earlier try's smoke was moved aside ($SM/p18501.try1): a further try needs its own amendment"; exit 3; }
fi
# the card rested (v2): the latest end of a REAL session of ours on this card, any day; dry blocks and blocks that opened no device skipped;
# a real block without its "session end" counted as ended at its last timestamped line (the log's final block: or its last write, the later)
last=""; lastw=""; lastt=0; lastkind=""
for L in build/e17[0-9]/session.log build/e18[0-4]/session.log build/e184/session-*.log build/e185/T[0-9]*/session.log; do   # e185: every log of ours
  [ -f "$L" ] || continue
  case "$L" in *-dry*|*dry-t*) continue ;; esac
  w=$(echo "$L" | cut -d/ -f2)
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
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E185 needs a rested card, at least 40 (the runbook's gate)"; exit 3; }
  if [ "$rest" -lt 60 ]; then
    [ "$HOUR" = --under-an-hour ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): A7-4's plan asks for an hour; to launch anyway, run again with --under-an-hour"; exit 3; }
    echo "departure: --under-an-hour: $rest minutes since $lastw's $what (A7-4's plan asks for an hour; the gate's 40 holds)"
  fi
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped)"
else
  echo "rest: no real session of ours in build/e17x, e18x or e185/T*/session.log"
fi
if [ "$LATER" = --later-try ] && [ -e "$SM/p18501" ]; then
  [ -e "$SM/p18501.try1" ] && { echo "REFUSED: p18501.try1 exists already: a third try needs its own amendment"; exit 3; }
  mv "$SM/p18501" "$SM/p18501.try1" && echo "moved the earlier smoke aside: p18501 -> p18501.try1"
fi
mkdir -p build/e185 build/q141k
T0=$(date +%s)
[ -e "build/e185/T$T0" ] && { echo "REFUSED: build/e185/T$T0 exists already (a second launch in the same second)"; exit 3; }
echo "$T0" > build/q141k/e185.t0
E185_T0=$T0 E185_LATEST_START="$LAST_START" E185_END_GATE="$LAST_END" setsid nohup bash tools/claims-v3/e185/session_e185.sh > "build/e185/session-$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e185 $(date '+%F %T %Z') T0 $T0 (gates: latest start $LAST_START, end gate $LAST_END; its files in build/e185/T$T0/)"
tail -n 6 "build/e185/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e185, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e185
rb_has '^departure: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^departure: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
rb_say "e185 launched on aifoundry3; wait with s20_wait_e185.sh (bounded), then step 12's end window (s12_a3_host_e185.sh end), then collect with s22_collect_e185.sh"
