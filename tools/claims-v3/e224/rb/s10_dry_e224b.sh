#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E209's kit's rb/s10_dry_e209.sh form): runbook step 8, THE DRY PASS: the box root's src/dry_e224b.sh (src/run_e224b.py
# in its --dry mode with E208's doubles and rgm211's host's double: no device node opened, no card lock taken; scale 0.02; the identity
# gate reads the box root's built ELF, so step 6 first), detached: E224 arm B's 105 runs in the registered order, every device call printed (dry/<T0>-a2c0-E224/device-calls.txt); DRY PASS when every run started, every process
# rc 0 with its check exact or approx, the order kept and the manifest written.
#   RB_OUT=... E224B_ROOT=... RB_QUIET=... RB_LANE=... bash tools/claims-v3/e224/rb/s10_dry_e224b.sh start      then
#   RB_OUT=... E224B_ROOT=... bash tools/claims-v3/e224/rb/s10_dry_e224b.sh wait      (while 17)
# Exits: start 0 started, 10 refused; wait 0 DRY PASS, 16 DRY FAIL or DRY REFUSED (read RB_OUT/dry.out), 17 still running, 13 past 900 s.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224b.sh"
rb_init s10_dry
e224b_window
rb_root
case "${1:-}" in
  start)
    e224b_quiet_ours
    [ -f "$E224B_ROOT/build/BUILD-mms.json" ] && [ -f "$E224B_ROOT/build/BUILD-e224b.json" ] || rb_die 10 "no build record (E208's and E224's): step 6 first"
    e224b_box_free || rb_die 10 "the box root's lock is held"
    t=$(rb_now); echo "$t" > "$RB_OUT/dry-start-$t"
    ( cd "$E224B_ROOT" && setsid nohup timeout 900 bash src/dry_e224b.sh 0.02 > "$RB_OUT/dry.out" 2>&1 < /dev/null & )
    sleep 2
    rb_ok "the dry pass started (RB_OUT/dry.out)" ;;
  wait)
    [ -f "$RB_OUT/dry.out" ] || rb_die 10 "no dry pass started in this RB_OUT"
    end=$(( $(rb_now) + E224B_BOUND_S ))
    while :; do
      grep -q '^DRY PASS ' "$RB_OUT/dry.out" && { tail -n 3 "$RB_OUT/dry.out"; rb_ok "DRY PASS"; }
      grep -qE '^DRY (FAIL|REFUSED)' "$RB_OUT/dry.out" && rb_die 16 "$(grep -E '^DRY (FAIL|REFUSED)' "$RB_OUT/dry.out" | tail -n 1)"
      st=$(ls "$RB_OUT"/dry-start-* | sort | tail -n 1); st=${st##*-}
      if [ $(( $(rb_now) - st )) -gt 900 ]; then rb_die 13 "past 900 s without its last line (read RB_OUT/dry.out)"; fi
      [ "$(rb_now)" -lt "$end" ] || rb_die 17 "the dry pass runs still: call again"
      sleep 5
    done ;;
  *) rb_die 10 "usage: s10_dry_e224b.sh start|wait" ;;
esac
