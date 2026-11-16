#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): THE QUIET DESK FLAG (E200.md 12; E194's form, rb/quiet_e194.sh in
# tools/claims-v3/e194, unchanged beside it, with E200's mark; the round's flag file for aifoundry2, W/locks/quiet-desk-aifoundry2). E200's
# sittings run on the box this round's orchestration runs on, so from the look (step 4) to the copy-back (step 11) no lane of ours may start
# on aifoundry2 a process named like a device process (_host$, ^ettelem$, ^dev_mngt_servi, ^et-powertop$, ^mmbench_launch, ^sys_emu$) or a
# script named session_eNNN*.sh or queue_eNNN*: the session reads such a process of our own as a holder (et-who) and stops. The card lane
# raises the flag right before the look and lowers it after the copy-back, and on every stop path after the raise; every step from 4 to 11
# refuses unless it is raised as E200's (rb_e200.sh, e200_quiet); other lanes read it before starting such a process. The flag is a file
# outside the repo, RB_QUIET, holding one line "e200 <lane> <time>".
#   bash tools/claims-v3/e200/rb/quiet_e200.sh raise <lane>     create RB_QUIET ("e200 <lane> <time>"); 0, or 10 when another lane's
#                                                               flag is up (never overwritten)
#   bash tools/claims-v3/e200/rb/quiet_e200.sh lower <lane>     remove it (only E200's own, for <lane>): 0, or 10 when it is not ours
#   bash tools/claims-v3/e200/rb/quiet_e200.sh check            0 when raised, 10 when not
#   bash tools/claims-v3/e200/rb/quiet_e200.sh count [--wait]   THE P2 COUNT on this box (the desk is the box): device-named processes of
#                                                               ours and session or queue scripts of ours (by each process's own script),
#                                                               as counts; 0 when it reads 0, 16 when not; --wait reads again up to 5
#                                                               times 2 s apart (our own live collector's `ettelem temp` lives for a
#                                                               moment once a second while nothing holds the card)
# It reaches no box and opens no device. SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
op=${1:-}; lane=${2:-}
need_flag() {
  [ -n "${RB_QUIET:-}" ] || { echo "QUIET: RB_QUIET is not set (the round's quiet-desk flag file for aifoundry2, outside the repo)"; exit 10; }
  case "$(cd "$(dirname "$RB_QUIET")" 2>/dev/null && pwd -P)/" in "$(cd "$REPO" && pwd -P)/"*) echo "QUIET: RB_QUIET is inside the lab repo: refused"; exit 10 ;; esac
}
case "$op" in
  raise)
    need_flag; [ -n "$lane" ] || { echo "QUIET: raise needs the card lane's name"; exit 10; }
    if [ -e "$RB_QUIET" ]; then
      read -r w o _ < "$RB_QUIET" 2>/dev/null
      if [ "${w:-}" = e200 ] && [ "${o:-}" = "$lane" ]; then echo "QUIET: raised (already, by $lane)"; exit 0; fi
      echo "QUIET: another flag is up ($(head -c 120 "$RB_QUIET" 2>/dev/null)): not overwritten"; exit 10
    fi
    echo "e200 $lane $(TZ=America/Los_Angeles date '+%F %T %Z')" > "$RB_QUIET" && echo "QUIET: raised by $lane ($RB_QUIET)" ;;
  lower)
    need_flag; [ -n "$lane" ] || { echo "QUIET: lower needs the card lane's name"; exit 10; }
    [ -e "$RB_QUIET" ] || { echo "QUIET: not raised (nothing to lower)"; exit 0; }
    read -r w o _ < "$RB_QUIET" 2>/dev/null
    if [ "${w:-}" = e200 ] && [ "${o:-}" = "$lane" ]; then rm -f -- "${RB_QUIET:?}" && echo "QUIET: lowered by $lane"; exit 0; fi
    echo "QUIET: the flag is not E200's for $lane ($(head -c 120 "$RB_QUIET" 2>/dev/null)): not removed"; exit 10 ;;
  check)
    need_flag
    if [ -f "$RB_QUIET" ]; then echo "QUIET: raised ($(head -c 120 "$RB_QUIET"))"; exit 0; fi
    echo "QUIET: not raised"; exit 10 ;;
  count)
    DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'   # lib.sh's DEV_COMM (k6's prelude)
    # shellcheck disable=SC1090
    . "$D/rb_e200.sh" >/dev/null 2>&1 || { echo "QUIET: rb_e200.sh did not load"; exit 10; }
    eval "$(e200_live_text)"
    tries=1; [ "$lane" = --wait ] && tries=5
    i=0
    while :; do
      i=$((i + 1))
      line=$(p2_count)
      echo "$(TZ=America/Los_Angeles date '+%T') $line"
      case "$line" in "P2 0 "*) exit 0 ;; esac
      [ "$i" -ge "$tries" ] && { echo "QUIET: the P2 count is not 0 after $i read(s): no launch (wait, bounded, or no session)"; exit 16; }
      sleep 2
    done ;;
  *) echo "usage: quiet_e200.sh raise|lower <lane> | check | count [--wait]"; exit 10 ;;
esac
