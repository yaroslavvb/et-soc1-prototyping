#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum; E192's file, a6fe5c20, unchanged beside it, ported to aifoundry1 card 1), the box step "the dry pass" (this file is s10): session_e199.sh --dry
# on aifoundry1: every refusal before anything (the host's name, USER, the pins, the binaries, the preflight), then the proposal's
# reference session in its DRY mode (every device call printed, nothing opened: no et-who, no lock, no sampler, no heater, no host) read by
# drycheck_e199.py (328 device calls, every one under timeout 10 with --stop-file, the order the registration writes out for aifoundry1).
# Its files go to build/e199/T<T0>-dry/ (every rest rule skips "-dry" paths and its "DRY" lines). As k6's detached job a1-dry-e199 (one at a
# time, never beside a session of ours; --dry on its command line, which k6's ours_live skips), then `wait` (bounded; 17 while it runs).
#   bash tools/claims-v3/e199/rb/s10_a1_dry_e199.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e199.sh"
rb_init s10_a1_dry
act=${1:-}
JOB=a1-dry-e199
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a1_dry_e199.sh start | wait" ;; esac
e199_window
[ -n "${RB_DRY:-}" ] || [ -n "$(e199_built)" ] || rb_die $RB_E_USAGE "E199 was not built today (RB_OUT/e199-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry1
  body=$(rb_file body)
  { echo "ER=$E199_R; KLS=$(e199_kitlist_sha)"
    cat <<'EOF2'
T0=$(date +%s)
E199_T0=$T0 E199_KITLIST_SHA256=$KLS bash "$ER/tools/claims-v3/e199/session_e199.sh" --dry > /dev/null 2>&1
rc=$?
grep -E 'refused|E199-DRY|session end' "build/e199/T$T0-dry/session.log" | cut -c1-260
echo "E199-DRY-PASS rc=$rc T0=$T0"
[ "$rc" -eq 0 ] && grep -q 'E199-DRY OK: 328 device calls' "build/e199/T$T0-dry/session.log"
EOF2
  } > "$body"
  rb_job_start aifoundry1 "$JOB" "$body"
  rb_say "the dry pass $JOB started on aifoundry1: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe aifoundry1
rb_job_wait aifoundry1 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 -o 'E199-DRY OK: [^;]*' "$RB_CAP")"; exit 0; }
exit "$rc"
