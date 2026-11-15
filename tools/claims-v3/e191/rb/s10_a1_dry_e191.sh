#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum), the box step "the dry pass" (this file
# is s10): run_e191.py's whole session path on aifoundry1 with its doubles, no device. E189's step 8 (tools/claims-v3/e189/rb/
# s10_a3_dry_e189.sh, unchanged beside it) with E191's box and runner: energy_stub.py's alt card under fake_card_e191.py's sampler (which
# holds a stand-in node), its hosts, config and et-who (card 1's identity block and stand-in nodes, so THE IDENTITY GATE (a) and (b) and the
# host watch run in it too), a lock file in its own directory, every line DRY, its files in build/e191/T<T0>-dry/ (the rest rule skips it).
# One pass of each configuration the day will run (the programs step 6 built today), the stop-path test and the ramped smoke, each launch at
# 20% of the forecast's seconds and 1 s idles. Its end ASSERTS E191's dated note 1, item 4 (the runner's dry check over every
# device-opening command line the real path would run: ET_DEVICES=1 on each; none names etsoc-shire0, /dev/et0_ or ET_DEVICES=0; none
# unsets ET_DEVICES; no dev_mngt_service or et-powertop; the real lock card 1's) and the identity lines. As k6's detached job a1-dry-e191
# (one at a time, never beside a session of ours), then `wait` (bounded; 17 while it runs).
#   bash tools/claims-v3/e191/rb/s10_a1_dry_e191.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s10_a1_dry
act=${1:-}
JOB=a1-dry-e191
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a1_dry_e191.sh start | wait" ;; esac
e191_window
prog=$(e191_programs)
[ -n "${RB_DRY:-}" ] && prog=${prog:-ledger,spp}
[ -n "$prog" ] || rb_die $RB_E_USAGE "no program was built today (RB_OUT/e191-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry1
  body=$(rb_file body)
  { echo "PROG=$prog"
    cat <<'EOF2'
T0=$(date +%s)
E191_FAKE_SCALE=0.2 python3 -B tools/claims-v3/e191/run_e191.py session --dry --double alt --t0 "$T0" --out "build/e191/T$T0-dry" \
  --programs "$PROG" --sequence short --idle-before 1 --idle-after 1 --anchor-s 1 --die-wait-s 5
rc=$?
L=build/e191/T$T0-dry/session.log
grep -E 'identity|stop-path|smoke gate|pass [0-9]+:.*done|SKIPPED|STOP|device-command check|session end' "$L" | cut -c1-220
n=$(grep -c 'pass [0-9]*: .* done: host rc 0, status PASS, reading PASS' "$L")
dc=$(grep -c 'the device-command check: [0-9]* device-opening command(s), each with ET_DEVICES=1; none names card 0, unsets ET_DEVICES or calls dev_mngt_service or et-powertop; the lock card 1.s: ok' "$L")
id=$(grep -c 'identity (a): /dev/et1_mgmt, device ID 1, minion_mv below 510\|identity (b): et-who with the sampler running' "$L")
echo "E191-DRY rc=$rc passes=$n dry-check=$dc identity-lines=$id"
[ "$rc" -eq 0 ] && [ "$n" -ge 1 ] && [ "$dc" -eq 1 ] && [ "$id" -eq 2 ] && grep -q 'smoke gate passed' "$L"
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
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 '^E191-DRY' "$RB_CAP")"; exit 0; }
exit "$rc"
