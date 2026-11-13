#!/usr/bin/env bash
# E189 (Q167, the kit), the box step "the sync" (this file is s07): aifoundry3's one rsync for E189, after the look read FREE. E188's step 5's
# form (tools/claims-v3/e188/rb/s07_a3_sync_e188.sh):
#   1. the window rule first (written today for E189; now before the last start);
#   2. the box read first: k6's ours_live (any session_eNNN.sh of ours) and jobs_live (a runbook job still running); either above 0 is
#      REFUSED on the box and 10 here, before anything is synced;
#   3. the sync list is harness-e189.json's files (check_e189.py --list), and nothing is synced unless they are committed (uncommitted
#      changes refuse, 16) and the lab clone's copies read at their sha256 (check_e189.py --box: HARNESS OK); the rsync is E188's form with
#      -c -R -i into aifoundry3:aifoundry/, its itemized lines naming every file whose content it sent.
#   bash tools/claims-v3/e189/rb/s07_a3_sync_e189.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e189.sh"
rb_init s07_a3_sync
e189_window
rb_need_start
rb_probe aifoundry3
f=$(rb_file notours)
{ rb_prelude aifoundry3
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E189's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E189's sync never runs under one"; exit 3; fi
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read aifoundry3 "no card session of ours and no runbook job on the box before the sync" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
while IFS= read -r p; do [ -n "$p" ] && P+=("$p"); done <<EOF2
$(/usr/bin/python3 -I -B tools/claims-v3/e189/check_e189.py --list)
EOF2
[ "${#P[@]}" -gt 10 ] || rb_die $RB_E_USAGE "the sync list could not be read from check_e189.py --list"
P+=(tools/claims-v3/e189/harness-e189.json)
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e189.json's files at their sha256" /usr/bin/python3 -I -B tools/claims-v3/e189/check_e189.py --box
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e189.json: nothing is synced"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: harness-e189.json's files (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  rb_say "synced to aifoundry3:aifoundry/ (${#P[@]} paths); the rsync sent $(grep -cE '^[<>]f' "$RB_CAP") files' contents there"
else
  rb_say "synced to aifoundry3:aifoundry/ every file of harness-e189.json"
fi
exit 0
