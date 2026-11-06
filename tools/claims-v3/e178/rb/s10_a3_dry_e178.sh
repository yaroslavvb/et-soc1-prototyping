#!/usr/bin/env bash
# E178 (Q146, the kit), step 10: E178's V3_DRY pass on aifoundry3, as one detached job of the runbook (k6's rb_job_start / rb_job_wait), no
# device opened: a kinds pass (78 launches through the wrapper, the registered order), the smoke (10), and the session's start gate
# refusing (exit 8) at a past E178_LATEST_START. No dry pass runs during a session there (the job refuses), and no session starts while a dry
# pass runs (rb_guard_text). A port of ../../q141k-runbook/k6/s10_a3_dry_k6.sh.
#
#   bash tools/claims-v3/e178/rb/s10_a3_dry_e178.sh start       then        ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e178.sh"
rb_init s10_a3_dry
act=${1:-}
case "$act" in
  start)
    rb_window
    body=$(rb_file body)
    { echo "LAST_START=$(printf '%q' "$RB_LAST_START")"
      echo "LAST_END=$(printf '%q' "$RB_LAST_END")"
      cat <<'EOF2'
echo "== E178's V3_DRY blocks"
bad=0
V3_DRY=1 bash tools/claims-v3/e178/block_e178.sh 17810; r=$?; echo "E178 dry 17810 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e178/block_e178.sh 17801 --smoke; r=$?; echo "E178 dry 17801 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E178's start gate at a past E178_LATEST_START"
V3_DRY=1 E178_T0=$(date +%s) E178_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E178_DEADLINE="$LAST_END" bash tools/claims-v3/e178/session_e178.sh
g=$?; echo "E178 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf build/claims-v3-dry/aifoundry3/e178 build/claims-v3-dry/aifoundry3/e178-smoke
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e178 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e178; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E178 dry 17810 rc=' 'E178 dry 17801 --smoke rc=' 'E178 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e178.sh start|wait" ;;
esac
