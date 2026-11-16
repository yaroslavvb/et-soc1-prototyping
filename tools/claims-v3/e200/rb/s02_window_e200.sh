#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum), the box step "the window" (this file is s02), ONE PER SITTING: record
# the window for this sitting (the last start and the last end, PST) in $RB_OUT/window.env and say which plan fits it now. E197's step 1
# (tools/claims-v3/e197/rb/s02_window_e197.sh, unchanged beside it) with E200's window (E200.md 12, E194's amended form, its A1-4): G = the
# moment the card lane holds the aifoundry2 booking for the sitting (`book.sh take` prints BOOKED; its owner file records the time); last
# start G+1:30 and last end G+3:30, each ROUNDED UP to the whole minute, inside that Pacific day, so G at 20:29:00 PST or earlier; the
# start is the sitting's first card command, the end its sampler's stop. A card lane that books once for both sittings uses that G for
# sitting 1; sitting 2's G is then sitting 1's end plus 40 minutes (its rest's opening). E200.md 5: sitting 1 runs the full plan (cap
# 3,000 s) unless, at its first card command, the time left to the last end is less than that cap plus the kit's closing steps (900 s: the
# collection must start 10 minutes before the last end); then the short plan (cap 2,400 s), if it fits; sitting 2 runs the ext plan (cap
# 2,100 s). This step only reports what fits now; step 7's wrapper decides at the first card command and logs it. It reaches no box. The
# same window.env keys as E197's, with RB_PLAN=e200 and RB_SITTING (every E200 step refuses a window written for another runbook, another
# sitting or another day). It is each sitting's FIRST step, in that sitting's own RB_OUT.
#
#   bash tools/claims-v3/e200/rb/s02_window_e200.sh <1|2> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e200.sh"
rb_init s02_window
[ $# -ge 4 ] || rb_die $RB_E_USAGE "usage: s02_window_e200.sh <1|2> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
sit=$1; day=$2; ls=$3; le=$4
e200_sit_ok "$sit" || rb_die $RB_E_USAGE "the sitting is 1 or 2, not '$sit'"
[ -n "${RB_DRY:-}" ] || [ "$day" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "the window's day $day is not today (Pacific): a window serves the day it is written"
out=$(TZ=America/Los_Angeles "$RB_PY" -B - "$day" "$ls" "$le" <<'PY'
import sys, time
day, ls, le = sys.argv[1:4]
def ep(hm):
    return int(time.mktime(time.strptime(f"{day} {hm}", "%Y-%m-%d %H:%M")))
def st(e):
    return time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(e))
a, b = ep(ls), ep(le)
print(a, b, st(a), st(b), sep="|")
PY
) || rb_die $RB_E_USAGE "unreadable day or time: $day $ls $le"
IFS='|' read -r lse lee lss les <<EOF2
$out
EOF2
now=$(date +%s)
[ "$lse" -lt "$lee" ] || rb_die $RB_E_USAGE "the last start must come before the last end"
[ $((lee - lse)) -eq 7200 ] || rb_die $RB_E_USAGE "the last end is not the last start + 2:00 (E200.md 12: last start G+1:30, last end G+3:30, each rounded up to the whole minute)"
fits=""
if [ "$sit" = 1 ]; then
  if [ $((lee - now)) -ge $(( $(e200_cap_s full) + E200_CLOSE_S )) ]; then fits=" E200 sitting 1, the full plan (its 50 card-minutes)"
  elif [ $((lee - now)) -ge $(( $(e200_cap_s short) + E200_CLOSE_S )) ]; then fits=" E200 sitting 1, the short plan only (its 40 card-minutes)"; fi
else
  [ $((lee - now)) -ge $(( $(e200_cap_s ext) + E200_CLOSE_S )) ] && fits=" E200 sitting 2 (its 35 card-minutes)"
fi
rb_say "window for sitting $sit: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the sync, the build, the dry pass, the rest, the reads, the copy-back)"
{
  echo "# the window, recorded $(date '+%F %T %Z') by s02_window_e200.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e200"
  echo "RB_SITTING=$sit"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window sitting=$sit last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
