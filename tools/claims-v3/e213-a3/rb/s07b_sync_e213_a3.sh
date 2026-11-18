#!/usr/bin/env bash
# E213 Amendment A3 (Q219, lane a3-e213, Wed 18 Nov 2026, before any datum of E213's arm B), ROW 5b FOR ARM B, NEW: A3's box files into the box's
# tree, right after the kit's step 5 (tools/claims-v3/e213/rb/s07_sync_e213.sh B, unchanged: it syncs harness-e213.json's files, among them
# the registration's points-e213.json and the runner, which A3's check reads on the box) and before step 6. Each call, in this order (nothing is
# synced before the gate above it passes):
#   1. the window rule (written today for E213 arm B; now before the last start); arm A is refused (10): A3 is arm B's alone;
#   2. THE PINS at the desk: A3's three box files (tools/claims-v3/e213-a3/run_e213_a3.py, session_e213.sh, sequence-B-a3.json) committed,
#      unmodified and at their sha256 in the lab clone (rb/rb_e213_a3.sh), else 16;
#   3. the box read first, the kit's step 5's own lines: E213's ours_live (any session_eNNN*.sh of ours, by its own script) and k6's jobs_live
#      (a runbook job still running); either above 0 is REFUSED on the box and 10 here, before anything is synced;
#   4. ONE rsync -a -c -R -i of the three files into the box's tree (nekko), at their committed bytes (it writes only those three paths, under
#      tools/claims-v3/e213-a3/; never build/);
#   5. on the box: their sha256 (A3-PINS OK 3 of 3) and the wrapper's own check (`python3 -I -B tools/claims-v3/e213-a3/run_e213_a3.py check`:
#      points-e213.json at its registered sha256, the sequence file at its pin and EQUAL to A3's order derived from that points file; no device,
#      no lock): "A3-ORDER OK: ...", else A3-STOP and 16;
#   6. RB_OUT/e213-a3-sync-B.txt ("A3-SYNC-B: OK; ..."), which A3's step 9 requires from today.
# Exits: 0 pass; 10 refused (usage, arm A, the window, a session or runbook job of ours on the box); 11 a login link; 12 no answer; 13 past a
# bound; 14 a call failed; 16 a gate says stop (A3's files off their pins at the desk or on the box, or A3's order check refused: no session
# today until it passes: row E, tell the orchestrator).
#   bash tools/claims-v3/e213-a3/rb/s07b_sync_e213_a3.sh B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e213_a3.sh"
rb_init s07b_sync_a3
e213_arm "${1:-}"
e213a3_only_B
e213_window
rb_need_start
e213a3_check_desk
# 3. the box read first (the kit's step 5's lines, verbatim)
rb_probe "$BOX"
f=$(rb_file a3notours)
{ rb_prelude "$BOX"
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E213's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E213's sync never runs under one"; exit 3; fi
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read "$BOX" "no card session of ours and no runbook job on the box before A3's sync" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before A3's sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before A3's sync gave no answer: nothing synced"
# 4. A3's box files into the box's tree
rb_probe "$BOX"
rb_local copy "$BOX" "$BOX's rsync: A3's box files (the runner's wrapper, its session wrapper, the order), itemized" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" $E213A3_BOXFILES "$BOX:$(rb_tree "$BOX")/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync of A3's box files exited $RB_RC"
rs=$RB_CAP
# 5. the pins and A3's order check on the box (no device)
f=$(rb_file a3check)
{ rb_prelude "$BOX"; e213a3_box_text "no session until row 5b passes"; } > "$f"
rb_remote read "$BOX" "A3's box files at their pinned sha256 and A3's order check on the box (the wrapper's check; no device)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^A3-STOP' && rb_die $RB_E_GATE "$(grep -m1 '^A3-STOP' "$RB_CAP" | cut -c1-300) (Amendment A3): no session today until row 5b passes; tell the orchestrator"
{ [ "$RB_RC" -eq 0 ] && rb_has '^A3-PINS OK 3 of 3$' && rb_has '^A3-ORDER OK: arm B 85 runs, '; } ||
  rb_die $RB_E_GATE "A3's check on $BOX gave no A3-PINS OK 3 of 3 and A3-ORDER OK (exit $RB_RC): no session today until row 5b passes"
m="A3-SYNC-B: OK; the rsync sent $(grep -cE '^[<>]f' "$rs") files' contents; $(grep -m1 '^A3-PINS OK' "$RB_CAP"); $(grep -m1 '^A3-ORDER OK: ' "$RB_CAP" | cut -c1-260)"
echo "$(date '+%F %T %Z') $m" > "$RB_OUT/e213-a3-sync-B.txt"
echo "$(date '+%F %T %Z') step=$RB_STEP $m" >> "$RB_LOG"
rb_say "A3's box files synced to $BOX:$(rb_tree "$BOX")/ and checked there: $(grep -m1 '^A3-PINS OK' "$RB_CAP"); $(grep -m1 '^A3-ORDER OK: ' "$RB_CAP" | cut -c1-200)"
exit 0
