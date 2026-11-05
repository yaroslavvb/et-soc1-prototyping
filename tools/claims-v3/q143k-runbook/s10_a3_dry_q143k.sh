#!/usr/bin/env bash
# Q143(k), step 10: E176's dry passes on aifoundry3 (its README, box step 4), as one detached job of the runbook (v3.1's rb_job_start /
# rb_job_wait), no device opened: the V3_DRY session (no E176_DESK, so every file of the box list is checked; its dry smoke ends 1 and its
# gate reads NO-GO on a toy card whose board never rises: expected, as E154's and E166's), the measured pass through the block on the toy
# (exit 0), the start gate at a 53.4 C dry room (exit 7), and the session's gate at a past E176_LATEST_START (exit 8). No dry pass runs during
# a session there (the job refuses), and no session starts while a dry pass runs (rb_guard_text).
#
#   bash tools/claims-v3/q143k-runbook/s10_a3_dry_q143k.sh start       then        ... wait   (repeat while it says 17)
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
      cat <<'EOF2'
bad=0
echo "== E176's V3_DRY session (no E176_DESK)"
V3_DRY=1 E176_T0=$(date +%s) E176_LATEST_START="$LAST_START" E176_END_GATE="$LAST_END" bash tools/claims-v3/e176/session_e176.sh; r=$?
echo "E176 dry session rc=$r (its dry smoke ends 1 and its gate reads NO-GO: expected on a toy card)"; [ "$r" -eq 0 ] || bad=1
grep -q 'frozen-e176.sha256: every file as registered' build/e176/session.log || { echo "E176 dry session: the box list did not read clean"; bad=1; }
tail -n 14 build/e176/session.log | cut -c1-300
echo "== E176's V3_DRY measured pass through the block (the full design on the toy)"
V3_DRY=1 E176_DEADLINE_EPOCH=$(( $(date +%s) + 4500 )) bash tools/claims-v3/e176/block_e176.sh 17690; r=$?; echo "E176 dry 17690 rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E176's start gate at a 53.4 C dry room"
V3_DRY=1 E176_DRY_ROOM_C=53.4 E176_DEADLINE_EPOCH=$(( $(date +%s) + 4500 )) bash tools/claims-v3/e176/block_e176.sh 17691; r=$?; echo "E176 dry 17691 (G0) rc=$r (want 7)"; [ "$r" -eq 7 ] || bad=1
echo "== E176's session gate at a past E176_LATEST_START"
V3_DRY=1 E176_T0=$(date +%s) E176_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E176_END_GATE="$LAST_END" bash tools/claims-v3/e176/session_e176.sh
g=$?; echo "E176 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf build/claims-v3-dry/aifoundry3/e176 build/claims-v3-dry/aifoundry3/e176-smoke
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e176 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e176; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E176 dry session rc=' 'E176 dry 17690 rc=' 'E176 dry 17691 (G0) rc=' 'E176 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_q143k.sh start|wait" ;;
esac
