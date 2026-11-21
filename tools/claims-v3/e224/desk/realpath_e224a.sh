#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): the REAL-PATH desk test's namespaces, E215 arm A's desk/realpath_e215.sh form
# (landed in 8bde0182) for E224's arm A, aifoundry1 card 1 (E215 arm B's). realpath_e224a.py runs under bubblewrap with aifoundry1 as the hostname (a private UTS namespace), a
# private PID namespace and its own /proc (so `ps` and the stand-in et-who read only the test's processes). Run it ONLY inside the sandbox with no
# /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): it refuses otherwise.
#   bash tools/claims-v3/e224/desk/realpath_e224a.sh <an empty scratch dir outside the repo> > logs/realpath-e224a.txt
# The last line: REALPATH-E224A <n> of <m> PASS (or FAIL).
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "$S is not empty"; exit 2; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
echo "== arm A: hostname aifoundry1 (a private UTS namespace), a private PID namespace"
/usr/bin/bwrap --dev-bind / / --unshare-uts --hostname aifoundry1 --unshare-pid --proc /proc --die-with-parent -- \
  /usr/bin/python3 -B "$D/realpath_e224a.py" "$S" A > "$S/arm-A.txt" 2>&1
echo "rc $?"
cat "$S/arm-A.txt"
l=$(grep -E "^REALPATH-E224A arm A: [0-9]+ of [0-9]+" "$S/arm-A.txt" | tail -n 1)
n=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\1/'); m=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\2/')
[ -n "$n" ] && [ "${n:-0}" -eq "${m:-1}" ] && v=PASS || v=FAIL
echo "REALPATH-E224A ${n:-0} of ${m:-0} $v"
[ "$v" = PASS ]
