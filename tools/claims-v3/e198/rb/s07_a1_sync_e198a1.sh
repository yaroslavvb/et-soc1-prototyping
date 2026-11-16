#!/usr/bin/env bash
# E198 dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): step 5 (A1), THE SYNC. It is
# s07_a1_sync_e198.sh below (kit-e198, unchanged beside it) with the A1 harness: the sync list is harness_e198a1.py --list (the A1 box files,
# the lab's runner copy among them, and harness-e198-a1.json last), the lab clone's copies are read at harness-e198-a1.json's sha256, and the
# box reads HARNESS OK and TREE OK by harness_e198a1.py. Nothing else changes. v1's header, read with harness-e198-a1.json for harness-e198.json:
# E198 (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum; ported from E193's file of the same step, unchanged in logic but the names below), the box step "the sync" (this file is s07): aifoundry1's one rsync for E198, after the look read FREE, into E198's
# own root there, build/claims-v3/aifoundry1/e198 under the box's tree (~/nekko): a folder of ours, never another session's tree.
# E189's step 5's form (tools/claims-v3/e189/rb/s07_a1_sync_e189.sh):
#   1. the window rule first (written today for E198 and this RB_OUT's sitting; now before the last start);
#   2. the box read first: k6's ours_live (any session_eNNN.sh of ours) and jobs_live (a runbook job still running); either above 0 is
#      REFUSED on the box and 10 here, before anything is synced; E198's root is made there (mkdir -p) and nothing else is written;
#   3. the sync list is harness-e198.json's files (harness_e198.py --list: the registration's 29 files and its list, the kit's box files,
#      E128's guard, the device-command checker and its table, harness-e198.json), and nothing is synced unless they are committed
#      (uncommitted changes refuse, 16) and the lab clone's copies read at their sha256 (harness_e198.py --box: HARNESS OK); the rsync is
#      E189's form with -c -R -i into aifoundry1:nekko/build/claims-v3/aifoundry1/e198/, so each file lands at its repository path
#      under E198's root, its itemized lines naming every file whose content it sent.
#   bash tools/claims-v3/e198/rb/s07_a1_sync_e198.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198a1.sh"
rb_init s07_a1_sync_A1
e198_window
rb_need_start
rb_probe aifoundry1
f=$(rb_file notours)
{ rb_prelude aifoundry1
  echo "ROOT=$E198_ROOT"
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E198's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E198's sync never runs under one"; exit 3; fi
mkdir -p "$ROOT" || { echo "REFUSED: cannot make $ROOT"; exit 3; }
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX; E198's root $ROOT is there"
EOF3
} > "$f"
rb_remote read aifoundry1 "no card session of ours and no runbook job on the box before the sync; E198's root made" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
while IFS= read -r p; do [ -n "$p" ] && P+=("$p"); done <<EOF2
$(/usr/bin/python3 -I -B tools/claims-v3/e198/harness_e198a1.py --list)
EOF2
[ "${#P[@]}" -gt 30 ] || rb_die $RB_E_USAGE "the sync list could not be read from harness_e198a1.py --list"
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e198-a1.json's files at their sha256" /usr/bin/python3 -I -B tools/claims-v3/e198/harness_e198a1.py --box
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e198-a1.json: nothing is synced"
rb_probe aifoundry1
rb_local copy aifoundry1 "aifoundry1's rsync into E198's root: harness-e198-a1.json's files (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" "aifoundry1:nekko/$E198_ROOT/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
sent=$(grep -cE '^[<>]f' "$RB_CAP")
# THE TREE'S COPY OF E191'S GUARD (the guard shim runs it there: it reads the reader as ../../../build/ettelem/ettelem of its own folder):
# rsync -c of that one committed file to its repository path in the box's tree; a copy already there at the same bytes is left as it is
# (rsync -c sends nothing), and the box's copy is then read at its sha256 (6fd26f51...), with the reader at its pin (8008f96f...).
rb_local read local "E191's guard in the lab clone, committed and clean" git -C "$RB_REPO" status --short tools/claims-v3/e191/ettelem_guard_e191.sh
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E191's guard has uncommitted changes: sync only the pushed commit"
rb_probe aifoundry1
rb_local copy aifoundry1 "the tree's copy of E191's guard (rsync -c: sends nothing when the box holds the same bytes)" \
  rsync -a -c -R -i -e "$RB_RSH" tools/claims-v3/e191/ettelem_guard_e191.sh "aifoundry1:nekko/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the guard's rsync exited non-zero"
gsent=$(grep -cE '^[<>]f' "$RB_CAP")
f=$(rb_file tree)
{ rb_prelude aifoundry1
  echo "ROOT=$E198_ROOT"
  echo 'python3 -I -B "$ROOT/tools/claims-v3/e198/harness_e198a1.py" --box --root "$ROOT" | tail -n 1; python3 -I -B "$ROOT/tools/claims-v3/e198/harness_e198a1.py" --tree --root "$ROOT" | tail -n 1'
} > "$f"
rb_remote read aifoundry1 "E198's root at its harness and the box's tree files at their pins" "$f"
[ -n "${RB_DRY:-}" ] && { rb_say "synced to aifoundry1:nekko/$E198_ROOT/ every file of harness-e198-a1.json; the tree's E191 guard; HARNESS OK and TREE OK read on the box"; exit 0; }
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the box's copies differ from harness-e198-a1.json after the sync (the line above)"
rb_has '^TREE OK: ' || rb_die $RB_E_GATE "the box's tree files are not at their pins (E191's guard, the reader): no sitting on this box as it is"
rb_say "synced to aifoundry1:nekko/$E198_ROOT/ (${#P[@]} paths; the rsync sent $sent files' contents there); the tree's E191 guard ($gsent sent); HARNESS OK and TREE OK on the box"
exit 0
