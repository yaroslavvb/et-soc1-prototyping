#!/usr/bin/env bash
# E198, the runbook's FIRST step (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): THE WINDOW FROM G (E198.md 12). G is the
# card lane's booking of aifoundry1 for the sitting (`book.sh take aifoundry1 <lane>`; for sitting B under one booking, sitting A's session
# end + 40 minutes, the rest's opening). Last start = G + 1:30, last end = G + 3:30, each rounded UP to the whole minute, both inside G's
# Pacific day (else refused: the sitting waits for a later day and a new booking). It writes RB_OUT's window.env for E198 and the sitting
# (one RB_OUT per sitting) and says what fits now (the sitting's cap before the last end).
#   RB_OUT=<dir> RB_LOCK=<file> bash tools/claims-v3/e198/rb/s02_window_e198.sh <A|B> <YYYY-MM-DD> <G as HH:MM:SS>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window_e198.sh <A|B> <YYYY-MM-DD> <G HH:MM:SS> (G: the card lane's booking of aifoundry1 for this sitting)"
sit=$1; day=$2; g=$3
cap=$(e198_cap_s "$sit") || rb_die $RB_E_USAGE "the sitting is A or B, not '$sit'"
[ -n "${RB_DRY:-}" ] || [ "$day" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "the window's day $day is not today (Pacific): a window serves the day it is written"
out=$(TZ=America/Los_Angeles "$RB_PY" -I -B - "$day" "$g" <<'PY'
import sys, time
day, g = sys.argv[1:3]
G = int(time.mktime(time.strptime(f"{day} {g}", "%Y-%m-%d %H:%M:%S")))
def up(e):                       # rounded up to the whole minute
    return e if e % 60 == 0 else e - e % 60 + 60
ls, le = up(G + 90 * 60), up(G + 210 * 60)
endday = int(time.mktime(time.strptime(f"{day} 23:59:59", "%Y-%m-%d %H:%M:%S")))
st = lambda e: time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(e))
print(G, ls, le, st(G), st(ls), st(le), time.strftime("%H:%M", time.localtime(ls)),
      time.strftime("%H:%M", time.localtime(le)), "inside" if le <= endday else "outside", sep="|")
PY
) || rb_die $RB_E_USAGE "unreadable day or G: $day $g"
IFS='|' read -r ge lse lee gs lss les lshm lehm inday <<EOF2
$out
EOF2
[ "$inday" = inside ] || rb_die $RB_E_GATE "G $day $g puts the last end at $les, past G's Pacific day: no sitting today (E198.md 12: a window that does not fit waits for a later day and a new booking)"
now=$(date +%s)
fits=""
[ $((lee - now)) -ge "$cap" ] && fits=" E198 sitting $sit (its $((cap / 60)) card-minutes)"
rb_say "window for sitting $sit from G $day $g: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); fits now:${fits:- nothing} (before the box steps' own time: the sync, the build, the reads, the dry pass, the copy-back)"
{
  echo "# G (the card lane's booking of aifoundry1 for sitting $sit), recorded $(date '+%F %T %Z') by s02_window_e198.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_G=$(printf '%q' "$g")"
  echo "RB_G_EPOCH=$ge"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$lshm")"
  echo "RB_LAST_END_HM=$(printf '%q' "$lehm")"
  echo "RB_PLAN=e198"
  echo "RB_SITTING=$sit"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window sitting=$sit G='$day $g' last_start='$lss' last_end='$les'" >> "$RB_LOG"
cat "$RB_OUT/window.env"
