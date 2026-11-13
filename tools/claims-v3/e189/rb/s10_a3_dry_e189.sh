#!/usr/bin/env bash
# E189 (Q167, the kit), the box step "the dry pass" (this file is s10): run_e189.py's whole session path on aifoundry3 with its doubles,
# no device: energy_stub.py's alt sampler (E189's card-free double of `ettelem sample`), fake_card_e189.py's hosts, config and et-who, a lock
# file in its own directory, every line DRY, its files in build/e189/T<T0>-dry/ (the rest rule skips it). One pass of each configuration
# the day will run (the programs step 6 built today), the stop-path test and the ramped smoke, each launch at 20% of the forecast's seconds
# and 1 s idles. As k6's detached job a3-dry-e189 (one at a time, never beside a session of ours), then `wait` (bounded; 17 while it runs).
#   bash tools/claims-v3/e189/rb/s10_a3_dry_e189.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e189.sh"
rb_init s10_a3_dry
act=${1:-}
JOB=a3-dry-e189
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e189.sh start | wait" ;; esac
e189_window
prog=$(e189_programs)
[ -n "${RB_DRY:-}" ] && prog=${prog:-ledger,spp}
[ -n "$prog" ] || rb_die $RB_E_USAGE "no program was built today (RB_OUT/e189-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  body=$(rb_file body)
  { echo "PROG=$prog"
    cat <<'EOF2'
T0=$(date +%s)
E189_FAKE_SCALE=0.2 python3 -B tools/claims-v3/e189/run_e189.py session --dry --double alt --t0 "$T0" --out "build/e189/T$T0-dry" \
  --programs "$PROG" --sequence short --idle-before 1 --idle-after 1 --anchor-s 1 --die-wait-s 5
rc=$?
grep -E 'stop-path|smoke gate|pass [0-9]+:.*done|SKIPPED|STOP|session end' "build/e189/T$T0-dry/session.log" | cut -c1-200
n=$(grep -c 'pass [0-9]*: .* done: host rc 0, status PASS' "build/e189/T$T0-dry/session.log")
echo "E189-DRY rc=$rc passes=$n"
[ "$rc" -eq 0 ] && [ "$n" -ge 1 ] && grep -q 'smoke gate passed' "build/e189/T$T0-dry/session.log"
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
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 '^E189-DRY' "$RB_CAP")"; exit 0; }
exit "$rc"
