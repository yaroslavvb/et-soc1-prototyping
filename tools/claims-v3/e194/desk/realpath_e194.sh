#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration and before any E194 datum): the REAL-PATH desk test's two
# namespaces (E191's form, tools/claims-v3/e191/desk/realpath_e191.sh). realpath_e194.py runs under bubblewrap with a private UTS namespace
# (hostname aifoundry2: the box E194 runs on; then aifoundry1: the wrong-box case), a private PID namespace and its own /proc (so `ps` and
# the stand-in et-who read only the test's processes). Run it ONLY inside the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh
# on aifoundry2): it refuses otherwise.
#   bash tools/claims-v3/e194/desk/realpath_e194.sh <an empty scratch dir outside the repo> > realpath-e194.txt
# The scratch root reads <scratch> in the output. The last line: REALPATH-E194 <n> of <m> PASS (or FAIL).
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
for h in aifoundry2 aifoundry1; do
  echo "== hostname $h (a private UTS namespace), a private PID namespace"
  mkdir -p "$S/$h"
  /usr/bin/bwrap --dev-bind / / --unshare-uts --hostname "$h" --unshare-pid --proc /proc --die-with-parent -- \
    /usr/bin/python3 -B "$D/realpath_e194.py" "$S/$h" "$h" > "$S/$h.txt" 2>&1
  echo "rc $?"
  sed "s#$S#<scratch>#g" "$S/$h.txt"      # the scratch root masked (E191's log form)
  l=$(grep -E "^REALPATH-E194 $h: [0-9]+ of [0-9]+" "$S/$h.txt" | tail -n 1)
  a=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\1/'); b=$(echo "$l" | sed -E 's/^.*: ([0-9]+) of ([0-9]+).*$/\2/')
  n=$((n + ${a:-0})); m=$((m + ${b:-1}))
done
[ "$n" -eq "$m" ] && v=PASS || v=FAIL
echo "REALPATH-E194 $n of $m $v"
[ "$v" = PASS ]
