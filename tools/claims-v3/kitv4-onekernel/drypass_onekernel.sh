#!/usr/bin/env bash
# Kit v4's one-kernel option: the dry pass on the Intel. run_hpl.py --dry (its toy card: no device opened, no lock taken, no
# ssh, nothing read from a box) twice on the same three-burst protocol: first the v3 form (the committed runner as it is),
# then the one-kernel form (run_hpl_onekernel.py: the same runner with onekernel.install). Then the desk test's dry part reads
# both sessions (T6 the launch records, T7 the reduction, T8 the dip term's exposure). Every scratch path printed is <scratch>.
#
#   bash tools/claims-v3/kitv4-onekernel/drypass_onekernel.sh <a new empty scratch dir> > tools/claims-v3/kitv4-onekernel/drypass-onekernel.txt
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 1
S=${1:?usage: drypass_onekernel.sh <a new empty scratch dir>}
[ -d "$S" ] && [ -n "$(ls -A "$S" 2>/dev/null)" ] && { echo "refused: $S is not empty"; exit 2; }
mkdir -p "$S" || exit 2
PY=${PY:-/usr/bin/python3}
export PYTHONDONTWRITEBYTECODE=1
K=tools/claims-v3/kitv4-onekernel
t0=$(date +%s)
"$PY" -B tools/claims-v3/hpl/run_hpl.py --protocol $K/protocol-onekernel-dry.json --out "$S/v3" --dry > "$S/v3.out" 2>&1
r3=$?
t1=$(date +%s)
"$PY" -B $K/run_hpl_onekernel.py --protocol $K/protocol-onekernel-dry.json --out "$S/v4" --dry > "$S/v4.out" 2>&1
r4=$?
t2=$(date +%s)
echo "kit v4 one-kernel option, dry pass on the Intel ($("$PY" --version 2>&1)): run_hpl.py --dry rc $r3 in $((t1 - t0)) s (v3 form); run_hpl_onekernel.py --dry rc $r4 in $((t2 - t1)) s (one kernel per burst); the toy card, no device, no lock, no ssh"
echo "the v4 session's install record (onekernel.json):"
"$PY" -B -c 'import json,sys; d=json.load(open(sys.argv[1])); print("  watcher", d["watcher"]["watcher"], d["watcher"]["watcher_sha256"][:12], "installed", d["watcher"]["installed"]); o=d["onekernel"]; print("  onekernel", o["onekernel_sha256"][:12], "installed", o["installed"], "run_hpl", o["run_hpl_sha256"][:12], "t600_s", o["t600_s"], "iters", o["iters"])' "$S/v4/onekernel.json"
for t in v3 v4; do
  echo "the $t session's end: $(tail -n 1 "$S/$t/end.json" 2>/dev/null | cut -c1-200)"
done
"$PY" -B $K/selftest_onekernel.py --dry "$S/v3" "$S/v4" > "$S/dry-test.json"
echo "selftest_onekernel.py --dry: rc $?"
sed "s#$S#<scratch>#g" "$S/dry-test.json"
