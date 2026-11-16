#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), the box step "the dry pass" (this file is s10): session_e196.sh
# --dry on aifoundry3: every refusal before anything (the host's name, USER, the pins, today's build record and both hosts, the preflight,
# the node count), then the port's DRY mode twice, the full plan and the cut order (every device call printed, nothing opened: no et-who,
# no lock, no configuration read, no sampler, no host), read by drycheck_e196.py (255 device calls, 237 cut, line for line the registered
# commands in the written orders, every one under timeout 10 with --stop-file). Its files go to build/e196/T<T0>-dry/ (every rest rule skips
# "-dry" paths and its "DRY" lines). E192's step 8's form (tools/claims-v3/e192/rb/s10_a3_dry_e192.sh): k6's detached job a3-dry-e196 (one at
# a time, never beside a session of ours; --dry on its command line, which k6's ours_live skips), then `wait` (bounded; 17 while it runs).
#   bash tools/claims-v3/e196/rb/s10_a3_dry_e196.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e196.sh"
rb_init s10_a3_dry
act=${1:-}
JOB=a3-dry-e196
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e196.sh start | wait" ;; esac
e196_window
[ -n "${RB_DRY:-}" ] || [ -n "$(e196_built)" ] || rb_die $RB_E_USAGE "E196 was not built today (RB_OUT/e196-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  body=$(rb_file body)
  { echo "ER=$E196_R; KLS=$(e196_kitlist_sha)"
    cat <<'EOF2'
T0=$(date +%s)
E196_T0=$T0 E196_KITLIST_SHA256=$KLS bash "$ER/tools/claims-v3/e196/session_e196.sh" --dry > /dev/null 2>&1
rc=$?
grep -E 'refused|E196-DRY|session end' "build/e196/T$T0-dry/session.log" | cut -c1-260
echo "E196-DRY-PASS rc=$rc T0=$T0"
[ "$rc" -eq 0 ] && grep -q 'E196-DRY OK: 255 device calls (237 with the cut order)' "build/e196/T$T0-dry/session.log"
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
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 -o 'E196-DRY OK: [^;]*' "$RB_CAP")"; exit 0; }
exit "$rc"
