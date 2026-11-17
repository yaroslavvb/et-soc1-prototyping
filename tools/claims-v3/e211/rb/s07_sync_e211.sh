#!/usr/bin/env bash
# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum), the box step "the sync" (this file is s07; step 5), after the look read
# FREE: E206's step 5 (tools/claims-v3/e206/rb/s07_sync_e206.sh, landed in 906699ea), as E207's kit ported it (Q199), for E211's one box, whose tree is an rsync target with no
# git (aifoundry3 ~/aifoundry):
#   1. the window rule first (written today for E211; now before the last start);
#   2. the box read first: E211's ours_live (any session_eNNN.sh of ours, by its own script) and k6's jobs_live (a runbook job still running);
#      either above 0 is REFUSED on the box and 10 here, before anything is synced;
#   3. the sync list is harness-e211.json's files (check_e211.py --list: E211's box files, the registration's plan, points, forecast, kernel
#      record and identity gate, E206's check_e206.py and e206_common.py (the gate imports them), the checker v2 and its table, the tile
#      manifest, the two tiles, the two kernels' twenty sources) and harness-e211.json;
#      nothing is synced unless they are committed (uncommitted changes refuse, 16) and the lab clone's copies read at their sha256
#      (check_e211.py --box: HARNESS OK); ONE rsync -a -c -R -i into aifoundry3:aifoundry/, its itemized lines naming every file whose content it
#      sent; then check_e211.py --box ON THE BOX: HARNESS OK. It writes only those paths in the box's tree (E211's own files and the shared files
#      at their committed bytes); never build/.
#   bash tools/claims-v3/e211/rb/s07_sync_e211.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e211.sh"
rb_init s07_sync
e211_arm "${1:-}"
e211_window
rb_need_start
rb_probe "$BOX"
f=$(rb_file notours)
{ rb_prelude "$BOX"
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E211's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E211's sync never runs under one"; exit 3; fi
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read "$BOX" "no card session of ours and no runbook job on the box before the sync" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
while IFS= read -r p; do [ -n "$p" ] && P+=("$p"); done <<EOF2
$(/usr/bin/python3 -I -B tools/claims-v3/e211/check_e211.py --list)
EOF2
[ "${#P[@]}" -gt 10 ] || rb_die $RB_E_USAGE "the sync list could not be read from check_e211.py --list"
P+=(tools/claims-v3/e211/harness-e211.json)
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e211.json's files at their sha256" /usr/bin/python3 -I -B tools/claims-v3/e211/check_e211.py --box
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e211.json: nothing is synced"
rb_probe "$BOX"
rb_local copy "$BOX" "$BOX's rsync: harness-e211.json's files (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" "$BOX:$(rb_tree "$BOX")/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rs=$RB_CAP
f=$(rb_file harness)
{ rb_prelude "$BOX"; echo 'python3 -B tools/claims-v3/e211/check_e211.py --box | tail -n 1'; } > "$f"
rb_remote read "$BOX" "the harness at its sha256 on the box" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the box's copies differ from harness-e211.json after the sync (the line above)"
rb_say "synced to $BOX:$(rb_tree "$BOX")/ (${#P[@]} paths); the rsync sent $(grep -cE '^[<>]f' "$rs") files' contents there; HARNESS OK on the box"
exit 0
