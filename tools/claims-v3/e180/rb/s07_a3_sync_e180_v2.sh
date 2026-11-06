#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, ../KIT.md.dated-note-1.md section 4), step 7, v2: aifoundry3's one rsync for E180, after the look read
# FREE (k6's s05_look_k6.sh aifoundry3). It replaces s07_a3_sync_e180.sh (v1, which stays as committed) in the runbook. v1 synced E180's
# directory and the committed workloads/enercat, and relied on aifoundry3's ~/aifoundry still holding the harness's four other files at their
# committed hashes: lib.sh, E128's guard, dmcmd_audit.py and its table (the adversarial verifier's fault 8, the E174 class, mitigated: they
# last changed on 28 Sep and 2 Nov, and E171 and E176 ran them there on 5 Nov). v2 syncs v1's paths AND every other file harness-e180-v2.json
# names, the list read from the harness itself by ../sync_paths_e180.py (E178's s07_a3_sync_e178_v2.sh form), so step 8's check and this
# sync agree by construction. rsync -c sends nothing where a file already matches; the form is v1's (and E171's, E176's, E178's) unchanged.
# Only the pushed commit is synced: uncommitted changes in these paths refuse. And nothing is synced unless the lab clone's harness files read
# at their sha256 (check_e180_v2.py harness, as step 3 runs it): v2 sends four files v1 never sent, so a later commit to one of them (lib.sh is
# shared by every kit) must stop here, before it can overwrite the box's good copy.
#
#   bash tools/claims-v3/e180/rb/s07_a3_sync_e180_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s07_a3_sync_v2
L=$("$RB_PY" -B tools/claims-v3/e180/sync_paths_e180.py tools/claims-v3/e180/harness-e180-v2.json "${E180_PATHS[@]}") ||
  rb_die $RB_E_USAGE "the sync list could not be read from harness-e180-v2.json: $L"
P=(); cover=""
while IFS= read -r ln; do
  case "$ln" in "SYNC "*) P+=("${ln#SYNC }") ;; "COVER "*) cover=${ln#COVER } ;; esac
done <<EOF2
$L
EOF2
set -- $cover
[ "$#" -eq 4 ] && [ "$1" -eq "$4" ] && [ "${#P[@]}" -eq $((${#E180_PATHS[@]} + $3)) ] ||
  rb_die $RB_E_USAGE "the sync list does not cover the harness (COVER '$cover', ${#P[@]} paths)"
rb_say "the sync list: v1's ${#E180_PATHS[@]} paths (they hold $2 of the harness's $1 files) and its $3 other files: all $4 of them"
rb_local read local "E180's paths clean before the sync (v1's and the harness's other $3 files)" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E180's paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of the harness's files at their sha256 (check_e180_v2.py harness)" \
  "$RB_PY" -B tools/claims-v3/e180/check_e180_v2.py harness
rb_has "^HARNESS OK: " || rb_die $RB_E_GATE "a file the sync would send differs from harness-e180-v2.json (the lines above): nothing is synced; a dated amendment registers it first"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E180's directory, the committed workloads/enercat and the harness's other files" \
  rsync -a -c -R --exclude __pycache__ --exclude build -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced to aifoundry3:aifoundry/ every file of harness-e180-v2.json ($4 files, in ${#P[@]} paths)"
