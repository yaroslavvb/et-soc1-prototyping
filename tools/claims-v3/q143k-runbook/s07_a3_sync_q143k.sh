#!/usr/bin/env bash
# Q143(k), step 7: aifoundry3's one rsync for E176 (its README, box step 2), after the look read FREE: E176's kit and every repo file its box
# list (frozen-e176.sha256) names, from the pushed commit only (uncommitted changes in these paths refuse). The reused files are E166's and
# E78's, unchanged; rsync -c sends only what differs.
#
#   bash tools/claims-v3/q143k-runbook/s07_a3_sync_q143k.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s07_a3_sync
P=(tools/claims-v3/e176/)
while read -r _ p; do case "$p" in build/*|tools/claims-v3/e176/*) ;; *) P+=("$p") ;; esac; done < "$RB_REPO/tools/claims-v3/e176/frozen-e176.sha256"
rb_local read local "E176's paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E176's paths have uncommitted changes: sync only the pushed commit"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E176's kit and the ${#P[@]} paths of its box list" \
  rsync -a -c -R --exclude __pycache__ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced E176's kit and its box list's repo files to aifoundry3:aifoundry/"
