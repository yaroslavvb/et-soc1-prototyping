#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1), step 10 v2: E182's V3_DRY pass on aifoundry3 as one detached job of the runbook (k6's rb_job_start /
# rb_job_wait), no device opened. It is v1 (rb/s10_a3_dry_e182.sh, which stays as committed) with the registered fallback added (the
# verifier's MAJOR 1: v1 always dry-ran train block 18215 and the smoke with the trains on, whose preflight needs the train host even under
# V3_DRY, so after a failed build the dry job ended 1 and step 11 refused):
#   start | wait                 (the trains, as v1): job a3-dry-e182: 18220 (70 launches), 18215 (T1: four anchors and 64 processes), the
#                                smoke 18201 (10 items and two train processes), the session's start gate refusing (8);
#   start --no-trains | wait --no-trains   (the fallback, PASSES): job a3-dry-e182-nt: 18220, the smoke with E182_TRAINS=no (10 items),
#                                and the start gate with E182_PLAN=PASSES E182_TRAINS=no refusing (8). No train block, no train host.
# Step 11 v2 reads the job its plan needs: FULL yes needs a3-dry-e182, PASSES no needs a3-dry-e182-nt (or a3-dry-e182).
#
#   bash tools/claims-v3/e182/rb/s10_a3_dry_e182_v2.sh start [--no-trains]     then     ... wait [--no-trains]   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s10_a3_dry_v2
act=${1:-}
NT=; case "${2:-}" in --no-trains) NT=1 ;; '') ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e182_v2.sh start|wait [--no-trains]" ;; esac
JOB=a3-dry-e182; [ -n "$NT" ] && JOB=a3-dry-e182-nt
case "$act" in
  start)
    rb_window
    body=$(rb_file body)
    { echo "LAST_START=$(printf '%q' "$RB_LAST_START")"
      echo "LAST_END=$(printf '%q' "$RB_LAST_END")"
      if [ -z "$NT" ]; then
        cat <<'EOF2'
echo "== E182's V3_DRY blocks (the trains)"
bad=0
V3_DRY=1 bash tools/claims-v3/e182/block_e182.sh 18220; r=$?; echo "E182 dry 18220 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e182/block_e182.sh 18215; r=$?; echo "E182 dry 18215 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e182/block_e182.sh 18201 --smoke; r=$?; echo "E182 dry 18201 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E182's start gate at a past E182_LATEST_START"
V3_DRY=1 E182_T0=$(date +%s) E182_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E182_DEADLINE="$LAST_END" bash tools/claims-v3/e182/session_e182.sh
g=$?; echo "E182 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
EOF2
      else
        cat <<'EOF2'
echo "== E182's V3_DRY blocks (the fallback, PASSES: no train block, no train host)"
bad=0
V3_DRY=1 bash tools/claims-v3/e182/block_e182.sh 18220; r=$?; echo "E182 dry 18220 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 E182_TRAINS=no bash tools/claims-v3/e182/block_e182.sh 18201 --smoke; r=$?; echo "E182 dry 18201 --smoke trains=no rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E182's start gate at a past E182_LATEST_START (PASSES, trains no)"
V3_DRY=1 E182_T0=$(date +%s) E182_PLAN=PASSES E182_TRAINS=no E182_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E182_DEADLINE="$LAST_END" bash tools/claims-v3/e182/session_e182.sh
g=$?; echo "E182 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
EOF2
      fi
      cat <<'EOF2'
rm -rf build/claims-v3-dry/aifoundry3/e182 build/claims-v3-dry/aifoundry3/e182-smoke
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
      if [ -z "$NT" ]; then K=('E182 dry 18220 rc=' 'E182 dry 18215 rc=' 'E182 dry 18201 --smoke rc=' 'E182 start gate rc=')
      else K=('E182 dry 18220 rc=' 'E182 dry 18201 --smoke trains=no rc=' 'E182 start gate rc='); fi
      for k in "${K[@]}"; do grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"; done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e182_v2.sh start|wait [--no-trains]" ;;
esac
