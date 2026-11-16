#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "the window" (this file is s02): record his go's window
# (the last start and the last end, PST) in $RB_OUT/window.env and say whether E195's session fits it: its cap is 45 card-minutes (2,700 s)
# before the last end at the launch (E195.md sections 6 and 11), after about 40 minutes of box steps (the look, the sync, the build, the
# reads, the dry pass). It reaches no box. E192's step 1 (rb/s02_window_e192.sh) with E195's names: the same window.env keys, so k6's own
# steps (s05, s09) read it too, with RB_PLAN=e195 (every E195 step refuses a window written for another runbook, or on another day). It is
# the runbook's FIRST step. THE WINDOW (E195.md section 6, the lab's choice: E193 sitting A's form): from his go at G (or, under his
# standing go, the time the go lines define), last start G+1:30 and last end G+3:00, inside one Pacific day; after another session of
# ours on aifoundry3 the same day, its end plus the 40-minute rest before E195's first card command (step 9 reads the rest on the box).
#   bash tools/claims-v3/e195/rb/s02_window_e195.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_e195.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
day=$1; ls=$2; le=$3
[ -n "${RB_DRY:-}" ] || [ "$day" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "the window's day $day is not today (Pacific): a window serves the day it is written"
out=$(TZ=America/Los_Angeles "$RB_PY" -I -B - "$day" "$ls" "$le" <<'PY'
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
[ $((lee - now)) -ge "$E195_CAP_S" ] && fits=" E195 (its $((E195_CAP_S / 60)) card-minutes)"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the look, the sync, the build, the reads, the dry pass, the copy-back)"
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window_e195.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e195"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
