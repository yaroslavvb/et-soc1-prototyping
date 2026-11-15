#!/usr/bin/env bash
# E193 (Q177, the kit), the box step "the sync" (this file is s07): aifoundry3's one rsync for E193, after the look read FREE, into E193's
# own root there, build/claims-v3/aifoundry3/e193 under the box's tree (~/aifoundry): a folder of ours, never another session's tree.
# E189's step 5's form (tools/claims-v3/e189/rb/s07_a3_sync_e189.sh):
#   1. the window rule first (written today for E193 and this RB_OUT's sitting; now before the last start);
#   2. the box read first: k6's ours_live (any session_eNNN.sh of ours) and jobs_live (a runbook job still running); either above 0 is
#      REFUSED on the box and 10 here, before anything is synced; E193's root is made there (mkdir -p) and nothing else is written;
#   3. the sync list is harness-e193.json's files (harness_e193.py --list: the registration's 29 files and its list, the kit's box files,
#      E128's guard, the device-command checker and its table, harness-e193.json), and nothing is synced unless they are committed
#      (uncommitted changes refuse, 16) and the lab clone's copies read at their sha256 (harness_e193.py --box: HARNESS OK); the rsync is
#      E189's form with -c -R -i into aifoundry3:aifoundry/build/claims-v3/aifoundry3/e193/, so each file lands at its repository path
#      under E193's root, its itemized lines naming every file whose content it sent.
#   bash tools/claims-v3/e193/rb/s07_a3_sync_e193.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e193.sh"
rb_init s07_a3_sync
e193_window
rb_need_start
rb_probe aifoundry3
f=$(rb_file notours)
{ rb_prelude aifoundry3
  echo "ROOT=$E193_ROOT"
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E193's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E193's sync never runs under one"; exit 3; fi
mkdir -p "$ROOT" || { echo "REFUSED: cannot make $ROOT"; exit 3; }
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX; E193's root $ROOT is there"
EOF3
} > "$f"
rb_remote read aifoundry3 "no card session of ours and no runbook job on the box before the sync; E193's root made" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
while IFS= read -r p; do [ -n "$p" ] && P+=("$p"); done <<EOF2
$(/usr/bin/python3 -I -B tools/claims-v3/e193/harness_e193.py --list)
EOF2
[ "${#P[@]}" -gt 30 ] || rb_die $RB_E_USAGE "the sync list could not be read from harness_e193.py --list"
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e193.json's files at their sha256" /usr/bin/python3 -I -B tools/claims-v3/e193/harness_e193.py --box
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e193.json: nothing is synced"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync into E193's root: harness-e193.json's files (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" "aifoundry3:aifoundry/$E193_ROOT/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  rb_say "synced to aifoundry3:aifoundry/$E193_ROOT/ (${#P[@]} paths); the rsync sent $(grep -cE '^[<>]f' "$RB_CAP") files' contents there"
else
  rb_say "synced to aifoundry3:aifoundry/$E193_ROOT/ every file of harness-e193.json"
fi
exit 0
