#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "the dry pass" (this file is s10): session_e195.sh --dry
# on aifoundry3: every refusal and pin before anything (the host's name, USER, the window, the stop files, the harness at the sha256 the lab
# clone's committed harness-e195.json has, today's build record, the preflight GO), then each block with V3_DRY=1 (every device call
# printed by the kit's runner, nothing opened: no et-who, no lock, no config read, no sampler, no heater, no host), the listing checked
# against the kit's committed listing for aifoundry3 (check_e195.py dry: "E195-DRY OK: 288 device calls"). Its files go to
# build/e195/T<T0>-dry/ and E195's root's build/claims-v3-dry/ (every rest rule skips "-dry" paths and its "DRY" lines). As k6's detached
# job a3-dry-e195 (one at a time, never beside a session of ours; --dry on its command line, which k6's ours_live skips), then `wait`
# (bounded; 17 while it runs: about 3 minutes, the registered 15 s between passes included).
#   bash tools/claims-v3/e195/rb/s10_a3_dry_e195.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
rb_init s10_a3_dry
act=${1:-}
JOB=a3-dry-e195
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e195.sh start | wait" ;; esac
e195_window
[ -n "${RB_DRY:-}" ] || [ -n "$(e195_built)" ] || rb_die $RB_E_USAGE "E195 was not built today (RB_OUT/e195-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  body=$(rb_file body)
  { echo "ER=$E195_R; HS=$(e195_harness_sha); LS=${RB_LAST_START_EPOCH:-0}; LE=${RB_LAST_END_EPOCH:-0}"
    cat <<'EOF2'
mkdir -p build/e195; T0=$(date +%s)
E195_T0=$T0 X9_LATEST_START=@$LS X9_DEADLINE=@$LE E195_HARNESS_SHA256=$HS bash "$ER/tools/claims-v3/e195/session_e195.sh" --dry > "build/e195/launch-T$T0-dry.out" 2>&1
rc=$?
grep -E 'refused|E195-DRY|GATE-STOP|session end' "build/e195/T$T0-dry/session.log" | cut -c1-260
echo "E195-DRY-PASS rc=$rc T0=$T0"
[ "$rc" -eq 0 ] && grep -q 'E195-DRY OK: 288 device calls' "build/e195/T$T0-dry/session.log"
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
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 -o 'E195-DRY OK: [0-9]* device calls' "$RB_CAP")"; exit 0; }
exit "$rc"
