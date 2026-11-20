#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E209's kit's rb/s02_window_e209.sh form): runbook step 1, THE WINDOW (E220.md 6): G = the card lane's booking
# of aifoundry2 on its day; the last start G + 1:30 and the last end G + 3:30, each rounded up to the whole minute, inside G's Pacific
# day; G at 20:29:00 PST or earlier. It writes RB_OUT/window.env (read by every later step: written today, naming today) and prints the
# window. Refused (10): no G, a G that is not today, a G later than 20:29:00, a last end outside G's day, an RB_OUT with a window of
# another day. One RB_OUT a day.
#   RB_OUT=<the day's folder> bash tools/claims-v3/e220/rb/s02_window_e220b.sh <G: epoch seconds of the booking>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220b.sh"
rb_init s02_window
rb_need RB_OUT
G=${1:-}
case "$G" in ''|*[!0-9]*) rb_die 10 "usage: s02_window_e220b.sh <G epoch>" ;; esac
NOW=$(rb_now)
[ "$G" -le "$NOW" ] || rb_die 10 "G ($G) is in the future"
DAY=$(TZ=America/Los_Angeles date -d "@$G" +%F)
TODAY=$(TZ=America/Los_Angeles date -d "@$NOW" +%F)
[ "$DAY" = "$TODAY" ] || rb_die 10 "G is on $DAY, not today ($TODAY)"
LIM=$(TZ=America/Los_Angeles date -d "$DAY 20:29:00" +%s)
[ "$G" -le "$LIM" ] || rb_die 10 "G ($(rb_pst -d "@$G")) is later than 20:29:00 PST: no booking that day (THE DAY: wait until 00:00:30 the next day)"
up() { local t=$1; echo $(( (t + 59) / 60 * 60 )); }
LS=$(up $((G + 5400)))
LE=$(up $((G + 12600)))
[ "$(TZ=America/Los_Angeles date -d "@$LE" +%F)" = "$DAY" ] || rb_die 10 "the last end ($(rb_pst -d "@$LE")) is not inside G's day"
if [ -f "$RB_OUT/window.env" ]; then
  # shellcheck disable=SC1091
  OLD=$(. "$RB_OUT/window.env"; echo "${E220B_WINDOW_DAY:-}:${E220B_G:-}")
  [ "$OLD" = "$DAY:$G" ] || rb_die 10 "this RB_OUT holds another window ($OLD): one RB_OUT a day, one G"
fi
cat > "$RB_OUT/window.env" <<EOF
E220B_WINDOW_DAY=$DAY
E220B_G=$G
E220B_LAST_START=$LS
E220B_LAST_END=$LE
EOF
echo "G $(rb_pst -d "@$G"); last start $(rb_pst -d "@$LS"); last end $(rb_pst -d "@$LE") (G + 1:30 and G + 3:30, rounded up)"
rb_ok "the window written to RB_OUT/window.env"
