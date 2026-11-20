#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E209's kit's rb/s08_build_e209.sh form): runbook step 6, THE BUILDS:
# E208's src/build_mms.sh, unchanged, then E220's src/build_e220b.sh, both from the box root, detached, each under a plain `timeout 900` (never
# -k; neither opens a device): rgm136 and the lab's ettelem against this box's /opt/et (nice 10, 2 jobs); THE KERNEL BY ITS BYTES (E136's pin
# aace138c..., a gate); the host's four refusals; build/BUILD-mms.json; then rgm211 from E211's sources at kernel-e220.json's pins into
# build/e220brgm211 (its host's eight refusals inside a bubblewrap with no card node; rgm136's ELF through the identity gate for both families,
# rgm211's own ELF refused by both); build/BUILD-e220b.json. E220's build runs only after E208's ended BUILT (it refuses otherwise). The hosts'
# sha256 depend on the box root's path (a host keeps its kernel's default path), so the gates are the kernel ELF's bytes and the records of
# the day, as in E208 and E209.
#   RB_OUT=... E220B_ROOT=... RB_QUIET=... RB_LANE=... bash tools/claims-v3/e220/rb/s08_build_e220b.sh start     then
#   RB_OUT=... E220B_ROOT=... bash tools/claims-v3/e220/rb/s08_build_e220b.sh wait     (while 17)
# Exits: start 0 started, 10 refused (no flag, builds already started twice today, the box root's lock held); wait 0 both BUILT (the kernel
# at its pin, rgm211's host gated), 16 a build FAILED or REFUSED (read RB_OUT/build.out: no card that day unless the reason is fixed in a new
# start within the limit), 17 still building (call again), 13 past 1800 s.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220b.sh"
rb_init s08_build
e220b_window
rb_root
case "${1:-}" in
  start)
    e220b_quiet_ours
    n=$(ls "$RB_OUT"/build-start-* 2>/dev/null | wc -l)
    [ "$n" -lt 2 ] || rb_die 10 "two builds started today already (RB_OUT/build-start-*): no third"
    e220b_box_free || rb_die 10 "the box root's lock is held (a session, a build or a dry pass of the kit)"
    t=$(rb_now); echo "$t" > "$RB_OUT/build-start-$t"
    ( setsid nohup bash "$RB_E220B_DIR/s08_builds_e220b.sh" "$E220B_ROOT" > "$RB_OUT/build.out" 2>&1 < /dev/null & )
    sleep 2
    rb_ok "the builds started (RB_OUT/build.out)" ;;
  wait)
    [ -f "$RB_OUT/build.out" ] || rb_die 10 "no build started in this RB_OUT"
    end=$(( $(rb_now) + E220B_BOUND_S ))
    while :; do
      if grep -q '^MMS-BUILT rc=0' "$RB_OUT/build.out" && grep -q '^E220-BUILT rc=0' "$RB_OUT/build.out"; then
        grep -E '^(KERNEL|HOST|READER|HOSTCHECK|GATE|IDENT|SOURCES)' "$RB_OUT/build.out"
        K=$(sha256sum "$E220B_ROOT/build/rgm/kernel/sparsity.elf" | cut -c1-64)
        [ "$K" = aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0 ] || rb_die 16 "the kernel ELF is $K, not E136's pin"
        rb_ok "MMS-BUILT and E220-BUILT: the kernel at E136's pin, rgm211's host gated for family G; the records of today $(grep -o '"day": "[^"]*"' "$E220B_ROOT/build/BUILD-mms.json") $(grep -o '"day": "[^"]*"' "$E220B_ROOT/build/BUILD-e220b.json")"
      fi
      grep -qE '^(MMS|E220)-BUILD-(FAILED|REFUSED)' "$RB_OUT/build.out" && rb_die 16 "$(grep -E '^(MMS|E220)-BUILD-(FAILED|REFUSED)' "$RB_OUT/build.out" | tail -n 1)"
      st=$(ls "$RB_OUT"/build-start-* | sort | tail -n 1); st=${st##*-}
      if [ $(( $(rb_now) - st )) -gt 1800 ]; then rb_die 13 "past 1800 s without both last lines (read RB_OUT/build.out)"; fi
      [ "$(rb_now)" -lt "$end" ] || rb_die 17 "still building: call again"
      sleep 10
    done ;;
  *) rb_die 10 "usage: s08_build_e220b.sh start|wait" ;;
esac
