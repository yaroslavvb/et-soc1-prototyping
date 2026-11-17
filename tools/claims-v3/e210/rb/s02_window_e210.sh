#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c), the box step "the window" (this file is s02; step 1): record the window
# (G = this card lane's booking of aifoundry3; the last start G + 1:30 and the last end G + 3:30, each rounded up to the whole minute, inside
# G's Pacific day; G at 20:29:00 PST or earlier: E210.md 6) in $RB_OUT/window.env and say whether an E210 session fits it: a session's cap is 95
# card-minutes, and the launch needs 6,000 s before the last end (E210_BUDGET_S: the cap, the closing and a margin) AND must come by the last
# start, after the box steps (the look, the never-run search, the sync, the build, step 7's reads, the dry pass). It reaches no box. E206's
# step 1 (tools/claims-v3/e206/rb/s02_window_e206.sh) for E210's one arm: the same window.env keys (k6's own steps read them too), with
# RB_PLAN=e210 and RB_ARM=A (every E210 step refuses a window written for another runbook, another arm, or another day). It is the runbook's
# FIRST step; ONE RB_OUT for E210's card day.
#   bash tools/claims-v3/e210/rb/s02_window_e210.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e210.sh"
rb_init s02_window
e210_arm "${1:-}"
[ $# -ge 4 ] || rb_die $RB_E_USAGE "usage: s02_window_e210.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>"
day=$2; ls=$3; le=$4
[ -n "${RB_DRY:-}" ] || [ "$day" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "the window's day $day is not today (Pacific): a window serves the day it is written"
if [ -f "$RB_OUT/window.env" ] && [ -z "${RB_DRY:-}" ]; then
  # shellcheck disable=SC1091
  ( . "$RB_OUT/window.env"; [ -z "${RB_ARM:-}" ] || [ "${RB_ARM:-}" = "$ARM" ] ) || rb_die $RB_E_USAGE "RB_OUT holds another arm's window: one RB_OUT per runbook and arm"
  ( . "$RB_OUT/window.env"; [ -z "${RB_PLAN:-}" ] || [ "${RB_PLAN:-}" = e210 ] ) || rb_die $RB_E_USAGE "RB_OUT holds another runbook's window: one RB_OUT per runbook"
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
[ $((lee - now)) -ge "$E210_BUDGET_S" ] && [ "$now" -le "$lse" ] && fits=" an E210 session (its 95 card-minutes and the closing, before the last start)"
rb_say "window (arm $ARM, $BOX): last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the look, the sync, the build, step 7, the dry pass, the copy-back)"
{
  echo "# E210's window, recorded $(date '+%F %T %Z') by s02_window_e210.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_PLAN=e210"
  echo "RB_ARM=$ARM"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM window last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
