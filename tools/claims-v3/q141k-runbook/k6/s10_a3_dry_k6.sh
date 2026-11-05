#!/usr/bin/env bash
# Q142(k6), step 10: E171's V3_DRY pass on aifoundry3 (E171's README, box step 8), as one detached job of the runbook (v3.1's
# rb_job_start / rb_job_wait), no device opened: a kinds pass (86 launches through the wrapper), the smoke (10), and the session's start
# gate refusing (exit 8) at a past E171_LATEST_START. No dry pass runs during a session there (the job refuses), and no session starts
# while a dry pass runs (rb_guard_text).
#
#   bash tools/claims-v3/q141k-runbook/k6/s10_a3_dry_k6.sh start       then        ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s10_a3_dry
act=${1:-}
case "$act" in
  start)
    rb_window
    body=$(rb_file body)
    { echo "LAST_START=$(printf '%q' "$RB_LAST_START")"
      echo "LAST_END=$(printf '%q' "$RB_LAST_END")"
      cat <<'EOF'
echo "== E171's V3_DRY blocks"
bad=0
V3_DRY=1 bash tools/claims-v3/e171/block_e171.sh 17110; r=$?; echo "E171 dry 17110 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e171/block_e171.sh 17101 --smoke; r=$?; echo "E171 dry 17101 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E171's start gate at a past E171_LATEST_START"
V3_DRY=1 E171_T0=$(date +%s) E171_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E171_DEADLINE="$LAST_END" bash tools/claims-v3/e171/session_e171.sh
g=$?; echo "E171 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf build/claims-v3-dry/aifoundry3/e171 build/claims-v3-dry/aifoundry3/e171-smoke
[ "$bad" -eq 0 ]
EOF
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e171 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e171; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E171 dry 17110 rc=' 'E171 dry 17101 --smoke rc=' 'E171 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_k6.sh start|wait" ;;
esac
