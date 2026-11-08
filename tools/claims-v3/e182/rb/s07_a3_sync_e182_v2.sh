#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1), step 7 v2: aifoundry3's one rsync for E182, after the look read FREE. It is v1
# (rb/s07_a3_sync_e182.sh, which stays as committed) with the verifier's MAJOR 2 closed (the E174 class): the sync list is v1's (E182's
# paths and every other file harness-e182.json names but what the box builds) PLUS every file harness-e182-note1.json names: the train
# host's 8 build inputs under workloads/sparsity/ that v1 never sent, and note 1's two box files. Both lists are read by
# sync_paths_e182.py, unchanged, from the two harness files themselves, so what step 8 v2 checks on the box and what this step sends agree
# by construction. As in v1: only the pushed commit is synced (uncommitted changes in any synced path refuse, 16), and nothing is synced
# unless the lab clone's copies read at their sha256 (check_e182.py --desk, HARNESS OK 66; new: check_inputs_e182.py, NOTE1 FILES OK 10).
# The rsync is v1's form with -i added: its itemized lines name every file whose content it sent to the box, and the step reports any
# build input among them (the box held a different copy until now).
#
#   bash tools/claims-v3/e182/rb/s07_a3_sync_e182_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s07_a3_sync_v2
P=(); seen=" "
for H in harness-e182.json harness-e182-note1.json; do
  L=$(/usr/bin/python3 -B tools/claims-v3/e182/sync_paths_e182.py "tools/claims-v3/e182/$H" "${E182_PATHS[@]}") ||
    rb_die $RB_E_USAGE "the sync list could not be read from $H: $L"
  cover=""; np=0
  while IFS= read -r ln; do
    case "$ln" in
      "SYNC "*) p=${ln#SYNC }; np=$((np + 1)); case "$seen" in *" $p "*) ;; *) P+=("$p"); seen="$seen$p " ;; esac ;;
      "COVER "*) cover=${ln#COVER } ;;
    esac
  done <<EOF2
$L
EOF2
  set -- $cover
  [ "$#" -eq 5 ] && [ "$1" -eq "$5" ] && [ "$np" -eq $((${#E182_PATHS[@]} + $4)) ] ||
    rb_die $RB_E_USAGE "the sync list does not cover $H (COVER '$cover', $np paths)"
  rb_say "$H: $1 files to sync, all covered ($3 by E182's ${#E182_PATHS[@]} paths, $4 more); $2 built on the box, checked in step 8"
done
rb_say "the sync list: ${#P[@]} paths"
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e182.json's files at their sha256 (check_e182.py --desk)" \
  /usr/bin/python3 -B tools/claims-v3/e182/check_e182.py --desk
rb_has '^HARNESS OK: 66 files' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e182.json (the lines above): nothing is synced; a dated amendment registers it first"
rb_local read local "the lab clone's copies of harness-e182-note1.json's files at their sha256 (check_inputs_e182.py)" \
  /usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py
rb_has '^NOTE1 FILES OK: 10 files' || rb_die $RB_E_GATE "a build input or note 1 box file differs from harness-e182-note1.json (the lines above): nothing is synced"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: v1's paths, the train host's 8 build inputs and note 1's box files (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ --exclude logs/ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  ch=$(grep -cE '^[<>]f' "$RB_CAP"); bi=$(grep -E '^[<>]f' "$RB_CAP" | grep -c ' workloads/sparsity/')   # content sent (an attribute-only line reads .f)
  rb_say "synced to aifoundry3:aifoundry/ (${#P[@]} paths); the rsync sent $ch files' contents there, $bi of them under workloads/sparsity/"
  [ "$bi" -gt 0 ] && rb_say "NOTE: the box held other copies of $bi workload files until now (the itemized lines above): its new copies are the committed ones; step 8 v2 checks them before the build, and the smoke's train gate and the desk's check of C judge what the host does with them"
else
  rb_say "synced to aifoundry3:aifoundry/ every file of the two harness files but what the box builds"
fi
exit 0
