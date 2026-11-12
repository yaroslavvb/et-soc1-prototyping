#!/usr/bin/env bash
# E188 (Q165, the kit), KIT.md box step 8 (this file is s10): E188's V3_DRY pass on aifoundry3 as one detached job of the runbook (k6's
# rb_job_start / rb_job_wait), no device opened. A port of E186's step 8 (tools/claims-v3/e186/rb/s10_a3_dry_e186.sh, run on 9 Nov 2026;
# itself E182's v2) with E188's blocks, each change marked E188:
#   start | wait                 (the trains): job a3-dry-e188: the trains 18810 (B05: four anchors and 76 processes) and 18811 (PAIR), the
#                                FULL kinds pass 18820 (44 runs), the smoke 18801 (13 items and two B05 processes), and the session's start
#                                gate refusing (8) at a past E188_LATEST_START; every train block reads the train host's change from its
#                                behaviour (train_check_e188.sh) before it lists a launch, as the real block does;
#   start --no-trains | wait --no-trains   (the fallback, PASSES): job a3-dry-e188-nt: the fallback kinds pass 18830 (35 runs), the smoke
#                                with E188_TRAINS=no (13 items), and the start gate with E188_PLAN=PASSES E188_TRAINS=no refusing (8). No
#                                train block, no train host.
# Step 9 reads the job its plan needs: FULL yes needs a3-dry-e188, PASSES no needs a3-dry-e188-nt (or a3-dry-e188). The window rule first
# on start (written today; now before the last start).
#
#   bash tools/claims-v3/e188/rb/s10_a3_dry_e188.sh start [--no-trains]     then     ... wait [--no-trains]   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e188.sh"
rb_init s10_a3_dry
act=${1:-}
NT=; case "${2:-}" in --no-trains) NT=1 ;; '') ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e188.sh start|wait [--no-trains]" ;; esac
JOB=a3-dry-e188; [ -n "$NT" ] && JOB=a3-dry-e188-nt
case "$act" in
  start)
    e188_window
    rb_need_start
    body=$(rb_file body)
    { echo "LAST_START=$(printf '%q' "$RB_LAST_START")"
      echo "LAST_END=$(printf '%q' "$RB_LAST_END")"
      if [ -z "$NT" ]; then
        cat <<'EOF2'
echo "== E188's V3_DRY blocks (the trains)"
bad=0
for b in 18810 18811 18820; do
  V3_DRY=1 bash tools/claims-v3/e188/block_e188.sh $b; r=$?; echo "E188 dry $b rc=$r"; [ "$r" -eq 0 ] || bad=1
done
V3_DRY=1 bash tools/claims-v3/e188/block_e188.sh 18801 --smoke; r=$?; echo "E188 dry 18801 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E188's start gate at a past E188_LATEST_START"
V3_DRY=1 E188_T0=$(date +%s) E188_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E188_DEADLINE="$LAST_END" bash tools/claims-v3/e188/session_e188.sh
g=$?; echo "E188 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
EOF2
      else
        cat <<'EOF2'
echo "== E188's V3_DRY blocks (the fallback, PASSES: no train block, no train host)"
bad=0
V3_DRY=1 bash tools/claims-v3/e188/block_e188.sh 18830; r=$?; echo "E188 dry 18830 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 E188_TRAINS=no bash tools/claims-v3/e188/block_e188.sh 18801 --smoke; r=$?; echo "E188 dry 18801 --smoke trains=no rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E188's start gate at a past E188_LATEST_START (PASSES, trains no)"
V3_DRY=1 E188_T0=$(date +%s) E188_PLAN=PASSES E188_TRAINS=no E188_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E188_DEADLINE="$LAST_END" bash tools/claims-v3/e188/session_e188.sh
g=$?; echo "E188 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
EOF2
      fi
      cat <<'EOF2'
rm -rf build/claims-v3-dry/aifoundry3/e188 build/claims-v3-dry/aifoundry3/e188-smoke
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 "$JOB" "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 "$JOB"; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      if [ -z "$NT" ]; then K=('E188 dry 18810 rc=' 'E188 dry 18811 rc=' 'E188 dry 18820 rc=' 'E188 dry 18801 --smoke rc=' 'E188 start gate rc=')
      else K=('E188 dry 18820 rc=' 'E188 dry 18801 --smoke trains=no rc=' 'E188 start gate rc='); fi
      for k in "${K[@]}"; do grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"; done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e188.sh start|wait [--no-trains]" ;;
esac
