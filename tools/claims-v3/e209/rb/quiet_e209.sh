#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): THE QUIET DESK FLAG (E209.md 6; E194's and E200's form): the round's
# file RB_QUIET (W/locks/quiet-desk-aifoundry2), one line '<lane> <time>', stands while a card lane of ours uses aifoundry2's own card;
# while it stands no lane starts on aifoundry2 a process whose comm matches _host$, ^ettelem$, ^dev_mngt_servi, ^et-powertop$,
# ^mmbench_launch or ^sys_emu$, nor a script named session_eNNN*.sh or queue_eNNN* (desk tests wait). The card lane raises it right before
# the look (step 4) and lowers it after the copy-back (step 11), and on every stop path in between (rb/end_e209.sh). It never overwrites
# or removes another lane's flag.
#   RB_QUIET=<flag file> bash tools/claims-v3/e209/rb/quiet_e209.sh raise <lane>     0 up (ours, or already ours); 10 another's flag stands
#   RB_QUIET=<flag file> bash tools/claims-v3/e209/rb/quiet_e209.sh lower <lane>     0 down (or already down); 10 another's flag (left)
#   RB_QUIET=<flag file> bash tools/claims-v3/e209/rb/quiet_e209.sh check <lane>     0 up and ours; 10 otherwise
#   bash tools/claims-v3/e209/rb/quiet_e209.sh count [--wait]                         THE P2 COUNT: 0 when no device-named process of ours
#                                                                                     and no session or queue script of ours runs; else 17
#                                                                                     (--wait: re-read every 10 s for up to 520 s first)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init quiet
op=${1:-}; lane=${2:-}
case "$op" in
  raise|lower|check)
    rb_need RB_QUIET
    [ -n "$lane" ] || rb_die 10 "usage: quiet_e209.sh $op <lane>"
    case "$lane" in *[!A-Za-z0-9._-]*) rb_die 10 "a lane name of letters, digits, '.', '_' and '-' only" ;; esac ;;
  count) ;;
  *) rb_die 10 "usage: quiet_e209.sh raise|lower|check <lane> | count [--wait]" ;;
esac
owner() { head -n 1 "$RB_QUIET" 2>/dev/null | cut -d' ' -f1; }
case "$op" in
  raise)
    if [ -e "$RB_QUIET" ]; then
      [ "$(owner)" = "$lane" ] && rb_ok "THE QUIET DESK FLAG is already ours: $(head -n 1 "$RB_QUIET")"
      rb_die 10 "THE QUIET DESK FLAG stands for another: '$(head -n 1 "$RB_QUIET")' (never overwritten): wait in bounded chunks"
    fi
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
    end=$(( $(rb_now) + E209_BOUND_S ))
    while :; do
      p2_count
      [ "$P2_N" -eq 0 ] && rb_ok "THE P2 COUNT is 0"
      [ "${2:-}" = --wait ] && [ "$(rb_now)" -lt "$end" ] || rb_die 17 "THE P2 COUNT is $P2_N: call again (never kill one)"
      sleep 10
    done ;;
esac
