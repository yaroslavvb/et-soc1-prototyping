#!/usr/bin/env bash
# Q142(k6), step 7: aifoundry3's one rsync for E171 (E171's README, box step 4), after the look read FREE. The paths are E171's own:
# its kit, pool 8, and the three pinned watcher files; E163's card code, the ccheck files, the guard and the host source are already in
# ~/aifoundry unchanged (check_e171.py says so in step 8). Only the pushed commit is synced: uncommitted changes in these paths refuse.
#
#   bash tools/claims-v3/q141k-runbook/k6/s07_a3_sync_k6.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s07_a3_sync
P=(tools/claims-v3/e171/ tools/claims-v3/kinds/blind8/ tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/hpl/run_hpl.py.dated-note.md
   tools/claims-v3/hpl/run_hpl.py.dated-note-2.md)
rb_local read local "E171's paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E171's paths have uncommitted changes: sync only the pushed commit"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E171's kit, pool 8 and the pinned watcher files" \
  rsync -a -c -R --exclude __pycache__ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced E171's kit, pool 8 and the pinned watcher files to aifoundry3:aifoundry/"
