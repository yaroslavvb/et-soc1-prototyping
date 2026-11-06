#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, ../KIT.md.dated-note-1.md section 6), step 10, v2: E180's V3_DRY pass on aifoundry3, as one detached job
# of the runbook, no device opened. s10_a3_dry_e180.sh (v1, which stays as committed) with v2's block and session: a pass (47 runs in the
# plan's order), the smoke (4) and the stop-path test (no launch) through block_e180_v2.sh, and session_e180_v2.sh's start gate refusing
# (exit 8) at a past E180_LATEST_START; the job is named a3-dry-e180-v2, which step 11 v2 needs. The dry session writes
# build/e180/session-dry.log, never the real session's log. V3_DRY keeps lib.sh's stub of the other-user test (no one present), so D1 itself
# is tested at the desk (../selftest_others_e180_v2.sh), not here.
#
#   bash tools/claims-v3/e180/rb/s10_a3_dry_e180_v2.sh start       then        ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s10_a3_dry_v2
act=${1:-}
case "$act" in
  start)
    rb_window
    body=$(rb_file body)
    { echo "LAST_START=$(printf '%q' "$RB_LAST_START")"
      echo "LAST_END=$(printf '%q' "$RB_LAST_END")"
      cat <<'EOF2'
echo "== E180's V3_DRY blocks (kit v2)"
bad=0
V3_DRY=1 bash tools/claims-v3/e180/block_e180_v2.sh 18010; r=$?; echo "E180 dry 18010 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e180/block_e180_v2.sh 18001 --smoke; r=$?; echo "E180 dry 18001 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e180/block_e180_v2.sh 18002 --stoptest; r=$?; echo "E180 dry 18002 --stoptest rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E180's start gate at a past E180_LATEST_START (kit v2)"
V3_DRY=1 E180_T0=$(date +%s) E180_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E180_DEADLINE="$LAST_END" bash tools/claims-v3/e180/session_e180_v2.sh
g=$?; echo "E180 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf build/claims-v3-dry/aifoundry3/e180 build/claims-v3-dry/aifoundry3/e180-smoke build/claims-v3-dry/aifoundry3/e180-stoptest
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e180-v2 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e180-v2; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E180 dry 18010 rc=' 'E180 dry 18001 --smoke rc=' 'E180 dry 18002 --stoptest rc=' 'E180 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e180_v2.sh start|wait" ;;
esac
