#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 1: record his go's window (the round's last start and last end, PST) in
# $RB_OUT/window.env, and say which of E184's arms fit it: arm S needs 8,100 s before the last end (its 135 card-minute cap), arm B 1,500 s (25).
# It reaches no box. ../../e180/rb/s02_window_e180.sh's form, with the same window.env keys, so k6's own steps (s05, s09) read it too. One
# window file per runbook (kit v5's lesson): each arm's card day keeps its own RB_OUT.
#
#   bash tools/claims-v3/e184/rb/s02_window_e184.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_e184.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
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
[ $((lee - now)) -ge 8100 ] && fits="$fits E184-S"
[ $((lee - now)) -ge 1500 ] && fits="$fits E184-B"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); E184 arms that fit now:${fits:- none}"
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window_e184.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e184"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
