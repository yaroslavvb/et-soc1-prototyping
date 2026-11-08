#!/usr/bin/env bash
# E183 (Q155, the kit), KIT.md box step 1: his go's window, written into RB_OUT (E182's s02_window_e182.sh, ported). FIRST: every later
# step that needs the window refuses without it, and step 2 refuses unless it was written today.
#   bash tools/claims-v3/e183/rb/s02_window_e183.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>      (PST)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_e183.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
day=$1; ls=$2; le=$3
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
[ $((lee - now)) -ge 3900 ] && fits="$fits E183-FULL"
[ $((lee - now)) -ge 1920 ] && fits="$fits E183-SHORT"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); E183 plans that fit now:${fits:- none}"
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window_e183.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e183"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
