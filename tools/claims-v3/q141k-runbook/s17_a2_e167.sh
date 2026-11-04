#!/usr/bin/env bash
# Q141(k), go checklist step 17: E167 on aifoundry2, after E165's queue has ended (README.md.dated-note.md's table):
#   latch   python3 tools/claims-v3/e167/latch_check_e167.py --history ~/live/history/<UTC day>.jsonl (a file read; no device command):
#           GO (under 72 C): go on; NO-GO (72 C or more): skip E167 today and go on to E168 (16); UNREADABLE: go on, the smoke's
#           first samples are then the check;
#   config  bash tools/claims-v3/e167/run_e167.sh config start (the read-only ettelem config under the card lock, timeout 10);
#   go      bash tools/claims-v3/e167/run_e167.sh go <smoke-not-before> <smoke-latest> <no-start-after> <cutoff> (HH:MM, the box's
#           zone, PST), then the GO marker: touch build/e167/runs/GO (the day's post names aifoundry2 by then). The queue keeps E98's
#           two 15-minute no-launch rests itself: about 66-75 minutes of wall time for 35-39 card-minutes.
# The four gates are never defaulted (E167.md): E161's were smoke-not-before = now, smoke-latest an hour before no-start-after,
# no-start-after = the round's last start, cutoff = the round's last end. This step refuses gates past the window.
#
#   bash tools/claims-v3/q141k-runbook/s17_a2_e167.sh latch
#   bash tools/claims-v3/q141k-runbook/s17_a2_e167.sh config
#   bash tools/claims-v3/q141k-runbook/s17_a2_e167.sh go <HH:MM> <HH:MM> <HH:MM> <HH:MM>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s17_a2_e167
act=${1:-}
rb_window
[ "$RB_PLAN" = a ] && rb_die $RB_E_USAGE "plan a does not run E167"
LATCH="$RB_OUT/e167-latch.txt"
f=$(rb_file "e167-$act")
case "$act" in
  latch)
    { rb_prelude aifoundry2
      cat <<'EOF'
if [ -e build/e165/runs/status.json ] && ! grep -qE '"state": "(ended|halted)"' build/e165/runs/status.json; then
  echo "REFUSED: E165's queue has not ended (build/e165/runs/status.json)"; exit 3
fi
[ -e build/e165/runs ] || echo "note: E165 did not run today: E167's E2 arm will have no anchors (reported only)"
[ "$(ours_live)" -eq 0 ] || { echo "REFUSED: a card session of ours still runs"; exit 3; }
python3 tools/claims-v3/e167/latch_check_e167.py --history ~/live/history/$(date -u +%F).jsonl
echo "LATCH rc=$?"
EOF
    } > "$f"
    rb_probe aifoundry2
    rb_remote read aifoundry2 "E167's latch check on the box's history" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    rc=$(rb_val '^LATCH rc=([0-9]+)$')
    case "$rc" in
      0) echo "GO $(date +%s)" > "$LATCH"; rb_say "latch GO (under 72 C): E167 may go on" ;;
      2) echo "UNREADABLE $(date +%s)" > "$LATCH"; rb_say "latch UNREADABLE: go on; the smoke's first samples are the check" ;;
      3) echo "NO-GO $(date +%s)" > "$LATCH"; rb_die $RB_E_GATE "latch NO-GO (72 C or more): skip E167 today and go on to E168" ;;
      *) rb_die $RB_E_FAIL "the latch check gave no reading: $(grep -m1 '^REFUSED' "$RB_CAP")" ;;
    esac
    ;;
  config)
    { rb_prelude aifoundry2
      cat <<'EOF'
[ "$(ours_live)" -eq 0 ] || { echo "REFUSED: a card session of ours runs: the config read waits"; exit 3; }
bash tools/claims-v3/e167/run_e167.sh config start
EOF
    } > "$f"
    rb_probe aifoundry2
    rb_remote read aifoundry2 "run_e167.sh config start (read-only)" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_has '^config rc=0 ' || rb_die $RB_E_FAIL "the config read did not come back rc 0: read the output above"
    rb_say "E167's start config read (build/e167/config-start.txt on the box)"
    ;;
  go)
    [ $# -eq 5 ] || rb_die $RB_E_USAGE "usage: s17_a2_e167.sh go <smoke-not-before> <smoke-latest> <no-start-after> <cutoff> (HH:MM each)"
    nb=$2; sl=$3; nsa=$4; cut=$5
    for t in "$nb" "$sl" "$nsa" "$cut"; do
      echo "$t" | grep -qE '^([01][0-9]|2[0-3]):[0-5][0-9]$' || rb_die $RB_E_USAGE "not an HH:MM: $t"
    done
    m() { echo $(( 10#${1%:*} * 60 + 10#${1#*:} )); }
    [ "$(m "$nb")" -le "$(m "$sl")" ] && [ "$(m "$sl")" -lt "$(m "$nsa")" ] && [ "$(m "$nsa")" -lt "$(m "$cut")" ] ||
      rb_die $RB_E_USAGE "the gates must read smoke-not-before <= smoke-latest < no-start-after < cutoff"
    [ "$(m "$nsa")" -le "$(m "$RB_LAST_START_HM")" ] || rb_die $RB_E_GATE "no-start-after $nsa is past the round's last start $RB_LAST_START_HM"
    [ "$(m "$cut")" -le "$(m "$RB_LAST_END_HM")" ] || rb_die $RB_E_GATE "the cutoff $cut is past the round's last end $RB_LAST_END_HM"
    rb_need_start
    if [ -z "${RB_DRY:-}" ]; then
      case "$(cut -d' ' -f1 "$LATCH" 2>/dev/null)" in
        GO|UNREADABLE) ;;
        *) rb_die $RB_E_USAGE "run s17_a2_e167.sh latch first (after E165's queue): it must read GO or UNREADABLE" ;;
      esac
    fi
    { rb_prelude aifoundry2
      echo "NB=$nb; SL=$sl; NSA=$nsa; CUT=$cut"
      rb_guard_text
      cat <<'EOF'
bash tools/claims-v3/e167/run_e167.sh go "$NB" "$SL" "$NSA" "$CUT"; r=$?
echo "run_e167 go rc=$r"
[ "$r" -eq 0 ] || exit "$r"
[ -e build/e167/runs/queue.jsonl ] || [ -e build/e167/runs/status.json ] || { echo "no queue record: no GO touched"; exit 4; }
touch build/e167/runs/GO && echo "GO touched $(date '+%F %T %Z')"
echo "LAUNCHED e167 $(date '+%F %T %Z') (gates $NB / $SL / $NSA / $CUT)"
EOF
    } > "$f"
    rb_probe aifoundry2
    rb_remote launch aifoundry2 "run_e167.sh go and the GO marker" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_launched e167
    rb_say "E167's queue started and GO is touched; wait with s20_wait.sh e167 (about 66-75 minutes of wall time)"
    ;;
  *) rb_die $RB_E_USAGE "usage: s17_a2_e167.sh latch | config | go <HH:MM> <HH:MM> <HH:MM> <HH:MM>" ;;
esac
