#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE REAL-PATH DESK TEST's entry, E192's form
# (tools/claims-v3/e192/desk/desktest_realpath_e192.sh). The lesson (round log sections 104, 109 and 116): a check that runs only on the
# REAL path is never exercised by a dry pass, and a host's stdout on a real box can carry runtime lines inside its lines. This runs
# session_e196.sh's REAL path (no --dry) against stand-ins for every device tool (desk/standin_e196.py: the sampler and its config behind
# the box's own copy of E128's guard, the lab's sparsity host, the request's x14_host, et-who, ps), some of them printing the runtime's
# line INSIDE their own lines, the card lock (a lock file in a private /run/lock) and a stand-in box tree, through the smoke, both trains,
# two passes, the stop paths and the gates; the cases and their assertions are desk/realpath_e196.py's.
# THE SANDBOX: run it inside W/nodev.sh (aifoundry2 has a card of its own; nodev hides /dev/et*); it refuses if any /dev/et* is a
# device, then re-executes itself in bubblewrap with a private /dev holding TWO REGULAR FILES named /dev/et0_ops and /dev/et0_mgmt (the
# hosts' and the wrapper's node counts read names; nothing can be opened as a card), a private /run/lock, a private PID namespace and
# /proc, and the host name aifoundry3. Its two-card, no-card and no-mgmt cases nest a sandbox of their own inside.
#   bash tools/claims-v3/e196/desk/desktest_realpath_e196.sh <scratch dir outside the repo> > <log>
# Prints DESKTEST-REALPATH-E196 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
if [ -z "${E196_RP_INNER:-}" ]; then
  for d in /dev/et*; do
    [ -e "$d" ] || continue
    if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi
  done
  mkdir -p "$S" && S=$(cd "$S" && pwd -P)
  [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  : > "$S/et0_ops.regular-file"; : > "$S/et0_mgmt.regular-file"
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --bind "$S/et0_ops.regular-file" /dev/et0_ops \
    --bind "$S/et0_mgmt.regular-file" /dev/et0_mgmt \
    --unshare-pid --proc /proc --unshare-uts --hostname aifoundry3 --die-with-parent --setenv E196_RP_INNER 1 \
    -- /bin/bash "$SRC/tools/claims-v3/e196/desk/desktest_realpath_e196.sh" "$S"
fi
echo "inside the sandbox: hostname $(hostname); /dev/et*: $(ls -l /dev/et* 2>/dev/null | awk '{print $1, $NF}' | tr '\n' ' '); processes visible: $(ls /proc | grep -c '^[0-9]')"
exec /usr/bin/python3 -I -B "$SRC/tools/claims-v3/e196/desk/realpath_e196.py" "$SRC" "$S"
