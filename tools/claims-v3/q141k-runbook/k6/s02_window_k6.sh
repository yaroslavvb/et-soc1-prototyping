#!/usr/bin/env bash
# Q142(k6), step 2: record his go's window for the pool-8 card day (the round's last start and last end, PST) in $RB_OUT/window.env,
# and say which runs fit it: E171 needs its plan's budget before the last end (FULL 4,200 s, TWO 2,280 s, SHORT 1,800 s; E171.md), E172
# 3,900 s before its deadline, which is the last end less 600 s (E172.md: the round's time gate less 10 minutes). It reaches no box.
# A port of ../v3.1/s02_window.sh (the same window.env keys, so v3.1's own steps read it too), with E172's deadline in place of E164's.
#
#   bash tools/claims-v3/q141k-runbook/k6/s02_window_k6.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_k6.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
day=$1; ls=$2; le=$3
out=$(TZ=America/Los_Angeles "$RB_PY" -B - "$day" "$ls" "$le" <<'PY'
import sys, time
day, ls, le = sys.argv[1:4]
def ep(hm):
    return int(time.mktime(time.strptime(f"{day} {hm}", "%Y-%m-%d %H:%M")))
def st(e):
    return time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(e))
a, b = ep(ls), ep(le)
print(a, b, st(a), st(b), st(b - 600), sep="|")
PY
) || rb_die $RB_E_USAGE "unreadable day or time: $day $ls $le"
IFS='|' read -r lse lee lss les e172dl <<EOF
$out
EOF
now=$(date +%s)
[ "$lse" -lt "$lee" ] || rb_die $RB_E_USAGE "the last start must come before the last end"
fits=""
[ $((lee - now)) -ge 4200 ] && fits="$fits E171-FULL"
[ $((lee - now)) -ge 2280 ] && fits="$fits E171-TWO"
[ $((lee - 600 - now)) -ge 3900 ] && fits="$fits E172"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); runs that fit now:${fits:- none}"
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window_k6.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_E172_DEADLINE=$(printf '%q' "$e172dl")"
  echo "RB_PLAN=k6"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
