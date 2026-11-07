#!/usr/bin/env bash
# E182 (Q153, the kit), step 2: record his go's window (the round's last start and last end, PST) in $RB_OUT/window.env, and say which of
# E182's plans fit it: FULL needs 6,000 s before the last end, PASSES 2,400 s (E182.md section 7: caps 100 and 40 card-minutes). It reaches
# no box. A port of E178's step 2 (k6's form): the same window.env keys, so k6's own steps (s05, s09) read it too. It is the runbook's FIRST
# step: step 3 refuses without the window this step writes today (kit v5's lesson, "s02 before s03").
#
#   bash tools/claims-v3/e182/rb/s02_window_e182.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_e182.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
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
[ $((lee - now)) -ge 6000 ] && fits="$fits E182-FULL"
[ $((lee - now)) -ge 2400 ] && fits="$fits E182-PASSES"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); E182 plans that fit now:${fits:- none}"
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window_e182.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e182"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
