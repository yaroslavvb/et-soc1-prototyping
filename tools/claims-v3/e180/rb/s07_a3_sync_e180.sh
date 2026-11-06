#!/usr/bin/env bash
# E180 (Q146(f), the kit), step 7: aifoundry3's one rsync for E180, after the look read FREE (k6's s05_look_k6.sh aifoundry3). The paths are
# E180's own directory (the registration, its 25 operand images and the kit) and the committed workloads/enercat the box build copies; lib.sh,
# E128's guard and the device-command checker are already in ~/aifoundry (E171 and E178's kit ran them; check_e180.py says so in step 8). Only
# the pushed commit is synced: uncommitted changes in these paths refuse. tools/claims-v3/e178/rb/s07_a3_sync_e178.sh's form.
#
#   bash tools/claims-v3/e180/rb/s07_a3_sync_e180.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s07_a3_sync
rb_local read local "E180's paths clean before the sync" git -C "$RB_REPO" status --short "${E180_PATHS[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E180's paths have uncommitted changes: sync only the pushed commit"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E180's directory and the committed workloads/enercat" \
  rsync -a -c -R --exclude __pycache__ --exclude build -e "$RB_RSH" "${E180_PATHS[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced E180's directory and workloads/enercat to aifoundry3:aifoundry/"
