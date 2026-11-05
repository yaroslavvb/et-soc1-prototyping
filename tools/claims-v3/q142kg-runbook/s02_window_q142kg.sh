#!/usr/bin/env bash
# Q142(kg): records the window the owner's go sets for the pool-8 card day, for E173's and E174's launch gates (v3.1's s02_window.sh names
# E163-E169's plans; this one names none: each launch gates its own slot against the last end). Desk only: no ssh, nothing sent. Times are Pacific.
#
#   RB_OUT=<day dir> RB_LOCK=<file> bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
#
# It writes $RB_OUT/window-q142kg.env: RB_DAY, RB_LAST_START(_EPOCH), RB_LAST_END(_EPOCH), and E174's launch arguments (its deadline, the last end
# less 5 minutes, and the two window times in GNU date's form).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_q142kg.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
day=$1; ls=$2; le=$3
out=$(TZ=America/Los_Angeles "$RB_PY" -B - "$day" "$ls" "$le" <<'PY'
import sys, time
day, ls, le = sys.argv[1:4]
def ep(hm):
    return int(time.mktime(time.strptime(f"{day} {hm}", "%Y-%m-%d %H:%M")))
def st(e):
    return time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(e))
a, b = ep(ls), ep(le)
print(a, b, st(a), st(b), st(b - 300), sep="|")
PY
) || rb_die $RB_E_USAGE "unreadable day or time: $day $ls $le"
IFS='|' read -r lse lee lss les dl174 <<EOF
$out
EOF
now=$(date +%s)
[ "$lse" -lt "$lee" ] || rb_die $RB_E_USAGE "the last start must come before the last end"
[ -n "${RB_DRY:-}" ] || [ "$lee" -gt "$now" ] || rb_die $RB_E_GATE "the last end is past"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); E173 needs 48 min (subset 34), E174 45 (subset 30), after E172"
{
  echo "# the owner's go, recorded $(date '+%F %T %Z') by s02_window_q142kg.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_E174_DEADLINE=$(printf '%q' "$dl174")"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window-q142kg.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window-q142kg.env"
