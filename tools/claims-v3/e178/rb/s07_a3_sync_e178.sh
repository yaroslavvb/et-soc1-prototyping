#!/usr/bin/env bash
# E178 (Q146, the kit), step 7: aifoundry3's one rsync for E178, after the look read FREE (k6's s05_look_k6.sh aifoundry3). The paths are
# E178's own: its directory (the registration, the 34 new tiles, the kit), E78's six committed one-number tiles the registration runs under
# their own labels, and the three pinned watcher files; E163's card code, the ccheck files, the guard and the host source are already in
# ~/aifoundry unchanged (E171 ran them on 5 Nov 2026; check_e178.py says so in step 8). Only the pushed commit is synced: uncommitted changes
# in these paths refuse. A port of ../../q141k-runbook/k6/s07_a3_sync_k6.sh.
#
#   bash tools/claims-v3/e178/rb/s07_a3_sync_e178.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e178.sh"
rb_init s07_a3_sync
rb_local read local "E178's paths clean before the sync" git -C "$RB_REPO" status --short "${E178_PATHS[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E178's paths have uncommitted changes: sync only the pushed commit"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E178's directory, E78's six committed one-number tiles and the pinned watcher files" \
  rsync -a -c -R --exclude __pycache__ -e "$RB_RSH" "${E178_PATHS[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced E178's directory, E78's committed one-number tiles and the pinned watcher files to aifoundry3:aifoundry/"
