#!/usr/bin/env bash
# E182 (Q153, the kit), step 3: the desk check before any box step, on the Intel only. A port of E178's step 3 v2
# (tools/claims-v3/e178/rb/s03_desk_e178_v2.sh) with E182's files, and kit v5's first lesson: it REFUSES (10) unless step 2 has written
# today's window in RB_OUT (s02 before s03; E181's card day ran s03 before s02). Then: the pull; HEAD descends from 58b88850 (E182's
# registration); E182's paths clean; the two hash lists, each with its count (the registration's 32, the kit's); the harness rebuilt;
# the items, orders and trains verified; HARNESS OK without binaries; the train host's desk test log present. The october-forecast-model
# note (E182.md section 8) and any E182 data in any ref are reported, not gated.
#
#   bash tools/claims-v3/e182/rb/s03_desk_e182.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s03_desk
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e182.sh first (kit v5: s02 before s03)"
  [ "$(date -r "$RB_OUT/window.env" +%F)" = "$(date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window was not written today: run s02_window_e182.sh first"
fi
KITN=${E182_KIT_N:-$(grep -c . tools/claims-v3/e182/SHA256SUMS-e182-kit 2>/dev/null)}
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_E182_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E182_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E182's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e182
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for spec in "SHA256SUMS-e182-registration 32" "SHA256SUMS-e182-kit $KITN"; do
  set -- $spec
  rb_local read local "the hash list $1" shasum -a 256 -c "tools/claims-v3/e182/$1"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "tools/claims-v3/e182/$1")
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -gt 0 ] && [ "$n" -eq "$2" ]; } || bad="$bad $1($n of $m)"
  fi
done
rb_local read local "harness-e182.json rebuilt" /usr/bin/python3 -B tools/claims-v3/e182/make_harness_e182.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "the items, the registered orders and the trains (e182_common.py --verify)" /usr/bin/python3 -B tools/claims-v3/e182/e182_common.py --verify
rb_has '"problems": \[\]' || bad="$bad items"
rb_local read local "the harness without binaries (check_e182.py --desk)" /usr/bin/python3 -B tools/claims-v3/e182/check_e182.py --desk
rb_has '^HARNESS OK: 66 files' || bad="$bad harness"
rb_local read local "the train host's desk test, as committed" grep -c '^DESKTEST-HOST-E182 25 of 25 PASS' tools/claims-v3/e182/logs/desktest-host-e182.txt
rb_has '^1$' || bad="$bad host-desktest"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
m1=absent; [ -f tools/claims-v3/e182/E182.md.dated-note-M1.md ] && m1=present
rb_local read local "E182 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*-e182-*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
rb_say "desk check: the window written today, pulled, HEAD descends from $RB_E182_BASE, E182's paths clean, the two hash lists (32 and $KITN), the harness rebuilt, the orders and trains verified, HARNESS OK 66, the host desk test 25 of 25; october-forecast-model note M1 $m1 ($([ "$m1" = present ] && echo 'scored beside, by its reader' || echo 'not scored: E182.md section 8')); commits naming E182 data: $nd"
