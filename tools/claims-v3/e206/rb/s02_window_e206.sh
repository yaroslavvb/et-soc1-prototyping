#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum), the box step "the window" (this file is s02; step 1): record the arm's
# window (G = this card lane's booking of the arm's box; the last start G + 1:30 and the last end G + 3:30, each rounded up to the whole
# minute, inside G's Pacific day; G at 20:29:00 PST or earlier: E206.md 6) in $RB_OUT/window.env and say whether an E206 session fits it:
# a session's cap is 120 card-minutes, and the launch needs 7,500 s before the last end (E206_BUDGET_S: the cap, the closing and a margin),
# after the box steps (the look, the sync, the build, step 7's reads, the dry pass). It reaches no box. E190's step 1 with the arm as the
# first word: the same window.env keys (k6's own steps read them too), with RB_PLAN=e206 and RB_ARM=<arm> (every E206 step refuses a window
# written for another runbook, another arm, or another day). It is the runbook's FIRST step; ONE RB_OUT PER ARM.
#   bash tools/claims-v3/e206/rb/s02_window_e206.sh <A|B> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e206.sh"
rb_init s02_window
e206_arm "${1:-}"
[ $# -ge 4 ] || rb_die $RB_E_USAGE "usage: s02_window_e206.sh <A|B> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
day=$2; ls=$3; le=$4
[ -n "${RB_DRY:-}" ] || [ "$day" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "the window's day $day is not today (Pacific): a window serves the day it is written"
if [ -f "$RB_OUT/window.env" ] && [ -z "${RB_DRY:-}" ]; then
  # shellcheck disable=SC1091
  ( . "$RB_OUT/window.env"; [ -z "${RB_ARM:-}" ] || [ "${RB_ARM:-}" = "$ARM" ] ) || rb_die $RB_E_USAGE "RB_OUT holds the other arm's window: one RB_OUT per arm"
fi
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
[ $((lee - now)) -ge "$E206_BUDGET_S" ] && fits=" an E206 session of arm $ARM (its 120 card-minutes and the closing)"
rb_say "window (arm $ARM, $BOX): last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the look, the sync, the build, step 7, the dry pass, the copy-back)"
{
  echo "# the arm's window, recorded $(date '+%F %T %Z') by s02_window_e206.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e206"
  echo "RB_ARM=$ARM"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
