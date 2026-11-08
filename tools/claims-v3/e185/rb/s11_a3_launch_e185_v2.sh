#!/usr/bin/env bash
# E185, the runbook's step 10 (the launch), v2: the kit's dated note 1 (KIT.md.dated-note-1.md, Sat 7 Nov 2026). It is
# s11_a3_launch_e185.sh (460c352f, which stays as committed) with ONE change, the rest rule (the kit verifier's minor fault 6):
#   - v1 read build/e17x and e18[0-4]/session.log, E184's build/e184/session-*.log and E185's T0-named build/e185/T*/session.log. It never
#     read E183's T0-named log, build/e183/session-t<T0>.log (E183's kit, cc597bf2), so a session of E183 on this card the same day was
#     invisible to E185's 40-minute rest gate. v2 reads every build/e18x/session-*.log too (E183's and E184's), dry logs skipped by name.
#   - v1 counted a block's end only at a line ending "session end"; E183's and E184 v2's sessions end "session end (T0 <epoch>)", which v1
#     counted as a block without its end (at its last line: the same time, with a "note:"). v2 reads both forms as the session's end.
#   (Its refusal of an earlier smoke names this file: "run s11_a3_launch_e185_v2.sh --later-try".)
# Everything else is v1's, line for line (its header's provenance lines are corrected by the kit's dated note 1): the launch command,
#   E185_T0=$(date +%s) E185_LATEST_START=<the last start> E185_END_GATE=<the last end>
#     setsid nohup bash tools/claims-v3/e185/session_e185.sh > build/e185/session-$T0.out 2>&1 < /dev/null &
# A6's and A7's cool-hour plan (at or after 12:00 PST refused unless --after-noon, logged); refused (10) before any launch also on: no
# window, past the last start, fewer than 105 minutes left (session_e185.sh's budget, no subset), the dry job not ended rc 0 today, a dry
# pass of the runbook or a card session of ours on the box, under 40 minutes since our last real session end on this card (under an hour:
# refused unless --under-an-hour, logged), or an earlier E185 smoke on the box without --later-try (the smoke moved aside once, p18501 ->
# p18501.try1; a third try needs its own amendment). After a later try, step 14 v2 (s22_collect_e185_v2.sh) collects; v1's step 14 cannot.
#
#   bash tools/claims-v3/e185/rb/s11_a3_launch_e185_v2.sh [--later-try] [--under-an-hour] [--after-noon]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e185.sh"
rb_init s11_a3_launch_v2
LATER=""; HOUR=""; NOON=""
for x in "$@"; do
  case "$x" in --later-try) LATER=$x ;; --under-an-hour) HOUR=$x ;; --after-noon) NOON=$x ;;
    *) rb_die $RB_E_USAGE "usage: s11_a3_launch_e185_v2.sh [--later-try] [--under-an-hour] [--after-noon]" ;; esac
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
  [ -e "$SM/p18501" ] && { echo "REFUSED: an earlier E185 smoke is on the box ($SM/p18501): this is a later try: run s11_a3_launch_e185_v2.sh --later-try"; exit 3; }
  [ -e "$SM/p18501.try1" ] && { echo "REFUSED: an earlier try's smoke was moved aside ($SM/p18501.try1): a further try needs its own amendment"; exit 3; }
fi
# the card rested (v2): the latest end of a REAL session of ours on this card, any day; dry blocks and blocks that opened no device skipped;
# a real block without its "session end" counted as ended at its last timestamped line (the log's final block: or its last write, the later)
last=""; lastw=""; lastt=0; lastkind=""
for L in build/e17[0-9]/session.log build/e18[0-4]/session.log build/e18[0-9]/session-*.log build/e185/T[0-9]*/session.log; do   # v2: E183's and E184's session-*.log
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
    inblk && /session end( \(T0 [0-9]+\))?$/ && $0 !~ /DRY session end/ { endts = $1 " " $2 " " $3 }   # v2: both end forms
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
  echo "rest: no real session of ours in build/e17x, e18x (session.log and session-*.log) or e185/T*/session.log"
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
