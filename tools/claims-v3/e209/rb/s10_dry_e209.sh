#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): runbook step 8, THE DRY PASS: the box root's src/dry_e209.sh (E208's
# runner in its --dry mode with E208's doubles: no device node opened, no card lock taken; scale 0.02), detached: E209's 62 runs in the
# registered order, every device call printed (dry/<T0>-a2c0-E209/device-calls.txt); DRY PASS when every run started, every process
# rc 0 with its check exact or approx, the order kept and the manifest written.
#   RB_OUT=... E209_ROOT=... RB_QUIET=... RB_LANE=... bash tools/claims-v3/e209/rb/s10_dry_e209.sh start      then
#   RB_OUT=... E209_ROOT=... bash tools/claims-v3/e209/rb/s10_dry_e209.sh wait      (while 17)
# Exits: start 0 started, 10 refused; wait 0 DRY PASS, 16 DRY FAIL or DRY REFUSED (read RB_OUT/dry.out), 17 still running, 13 past 900 s.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init s10_dry
e209_window
rb_root
case "${1:-}" in
  start)
    e209_quiet_ours
    [ -f "$E209_ROOT/build/BUILD-mms.json" ] || rb_die 10 "no build record: step 6 first"
    e209_box_free || rb_die 10 "the box root's lock is held"
    t=$(rb_now); echo "$t" > "$RB_OUT/dry-start-$t"
    ( cd "$E209_ROOT" && setsid nohup timeout 900 bash src/dry_e209.sh 0.02 > "$RB_OUT/dry.out" 2>&1 < /dev/null & )
    sleep 2
    rb_ok "the dry pass started (RB_OUT/dry.out)" ;;
  wait)
    [ -f "$RB_OUT/dry.out" ] || rb_die 10 "no dry pass started in this RB_OUT"
    end=$(( $(rb_now) + E209_BOUND_S ))
    while :; do
      grep -q '^DRY PASS ' "$RB_OUT/dry.out" && { tail -n 3 "$RB_OUT/dry.out"; rb_ok "DRY PASS"; }
      grep -qE '^DRY (FAIL|REFUSED)' "$RB_OUT/dry.out" && rb_die 16 "$(grep -E '^DRY (FAIL|REFUSED)' "$RB_OUT/dry.out" | tail -n 1)"
      st=$(ls "$RB_OUT"/dry-start-* | sort | tail -n 1); st=${st##*-}
      if [ $(( $(rb_now) - st )) -gt 900 ]; then rb_die 13 "past 900 s without its last line (read RB_OUT/dry.out)"; fi
      [ "$(rb_now)" -lt "$end" ] || rb_die 17 "the dry pass runs still: call again"
      sleep 5
    done ;;
  *) rb_die 10 "usage: s10_dry_e209.sh start|wait" ;;
esac
