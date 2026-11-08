#!/usr/bin/env bash
# E182 (Q154, the kit's dated note 2), KIT.md box step 2 v3 (this file is s03 v3): the desk check before any box step, on the Intel only.
# It is step 2 v2 (rb/s03_desk_e182_v2.sh, which stays as committed) with every hash list's count PINNED here: v2 pinned only the
# registration's 32 and read the kit's and note 1's counts from the lists themselves (`grep -c .`), so a list that lost a line still
# matched its own count (the Q153 critic's fault 3). v3 checks FOUR lists, each against its pinned count: the registration 32, the kit 79,
# note 1 50 and note 2 49 (SHA256SUMS-e182-note2), with no override. Everything else is v2's, line for line (the window written today
# first, kit v5's lesson; the pull; HEAD descends from 58b88850; E182's paths and the workload clean; both harness files rebuilt; the
# items' check; HARNESS OK 66; NOTE1 FILES OK 10; note 1's four desk tests' logs; the october-forecast-model note and any E182 data in
# any ref reported), plus note 2's two desk-test logs: the runbook v3 desk test and the v2 desk test re-run with note 2.
#
#   bash tools/claims-v3/e182/rb/s03_desk_e182_v3.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s03_desk_v3
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e182.sh first (kit v5: s02 before s03)"
  [ "$(date -r "$RB_OUT/window.env" +%F)" = "$(date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window was not written today: run s02_window_e182.sh first"
fi
E=tools/claims-v3/e182
LISTS="SHA256SUMS-e182-registration:32 SHA256SUMS-e182-kit:79 SHA256SUMS-e182-note1:50 SHA256SUMS-e182-note2:49"   # v3: the pins
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_E182_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E182_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E182's paths and the workload clean" git -C "$RB_REPO" status --short tools/claims-v3/e182 workloads/sparsity
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for spec in $LISTS; do
  l=${spec%%:*}; pin=${spec##*:}
  rb_local read local "the hash list $l (pinned at $pin entries)" shasum -a 256 -c "$E/$l"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$E/$l" 2>/dev/null); m=${m:-0}
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ]; } || bad="$bad $l($n OK of $m; pinned $pin)"
  fi
done
rb_local read local "harness-e182.json rebuilt" /usr/bin/python3 -B $E/make_harness_e182.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "harness-e182-note1.json rebuilt (note 1)" /usr/bin/python3 -B $E/make_harness_e182_note1.py --check
rb_has '^CHECK PASS' || bad="$bad note1-harness-rebuild"
rb_local read local "the items, the registered orders and the trains (e182_common.py --verify)" /usr/bin/python3 -B $E/e182_common.py --verify
rb_has '"problems": \[\]' || bad="$bad items"
rb_local read local "the harness without binaries (check_e182.py --desk)" /usr/bin/python3 -B $E/check_e182.py --desk
rb_has '^HARNESS OK: 66 files' || bad="$bad harness"
rb_local read local "the build inputs and note 1's box files (check_inputs_e182.py)" /usr/bin/python3 -B $E/check_inputs_e182.py
rb_has '^NOTE1 FILES OK: 10 files' || bad="$bad note1-files"
for spec in "logs/desktest-host-e182.txt ^DESKTEST-HOST-E182.25.of.25.PASS" "logs/selftest-rb-e182-v2.txt ^SELFTEST-RB-E182-V2.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-stops-e182t.txt ^SELFTEST-STOPS-E182T.[0-9]+.of.[0-9]+.PASS" "logs/note1-checks-e182.txt ^NOTE1-CHECKS-E182.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rb-e182-v3.txt ^SELFTEST-RB-E182-V3.[0-9]+.of.[0-9]+.PASS" "logs/selftest-rb-e182-v2-note2.txt ^SELFTEST-RB-E182-V2.[0-9]+.of.[0-9]+.PASS"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
m1=absent; [ -f $E/E182.md.dated-note-M1.md ] && m1=present
rb_local read local "E182 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*-e182-*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
rb_say "desk check v3: the window written today, pulled, HEAD descends from $RB_E182_BASE, E182's paths and the workload clean, the four hash lists at their pinned counts (32, 79, 50 and 49), both harness files rebuilt, the orders and trains verified, HARNESS OK 66, NOTE1 FILES OK 10, the six desk tests' logs; october-forecast-model note M1 $m1 ($([ "$m1" = present ] && echo 'scored beside, by its reader' || echo 'not scored: E182.md section 8')); commits naming E182 data: $nd"
