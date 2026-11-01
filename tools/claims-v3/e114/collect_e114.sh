#!/usr/bin/env bash
# E114 (Q133): copy the raw session from aifoundry1 into the data directory and run the registered reduction. Desk
# compute, on the Intel, from the repository root's clone:
#
#   bash tools/claims-v3/e114/collect_e114.sh
#
# Copies build/e114/runs/{s1,smoke}, build/e114/ident, e114-start.json and the stage logs from aifoundry1:~/nekko, gzips
# the telemetry and launch records (reduce_hpl.jl reads .gz), then runs reduce_e114.py.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=docs/reports/data/2026-11-01-e114-card0-replicates
SSH='ssh -o BatchMode=yes -o ConnectTimeout=10'
mkdir -p "$D/logs"
rsync -a -e "$SSH" aifoundry1:nekko/build/e114/runs/s1 aifoundry1:nekko/build/e114/runs/smoke "$D/" || exit 1
rsync -a -e "$SSH" aifoundry1:nekko/build/e114/ident "$D/" || exit 1
rsync -a -e "$SSH" aifoundry1:nekko/build/e114/e114-start.json aifoundry1:nekko/build/e114/s1.log \
  aifoundry1:nekko/build/e114/smoke.log aifoundry1:nekko/build/e114/dry-smoke.log "$D/logs/" || true
for s in s1 smoke; do
  for f in "$D/$s"/tel/*.jsonl "$D/$s/launches.jsonl"; do
    [ -f "$f" ] && gzip -9 -f "$f"
  done
done
python3 tools/claims-v3/e114/reduce_e114.py "$D/s1" --out "$D/results.json" > "$D/reduce.txt" 2> "$D/reduce.log"
echo "reduce rc=$?"
du -sh "$D"
