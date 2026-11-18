#!/usr/bin/env bash
# E213 (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): the REAL-PATH desk test's namespaces, E206's desk/realpath_e206.sh form for its
# two arms (E211's copy ran arm A alone). realpath_e213.py runs under bubblewrap with the arm's box as the hostname (a private UTS namespace:
# aifoundry3 for arm A, aifoundry1 for arm B), a private PID namespace and its own /proc (so `ps` and the stand-in et-who read only the test's
# processes); arm A first (its real build gives arm B its real ELFs). Run it ONLY inside the sandbox with no /dev/et* and an empty /run/lock
# (W/nodev.sh on aifoundry2): it refuses otherwise.
#   bash tools/claims-v3/e213/desk/realpath_e213.sh <an empty scratch dir outside the repo> > logs/realpath-e213.txt
# The last line: REALPATH-E213 <n> of <m> PASS (or FAIL), both arms together.
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "$S is not empty"; exit 2; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
tn=0; tm=0
for a in A:aifoundry3 B:aifoundry1; do
  arm=${a%%:*}; host=${a##*:}
  echo "== arm $arm: hostname $host (a private UTS namespace), a private PID namespace"
  /usr/bin/bwrap --dev-bind / / --unshare-uts --hostname "$host" --unshare-pid --proc /proc --die-with-parent -- \
    /usr/bin/python3 -B "$D/realpath_e213.py" "$S" "$arm" > "$S/arm-$arm.txt" 2>&1
  echo "rc $?"
  cat "$S/arm-$arm.txt"
  l=$(grep -E "^REALPATH-E213 arm $arm: [0-9]+ of [0-9]+" "$S/arm-$arm.txt" | tail -n 1)
  n=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\1/'); m=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\2/')
  tn=$((tn + ${n:-0})); tm=$((tm + ${m:-1}))
done
[ "$tn" -eq "$tm" ] && v=PASS || v=FAIL
echo "REALPATH-E213 $tn of $tm $v"
[ "$v" = PASS ]
