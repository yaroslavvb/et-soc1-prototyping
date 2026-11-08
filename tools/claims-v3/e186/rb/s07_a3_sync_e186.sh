#!/usr/bin/env bash
# E186 (Q158, the kit), KIT.md box step 5 (this file is s07): aifoundry3's one rsync for E186, after the look read FREE. A port of E182's
# step 5 v2 (tools/claims-v3/e182/rb/s07_a3_sync_e182_v2.sh, its E174-class fix kept): the sync list is E186's paths and every other file
# harness-e186.json names but what the box builds (E182's files E186 calls, the train host's 8 build inputs under workloads/sparsity/, the
# merged list and M12's tiles among them), read by E182's sync_paths_e182.py, UNCHANGED, from the harness itself, so what step 6 checks on
# the box and what this step sends agree by construction. Only the pushed commit is synced (uncommitted changes in any synced path refuse,
# 16), and nothing is synced unless the lab clone's copies read at their sha256 (check_e186.py --desk, HARNESS OK 71; E182's
# check_inputs_e182.py, NOTE1 FILES OK 10). The rsync is E182 v2's form with -i: its itemized lines name every file whose content it sent,
# and the step reports any build input among them. E186: the window rule first (written today; now before the last start).
#
#   bash tools/claims-v3/e186/rb/s07_a3_sync_e186.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e186.sh"
rb_init s07_a3_sync
e186_window
rb_need_start
P=()
L=$(/usr/bin/python3 -B tools/claims-v3/e182/sync_paths_e182.py tools/claims-v3/e186/harness-e186.json "${E186_PATHS[@]}") ||
  rb_die $RB_E_USAGE "the sync list could not be read from harness-e186.json: $L"
cover=""; np=0
while IFS= read -r ln; do
  case "$ln" in
    "SYNC "*) P+=("${ln#SYNC }"); np=$((np + 1)) ;;
    "COVER "*) cover=${ln#COVER } ;;
  esac
done <<EOF2
$L
EOF2
set -- $cover
[ "$#" -eq 5 ] && [ "$1" -eq "$5" ] && [ "$np" -eq $((${#E186_PATHS[@]} + $4)) ] ||
  rb_die $RB_E_USAGE "the sync list does not cover harness-e186.json (COVER '$cover', $np paths)"
rb_say "harness-e186.json: $1 files to sync, all covered ($3 by E186's ${#E186_PATHS[@]} paths, $4 more); $2 built on the box, checked in step 6"
rb_say "the sync list: ${#P[@]} paths"
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e186.json's files at their sha256 (check_e186.py --desk)" \
  /usr/bin/python3 -B tools/claims-v3/e186/check_e186.py --desk
rb_has '^HARNESS OK: 71 files' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e186.json (the lines above): nothing is synced; a dated amendment registers it first"
rb_local read local "the train host's build inputs and E182 note 1's box files at their sha256 (check_inputs_e182.py)" \
  /usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py
rb_has '^NOTE1 FILES OK: 10 files' || rb_die $RB_E_GATE "a build input or E182 note 1 box file differs from harness-e182-note1.json (the lines above): nothing is synced"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E186's paths and every file of harness-e186.json but what the box builds (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ --exclude logs/ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  ch=$(grep -cE '^[<>]f' "$RB_CAP"); bi=$(grep -E '^[<>]f' "$RB_CAP" | grep -c ' workloads/sparsity/')
  rb_say "synced to aifoundry3:aifoundry/ (${#P[@]} paths); the rsync sent $ch files' contents there, $bi of them under workloads/sparsity/"
  [ "$bi" -gt 0 ] && rb_say "NOTE: the box held other copies of $bi workload files until now (the itemized lines above): its new copies are the committed ones; step 6 checks them before the build"
else
  rb_say "synced to aifoundry3:aifoundry/ every file of harness-e186.json but what the box builds"
fi
exit 0
