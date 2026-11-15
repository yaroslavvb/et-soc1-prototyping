#!/usr/bin/env bash
# E193 (Q177, the kit), the box step "the window" (this file is s02), ONE PER SITTING: record his go's window for this sitting (the last
# start and the last end, PST) in $RB_OUT/window.env and say whether the sitting fits it: its cap, 60 card-minutes for sitting A (3,600
# s) and 50 for B (3,000 s), before the last end at the launch (E193.md 6), after about 30 minutes of box steps. It reaches no box. E189's
# step 1 (rb/s02_window_e189.sh) with the sitting: the same window.env keys, so k6's own steps (s05, s09) read it too, with RB_PLAN=e193
# and RB_SITTING (every E193 step refuses a window written for another runbook, another sitting or another day). It is each sitting's
# FIRST step, in that sitting's own RB_OUT. On one day with both sittings: sitting A's window first, then sitting B's in a new RB_OUT,
# its last start at least A's end + 40 minutes of rest later (step 9 reads the rest on the box and refuses before it).
#
#   bash tools/claims-v3/e193/rb/s02_window_e193.sh <A|B> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e193.sh"
rb_init s02_window
[ $# -ge 4 ] || rb_die $RB_E_USAGE "usage: s02_window_e193.sh <A|B> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
sit=$1; day=$2; ls=$3; le=$4
cap=$(e193_cap_s "$sit") || rb_die $RB_E_USAGE "the sitting is A or B, not '$sit'"
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
fits=""
[ $((lee - now)) -ge "$cap" ] && fits=" E193 sitting $sit (its $((cap / 60)) card-minutes)"
rb_say "window for sitting $sit: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the sync, the build, the reads, the dry pass, the copy-back)"
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window_e193.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e193"
  echo "RB_SITTING=$sit"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window sitting=$sit last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
