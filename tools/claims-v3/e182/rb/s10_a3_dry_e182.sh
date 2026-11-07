#!/usr/bin/env bash
# E182 (Q153, the kit), step 10: E182's V3_DRY pass on aifoundry3, as one detached job of the runbook (k6's rb_job_start / rb_job_wait), no
# device opened: a kinds pass (18220: 70 launches through the wrapper, the registered order), a train (18215, T1: its four anchors and 64
# processes), the smoke (18201: 10 items and two train processes), and the session's start gate refusing (exit 8) at a past
# E182_LATEST_START. A port of E178's step 10.
#
#   bash tools/claims-v3/e182/rb/s10_a3_dry_e182.sh start       then        ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s10_a3_dry
act=${1:-}
case "$act" in
  start)
    rb_window
    body=$(rb_file body)
    { echo "LAST_START=$(printf '%q' "$RB_LAST_START")"
      echo "LAST_END=$(printf '%q' "$RB_LAST_END")"
      cat <<'EOF2'
echo "== E182's V3_DRY blocks"
bad=0
V3_DRY=1 bash tools/claims-v3/e182/block_e182.sh 18220; r=$?; echo "E182 dry 18220 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e182/block_e182.sh 18215; r=$?; echo "E182 dry 18215 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e182/block_e182.sh 18201 --smoke; r=$?; echo "E182 dry 18201 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E182's start gate at a past E182_LATEST_START"
V3_DRY=1 E182_T0=$(date +%s) E182_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E182_DEADLINE="$LAST_END" bash tools/claims-v3/e182/session_e182.sh
g=$?; echo "E182 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf build/claims-v3-dry/aifoundry3/e182 build/claims-v3-dry/aifoundry3/e182-smoke
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e182 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e182; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E182 dry 18220 rc=' 'E182 dry 18215 rc=' 'E182 dry 18201 --smoke rc=' 'E182 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e182.sh start|wait" ;;
esac
