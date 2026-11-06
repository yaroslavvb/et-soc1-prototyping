#!/usr/bin/env bash
# E181, step 7: aifoundry3's one rsync for E181 (its README, box step 2), after the look read FREE: E181's kit directory and every repo
# file its box list (frozen-e181.sha256) names, from the pushed commit only (uncommitted changes in these paths refuse). So what step 8 checks
# on the box (the box list, 30: these 27 repo files and the three box binaries) and what this step copies agree by construction, and the
# DRY-INTEL dry pass (../dry_intel_e181.sh) runs the session in a tree built from this list alone (E174's defect class). The reused files are
# E176's, E166's and E78's, unchanged; rsync -c sends only what differs. ../../q143k-runbook/s07_a3_sync_q143k.sh (92a1b27f) ported.
#
#   bash tools/claims-v3/e181/rb/s07_a3_sync_e181.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
rb_init s07_a3_sync
P=(tools/claims-v3/e181/)
while read -r _ p; do case "$p" in build/*|tools/claims-v3/e181/*) ;; *) P+=("$p") ;; esac; done < "$RB_REPO/tools/claims-v3/e181/frozen-e181.sha256"
rb_local read local "E181's paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E181's paths have uncommitted changes: sync only the pushed commit"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E181's kit and the ${#P[@]} paths of its box list" \
  rsync -a -c -R --exclude __pycache__ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced E181's kit and its box list's repo files to aifoundry3:aifoundry/"
