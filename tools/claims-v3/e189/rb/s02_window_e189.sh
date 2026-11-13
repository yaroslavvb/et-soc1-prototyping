#!/usr/bin/env bash
# E189 (Q167, the kit), the box step "the window" (this file is s02): record his go's window (the last start and the last end, PST) in
# $RB_OUT/window.env and say whether E189's session fits it: the session's cap is 110 card-minutes (6,600 s) before the last end at the
# launch (E189.md section 10), after about 30 minutes of box steps. It reaches no box. E188's step 1 (rb/s02_window_e188.sh) with E189's
# names: the same window.env keys, so k6's own steps (s05, s09) read it too, with RB_PLAN=e189 (every E189 step refuses a window written
# for another runbook, or on another day). It is the runbook's FIRST step. The window from his go at G (E189.md section 13): alone, last
# start G+1:30 and last end G+3:30; after E183 the same day, last start G+3:00 and last end G+5:00; inside one Pacific day and at least
# 30 minutes before the approval lapses (his go says when it lapses; this step does not know it).
#
#   bash tools/claims-v3/e189/rb/s02_window_e189.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e189.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_e189.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
day=$1; ls=$2; le=$3
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
[ $((lee - now)) -ge "$E189_BUDGET_S" ] && fits=" E189 (its 110 card-minutes)"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the sync, the build, the reads, the dry pass, the copy-back)"
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window_e189.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e189"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
