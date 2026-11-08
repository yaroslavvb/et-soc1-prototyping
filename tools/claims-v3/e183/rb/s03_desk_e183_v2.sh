#!/usr/bin/env bash
# E183 (Q155, the kit's dated note 1), KIT.md box step 2 v2 (this file is s03 v2): the desk check before any box step, on the Intel only.
# It is step 2 v1 (rb/s03_desk_e183.sh, which stays as committed) with note 1's hash list added at its pinned count: THREE lists, each
# against its pinned count, with no override: the registration 20, the kit 46 and note 1 46 (SHA256SUMS-e183-note1: note 1's own files and
# the 29 files outside E183's directory that the runbook, the collector and the desk tests call, source, read or compile, which no E183
# list pinned before: the kit verifier's fault 3), each checked OK in full; and note 1's two desk tests' logs as committed (the reduction
# v2's self-test and the runbook v2 desk test). The step is named s03_desk_v2 in the runbook's log. Everything else is v1's, line for line.
#   bash tools/claims-v3/e183/rb/s03_desk_e183_v2.sh
# v1's words follow:
# E183 (Q155, the kit), KIT.md box step 2: the desk check before any box step, on the Intel only (E182's step 2 v4, ported): the window
# written today first (kit v5's lesson: step 1 before step 2, refused here otherwise); the pull; HEAD descends from c98a7287 (the
# registration, committed alone); E183's paths and workloads/enercat clean; the two hash lists at their pinned counts, with no override
# (the registration's and the kit's), each checked OK in full; harness-e183.json rebuilt; the registration's files, images, plan and
# schedule verified (e183_common.py --verify); the harness without binaries (check_e183.py harness); the build inputs at their pins
# (check_inputs_e183.py); the desk tests' logs as committed. It reports the october-forecast-model note M1 present or absent and any E183
# data in any ref (none is expected before the session).
#   bash tools/claims-v3/e183/rb/s03_desk_e183.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s03_desk_v2
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e183.sh first (kit v5: s02 before s03)"
  [ "$(date -r "$RB_OUT/window.env" +%F)" = "$(date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window was not written today: run s02_window_e183.sh first"
fi
E=tools/claims-v3/e183
LISTS="SHA256SUMS-e183-registration:20 SHA256SUMS-e183-kit:46 SHA256SUMS-e183-note1:46"     # v2: the pins
HARNESS_N=80
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_E183_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E183_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E183's paths and the workload clean" git -C "$RB_REPO" status --short tools/claims-v3/e183 workloads/enercat
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for spec in $LISTS; do
  l=${spec%%:*}; pin=${spec##*:}
  rb_local read local "the hash list $l (pinned at $pin entries)" shasum -a 256 -c "$E/$l"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$E/$l" 2>/dev/null); m=${m:-0}
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ]; } || bad="$bad $l($n OK of $m; pinned $pin)"
  fi
done
rb_local read local "harness-e183.json rebuilt" /usr/bin/python3 -B $E/make_harness_e183.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "the registration's files, images, plan and schedule (e183_common.py --verify)" /usr/bin/python3 -B $E/e183_common.py --verify
rb_has '^E183 VERIFY OK' || bad="$bad verify"
rb_local read local "the harness without binaries (check_e183.py harness)" /usr/bin/python3 -B $E/check_e183.py harness
rb_has "^HARNESS OK: $HARNESS_N files" || bad="$bad harness"
rb_local read local "the build inputs at their pins (check_inputs_e183.py)" /usr/bin/python3 -B $E/check_inputs_e183.py
rb_has '^BUILD INPUTS OK: 40 files' || bad="$bad build-inputs"
for spec in "logs/desktest-host-e183.txt ^DESKTEST-HOST-E183.PASS" "logs/selftest-score-e183.txt ^SELFTEST-SCORE-E183.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rb-e183.txt ^SELFTEST-RB-E183.[0-9]+.of.[0-9]+.PASS" "logs/dry-intel-e183.txt ^DRY-INTEL-E183.PASS" \
            "logs/selftest-score-e183-v2.txt ^SELFTEST-SCORE-E183-V2.[0-9]+.of.[0-9]+.PASS" "logs/selftest-rb-e183-v2.txt ^SELFTEST-RB-E183-V2.[0-9]+.of.[0-9]+.PASS"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
m1=absent; [ -f $E/E183.md.dated-note-M1.md ] && m1=present
rb_local read local "E183 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*-e183-*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
rb_say "desk check v2: the window written today, pulled, HEAD descends from $RB_E183_BASE, E183's paths and the workload clean, the three hash lists at their pinned counts (20, 46 and 46), harness-e183.json rebuilt, the registration verified, HARNESS OK $HARNESS_N, BUILD INPUTS OK 40, the six desk tests' logs; october-forecast-model note M1 $m1 ($([ "$m1" = present ] && echo 'scored beside, by its reader' || echo 'his pair only, by E180 M2 reader: E183.md section 8')); commits naming E183 data: $nd"
