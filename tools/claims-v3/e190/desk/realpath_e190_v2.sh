#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): the REAL-PATH desk test v2's two namespaces.
# realpath_e190_v2.py runs once per arm under bubblewrap with the arm's box as the hostname (a private UTS namespace: aifoundry2 for arm
# A, aifoundry1 for arm B), a private PID namespace and its own /proc (so `ps` and the stand-in et-who read only the test's processes).
# Run it ONLY inside the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): it refuses otherwise.
#   bash tools/claims-v3/e190/desk/realpath_e190_v2.sh <an empty scratch dir outside the repo> > realpath-e190-v2.txt
# The last line: REALPATH-E190-V2 <n> of <m> PASS (or FAIL).
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "$S is not empty"; exit 2; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
n=0; m=0
for spec in A:aifoundry2 B:aifoundry1; do
  arm=${spec%%:*}; h=${spec#*:}
  echo "== arm $arm: hostname $h (a private UTS namespace), a private PID namespace"
  /usr/bin/bwrap --dev-bind / / --unshare-uts --hostname "$h" --unshare-pid --proc /proc --die-with-parent -- \
    /usr/bin/python3 -B "$D/realpath_e190_v2.py" "$S" "$arm" > "$S/arm-$arm.txt" 2>&1
  echo "rc $?"
  cat "$S/arm-$arm.txt"
  l=$(grep -E "^REALPATH-E190-V2 arm $arm: [0-9]+ of [0-9]+" "$S/arm-$arm.txt" | tail -n 1)
  a=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\1/'); b=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\2/')
  n=$((n + ${a:-0})); m=$((m + ${b:-1}))
done
[ "$n" -eq "$m" ] && v=PASS || v=FAIL
echo "REALPATH-E190-V2 $n of $m $v"
[ "$v" = PASS ]
