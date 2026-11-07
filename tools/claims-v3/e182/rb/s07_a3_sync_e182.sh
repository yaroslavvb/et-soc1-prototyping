#!/usr/bin/env bash
# E182 (Q153, the kit), step 7: aifoundry3's one rsync for E182, after the look read FREE (k6's s05_look_k6.sh aifoundry3). E178's step 7
# v2 (tools/claims-v3/e178/rb/s07_a3_sync_e178_v2.sh), unchanged but for its files: it syncs E182's paths AND every other file
# harness-e182.json names but what the box builds (its four box binaries and the train host's patched source: sync_paths_e182.py), so
# step 8's check and this sync agree by construction (the E174 class). Only the pushed commit is synced: uncommitted changes in these paths
# refuse, and nothing is synced unless the lab clone's files read at the harness's sha256 (check_e182.py --desk).
#
#   bash tools/claims-v3/e182/rb/s07_a3_sync_e182.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s07_a3_sync
L=$(/usr/bin/python3 -B tools/claims-v3/e182/sync_paths_e182.py tools/claims-v3/e182/harness-e182.json "${E182_PATHS[@]}") ||
  rb_die $RB_E_USAGE "the sync list could not be read from harness-e182.json: $L"
P=(); cover=""
while IFS= read -r ln; do
  case "$ln" in "SYNC "*) P+=("${ln#SYNC }") ;; "COVER "*) cover=${ln#COVER } ;; esac
done <<EOF2
$L
EOF2
set -- $cover
[ "$#" -eq 5 ] && [ "$1" -eq "$5" ] && [ "${#P[@]}" -eq $((${#E182_PATHS[@]} + $4)) ] ||
  rb_die $RB_E_USAGE "the sync list does not cover the harness (COVER '$cover', ${#P[@]} paths)"
rb_say "the sync list: E182's ${#E182_PATHS[@]} paths (they hold $3 of the harness's $1 files) and its $4 other files: all $5 of them; the $2 built on the box are checked in step 8"
rb_local read local "E182's paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E182's paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of the harness's $1 files at their sha256 (check_e182.py --desk)" \
  /usr/bin/python3 -B tools/claims-v3/e182/check_e182.py --desk
rb_has "^HARNESS OK: $1 files" || rb_die $RB_E_GATE "a file the sync would send differs from harness-e182.json (the lines above): nothing is synced; a dated amendment registers it first"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E182's directory, E178's six tiles, E78's committed tiles, the pinned watcher files and the harness's card code" \
  rsync -a -c -R --exclude __pycache__ --exclude logs/ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced to aifoundry3:aifoundry/ every file of harness-e182.json but what the box builds ($5 files, in ${#P[@]} paths)"
