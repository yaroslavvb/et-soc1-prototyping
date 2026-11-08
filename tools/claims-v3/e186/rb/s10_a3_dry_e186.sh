#!/usr/bin/env bash
# E186 (Q158, the kit), KIT.md box step 8 (this file is s10): E186's V3_DRY pass on aifoundry3 as one detached job of the runbook (k6's
# rb_job_start / rb_job_wait), no device opened. A port of E182's step 8 v2 (tools/claims-v3/e182/rb/s10_a3_dry_e182_v2.sh) with E186's
# blocks, each change marked E186:
#   start | wait                 (the trains): job a3-dry-e186: the fp16 train 18610 (H16: four anchors and 76 processes), an fp32 train
#                                18611 (S23) and an int8 train 18612 (Q63-sign), one fallback kinds pass 18620 (35 runs), the smoke 18601
#                                (11 items and two H16 processes), and the session's start gate refusing (8) at a past E186_LATEST_START;
#   start --no-trains | wait --no-trains   (the fallback, PASSES): job a3-dry-e186-nt: 18620, the smoke with E186_TRAINS=no (11 items),
#                                and the start gate with E186_PLAN=PASSES E186_TRAINS=no refusing (8). No train block, no train host.
# Step 9 reads the job its plan needs: FULL yes needs a3-dry-e186, PASSES no needs a3-dry-e186-nt (or a3-dry-e186). E186: the window rule
# first on start (written today; now before the last start).
#
#   bash tools/claims-v3/e186/rb/s10_a3_dry_e186.sh start [--no-trains]     then     ... wait [--no-trains]   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e186.sh"
rb_init s10_a3_dry
act=${1:-}
NT=; case "${2:-}" in --no-trains) NT=1 ;; '') ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e186.sh start|wait [--no-trains]" ;; esac
JOB=a3-dry-e186; [ -n "$NT" ] && JOB=a3-dry-e186-nt
case "$act" in
  start)
    e186_window
    rb_need_start
    body=$(rb_file body)
    { echo "LAST_START=$(printf '%q' "$RB_LAST_START")"
      echo "LAST_END=$(printf '%q' "$RB_LAST_END")"
      if [ -z "$NT" ]; then
        cat <<'EOF2'
echo "== E186's V3_DRY blocks (the trains)"
bad=0
for b in 18610 18611 18612 18620; do
  V3_DRY=1 bash tools/claims-v3/e186/block_e186.sh $b; r=$?; echo "E186 dry $b rc=$r"; [ "$r" -eq 0 ] || bad=1
done
V3_DRY=1 bash tools/claims-v3/e186/block_e186.sh 18601 --smoke; r=$?; echo "E186 dry 18601 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E186's start gate at a past E186_LATEST_START"
V3_DRY=1 E186_T0=$(date +%s) E186_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E186_DEADLINE="$LAST_END" bash tools/claims-v3/e186/session_e186.sh
g=$?; echo "E186 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
EOF2
      else
        cat <<'EOF2'
echo "== E186's V3_DRY blocks (the fallback, PASSES: no train block, no train host)"
bad=0
V3_DRY=1 bash tools/claims-v3/e186/block_e186.sh 18620; r=$?; echo "E186 dry 18620 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 E186_TRAINS=no bash tools/claims-v3/e186/block_e186.sh 18601 --smoke; r=$?; echo "E186 dry 18601 --smoke trains=no rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E186's start gate at a past E186_LATEST_START (PASSES, trains no)"
V3_DRY=1 E186_T0=$(date +%s) E186_PLAN=PASSES E186_TRAINS=no E186_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E186_DEADLINE="$LAST_END" bash tools/claims-v3/e186/session_e186.sh
g=$?; echo "E186 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
EOF2
      fi
      cat <<'EOF2'
rm -rf build/claims-v3-dry/aifoundry3/e186 build/claims-v3-dry/aifoundry3/e186-smoke
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
      if [ -z "$NT" ]; then K=('E186 dry 18610 rc=' 'E186 dry 18611 rc=' 'E186 dry 18612 rc=' 'E186 dry 18620 rc=' 'E186 dry 18601 --smoke rc=' 'E186 start gate rc=')
      else K=('E186 dry 18620 rc=' 'E186 dry 18601 --smoke trains=no rc=' 'E186 start gate rc='); fi
      for k in "${K[@]}"; do grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"; done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e186.sh start|wait [--no-trains]" ;;
esac
