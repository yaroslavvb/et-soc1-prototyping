#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE REAL-PATH DESK TEST's sandbox. E192's
# (tools/claims-v3/e192/desk/desktest_realpath_e192.sh, unchanged beside it) made aifoundry1 card 1's. Run it ONLY inside the round's
# no-device sandbox (W/nodev.sh, under W/slot.sh): it refuses if any /dev/et* here is a device node, then re-executes itself in bubblewrap
# with a private /dev holding aifoundry1's four node names as stand-ins (/dev/et0_ops, /dev/et0_mgmt, /dev/et1_ops, /dev/et1_mgmt, each
# a bind of /dev/null: a character node that is no card, so run_session.sh's own `[ -c /dev/et1_ops ]` and the identity watch read them
# as nodes), a private /run/lock (the test makes card 1's and card 0's lock files there), a private PID namespace and /proc, and the host
# name aifoundry1; then runs desk/realpath_e199.py. Nothing opens a card.
#   bash W/slot.sh bash W/nodev.sh bash tools/claims-v3/e199/desk/desktest_realpath_e199.sh <an empty scratch dir outside the repo>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
if [ -z "${E199_RP_INNER:-}" ]; then
  for d in /dev/et*; do
    [ -e "$d" ] || continue
    if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi
  done
  # fix-e199 (verify-e199 F7): never start, and never wait inside the sandbox, while THE QUIET DESK FLAG exists: NOT RUN (exit 5)
  if [ -n "${E199_QUIET_FLAG:-}" ] && [ -e "$E199_QUIET_FLAG" ]; then echo "DESKTEST-REALPATH-E199 NOT RUN: the quiet-desk flag exists"; exit 5; fi
  mkdir -p "$S" && S=$(cd "$S" && pwd -P)
  [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock \
    --dev-bind /dev/null /dev/et0_ops --dev-bind /dev/null /dev/et0_mgmt --dev-bind /dev/null /dev/et1_ops --dev-bind /dev/null /dev/et1_mgmt \
    --unshare-pid --proc /proc --unshare-uts --hostname aifoundry1 --die-with-parent --setenv E199_RP_INNER 1 \
    -- /bin/bash "$SRC/tools/claims-v3/e199/desk/desktest_realpath_e199.sh" "$S"
fi
echo "inside the sandbox: hostname $(hostname); /dev/et*: $(ls -l /dev/et* 2>/dev/null | awk '{print $1, $NF}' | tr '\n' ' '); processes visible: $(ls /proc | grep -c '^[0-9]')"
exec /usr/bin/python3 -I -B "$SRC/tools/claims-v3/e199/desk/realpath_e199.py" "$SRC" "$S"
