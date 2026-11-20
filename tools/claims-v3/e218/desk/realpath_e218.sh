#!/usr/bin/env bash
# E218 (Q230, lane kit-e218, Thu 19 Nov 2026, before any E218 datum): the REAL-PATH desk test's namespaces, E215 arm A's desk/realpath_e215.sh form
# (landed in 8bde0182) for E218's one arm. realpath_e218.py runs under bubblewrap with aifoundry3 as the hostname (a private UTS namespace), a
# private PID namespace and its own /proc (so `ps` and the stand-in et-who read only the test's processes). Run it ONLY inside the sandbox with no
# /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): it refuses otherwise.
#   bash tools/claims-v3/e218/desk/realpath_e218.sh <an empty scratch dir outside the repo> > logs/realpath-e218.txt
# The last line: REALPATH-E218 <n> of <m> PASS (or FAIL).
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "$S is not empty"; exit 2; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
echo "== arm A: hostname aifoundry3 (a private UTS namespace), a private PID namespace"
/usr/bin/bwrap --dev-bind / / --unshare-uts --hostname aifoundry3 --unshare-pid --proc /proc --die-with-parent -- \
  /usr/bin/python3 -B "$D/realpath_e218.py" "$S" A > "$S/arm-A.txt" 2>&1
echo "rc $?"
cat "$S/arm-A.txt"
l=$(grep -E "^REALPATH-E218 arm A: [0-9]+ of [0-9]+" "$S/arm-A.txt" | tail -n 1)
n=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\1/'); m=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\2/')
[ -n "$n" ] && [ "${n:-0}" -eq "${m:-1}" ] && v=PASS || v=FAIL
echo "REALPATH-E218 ${n:-0} of ${m:-0} $v"
[ "$v" = PASS ]
