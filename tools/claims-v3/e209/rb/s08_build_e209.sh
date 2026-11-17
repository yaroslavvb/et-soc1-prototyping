#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): runbook step 6, THE BUILD: E208's src/build_mms.sh, unchanged, from
# the box root, detached under a plain `timeout 900` (never -k; it opens no device): rgm136 and the lab's ettelem against this box's
# /opt/et, nice 10, 2 jobs; THE KERNEL BY ITS BYTES (E136's pin aace138c..., a gate); the host's four refusals before it opens a device;
# build/BUILD-mms.json (the runner refuses any other record, or one not written today on this box). The host's sha256 depends on the box
# root's path (the host keeps its kernel's default path), so the gate is the kernel's bytes and the record of the day, as in E208.
#   RB_OUT=... E209_ROOT=... RB_QUIET=... RB_LANE=... bash tools/claims-v3/e209/rb/s08_build_e209.sh start     then
#   RB_OUT=... E209_ROOT=... bash tools/claims-v3/e209/rb/s08_build_e209.sh wait     (while 17)
# Exits: start 0 started, 10 refused (no flag, a build already started twice today, the box root's lock held); wait 0 MMS-BUILT (the
# kernel at its pin), 16 MMS-BUILD-FAILED or REFUSED (read RB_OUT/build.out: no card that day unless the reason is fixed in a new build
# within the limit), 17 still building (call again), 13 past 900 s.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init s08_build
e209_window
rb_root
case "${1:-}" in
  start)
    e209_quiet_ours
    n=$(ls "$RB_OUT"/build-start-* 2>/dev/null | wc -l)
    [ "$n" -lt 2 ] || rb_die 10 "two builds started today already (RB_OUT/build-start-*): no third"
    e209_box_free || rb_die 10 "the box root's lock is held (a session, a build or a dry pass of the kit)"
    t=$(rb_now); echo "$t" > "$RB_OUT/build-start-$t"
    ( cd "$E209_ROOT" && setsid nohup timeout 900 bash src/build_mms.sh > "$RB_OUT/build.out" 2>&1 < /dev/null & )
    sleep 2
    rb_ok "the build started (RB_OUT/build.out)" ;;
  wait)
    [ -f "$RB_OUT/build.out" ] || rb_die 10 "no build started in this RB_OUT"
    end=$(( $(rb_now) + E209_BOUND_S ))
    while :; do
      if grep -q '^MMS-BUILT rc=0' "$RB_OUT/build.out"; then
        grep -E '^(KERNEL|HOST|READER|HOSTCHECK)' "$RB_OUT/build.out"
        K=$(sha256sum "$E209_ROOT/build/rgm/kernel/sparsity.elf" | cut -c1-64)
        [ "$K" = aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0 ] || rb_die 16 "the kernel ELF is $K, not E136's pin"
        rb_ok "MMS-BUILT: the kernel at E136's pin; the record of today $(grep -o '"day": "[^"]*"' "$E209_ROOT/build/BUILD-mms.json")"
      fi
      grep -qE '^MMS-BUILD-(FAILED|REFUSED)' "$RB_OUT/build.out" && rb_die 16 "$(grep -E '^MMS-BUILD-(FAILED|REFUSED)' "$RB_OUT/build.out" | tail -n 1)"
      st=$(ls "$RB_OUT"/build-start-* | sort | tail -n 1); st=${st##*-}
      if [ $(( $(rb_now) - st )) -gt 900 ]; then rb_die 13 "past 900 s without its last line (read RB_OUT/build.out)"; fi
      [ "$(rb_now)" -lt "$end" ] || rb_die 17 "still building: call again"
      sleep 10
    done ;;
  *) rb_die 10 "usage: s08_build_e209.sh start|wait" ;;
esac
