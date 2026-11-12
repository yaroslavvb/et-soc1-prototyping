#!/usr/bin/env bash
# E188 (Q165, the kit), KIT.md box step 5 (this file is s07): aifoundry3's one rsync for E188, after the look read FREE. A port of E186's
# step 5 v2 and v1 in one file (tools/claims-v3/e186/rb/s07_a3_sync_e186_v2.sh, then s07_a3_sync_e186.sh; E182's E174-class fix kept):
#   1. the window rule first (written today for E188; now before the last start);
#   2. E186 kit note 1's read on the box first: k6's ours_live (any session_eNNN.sh or queue_eNNN.sh of ours) and jobs_live (a runbook job
#      of any day still running, a build job among them); either above 0 is REFUSED on the box and 10 here, before anything is synced;
#   3. the sync list is E188's paths and every other file harness-e188.json names but what the box builds (E182's files E188 calls, the
#      train host's 8 build inputs under workloads/sparsity/, E188's kinds list and its fifteen kinds' tiles among them, lq_h0's and aq_h0's
#      at their committed data paths), read by E182's sync_paths_e182.py, UNCHANGED, from the harness itself, so what step 6 checks on the
#      box and what this step sends agree by construction. Only the pushed commit is synced (uncommitted changes in any synced path
#      refuse, 16), and nothing is synced unless the lab clone's copies read at their sha256 (check_e188.py --desk, HARNESS OK 72; E182's
#      check_inputs_e182.py, NOTE1 FILES OK 10). The rsync is E182 v2's form with -i: its itemized lines name every file whose content it
#      sent, and the step reports any build input among them.
#
#   bash tools/claims-v3/e188/rb/s07_a3_sync_e188.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e188.sh"
rb_init s07_a3_sync
e188_window
rb_need_start
rb_probe aifoundry3
f=$(rb_file notours)
{ rb_prelude aifoundry3
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E188's step 5 never syncs beside one (one session of ours at a time)"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E188's step 5 never syncs under one (read them with their own step first)"; exit 3; fi
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read aifoundry3 "no card session of ours and no runbook job on the box before the sync (k6's ours_live and jobs_live)" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
L=$(/usr/bin/python3 -B tools/claims-v3/e182/sync_paths_e182.py tools/claims-v3/e188/harness-e188.json "${E188_PATHS[@]}") ||
  rb_die $RB_E_USAGE "the sync list could not be read from harness-e188.json: $L"
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
[ "$#" -eq 5 ] && [ "$1" -eq "$5" ] && [ "$np" -eq $((${#E188_PATHS[@]} + $4)) ] ||
  rb_die $RB_E_USAGE "the sync list does not cover harness-e188.json (COVER '$cover', $np paths)"
rb_say "harness-e188.json: $1 files to sync, all covered ($3 by E188's ${#E188_PATHS[@]} paths, $4 more); $2 built on the box, checked in step 6"
rb_say "the sync list: ${#P[@]} paths"
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e188.json's files at their sha256 (check_e188.py --desk)" \
  /usr/bin/python3 -B tools/claims-v3/e188/check_e188.py --desk
rb_has '^HARNESS OK: 72 files' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e188.json (the lines above): nothing is synced; a dated amendment registers it first"
rb_local read local "the train host's build inputs and E182 note 1's box files at their sha256 (check_inputs_e182.py)" \
  /usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py
rb_has '^NOTE1 FILES OK: 10 files' || rb_die $RB_E_GATE "a build input or E182 note 1 box file differs from harness-e182-note1.json (the lines above): nothing is synced"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E188's paths and every file of harness-e188.json but what the box builds (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ --exclude logs/ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  ch=$(grep -cE '^[<>]f' "$RB_CAP"); bi=$(grep -E '^[<>]f' "$RB_CAP" | grep -c ' workloads/sparsity/')
  rb_say "synced to aifoundry3:aifoundry/ (${#P[@]} paths); the rsync sent $ch files' contents there, $bi of them under workloads/sparsity/"
  [ "$bi" -gt 0 ] && rb_say "NOTE: the box held other copies of $bi workload files until now (the itemized lines above): its new copies are the committed ones; step 6 checks them before the build"
else
  rb_say "synced to aifoundry3:aifoundry/ every file of harness-e188.json but what the box builds"
fi
exit 0
