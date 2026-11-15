#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): THE REAL-PATH DESK TEST's entry. The lesson (round log section 104,
# E183's two lost days): a check that runs only on the REAL path is never exercised by a dry pass. This runs session_e192.sh's REAL path
# (no --dry) against stand-ins for every device tool (desk/standin_e192.py: the sampler, the per-sensor sampler, E78's heater, the host,
# et-who, ps), the card lock (a lock file in a private /run/lock) and a stand-in box tree, through the smoke, the stop paths and passes;
# the cases and their assertions are desk/realpath_e192.py's.
# THE SANDBOX: run it inside W/nodev.sh (aifoundry2 has a card of its own; nodev hides /dev/et*); it refuses if any /dev/et* is a
# device, then re-executes itself in bubblewrap with a private /dev holding TWO REGULAR FILES named /dev/et0_ops and /dev/et0_mgmt (the
# host's and the wrapper's node counts read names; nothing can be opened as a card; fix-e192 added /dev/et0_mgmt, which the wrapper's node
# count now requires), a private /run/lock, a private PID namespace and /proc (the test sees its own processes only), and the host name
# aifoundry3 (the registered order is drawn on it). Its two-card, no-card and no-mgmt cases nest a sandbox of their own inside (a fresh
# private /dev holding only the regular files each case names).
#   bash tools/claims-v3/e192/desk/desktest_realpath_e192.sh <scratch dir outside the repo> > <log>
# Prints DESKTEST-REALPATH-E192 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
if [ -z "${E192_RP_INNER:-}" ]; then
  for d in /dev/et*; do
    [ -e "$d" ] || continue
    if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi
  done
  mkdir -p "$S" && S=$(cd "$S" && pwd -P)
  [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  : > "$S/et0_ops.regular-file"; : > "$S/et0_mgmt.regular-file"
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --bind "$S/et0_ops.regular-file" /dev/et0_ops \
    --bind "$S/et0_mgmt.regular-file" /dev/et0_mgmt \
    --unshare-pid --proc /proc --unshare-uts --hostname aifoundry3 --die-with-parent --setenv E192_RP_INNER 1 \
    -- /bin/bash "$SRC/tools/claims-v3/e192/desk/desktest_realpath_e192.sh" "$S"
fi
echo "inside the sandbox: hostname $(hostname); /dev/et*: $(ls -l /dev/et* 2>/dev/null | awk '{print $1, $NF}' | tr '\n' ' '); processes visible: $(ls /proc | grep -c '^[0-9]')"
exec /usr/bin/python3 -I -B "$SRC/tools/claims-v3/e192/desk/realpath_e192.py" "$SRC" "$S"
