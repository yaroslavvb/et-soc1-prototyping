#!/usr/bin/env bash
# E183 (Q155, the kit), KIT.md box step 5: one rsync of every file harness-e183.json names, and that file, to aifoundry3:aifoundry/ (E180's
# step 5 v2, ported; its path list is E180's sync_paths_e180.py, called unchanged on E183's harness, so what step 6 checks on the box and what
# this step copies there agree by construction). Nothing that the box builds is synced (build/ is excluded).
#   bash tools/claims-v3/e183/rb/s07_a3_sync_e183.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s07_a3_sync
L=$("$RB_PY" -B tools/claims-v3/e180/sync_paths_e180.py tools/claims-v3/e183/harness-e183.json "${E183_PATHS[@]}") ||
  rb_die $RB_E_USAGE "the sync list could not be read from harness-e183.json: $L"
P=(); cover=""
while IFS= read -r ln; do
  case "$ln" in "SYNC "*) P+=("${ln#SYNC }") ;; "COVER "*) cover=${ln#COVER } ;; esac
done <<EOF2
$L
EOF2
set -- $cover
[ "$#" -eq 4 ] && [ "$1" -eq "$4" ] && [ "${#P[@]}" -eq $((${#E183_PATHS[@]} + $3)) ] ||
  rb_die $RB_E_USAGE "the sync list does not cover the harness (COVER '$cover', ${#P[@]} paths)"
rb_say "the sync list: E183's directory (it holds $2 of the harness's $1 files) and its $3 other files: all $4 of them"
rb_local read local "E183's paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E183's paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of the harness's files at their sha256 (check_e183.py harness)" \
  "$RB_PY" -B tools/claims-v3/e183/check_e183.py harness
rb_has "^HARNESS OK: " || rb_die $RB_E_GATE "a file the sync would send differs from harness-e183.json (the lines above): nothing is synced; a dated amendment registers it first"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E183's directory, the committed workloads/enercat and the harness's other files" \
  rsync -a -c -R --exclude __pycache__ --exclude build -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced to aifoundry3:aifoundry/ every file of harness-e183.json ($4 files, in ${#P[@]} paths)"
