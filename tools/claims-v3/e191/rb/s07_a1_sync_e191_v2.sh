#!/usr/bin/env bash
# E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after
# E191's first session stopped at its smoke gate by a kit defect (1a4bc1e3), before any E191 pass datum; KIT.md.dated-note-2.md):
# step 5 v2: rb/s07_a1_sync_e191.sh (unchanged beside it) syncing HARNESS V2's 49 files (check_e191_v2.py --list: v1's 42, v1's
# harness-e191.json and the note's six box files) and reading both harnesses on the box after it (HARNESS OK, v1's 42; HARNESS-V2 OK, 49);
# every other line is v1's. v1's header: E191, the box step "the sync" (this file is
# s07): aifoundry1's one rsync for E191, after the look read FREE on both cards. E189's step 5 (tools/claims-v3/e189/rb/s07_a3_sync_e189.sh,
# unchanged beside it) with E191's box and tree, and E190 arm B's last read (rb/s07_sync_e190_v2.sh):
#   1. the window rule first (written today for E191; now before the last start);
#   2. the box read first: E191's ours_live (any session or queue of ours, by its own script) and jobs_live (a runbook job still running);
#      either above 0 is REFUSED on the box and 10 here, before anything is synced;
#   3. the sync list is harness-e191.json's files (check_e191.py --list), and nothing is synced unless they are committed (uncommitted
#      changes refuse, 16) and the lab clone's copies read at their sha256 (check_e191.py --box: HARNESS OK); ONE rsync -a -c -R -i into
#      aifoundry1:nekko/ (k6's tree for aifoundry1; the build directories of ours there are build/e191ledger and build/e191spp), its
#      itemized lines naming every file whose content it sent; then check_e191.py --box ON THE BOX: HARNESS OK.
#   bash tools/claims-v3/e191/rb/s07_a1_sync_e191.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s07_a1_sync_v2
e191_window
rb_need_start
rb_probe aifoundry1
f=$(rb_file notours)
{ rb_prelude aifoundry1
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E191's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E191's sync never runs under one"; exit 3; fi
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read aifoundry1 "no card session of ours and no runbook job on the box before the sync" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
while IFS= read -r p; do [ -n "$p" ] && P+=("$p"); done <<EOF2
$(/usr/bin/python3 -I -B tools/claims-v3/e191/check_e191_v2.py --list)
EOF2
[ "${#P[@]}" -gt 10 ] || rb_die $RB_E_USAGE "the sync list could not be read from check_e191_v2.py --list"
P+=(tools/claims-v3/e191/harness-e191-v2.json)
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e191-v2.json's files at their sha256" /usr/bin/python3 -I -B tools/claims-v3/e191/check_e191_v2.py --box
rb_has '^HARNESS-V2 OK: ' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e191-v2.json: nothing is synced"
rb_probe aifoundry1
rb_local copy aifoundry1 "aifoundry1's rsync: harness-e191-v2.json's files (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" aifoundry1:nekko/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rs=$RB_CAP
f=$(rb_file harness)
{ rb_prelude aifoundry1; echo 'python3 -B tools/claims-v3/e191/check_e191.py --box | tail -n 1; python3 -B tools/claims-v3/e191/check_e191_v2.py --box | tail -n 1'; } > "$f"
rb_remote read aifoundry1 "both harnesses at their sha256 on the box (v1's 42, v2's 49)" "$f"
[ -n "${RB_DRY:-}" ] && { rb_say "synced to aifoundry1:nekko/ every file of harness-e191-v2.json; HARNESS OK and HARNESS-V2 OK read on the box"; exit 0; }
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the box's copies differ from harness-e191.json after the sync (the line above)"
rb_has '^HARNESS-V2 OK: ' || rb_die $RB_E_GATE "the box's copies differ from harness-e191-v2.json after the sync (the line above)"
rb_say "synced to aifoundry1:nekko/ (${#P[@]} paths); the rsync sent $(grep -cE '^[<>]f' "$rs") files' contents there; HARNESS OK and HARNESS-V2 OK on the box"
exit 0
