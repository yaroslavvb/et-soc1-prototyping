#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1), step 3 v2: the desk check before any box step, on the Intel only. It is v1 (rb/s03_desk_e182.sh,
# which stays as committed) with note 1's files added: THREE hash lists, each with its count (the registration's 32, the kit's 79, note
# 1's), harness-e182-note1.json rebuilt from the committed files (make_harness_e182_note1.py --check), the build inputs and note 1's box
# files at their pins in the lab clone (check_inputs_e182.py, NOTE1 FILES OK 10), and note 1's three desk tests' logs as committed (the
# v2 runbook test, the train runner's stops, the half-widths and labels). Kit v5's first lesson is v1's: it REFUSES (10) unless step 2
# has written today's window in RB_OUT. The october-forecast-model note and any E182 data in any ref are reported, not gated, as in v1.
#
#   bash tools/claims-v3/e182/rb/s03_desk_e182_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s03_desk_v2
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e182.sh first (kit v5: s02 before s03)"
  [ "$(date -r "$RB_OUT/window.env" +%F)" = "$(date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window was not written today: run s02_window_e182.sh first"
fi
E=tools/claims-v3/e182
KITN=${E182_KIT_N:-$(grep -c . $E/SHA256SUMS-e182-kit 2>/dev/null)}
N1N=${E182_NOTE1_N:-$(grep -c . $E/SHA256SUMS-e182-note1 2>/dev/null)}
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_E182_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E182_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E182's paths and the workload clean" git -C "$RB_REPO" status --short tools/claims-v3/e182 workloads/sparsity
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for spec in "SHA256SUMS-e182-registration 32" "SHA256SUMS-e182-kit $KITN" "SHA256SUMS-e182-note1 $N1N"; do
  set -- $spec
  rb_local read local "the hash list $1" shasum -a 256 -c "$E/$1"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$E/$1")
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -gt 0 ] && [ "$n" -eq "$2" ]; } || bad="$bad $1($n of $m)"
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
            "logs/selftest-stops-e182t.txt ^SELFTEST-STOPS-E182T.[0-9]+.of.[0-9]+.PASS" "logs/note1-checks-e182.txt ^NOTE1-CHECKS-E182.[0-9]+.of.[0-9]+.PASS"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
m1=absent; [ -f $E/E182.md.dated-note-M1.md ] && m1=present
rb_local read local "E182 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*-e182-*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
rb_say "desk check v2: the window written today, pulled, HEAD descends from $RB_E182_BASE, E182's paths and the workload clean, the three hash lists (32, $KITN and $N1N), both harness files rebuilt, the orders and trains verified, HARNESS OK 66, NOTE1 FILES OK 10, the four desk tests' logs; october-forecast-model note M1 $m1 ($([ "$m1" = present ] && echo 'scored beside, by its reader' || echo 'not scored: E182.md section 8')); commits naming E182 data: $nd"
