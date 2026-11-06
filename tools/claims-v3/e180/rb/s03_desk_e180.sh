#!/usr/bin/env bash
# E180 (Q146(f), the kit), step 3: the desk check before any box step, on the Intel only: the lab clone pulled; HEAD descends from
# RB_E180_BASE (4dc5035f, the registration); E180's paths clean; the registration's hash list (71 OK) and the kit's (SHA256SUMS-e180-kit,
# every entry OK); the kit's own rebuild check (make_harness_e180.py --check); the plan and the forecasts re-made byte for byte
# (plan_e180.py --check, forecast_e180.py --check); the harness without binaries (check_e180.py harness). Reported, not a gate: whether a
# dated note in section 8's form (october-forecast-model) is committed, and that no E180 data is in any ref. tools/claims-v3/e178/rb/
# s03_desk_e178.sh's form.
#
#   bash tools/claims-v3/e180/rb/s03_desk_e180.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s03_desk
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_E180_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E180_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E180's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e180
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for spec in "SHA256SUMS-e180-registration 71" "SHA256SUMS-e180-kit 0"; do
  set -- $spec
  rb_local read local "the hash list $1" shasum -a 256 -c "tools/claims-v3/e180/$1"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "tools/claims-v3/e180/$1")
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && { [ "$2" -eq 0 ] || [ "$n" -eq "$2" ]; }; } || bad="$bad $1($n of $m)"
  fi
done
rb_local read local "harness-e180.json rebuilt" "$RB_PY" -B tools/claims-v3/e180/make_harness_e180.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "the plan re-made (plan_e180.py --check)" "$RB_PY" -B tools/claims-v3/e180/plan_e180.py --dir tools/claims-v3/e180 --check
rb_has '^CHECK PASS' || bad="$bad plan"
rb_local read local "the forecasts re-made (forecast_e180.py --check)" "$RB_PY" -B tools/claims-v3/e180/forecast_e180.py --dir tools/claims-v3/e180 --check
rb_has '^CHECK PASS' || bad="$bad forecast"
rb_local read local "the harness without binaries (check_e180.py harness)" "$RB_PY" -B tools/claims-v3/e180/check_e180.py harness
rb_has '^HARNESS OK: ' || bad="$bad harness"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
ofm=absent; ls tools/claims-v3/e180/E180.md.dated-note-*.md > /dev/null 2>&1 && grep -lq 'october-forecast-model, frozen' tools/claims-v3/e180/E180.md.dated-note-*.md 2>/dev/null && ofm=present
rb_local read local "E180 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e180*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
rb_say "desk check: pulled, HEAD descends from $RB_E180_BASE, E180's paths clean, the two hash lists, the harness rebuilt, the plan and forecasts re-made, HARNESS OK; october-forecast-model freeze $ofm; commits naming E180 data: $nd"
