#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum), the box step "the window" (this file is s02; step 1): record the window
# (G = this card lane's booking of aifoundry3; the last start G + 1:30 and the last end G + 3:30, each rounded up to the whole minute, inside G's
# Pacific day; G at 20:29:00 PST or earlier on Thu 19 Nov 2026, else from 00:00:30 PST Fri 20 Nov 2026, the queue bound 08:00 PST Fri: E220.md 6)
# in $RB_OUT/window.env and say whether an E220 session fits it: the session's cap is 70 card-minutes, and the launch needs E220A_BUDGET_S before
# the last end (the cap, the closing and a margin) AND must come by the last start, after the box steps (the look, the sync, the build, the
# never-run search, step 7's reads, the dry pass). It reaches no box. E215 arm A's step 1 (tools/claims-v3/e215/rb/s02_window_e215.sh, landed in
# 8bde0182): the same window.env keys (k6's own steps read them too), with RB_PLAN=e220a and RB_ARM=A (every E220 step refuses a window written
# for another runbook, another arm, or another day). It is the runbook's FIRST step; ONE RB_OUT for the card day.
#   bash tools/claims-v3/e220/rb/s02_window_e220a.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220a.sh"
rb_init s02_window
e220a_arm "${1:-}"
[ $# -ge 4 ] || rb_die $RB_E_USAGE "usage: s02_window_e220a.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
day=$2; ls=$3; le=$4
[ -n "${RB_DRY:-}" ] || [ "$day" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "the window's day $day is not today (Pacific): a window serves the day it is written"
if [ -f "$RB_OUT/window.env" ] && [ -z "${RB_DRY:-}" ]; then
  # shellcheck disable=SC1091
  ( . "$RB_OUT/window.env"; [ -z "${RB_ARM:-}" ] || [ "${RB_ARM:-}" = "$ARM" ] ) || rb_die $RB_E_USAGE "RB_OUT holds another arm's window: one RB_OUT per runbook and arm"
  ( . "$RB_OUT/window.env"; [ -z "${RB_PLAN:-}" ] || [ "${RB_PLAN:-}" = e220a ] ) || rb_die $RB_E_USAGE "RB_OUT holds another runbook's window: one RB_OUT per runbook"
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
[ $((lee - now)) -ge "$E220A_BUDGET_S" ] && [ "$now" -le "$lse" ] && fits=" an E220 arm $ARM session (its $CAP_MIN card-minutes and the closing, before the last start)"
rb_say "window (arm $ARM, $BOX): last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the look, the sync, the build, step 7, the dry pass, the copy-back)"
{
  echo "# E220's window, recorded $(date '+%F %T %Z') by s02_window_e220a.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e220a"
  echo "RB_ARM=$ARM"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
