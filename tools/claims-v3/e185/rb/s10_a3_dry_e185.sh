#!/usr/bin/env bash
# E185, step 10: E185's dry passes on aifoundry3 (its README, box step 4), as one detached job of the runbook (v3.1's rb_job_start /
# rb_job_wait), no device opened. ../../q143k-runbook/s10_a3_dry_q143k.sh (92a1b27f) ported, with the A6-A8 gate cases added:
#   1. the V3_DRY session (no E185_DESK, so every file of the box list is checked; its dry smoke ends 1 and its gate reads NO-GO on a toy card
#      whose board never rises: expected, as E154's, E166's and E176's). It writes only build/e185/T<T0>-dry/ (never a real T0 directory, never
#      build/e185/LAST_T0), so step 11's rest rule cannot read a dry session's end: checked here, with its manifest read back;
#   2. the measured pass through the block on the toy, F0 from the dry smoke's floor mark (exit 0);
#   3. G0-A6's room line at a 54.0 C dry room (exit 7);
#   4. A8-4's residue line at a 52.5 C dry room with the dry smoke's F0 (51.433 C: 1.067 - 0.414 > 0.50; exit 7);
#   5. A6-1's stop before the smoke's first launch at a 54.0 C dry floor (exit 7);
#   6. the session's gate at a past E185_LATEST_START (exit 8).
# No dry pass runs during a session there (the job refuses), and no session starts while a dry pass runs (rb_guard_text).
#
#   bash tools/claims-v3/e185/rb/s10_a3_dry_e185.sh start       then        ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e185.sh"
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
rm -rf "$DD/e185" "$DD/e185-smoke"
real0=$(ls -d build/e185/T[0-9]* 2>/dev/null | grep -vc -- '-dry$'); lt0=$(cat build/e185/LAST_T0 2>/dev/null || echo none)
echo "== E185's V3_DRY session (no E185_DESK)"
DT0=$(date +%s); DL=build/e185/T$DT0-dry/session-dry.log
V3_DRY=1 E185_T0=$DT0 E185_LATEST_START="$LAST_START" E185_END_GATE="$LAST_END" bash tools/claims-v3/e185/session_e185.sh; r=$?
echo "E185 dry session rc=$r (its dry smoke ends 1 and its gate reads NO-GO: expected on a toy card)"; [ "$r" -eq 0 ] || bad=1
grep -q 'frozen-e185.sha256: every file as registered' "$DL" || { echo "E185 dry session: the box list did not read clean"; bad=1; }
grep -q 'floor F0 (A6-1' "$DD/e185-smoke/p18501/run.log" || { echo "E185 dry session: no A6-1 floor mark in the dry smoke"; bad=1; }
real1=$(ls -d build/e185/T[0-9]* 2>/dev/null | grep -vc -- '-dry$'); lt1=$(cat build/e185/LAST_T0 2>/dev/null || echo none)
echo "E185 dry session wrote the real log: $([ "$real1" -eq "$real0" ] && [ "$lt1" = "$lt0" ] && echo no || echo YES) ($real0 -> $real1 real T0 directories; LAST_T0 $lt0 -> $lt1)"
{ [ "$real1" -eq "$real0" ] && [ "$lt1" = "$lt0" ]; } || bad=1
( sha256sum -c --quiet "build/e185/T$DT0-dry/MANIFEST.sha256" ) && echo "E185 dry session manifest reads back: $(grep -c . "build/e185/T$DT0-dry/MANIFEST.sha256") files" || { echo "E185 dry session manifest: DIFFERS"; bad=1; }
tail -n 14 "$DL" | cut -c1-300
FM=$DD/e185-smoke/p18501/marks.jsonl
echo "== E185's V3_DRY measured pass through the block (the full design on the toy, F0 from the dry smoke)"
V3_DRY=1 E185_FLOOR_MARKS="$FM" E185_DEADLINE_EPOCH=$(( $(date +%s) + 6240 )) bash tools/claims-v3/e185/block_e185.sh 18190; r=$?; echo "E185 dry 18190 rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== G0-A6's room line at a 54.0 C dry room"
V3_DRY=1 E185_FLOOR_MARKS="$FM" E185_DRY_ROOM_C=54.0 E185_DEADLINE_EPOCH=$(( $(date +%s) + 6240 )) bash tools/claims-v3/e185/block_e185.sh 18191; r=$?; echo "E185 dry 18191 (room) rc=$r (want 7)"; [ "$r" -eq 7 ] || bad=1
echo "== A8-4's residue line at a 52.5 C dry room (F0 from the dry smoke)"
V3_DRY=1 E185_FLOOR_MARKS="$FM" E185_DRY_ROOM_C=52.5 E185_DEADLINE_EPOCH=$(( $(date +%s) + 6240 )) bash tools/claims-v3/e185/block_e185.sh 18192; r=$?; echo "E185 dry 18192 (residue) rc=$r (want 7)"; [ "$r" -eq 7 ] || bad=1
grep -h '"kind": "start_gate"' "$DD/e185/p18191/marks.jsonl" "$DD/e185/p18192/marks.jsonl" 2>/dev/null | cut -c1-400
echo "== A6-1's stop before the smoke's first launch at a 54.0 C dry floor"
V3_DRY=1 E185_DRY_FLOOR_C=54.0 bash tools/claims-v3/e185/block_e185.sh 18193 --smoke; r=$?; echo "E185 dry 18193 (A6-1) rc=$r (want 7)"; [ "$r" -eq 7 ] || bad=1
n=$(grep -c '"kind": "launch"' "$DD/e185-smoke/p18193/marks.jsonl" 2>/dev/null); echo "E185 dry 18193 launches: ${n:-0} (want 0)"; [ "${n:-0}" -eq 0 ] || bad=1
echo "== E185's session gate at a past E185_LATEST_START"
V3_DRY=1 E185_T0=$(date +%s) E185_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E185_END_GATE="$LAST_END" bash tools/claims-v3/e185/session_e185.sh
g=$?; echo "E185 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf "$DD/e185" "$DD/e185-smoke" build/e185/T*-dry
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e185 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e185; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E185 dry session rc=' 'E185 dry session wrote the real log' 'E185 dry 18190 rc=' 'E185 dry 18191 (room) rc=' \
               'E185 dry 18192 (residue) rc=' 'E185 dry 18193 (A6-1) rc=' 'E185 dry 18193 launches' 'E185 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e185.sh start|wait" ;;
esac
