#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), the box step "the dry pass" (this file is s10): run_e202.py's whole
# session path on aifoundry3 with its doubles, no device: energy_stub.py's alt sampler (unchanged), fake_card_e202.py's host, config and
# et-who, a lock file in its own directory, every line DRY, its files in build/e202/T<T0>-dry/ (the rest rule skips it). The refusals'
# harness and preflight, the stop-path test, the smoke's five processes and its gate, the R rule, and one burst of each configuration the
# day runs, each launch at 20% of the forecast's seconds and 1 s rests. As k6's detached job a3-dry-e202 (one at a time, never beside a
# session of ours), then `wait` (bounded; 17 while it runs). E202-DRY rc=0 bursts=4 is the pass.
#   bash tools/claims-v3/e202/rb/s10_a3_dry_e202.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e202.sh"
rb_init s10_a3_dry
act=${1:-}
JOB=a3-dry-e202
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e202.sh start | wait" ;; esac
e202_window
[ -n "${RB_DRY:-}" ] || [ -n "$(e202_built)" ] || rb_die $RB_E_USAGE "E202 was not built today (RB_OUT/e202-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  body=$(rb_file body)
  cat > "$body" <<'EOF2'
T0=$(date +%s)
E202_FAKE_SCALE=0.2 python3 -B tools/claims-v3/e202/run_e202.py session --dry --double alt --t0 "$T0" --out "build/e202/T$T0-dry" \
  --sequence short --idle-before 1 --idle-after 1 --anchor-s 1 --die-wait-s 5
rc=$?
grep -E 'refused|stop-path|smoke|R rule|burst [0-9]+:.*done|STOP|GATE-STOP|session end' "build/e202/T$T0-dry/session.log" | cut -c1-220
n=$(grep -c 'burst [0-9]*: .* done: host rc 0, status PASS' "build/e202/T$T0-dry/session.log")
echo "E202-DRY rc=$rc bursts=$n"
[ "$rc" -eq 0 ] && [ "$n" -ge 2 ] && grep -q 'smoke gate passed' "build/e202/T$T0-dry/session.log"
EOF2
  rb_job_start aifoundry3 "$JOB" "$body"
  rb_say "the dry pass $JOB started on aifoundry3: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe aifoundry3
rb_job_wait aifoundry3 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 '^E202-DRY' "$RB_CAP")"; exit 0; }
exit "$rc"
