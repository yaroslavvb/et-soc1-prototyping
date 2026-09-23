#!/usr/bin/env bash
# Two passes each of the nocbench ring energies (manual 5) and the memhier levels (manual 4.2), which had
# been run on one card only, once the relay/hot-line reruns have released the card.
#   tools/ettelem/run_ring_level_reruns.sh <repo-dir> <out-dir>
cd "$1"; out=$2; mkdir -p "$out"
while pgrep -f "fill_reruns.sh|run_reruns.sh" > /dev/null; do sleep 10; done
export LD_LIBRARY_PATH=/opt/et/lib
for p in 1 2; do
  python3 workloads/nocbench/run_energy.py --host-bin build/nocbench/host/nocbench_host --out "$out/rings-pass$p" > "$out/rings-pass$p.log" 2>&1
  sleep 5
  python3 workloads/memhier/run_energy.py --host-bin build/memhier/host/memhier_host --out "$out/levels-pass$p" > "$out/levels-pass$p.log" 2>&1
  sleep 5
done
echo "ring/level reruns done" > "$out/done"
