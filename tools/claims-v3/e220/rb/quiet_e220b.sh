#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E209's kit's rb/quiet_e209.sh form): THE QUIET DESK FLAG (E220.md 6):
# the round's file RB_QUIET (W/locks/quiet-desk-aifoundry2), one line '<lane> <time>', stands while a card lane of ours uses aifoundry2's own
# card; while it stands no lane starts on aifoundry2 a process whose comm matches _host$, ^ettelem$, ^dev_mngt_servi, ^et-powertop$,
# ^mmbench_launch or ^sys_emu$, nor a script named session_eNNN*.sh or queue_eNNN* (desk tests wait). E220's ORDER (E220.md 6, E213-answers
# item 13's form): the card lane raises it ONLY ONCE EVERY OTHER CARD LANE OF OURS THAT HOLDS A BOOKING HAS PASSED ITS LAUNCH STEP (E215's
# arms first: their step 9 waits while the flag stands), before its own first card command, and lowers it after the copy-back (step 11) and
# on every stop path in between (rb/end_e220b.sh). It never overwrites or removes another lane's flag.
#   RB_QUIET=<flag file> RB_W=... RB_LANE=... RB_LAUNCHED=... bash tools/claims-v3/e220/rb/quiet_e220b.sh raise <lane>
#        0 up (ours, or already ours); 10 another's flag stands (never overwritten); 17 another card lane of ours holds a booking and has not
#        passed its launch step (THE ORDER: call again; nothing raised)
#   RB_QUIET=<flag file> bash tools/claims-v3/e220/rb/quiet_e220b.sh lower <lane>      0 down (or already down); 10 another's flag (left)
#   RB_QUIET=<flag file> bash tools/claims-v3/e220/rb/quiet_e220b.sh check <lane>      0 up and ours; 10 otherwise
#   RB_W=... RB_LANE=... RB_LAUNCHED=... bash tools/claims-v3/e220/rb/quiet_e220b.sh others [--wait]
#        THE ORDER alone: 0 when every booking another card lane of ours holds (bash RB_W/book.sh show) has its launch marker - the file
#        RB_LAUNCHED names for that lane ('<lane>=<file>' pairs joined by ':'), written at or after the booking's own time; 17 otherwise
#        (--wait: re-read every 20 s for up to 520 s first). A booking of the orchestrator's (an owner 'orch-...', a hold for a seal or for
#        frozen terms) is not a card lane's and is REPORTED, never waited for; a card lane's booking with no marker named is waited for.
#   bash tools/claims-v3/e220/rb/quiet_e220b.sh count [--wait]     THE P2 COUNT: 0 when no device-named process of ours and no session or
#                                                                 queue script of ours runs; else 17 (--wait: re-read every 10 s, 520 s)
# Desk tests only: RB_BOOKS names a file standing in for book.sh show's lines.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220b.sh"
rb_init quiet
op=${1:-}; lane=${2:-}
case "$op" in
  raise|lower|check)
    rb_need RB_QUIET
    [ -n "$lane" ] || rb_die 10 "usage: quiet_e220b.sh $op <lane>"
    case "$lane" in *[!A-Za-z0-9._-]*) rb_die 10 "a lane name of letters, digits, '.', '_' and '-' only" ;; esac ;;
  count|others) ;;
  *) rb_die 10 "usage: quiet_e220b.sh raise|lower|check <lane> | others [--wait] | count [--wait]" ;;
esac
owner() { head -n 1 "$RB_QUIET" 2>/dev/null | cut -d' ' -f1; }
others_once() {  # sets OTHERS_WAIT (lines waited for) and OTHERS_SAID (every booking read and its reading)
  OTHERS_WAIT=""; OTHERS_SAID=""
  local books ln key own d t when m f mk
  if [ -n "${RB_BOOKS:-}" ]; then books=$(cat "$RB_BOOKS"); else books=$(bash "$RB_W/book.sh" show 2>/dev/null); fi
  while IFS= read -r ln; do
    case "$ln" in ''|'(end)') continue ;; esac
    key=${ln%%:*}; own=$(echo "${ln#*: }" | awk '{print $1}'); d=$(echo "${ln#*: }" | awk '{print $2}'); t=$(echo "${ln#*: }" | awk '{print $3}')
    [ "$own" = "$RB_LANE" ] && { OTHERS_SAID="$OTHERS_SAID; $key: ours"; continue; }
    case "$own" in orch-*) OTHERS_SAID="$OTHERS_SAID; $key: $own (the orchestrator's hold, not a card lane: REPORTED)"; continue ;; esac
    when=$(TZ=America/Los_Angeles date -d "$d $t" +%s 2>/dev/null) || when=""
    mk=""
    IFS=: read -r -a PAIRS <<< "${RB_LAUNCHED:-}"
    for m in "${PAIRS[@]}"; do [ "${m%%=*}" = "$own" ] && mk=${m#*=}; done
    if [ -z "$mk" ]; then
      OTHERS_WAIT="$OTHERS_WAIT; $key: $own (booked $d $t; no launch marker named for it in RB_LAUNCHED)"; continue
    fi
    if [ -f "$mk" ] && [ -n "$when" ] && [ "$(stat -c %Y "$mk")" -ge "$when" ]; then
      OTHERS_SAID="$OTHERS_SAID; $key: $own launched (its marker written $(rb_pst -d "@$(stat -c %Y "$mk")"), after its booking $d $t)"
    else
      f="no marker yet"; [ -f "$mk" ] && f="its marker is older than the booking"
      OTHERS_WAIT="$OTHERS_WAIT; $key: $own (booked $d $t; $f: $mk)"
    fi
  done <<< "$books"
  OTHERS_SAID=${OTHERS_SAID#; }; OTHERS_WAIT=${OTHERS_WAIT#; }
}
others_ready() {  # 0 when nothing is waited for; with --wait re-read every 20 s for up to E220B_BOUND_S
  local end=$(( $(rb_now) + E220B_BOUND_S ))
  rb_need RB_LANE
  [ -n "${RB_BOOKS:-}" ] || { rb_need RB_W; [ -f "$RB_W/book.sh" ] || rb_die 10 "RB_W ($RB_W) holds no book.sh"; }
  while :; do
    others_once
    echo "THE ORDER: ${OTHERS_SAID:-no other booking}${OTHERS_WAIT:+; WAITING FOR: $OTHERS_WAIT}"
    [ -z "$OTHERS_WAIT" ] && return 0
    [ "${1:-}" = --wait ] && [ "$(rb_now)" -lt "$end" ] || return 17
    sleep 20
  done
}
case "$op" in
  others)
    others_ready "${2:-}" && rb_ok "THE ORDER: every other card lane of ours that holds a booking has passed its launch step"
    rb_die 17 "THE ORDER: another card lane of ours holds a booking and has not passed its launch step: call again (the flag stays down)" ;;
  raise)
    if [ -e "$RB_QUIET" ]; then
      [ "$(owner)" = "$lane" ] && rb_ok "THE QUIET DESK FLAG is already ours: $(head -n 1 "$RB_QUIET")"
      rb_die 10 "THE QUIET DESK FLAG stands for another: '$(head -n 1 "$RB_QUIET")' (never overwritten): wait in bounded chunks"
    fi
    others_ready || rb_die 17 "THE ORDER: another card lane of ours holds a booking and has not passed its launch step: the flag is NOT raised; call again"
    mkdir -p "$(dirname "$RB_QUIET")"
    ( set -o noclobber; echo "$lane $(rb_pst)" > "$RB_QUIET" ) 2>/dev/null || rb_die 10 "THE QUIET DESK FLAG appeared meanwhile: '$(head -n 1 "$RB_QUIET" 2>/dev/null)'"
    rb_log "raised: $(head -n 1 "$RB_QUIET")"
    rb_ok "THE QUIET DESK FLAG raised: $(head -n 1 "$RB_QUIET")" ;;
  lower)
    [ -e "$RB_QUIET" ] || rb_ok "THE QUIET DESK FLAG is down already"
    [ "$(owner)" = "$lane" ] || rb_die 10 "THE QUIET DESK FLAG is another's ('$(head -n 1 "$RB_QUIET")'): left as it is"
    rm -f -- "$RB_QUIET"
    rb_log "lowered"
    rb_ok "THE QUIET DESK FLAG lowered (was $lane's)" ;;
  check)
    [ -e "$RB_QUIET" ] && [ "$(owner)" = "$lane" ] && rb_ok "THE QUIET DESK FLAG is up and ours: $(head -n 1 "$RB_QUIET")"
    rb_die 10 "THE QUIET DESK FLAG is $( [ -e "$RB_QUIET" ] && echo "another's ('$(head -n 1 "$RB_QUIET")')" || echo "not up")" ;;
  count)
    end=$(( $(rb_now) + E220B_BOUND_S ))
    while :; do
      p2_count
      [ "$P2_N" -eq 0 ] && rb_ok "THE P2 COUNT is 0"
      [ "${2:-}" = --wait ] && [ "$(rb_now)" -lt "$end" ] || rb_die 17 "THE P2 COUNT is $P2_N: call again (never kill one)"
      sleep 10
    done ;;
esac
