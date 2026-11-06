#!/usr/bin/env bash
# E181, step 10: E181's dry passes on aifoundry3 (its README, box step 4), as one detached job of the runbook (v3.1's rb_job_start /
# rb_job_wait), no device opened. ../../q143k-runbook/s10_a3_dry_q143k.sh (92a1b27f) ported, with the A6-A8 gate cases added:
#   1. the V3_DRY session (no E181_DESK, so every file of the box list is checked; its dry smoke ends 1 and its gate reads NO-GO on a toy card
#      whose board never rises: expected, as E154's, E166's and E176's). It writes build/e181/session-dry.log, never build/e181/session.log,
#      so step 11's rest rule cannot read a dry session's end (E176's runbook note 2, section 1): checked here;
#   2. the measured pass through the block on the toy, F0 from the dry smoke's floor mark (exit 0);
#   3. G0-A6's room line at a 54.0 C dry room (exit 7);
#   4. A8-4's residue line at a 52.5 C dry room with the dry smoke's F0 (51.433 C: 1.067 - 0.414 > 0.50; exit 7);
#   5. A6-1's stop before the smoke's first launch at a 54.0 C dry floor (exit 7);
#   6. the session's gate at a past E181_LATEST_START (exit 8).
# No dry pass runs during a session there (the job refuses), and no session starts while a dry pass runs (rb_guard_text).
#
#   bash tools/claims-v3/e181/rb/s10_a3_dry_e181.sh start       then        ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
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
DD=build/claims-v3-dry/aifoundry3
rm -rf "$DD/e181" "$DD/e181-smoke"
real0=$(cat build/e181/session.log 2>/dev/null | wc -l | tr -d ' ')
echo "== E181's V3_DRY session (no E181_DESK)"
V3_DRY=1 E181_T0=$(date +%s) E181_LATEST_START="$LAST_START" E181_END_GATE="$LAST_END" bash tools/claims-v3/e181/session_e181.sh; r=$?
echo "E181 dry session rc=$r (its dry smoke ends 1 and its gate reads NO-GO: expected on a toy card)"; [ "$r" -eq 0 ] || bad=1
grep -q 'frozen-e181.sha256: every file as registered' build/e181/session-dry.log || { echo "E181 dry session: the box list did not read clean"; bad=1; }
grep -q 'floor F0 (A6-1' "$DD/e181-smoke/p18101/run.log" || { echo "E181 dry session: no A6-1 floor mark in the dry smoke"; bad=1; }
real1=$(cat build/e181/session.log 2>/dev/null | wc -l | tr -d ' ')
echo "E181 dry session wrote the real log: $([ "$real1" -eq "$real0" ] && echo no || echo YES) ($real0 -> $real1 lines)"; [ "$real1" -eq "$real0" ] || bad=1
tail -n 14 build/e181/session-dry.log | cut -c1-300
FM=$DD/e181-smoke/p18101/marks.jsonl
echo "== E181's V3_DRY measured pass through the block (the full design on the toy, F0 from the dry smoke)"
V3_DRY=1 E181_FLOOR_MARKS="$FM" E181_DEADLINE_EPOCH=$(( $(date +%s) + 4500 )) bash tools/claims-v3/e181/block_e181.sh 18190; r=$?; echo "E181 dry 18190 rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== G0-A6's room line at a 54.0 C dry room"
V3_DRY=1 E181_FLOOR_MARKS="$FM" E181_DRY_ROOM_C=54.0 E181_DEADLINE_EPOCH=$(( $(date +%s) + 4500 )) bash tools/claims-v3/e181/block_e181.sh 18191; r=$?; echo "E181 dry 18191 (room) rc=$r (want 7)"; [ "$r" -eq 7 ] || bad=1
echo "== A8-4's residue line at a 52.5 C dry room (F0 from the dry smoke)"
V3_DRY=1 E181_FLOOR_MARKS="$FM" E181_DRY_ROOM_C=52.5 E181_DEADLINE_EPOCH=$(( $(date +%s) + 4500 )) bash tools/claims-v3/e181/block_e181.sh 18192; r=$?; echo "E181 dry 18192 (residue) rc=$r (want 7)"; [ "$r" -eq 7 ] || bad=1
grep -h '"kind": "start_gate"' "$DD/e181/p18191/marks.jsonl" "$DD/e181/p18192/marks.jsonl" 2>/dev/null | cut -c1-400
echo "== A6-1's stop before the smoke's first launch at a 54.0 C dry floor"
V3_DRY=1 E181_DRY_FLOOR_C=54.0 bash tools/claims-v3/e181/block_e181.sh 18193 --smoke; r=$?; echo "E181 dry 18193 (A6-1) rc=$r (want 7)"; [ "$r" -eq 7 ] || bad=1
n=$(grep -c '"kind": "launch"' "$DD/e181-smoke/p18193/marks.jsonl" 2>/dev/null); echo "E181 dry 18193 launches: ${n:-0} (want 0)"; [ "${n:-0}" -eq 0 ] || bad=1
echo "== E181's session gate at a past E181_LATEST_START"
V3_DRY=1 E181_T0=$(date +%s) E181_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E181_END_GATE="$LAST_END" bash tools/claims-v3/e181/session_e181.sh
g=$?; echo "E181 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf "$DD/e181" "$DD/e181-smoke"
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e181 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e181; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E181 dry session rc=' 'E181 dry session wrote the real log' 'E181 dry 18190 rc=' 'E181 dry 18191 (room) rc=' \
               'E181 dry 18192 (residue) rc=' 'E181 dry 18193 (A6-1) rc=' 'E181 dry 18193 launches' 'E181 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e181.sh start|wait" ;;
esac
