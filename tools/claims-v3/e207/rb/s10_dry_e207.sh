#!/usr/bin/env bash
# E207 (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum), the box step "the dry pass" (this file is s10; step 8): E206's step 8
# (tools/claims-v3/e206/rb/s10_dry_e206.sh, landed in 906699ea) running run_e207.py's whole session path on aifoundry3 with its doubles, no
# device: fake_card_e207.py's sampler (holding a stand-in node in the dry directory), config (its identity block), et-who (who holds the stand-in
# nodes and lock, read from /proc) and host, a lock file in its own directory, every line DRY, its files in build/e207/T<T0>-A-dry/ (the rest rule
# skips "-dry" paths): the identity gate, the identity read, the smoke (b01, b02, b03 against MM1-v1's counter-mean forecast; the host's card and
# the board's rise) and the stop-path test, the tie and two points of pass 1, each process at a twentieth of its time, short rest reads. As k6's
# detached job a3-dry-e207 (one at a time, never beside a session of ours), then `wait` (bounded; 17 while it runs).
#   bash tools/claims-v3/e207/rb/s10_dry_e207.sh A start      then      ... A wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e207.sh"
rb_init s10_dry
e207_arm "${1:-}"
act=${2:-}
e207_jobs "$ARM"
JOB=$JOB_DRY
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_dry_e207.sh A start | wait" ;; esac
e207_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe "$BOX"
  body=$(rb_file body)
  { echo "ARM=$ARM"
    cat <<'EOF2'
T0=$(date +%s)
D=build/e207/T$T0-$ARM-dry
E207_FAKE_SCALE=0.05 E207_FAKE_TAU_S=1 python3 -B tools/claims-v3/e207/run_e207.py session --dry --arm "$ARM" --t0 "$T0" --out "$D" \
  --sequence short --rest-s 1 --smoke-rest-s 3 --tail-s 0.5 --gate-wait-s 20
rc=$?
grep -E 'identity|stop-path|smoke gate|run [0-9]+-.* done|STOP|HUNG|session end' "$D/session.log" | cut -c1-200
n=$(grep -c 'run [0-9]*-.* done: .* rc \[0\]' "$D/session.log")
echo "E207-DRY arm $ARM rc=$rc runs=$n"
[ "$rc" -eq 0 ] && [ "$n" -ge 3 ] && grep -q 'smoke gate passed' "$D/session.log" && grep -q 'stop-path test passed' "$D/session.log" && \
  grep -q 'the identity read: ' "$D/session.log" && [ -s "$D/MANIFEST.sha256" ]
EOF2
  } > "$body"
  rb_job_start "$BOX" "$JOB" "$body"
  rb_say "the dry pass $JOB started on $BOX: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe "$BOX"
rb_job_wait "$BOX" "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 '^E207-DRY' "$RB_CAP")"; exit 0; }
exit "$rc"
