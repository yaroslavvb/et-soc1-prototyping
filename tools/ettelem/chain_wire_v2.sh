#!/usr/bin/env bash
# When the v1 run on this card is done, start v2 on it.
repo=$1; v1log=$2; out=$3; warm=$4
cd "$repo"
until grep -q "^done" "$v1log" 2>/dev/null; do sleep 20; done
sleep 10
mkdir -p "$out"
cat /sys/bus/pci/devices/*/err_stats/ce_count /sys/bus/pci/devices/*/err_stats/uce_count > "$out/err_stats_before.txt" 2>/dev/null
python3 workloads/enercat/run_wire.py "$out" --set v2 --host-bin "$repo/build/enercat_v2/host/enercat_host" --passes 3 $warm > "$out/driver.log" 2>&1
