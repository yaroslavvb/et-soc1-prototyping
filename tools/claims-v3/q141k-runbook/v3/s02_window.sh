#!/usr/bin/env bash
# Q141(k), go checklist step 2 (his: say go, with the window). Records the window his go sets, for every later step's gates. Desk
# only: no ssh, nothing sent. Times are Pacific (the boxes' zone, PST in November).
#
#   RB_OUT=<day dir> RB_LOCK=<file> bash tools/claims-v3/q141k-runbook/s02_window.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM> [full|a|b]
#
# The plan (Q141(f)'s card plan): full = all seven, needs the last end at least about 4 h 15 min after now and the last start at
# least 3 h 30 min after it; b = everything but E168 and E169, about 3 h; a = E163 (FULL, or TWO) on aifoundry3 instead of E166,
# plus E164 and E165, about 1 h 45 min. A plan the window cannot hold is refused (16), with the plans it can.
# It writes $RB_OUT/window.env: the round's last start and last end (E163_LATEST_START / E166_LATEST_START and E163_DEADLINE /
# E166_END_GATE; every slot must end by the last end), E164's deadline (the last end less 10 minutes), and the plan.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s02_window
[ $# -ge 3 ] || rb_die $RB_E_USAGE "usage: s02_window.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM> [full|a|b]"
day=$1; ls=$2; le=$3; plan=${4:-full}
case "$plan" in full|a|b) ;; *) rb_die $RB_E_USAGE "the plan is full, a or b" ;; esac
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
IFS='|' read -r lse lee lss les e164dl <<EOF
$out
EOF
now=$(date +%s)
[ "$lse" -lt "$lee" ] || rb_die $RB_E_USAGE "the last start must come before the last end"
fits=""
[ $((lee - now)) -ge 15300 ] && [ $((lse - now)) -ge 12600 ] && fits="$fits full"
[ $((lee - now)) -ge 10800 ] && fits="$fits b"
[ $((lee - now)) -ge 6300 ] && fits="$fits a"
rb_say "window: last start $lss, last end $les ($(( (lee - now) / 60 )) min from now); plans that fit:${fits:- none}"
case " $fits " in *" $plan "*) ;; *) [ -n "${RB_DRY:-}" ] || rb_die $RB_E_GATE "plan $plan does not fit this window (fits:${fits:- none})" ;; esac
{
  echo "# his go, recorded $(date '+%F %T %Z') by s02_window.sh"
  echo "RB_DAY=$(printf '%q' "$day")"
  echo "RB_LAST_START=$(printf '%q' "$lss")"
  echo "RB_LAST_END=$(printf '%q' "$les")"
  echo "RB_LAST_START_EPOCH=$lse"
  echo "RB_LAST_END_EPOCH=$lee"
  echo "RB_LAST_START_HM=$(printf '%q' "$ls")"
  echo "RB_LAST_END_HM=$(printf '%q' "$le")"
  echo "RB_E164_DEADLINE=$(printf '%q' "$e164dl")"
  echo "RB_PLAN=$plan"
  echo "RB_GO_EPOCH=$now"
} > "$RB_OUT/window.env"
echo "$(date '+%F %T %Z') step=$RB_STEP window last_start='$lss' last_end='$les' plan=$plan" >> "$RB_LOG"
cat "$RB_OUT/window.env"
