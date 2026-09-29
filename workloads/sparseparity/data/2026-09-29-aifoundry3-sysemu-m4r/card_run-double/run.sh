#!/usr/bin/env bash
# card_run.sh m4's gate, speed ratio and deferred offline oracle, exercised with a test double of the host: no device,
# no lock (the flock shim drops "-n LOCK"), et-who always free. Never point this at a real build.
#   bash run.sh TREE KERNEL_ELF WORKDIR     TREE: the sources' root (workloads/sparseparity/card_run.sh under it)
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$1 ELF=$2 W=$3
rm -rf "$W"; mkdir -p "$W/host" "$W/kernel" "$W/shim"
cp "$HERE/sparseparity_host" "$HERE/spp_selftest" "$W/host/"
cp "$HERE/flock" "$HERE/et-who" "$HERE/et-lab-manifest" "$W/shim/"
cp "$ELF" "$W/kernel/sparseparity.elf"
chmod +x "$W"/host/* "$W"/shim/*
export PATH=$W/shim:$PATH
CR=$TREE/workloads/sparseparity/card_run.sh
echo "== t1: m4-32s-f5-h1-m4 at x1.5 of its model: m4-32s-f5-m4 is skipped, the run ends DONE"
FAKE_SLOW=m4-32s-f5-h1-m4 bash "$CR" m4 --build "$W" --out "$W/t1" --from m4-32s-l2-m4d; echo "exit $?"
echo "== t2: every gate fast, the offline full oracle of m4-32s-f5-m4 disagrees: STOP, exit 1"
FAKE_VERIFY_BAD=m4-32s-f5-m4 bash "$CR" m4 --build "$W" --out "$W/t2" --from m4-32s-l2-m4d; echo "exit $?"
echo "== t3: resumed at m4-32s-f5-m4 in a new --out: no gates there, skipped"
bash "$CR" m4 --build "$W" --out "$W/t3" --from m4-32s-f5-m4; echo "exit $?"
echo "== t4: resumed at m4-32s-f5-m4 in t2's --out: its gates are there, it runs"
bash "$CR" m4 --build "$W" --out "$W/t2" --from m4-32s-f5-m4; echo "exit $?"
