#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): THE REAL-PATH DESK TEST's entry, E196's form
# (tools/claims-v3/e196/desk/desktest_realpath_e196.sh). The lesson (round log sections 104, 109 and 116): a check that runs only on the
# REAL path is never exercised by a dry pass, and a host's stdout on a real box can carry runtime lines inside its lines. This runs
# session_e202.sh's REAL path (no --dry), exactly as step 9 launches it, against stand-ins for every device tool (desk/standin_e202.py:
# the sampler and its config behind the box copy of E128's guard, the mnistmlp host, et-who), some printing a runtime line INSIDE their
# own lines, the card lock (a lock file in a private /run/lock) and a stand-in box tree; the cases and their assertions, and the audit of
# every dry branch, are desk/realpath_e202.py's.
# THE SANDBOX: run it inside W/nodev.sh (aifoundry2 has a card of its own; nodev hides /dev/et*); it refuses if any /dev/et* is a
# device, then re-executes itself in bubblewrap with a private /dev holding TWO REGULAR FILES named /dev/et0_ops and /dev/et0_mgmt (the
# runner counts the names; nothing can be opened as a card), a private /run/lock, a private PID namespace and /proc, and the host name
# aifoundry3. Its other-host and two-card cases nest a sandbox of their own inside.
#   bash tools/claims-v3/e202/desk/desktest_realpath_e202.sh <scratch dir outside the repo> <a box tree built today by build_e202.sh>
# Prints DESKTEST-REALPATH-E202 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
BUILT=${2:?a box tree where build_e202.sh read E202-BUILT today (its build/e202mnist and build/e202files are used)}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
if [ -z "${E202_RP_INNER:-}" ]; then
  for d in /dev/et*; do
    [ -e "$d" ] || continue
    if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi
  done
  mkdir -p "$S" && S=$(cd "$S" && pwd -P)
  [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  : > "$S/et0_ops.regular-file"; : > "$S/et0_mgmt.regular-file"
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --bind "$S/et0_ops.regular-file" /dev/et0_ops \
    --bind "$S/et0_mgmt.regular-file" /dev/et0_mgmt \
    --unshare-pid --proc /proc --unshare-uts --hostname aifoundry3 --die-with-parent --setenv E202_RP_INNER 1 \
    -- /bin/bash "$SRC/tools/claims-v3/e202/desk/desktest_realpath_e202.sh" "$S" "$BUILT"
fi
unset E202_RP_INNER
echo "inside the sandbox: hostname $(hostname); /dev/et*: $(ls -l /dev/et* 2>/dev/null | awk '{print $1, $NF}' | tr '\n' ' '); processes visible: $(ls /proc | grep -c '^[0-9]')"
exec /usr/bin/python3 -I -B "$SRC/tools/claims-v3/e202/desk/realpath_e202.py" "$SRC" "$S" "$BUILT"
