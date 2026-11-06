#!/usr/bin/env bash
# E178 (Q146; the kit's dated note 1, ../KIT.md.dated-note-1.md section 6), step 3, v2: the desk check before any box step, on the Intel
# only. It replaces s03_desk_e178.sh (v1, which stays as committed) in the runbook, with two changes:
#   1. HEAD must descend from c212a345 (E178's dated note A2, 00:05:00 PST Fri 6 Nov 2026, required before any datum), not only from A1;
#   2. the hash lists are five, each with its count: the registration's (76) and A1's (27), as v1; the kit's, now pinned at 72 (v1 took
#      any count); A2's (17); and dated note 1's own (SHA256SUMS-e178-kit-note1, 47), which holds the v2 steps the runbook now runs.
# Everything else is v1's, line for line: the pull, E178's paths clean, the kit and harness rebuilt, the items and orders, HARNESS OK 80
# without binaries; dated note M1 and any E178 data in any ref reported, not gated.
#
#   bash tools/claims-v3/e178/rb/s03_desk_e178_v2.sh
# SPDX-License-Identifier: Apache-2.0
RB_E178_BASE=${RB_E178_BASE:-c212a345}
. "$(dirname "${BASH_SOURCE[0]}")/rb_e178.sh"
rb_init s03_desk_v2
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_E178_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E178_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E178's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e178
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for spec in "SHA256SUMS-e178-registration 76" "SHA256SUMS-e178-a1 27" "SHA256SUMS-e178-kit 72" "SHA256SUMS-e178-a2 17" \
            "SHA256SUMS-e178-kit-note1 47"; do
  set -- $spec
  rb_local read local "the hash list $1" shasum -a 256 -c "tools/claims-v3/e178/$1"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "tools/claims-v3/e178/$1")
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -gt 0 ] && { [ "$2" -eq 0 ] || [ "$n" -eq "$2" ]; }; } || bad="$bad $1($n of $m)"
  fi
done
rb_local read local "kit-e178.json rebuilt" "$RB_PY" -B tools/claims-v3/e178/make_kit_e178.py --check
rb_has '^CHECK PASS' || bad="$bad kit"
rb_local read local "harness-e178.json rebuilt" "$RB_PY" -B tools/claims-v3/e178/make_harness_e178.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "the items and the registered orders (e178_common.py --verify)" "$RB_PY" -B tools/claims-v3/e178/e178_common.py --verify
rb_has '"problems": \[\]' || bad="$bad items"
rb_local read local "the harness without binaries (check_e178.py --desk)" "$RB_PY" -B tools/claims-v3/e178/check_e178.py --desk
rb_has '^HARNESS OK: 80 files' || bad="$bad harness"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
m1=absent; [ -f tools/claims-v3/e178/E178.md.dated-note-M1.md ] && m1=present
rb_local read local "E178 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e178*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
rb_say "desk check: pulled, HEAD descends from $RB_E178_BASE (A2), E178's paths clean, the five hash lists (76, 27, 72, 17 and 47), the kit and harness rebuilt, the orders verified, HARNESS OK 80; dated note M1 $m1 ($([ "$m1" = present ] && echo 'the october-forecast-model forecast is scored beside, by its sha256' || echo 'the october-forecast-model forecast is not scored here, E178.md section 8 and A2')); commits naming E178 data: $nd"
