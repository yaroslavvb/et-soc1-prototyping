#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, ../KIT.md.dated-note-1.md section 6), step 3, v2: the desk check before any box step, on the Intel
# only. It replaces s03_desk_e180.sh (v1, which stays as committed) in the runbook, with three changes:
#   1. HEAD must descend from 879197e3 (the registration's dated note A1, required before any datum), not only from the registration;
#   2. the hash lists are four, each with its count: the registration's (71) and the kit's, now pinned at 55 (v1 took any count), as v1;
#      A1's (SHA256SUMS-e180-a1, 41); and the kit's dated note 1's own (SHA256SUMS-e180-kit-note1, 90), which holds the v2 files the
#      session and the runbook now run;
#   3. the harness is v2's: make_harness_e180_v2.py --check, and check_e180_v2.py harness without binaries.
# Everything else is v1's, line for line: the pull, E180's paths clean, the plan and the forecasts re-made, the october-forecast-model
# freeze and any E180 data in any ref reported, not gated.
#
#   bash tools/claims-v3/e180/rb/s03_desk_e180_v2.sh
# SPDX-License-Identifier: Apache-2.0
RB_E180_BASE=${RB_E180_BASE:-879197e3}
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s03_desk_v2
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_E180_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E180_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E180's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e180
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for spec in "SHA256SUMS-e180-registration 71" "SHA256SUMS-e180-kit 55" "SHA256SUMS-e180-a1 41" "SHA256SUMS-e180-kit-note1 90"; do
  set -- $spec
  rb_local read local "the hash list $1" shasum -a 256 -c "tools/claims-v3/e180/$1"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "tools/claims-v3/e180/$1")
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -gt 0 ] && [ "$n" -eq "$2" ]; } || bad="$bad $1($n of $m)"
  fi
done
rb_local read local "harness-e180-v2.json rebuilt" "$RB_PY" -B tools/claims-v3/e180/make_harness_e180_v2.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "the plan re-made (plan_e180.py --check)" "$RB_PY" -B tools/claims-v3/e180/plan_e180.py --dir tools/claims-v3/e180 --check
rb_has '^CHECK PASS' || bad="$bad plan"
rb_local read local "the forecasts re-made (forecast_e180.py --check)" "$RB_PY" -B tools/claims-v3/e180/forecast_e180.py --dir tools/claims-v3/e180 --check
rb_has '^CHECK PASS' || bad="$bad forecast"
rb_local read local "the harness without binaries (check_e180_v2.py harness)" "$RB_PY" -B tools/claims-v3/e180/check_e180_v2.py harness
rb_has '^HARNESS OK: ' || bad="$bad harness"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
ofm=absent; ls tools/claims-v3/e180/E180.md.dated-note-*.md > /dev/null 2>&1 && grep -lq 'october-forecast-model, frozen' tools/claims-v3/e180/E180.md.dated-note-*.md 2>/dev/null && ofm=present
rb_local read local "E180 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e180*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
rb_say "desk check (v2): pulled, HEAD descends from $RB_E180_BASE (A1), E180's paths clean, the four hash lists (71, 55, 41 and 90), harness v2 rebuilt, the plan and forecasts re-made, HARNESS OK (v2); october-forecast-model freeze $ofm; commits naming E180 data: $nd"
