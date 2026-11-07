#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 5: an arm's one rsync, after the look read FREE (k6's s05_look_k6.sh
# <box>). ../../e180/rb/s07_a3_sync_e180_v2.sh's form, for either box: E184's directory, the committed workloads/enercat and every other file
# harness-e184-v2.json names, the list read from the harness itself by ../../e180/sync_paths_e180.py (unchanged), so step 6's box check and
# this sync agree by construction (the E174 class). Only the pushed commit is synced: uncommitted changes in these paths refuse (16), and
# nothing is synced unless the lab clone's harness files read at their sha256 (check_e184_v2.py harness). rsync -c sends nothing where a file
# already matches. Arm S: aifoundry3:aifoundry/; arm B: aifoundry1:nekko/.
#
#   bash tools/claims-v3/e184/rb/s07_sync_e184.sh S|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s07_sync
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s07_sync_e184.sh S|B"
L=$("$RB_PY" -B tools/claims-v3/e180/sync_paths_e180.py tools/claims-v3/e184/harness-e184-v2.json "${E184_PATHS[@]}") ||
  rb_die $RB_E_USAGE "the sync list could not be read from harness-e184-v2.json: $L"
P=(); cover=""
while IFS= read -r ln; do
  case "$ln" in "SYNC "*) P+=("${ln#SYNC }") ;; "COVER "*) cover=${ln#COVER } ;; esac
done <<EOF2
$L
EOF2
set -- $cover
[ "$#" -eq 4 ] && [ "$1" -eq "$4" ] && [ "${#P[@]}" -eq $((${#E184_PATHS[@]} + $3)) ] ||
  rb_die $RB_E_USAGE "the sync list does not cover the harness (COVER '$cover', ${#P[@]} paths)"
rb_say "the sync list: E184's ${#E184_PATHS[@]} paths (they hold $2 of the harness's $1 files) and its $3 other files: all $4 of them"
rb_local read local "E184's paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E184's paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of the harness's files at their sha256 (check_e184_v2.py harness)" \
  "$RB_PY" -B tools/claims-v3/e184/check_e184_v2.py harness
rb_has "^HARNESS OK: " || rb_die $RB_E_GATE "a file the sync would send differs from harness-e184-v2.json (the lines above): nothing is synced; a dated amendment registers it first"
rb_probe "$E184_BOX"
rb_local copy "$E184_BOX" "$E184_BOX's rsync: E184's directory, the committed workloads/enercat and the harness's other files" \
  rsync -a -c -R --exclude __pycache__ --exclude build -e "$RB_RSH" "${P[@]}" "$E184_BOX:$E184_TREE/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced to $E184_BOX:$E184_TREE/ every file of harness-e184-v2.json ($4 files, in ${#P[@]} paths)"
