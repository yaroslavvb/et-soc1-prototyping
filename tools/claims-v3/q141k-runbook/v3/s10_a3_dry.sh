#!/usr/bin/env bash
# Q141(k), go checklist step 10: aifoundry3's dry passes, no device opened, detached on the box as one job, before any session there:
#   the V3_DRY E166 session (E166 README box step 4; no E166_DESK, so every file is checked; its dry smoke ends 1 and the gate reads
#   NO-GO on the box, as E154's did: expected); V3_DRY block_e163.sh 16310, 16350 and 16301 --smoke (E163 README step 8); the E163
#   session's start gate refusing with exit 8 at a past E163_LATEST_START.
#
#   bash tools/claims-v3/q141k-runbook/s10_a3_dry.sh start      # one launch: returns at once
#   bash tools/claims-v3/q141k-runbook/s10_a3_dry.sh wait       # one bounded wait (at most 520 s on the box); 17 = call again
#
# The window (s02_window.sh) gives E166's gates. The job refuses to start while a card session of ours runs on aifoundry3.
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
echo "== E166's V3_DRY session (no E166_DESK)"
V3_DRY=1 E166_T0=$(date +%s) E166_LATEST_START="$LAST_START" E166_END_GATE="$LAST_END" bash tools/claims-v3/e166/session_e166.sh
echo "E166 dry session rc=$? (its dry smoke ends 1 and its gate reads NO-GO: expected on a toy card)"
tail -n 12 build/e166/session.log | cut -c1-300
echo "== E163's V3_DRY blocks"
bad=0
V3_DRY=1 bash tools/claims-v3/e163/block_e163.sh 16310; r=$?; echo "E163 dry 16310 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e163/block_e163.sh 16350; r=$?; echo "E163 dry 16350 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e163/block_e163.sh 16301 --smoke; r=$?; echo "E163 dry 16301 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E163's start gate at a past E163_LATEST_START"
V3_DRY=1 E163_T0=$(date +%s) E163_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E163_DEADLINE="$LAST_END" bash tools/claims-v3/e163/session_e163.sh
g=$?; echo "E163 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
[ "$bad" -eq 0 ]
EOF
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E166 dry session rc=' 'E163 dry 16310 rc=' 'E163 dry 16350 rc=' 'E163 dry 16301 --smoke rc=' 'E163 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry.sh start|wait" ;;
esac
