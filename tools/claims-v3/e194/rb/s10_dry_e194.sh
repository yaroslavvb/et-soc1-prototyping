#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "the dry pass" (this file
# is s10): run_e194.py's whole session path on aifoundry2 with its doubles, no device. E191's step 8 (tools/claims-v3/e191/rb/
# s10_a1_dry_e191.sh, unchanged beside it) with E194's box and runner: fake_card_e194.py's sampler (which holds a stand-in node, its clock
# 600 MHz at rest and 800 MHz in a burst after its climb), its hosts, config and et-who (card 0's identity block and stand-in nodes, so THE
# IDENTITY GATE (a) and (b), the host watch and THE CLOCK RULE run in it too), a lock file in its own directory, every line DRY, its files
# in build/e194/T<T0>-dry/ (the rest rule skips it). One pass of each configuration the day will run (the programs step 6 built today),
# the stop-path test and the ramped smoke, each launch at 20% of the forecast's seconds and 1 s idles (the clock rule's climb scaled to
# 0.2 s with them). Its end ASSERTS the runner's dry check over every device-opening command line the real path would run (no ET_DEVICES
# and no V3_DEVICE on each; none names another card or an ET_DEVICES setting, dev_mngt_service or et-powertop; the real lock card 0's), the
# identity lines and that every pass read the clock at 800 MHz. As k6's detached job a2-dry-e194 (one at a time, never beside a session of
# ours), then `wait` (bounded; 17 while it runs). THE QUIET DESK FLAG must be raised.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e194/rb/s10_dry_e194.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s10_dry
act=${1:-}
JOB=a2-dry-e194
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_dry_e194.sh start | wait" ;; esac
e194_window
e194_quiet
prog=$(e194_programs)
[ -n "${RB_DRY:-}" ] && prog=${prog:-ledger,spp}
[ -n "$prog" ] || rb_die $RB_E_USAGE "no program was built today (RB_OUT/e194-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry2
  body=$(rb_file body)
  { echo "PROG=$prog"
    cat <<'EOF2'
T0=$(date +%s)
unset ET_DEVICES V3_DEVICE
E194_FAKE_SCALE=0.2 python3 -B tools/claims-v3/e194/run_e194.py session --dry --double alt --t0 "$T0" --out "build/e194/T$T0-dry" \
  --programs "$PROG" --sequence short --idle-before 1 --idle-after 1 --anchor-s 1 --die-wait-s 5 --climb-s 0.3
rc=$?
L=build/e194/T$T0-dry/session.log
grep -E 'identity|stop-path|smoke gate|pass [0-9]+:.*done|SKIPPED|STOP|device-command check|session end' "$L" | cut -c1-220
n=$(grep -c 'pass [0-9]*: .* done: host rc 0, status PASS, reading PASS, the clock ok' "$L")
all=$(grep -c 'pass [0-9]*: .* done: ' "$L")
dc=$(grep -c 'the device-command check: [0-9]* device-opening command(s), each with ET_DEVICES and V3_DEVICE unset; none names another card or an ET_DEVICES setting, or calls dev_mngt_service or et-powertop; the lock card 0.s: ok' "$L")
id=$(grep -c 'identity (a): /dev/et0_mgmt, device ID 0, minion_mv between 450 and 600\|identity (b): et-who with the sampler running' "$L")
echo "E194-DRY rc=$rc passes=$n of $all (each PASS with the clock ok) dry-check=$dc identity-lines=$id"
[ "$rc" -eq 0 ] && [ "$n" -ge 1 ] && [ "$n" -eq "$all" ] && [ "$dc" -eq 1 ] && [ "$id" -eq 2 ] && grep -q 'smoke gate passed' "$L"
EOF2
  } > "$body"
  rb_job_start aifoundry2 "$JOB" "$body"
  rb_say "the dry pass $JOB started on aifoundry2: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe aifoundry2
rb_job_wait aifoundry2 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 '^E194-DRY' "$RB_CAP")"; exit 0; }
exit "$rc"
