#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), the box step "the window" (this file is s02): record his go's
# window (the last start and the last end, PST) in $RB_OUT/window.env and say whether E196's session fits it: its cap is 60 card-minutes
# (3,600 s) before the last end at the launch (E196.md section 10), after the box steps (the look, the sync, the two builds, the reads,
# the dry pass). It reaches no box. E192's step 1 (rb/s02_window_e192.sh) with E196's names: the same window.env keys, so k6's own steps
# (s05, s09) read it too, with RB_PLAN=e196 (every E196 step refuses a window written for another runbook, or on another day). It is the
# runbook's FIRST step. The window (E196.md section 12): from G, his go as the go lines define it, last start G + 1:30 and last end
# G + 3:00, both inside the Pacific day of G; after another session of ours on aifoundry3 the same day (E195's, in the round's order),
# E196's first card command at least 40 minutes after its end (step 9's rest rule reads it on the box).
#   bash tools/claims-v3/e196/rb/s02_window_e196.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e196.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_e196.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
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
[ $((lee - now)) -ge "$E196_CAP_S" ] && fits=" E196 (its 60 card-minutes)"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the look, the sync, the build, the reads, the dry pass, the copy-back)"
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window_e196.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e196"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
