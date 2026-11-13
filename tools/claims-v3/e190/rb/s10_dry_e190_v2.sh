#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum), the box step "the dry pass" v2 (this file is
# s10 v2), for one arm: rb/s10_dry_e190.sh (the kit, unchanged beside it) running run_e190_v2.py's whole session path on the arm's box
# with its v2 doubles, no device: fake_card_e190_v2.py's sampler (holding a stand-in node in the dry directory), config (its identity
# block), et-who (who holds the stand-in nodes and lock, read from /proc) and host, a lock file in its own directory, every line DRY, its
# files in build/e190/T<T0>-<arm>-dry/ (the rest rule skips "-dry" paths): the identity gate, the stop-path test, the identity read, the
# smoke (the host's card and the board's rise), the three P1 bursts and S1's twelve processes, each process at a tenth of its time, 1 s
# rest reads. As k6's detached job a2-dry-e190v2 or a1-dry-e190v2 (one at a time, never beside a session of ours), then `wait` (bounded;
# 17 while it runs).
#   bash tools/claims-v3/e190/rb/s10_dry_e190_v2.sh <A|B> start      then      ... <A|B> wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190_v2.sh"
rb_init s10_dry_v2
e190_arm "${1:-}"
act=${2:-}
e190_jobs_v2 "$ARM"
JOB=$JOB_DRY
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_dry_e190_v2.sh <A|B> start | wait" ;; esac
e190_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe "$BOX"
  body=$(rb_file body)
  { echo "ARM=$ARM"
    cat <<'EOF2'
T0=$(date +%s)
D=build/e190/T$T0-$ARM-dry
E190_FAKE_SCALE=0.1 E190_FAKE_TAU_S=1 python3 -B tools/claims-v3/e190/run_e190_v2.py session --dry --arm "$ARM" --t0 "$T0" --out "$D" \
  --sequence short --rest-s 1 --smoke-rest-s 3 --tail-s 0.5 --gate-wait-s 20
rc=$?
grep -E 'identity|stop-path|smoke gate|run [0-9]+-.* done|STOP|session end' "$D/session.log" | cut -c1-200
n=$(grep -c 'run [0-9]*-.* done: .* rc \[0' "$D/session.log")
echo "E190-DRY-V2 arm $ARM rc=$rc runs=$n"
[ "$rc" -eq 0 ] && [ "$n" -ge 4 ] && grep -q 'smoke gate passed' "$D/session.log" && grep -q 'the identity read: ' "$D/session.log" && [ -s "$D/MANIFEST.sha256" ]
EOF2
  } > "$body"
  rb_job_start "$BOX" "$JOB" "$body"
  rb_say "the dry pass v2 $JOB started on $BOX: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe "$BOX"
rb_job_wait "$BOX" "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] && { rb_say "the dry pass v2 ended rc 0: $(grep -m1 '^E190-DRY-V2' "$RB_CAP")"; exit 0; }
exit "$rc"
