#!/usr/bin/env bash
# E181, step 2: record the window for M11's session 2 (the last start and last end, PST) in $RB_OUT/window.env, and say whether E181 fits
# it: E181 needs its 76-card-minute budget from T0 before the last end (session_e181.sh's BUDGET_S, REGISTRATION.md section 5's cap). It also
# says whether the window keeps A6's and A7's cool-hour plan (launch before 12:00 PST: step 11 refuses at or after noon without
# --after-noon). It reaches no box. ../../q143k-runbook/s02_window_q143k.sh (92a1b27f) ported: the same window.env keys.
#
#   bash tools/claims-v3/e181/rb/s02_window_e181.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_e181.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
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
[ $((lee - now)) -ge 4560 ] && fits="$fits E181"
cool="the cool-hour plan holds (the last start is before 12:00 PST)"
case "$ls" in 0*|10:*|11:*) ;; *) cool="the last start $ls is at or after 12:00 PST: A6/A7's cool-hour plan asks for a launch before noon (step 11 needs --after-noon then)" ;; esac
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); runs that fit now:${fits:- none}; $cool"
{
  echo "# the window, recorded $(date '+%F %T %Z') by s02_window_e181.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e181"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
