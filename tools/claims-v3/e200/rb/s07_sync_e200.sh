#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum), the box step "the sync" (this file is s07): aifoundry2's one rsync
# for E200, after the look read FREE, into E200's own root there, build/claims-v3/aifoundry2/e200 under the box's tree
# (~/claude/et-soc1-prototyping, k6's rb_tree for aifoundry2; its build/ is git-ignored there): a build folder of ours, never the box
# tree's own files and never another session's tree. E197's step 5 (tools/claims-v3/e197/rb/s07_a3_sync_e197.sh, unchanged beside it)
# with E200's box, root and harness, reached through k6's drivers by ssh to this box itself (E194's way):
#   1. the window rule first (written today for E200 and this RB_OUT's sitting; now before the last start) and THE QUIET DESK FLAG raised;
#   2. the box read first: E194's ours_live (any session_eNNN.sh of ours, by each process's own script) and jobs_live (a runbook job still
#      running); either above 0 is REFUSED on the box and 10 here, before anything is synced; E200's root is made there (mkdir -p) and
#      nothing else is written;
#   3. the sync list is harness-e200.json's files (harness_e200.py --list: E197's registration's 35 files and its list, E200's W1 diff,
#      the kit's box files with E200's guard, the device-command checker v2 and its table, the lab's firmware gate with its records, E194's
#      common module, harness-e200.json), and nothing is synced unless they are committed (uncommitted changes refuse, 16) and the lab
#      clone's copies read at their sha256 (harness_e200.py --box: HARNESS OK); the rsync is E189's form with -c -R -i into
#      aifoundry2:claude/et-soc1-prototyping/build/claims-v3/aifoundry2/e200/, so each file lands at its repository path under E200's
#      root, its itemized lines naming every file whose content it sent.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e200/rb/s07_sync_e200.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e200.sh"
rb_init s07_sync
e200_window
e200_quiet
rb_need_start
rb_probe aifoundry2
f=$(rb_file notours)
{ rb_prelude aifoundry2
  echo "ROOT=$E200_ROOT"
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E200's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E200's sync never runs under one"; exit 3; fi
mkdir -p "$ROOT" || { echo "REFUSED: cannot make $ROOT"; exit 3; }
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX; E200's root $ROOT is there"
EOF3
} > "$f"
rb_remote read aifoundry2 "no card session of ours and no runbook job on the box before the sync; E200's root made" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
while IFS= read -r p; do [ -n "$p" ] && P+=("$p"); done <<EOF2
$(/usr/bin/python3 -I -B tools/claims-v3/e200/harness_e200.py --list)
EOF2
[ "${#P[@]}" -gt 30 ] || rb_die $RB_E_USAGE "the sync list could not be read from harness_e200.py --list"
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e200.json's files at their sha256" /usr/bin/python3 -I -B tools/claims-v3/e200/harness_e200.py --box
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e200.json: nothing is synced"
rb_probe aifoundry2
rb_local copy aifoundry2 "aifoundry2's rsync into E200's root: harness-e200.json's files (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" "aifoundry2:claude/et-soc1-prototyping/$E200_ROOT/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  rb_say "synced to aifoundry2:claude/et-soc1-prototyping/$E200_ROOT/ (${#P[@]} paths); the rsync sent $(grep -cE '^[<>]f' "$RB_CAP") files' contents there"
else
  rb_say "synced to aifoundry2:claude/et-soc1-prototyping/$E200_ROOT/ every file of harness-e200.json"
fi
exit 0
