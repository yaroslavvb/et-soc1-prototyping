#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c), the box step "the dry pass" (this file is s10; step 8): E206's step 8
# (tools/claims-v3/e206/rb/s10_dry_e206.sh, landed in 906699ea) running run_e210.py's whole session path on aifoundry3 with its doubles, no
# device: fake_card_e210.py's sampler (holding a stand-in node in the dry directory), config (its identity block), et-who (who holds the stand-in
# nodes and lock, read from /proc) and host, a lock file in its own directory, every line DRY, its files in build/e210/T<T0>-A-dry/ (the rest rule
# skips "-dry" paths): the identity gate, the identity read, the opening (the smoke: random@S1, zeros@S1 and random@S2 against E206's cycles an
# op at the shape, the host's card and the board's rise; THE PROBE of maxalte@S2; the stop-path test), the warm-up tie and two runs of pass 1
# (004 sparse50@S1, 007 bhalfeq@S1: the doubles read every tile file of the run from the box tree, as rgm136's fillPools does, so the synced
# tiles are shown to resolve there), each process at a twentieth of its time, short rest reads. As k6's detached job a3-dry-e210 (one at a
# time, never beside a session of ours), then `wait` (bounded; 17 while it runs).
#   bash tools/claims-v3/e210/rb/s10_dry_e210.sh A start      then      ... A wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e210.sh"
rb_init s10_dry
e210_arm "${1:-}"
act=${2:-}
e210_jobs "$ARM"
JOB=$JOB_DRY
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_dry_e210.sh A start | wait" ;; esac
e210_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe "$BOX"
  body=$(rb_file body)
  { echo "ARM=$ARM"
    cat <<'EOF2'
T0=$(date +%s)
D=build/e210/T$T0-$ARM-dry
E210_FAKE_SCALE=0.05 E210_FAKE_TAU_S=1 python3 -B tools/claims-v3/e210/run_e210.py session --dry --arm "$ARM" --t0 "$T0" --out "$D" \
  --sequence short --rest-s 1 --smoke-rest-s 3 --tail-s 0.5 --gate-wait-s 20
rc=$?
grep -E 'identity|stop-path|smoke gate|the probe|run [0-9]+-.* done|STOP|HUNG|session end' "$D/session.log" | cut -c1-200
n=$(grep -c 'run [0-9]*-.* done: .* rc \[0\]' "$D/session.log")
echo "E210-DRY arm $ARM rc=$rc runs=$n"
[ "$rc" -eq 0 ] && [ "$n" -ge 3 ] && grep -q 'smoke gate passed' "$D/session.log" && grep -q 'stop-path test passed' "$D/session.log" && \
  grep -q 'the probe maxalte@S2: IN' "$D/session.log" && grep -q 'the identity read: ' "$D/session.log" && [ -s "$D/MANIFEST.sha256" ] && \
  ! grep -rqs 'cannot read 2 x 1024 bytes' "$D"
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
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 '^E210-DRY' "$RB_CAP")"; exit 0; }
exit "$rc"
