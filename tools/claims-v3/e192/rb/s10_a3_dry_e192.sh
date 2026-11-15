#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum), the box step "the dry pass" (this file is s10): session_e192.sh --dry
# on aifoundry3: every refusal before anything (the host's name, USER, the pins, the binaries, the preflight), then the proposal's
# reference session in its DRY mode (every device call printed, nothing opened: no et-who, no lock, no sampler, no heater, no host) read by
# drycheck_e192.py (328 device calls, every one under timeout 10 with --stop-file, the order the registration writes out for aifoundry3).
# Its files go to build/e192/T<T0>-dry/ (every rest rule skips "-dry" paths and its "DRY" lines). As k6's detached job a3-dry-e192 (one at a
# time, never beside a session of ours; --dry on its command line, which k6's ours_live skips), then `wait` (bounded; 17 while it runs).
#   bash tools/claims-v3/e192/rb/s10_a3_dry_e192.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e192.sh"
rb_init s10_a3_dry
act=${1:-}
JOB=a3-dry-e192
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e192.sh start | wait" ;; esac
e192_window
[ -n "${RB_DRY:-}" ] || [ -n "$(e192_built)" ] || rb_die $RB_E_USAGE "E192 was not built today (RB_OUT/e192-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  body=$(rb_file body)
  { echo "ER=$E192_R; KLS=$(e192_kitlist_sha)"
    cat <<'EOF2'
T0=$(date +%s)
E192_T0=$T0 E192_KITLIST_SHA256=$KLS bash "$ER/tools/claims-v3/e192/session_e192.sh" --dry > /dev/null 2>&1
rc=$?
grep -E 'refused|E192-DRY|session end' "build/e192/T$T0-dry/session.log" | cut -c1-260
echo "E192-DRY-PASS rc=$rc T0=$T0"
[ "$rc" -eq 0 ] && grep -q 'E192-DRY OK: 328 device calls' "build/e192/T$T0-dry/session.log"
EOF2
  } > "$body"
  rb_job_start aifoundry3 "$JOB" "$body"
  rb_say "the dry pass $JOB started on aifoundry3: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe aifoundry3
rb_job_wait aifoundry3 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 -o 'E192-DRY OK: [^;]*' "$RB_CAP")"; exit 0; }
exit "$rc"
