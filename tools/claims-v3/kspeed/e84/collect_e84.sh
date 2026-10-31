#!/usr/bin/env bash
# E84 (Q130): copy the raw session from aifoundry1 into the data directory and run the registered reduction. Desk
# compute, on the Intel, from the repository root's clone:
#
#   bash tools/claims-v3/kspeed/e84/collect_e84.sh
#
# Copies build/e84/runs/{s1,smoke}, build/e84/ident and the stage logs from aifoundry1:~/nekko, gzips the telemetry and
# launch records (reduce_hpl.jl reads .gz), then runs reduce_e84.py with E80's results beside it.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.."
D=docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0
SSH='ssh -o BatchMode=yes -o ConnectTimeout=10'
mkdir -p "$D/logs"
rsync -a -e "$SSH" aifoundry1:nekko/build/e84/runs/s1 aifoundry1:nekko/build/e84/runs/smoke "$D/" || exit 1
rsync -a -e "$SSH" aifoundry1:nekko/build/e84/ident "$D/" || exit 1
rsync -a -e "$SSH" aifoundry1:nekko/build/e84/s1.log aifoundry1:nekko/build/e84/smoke.log \
  aifoundry1:nekko/build/e84/dry-smoke.log "$D/logs/" || true
for s in s1 smoke; do
  for f in "$D/$s"/tel/*.jsonl "$D/$s/launches.jsonl"; do
    [ -f "$f" ] && gzip -9 -f "$f"
  done
done
python3 tools/claims-v3/kspeed/e84/reduce_e84.py "$D/s1" --e80 docs/reports/data/2026-10-31-e80-kinds-speed/results.json \
  --out "$D/results.json" > "$D/reduce.txt" 2> "$D/reduce.log"
echo "reduce rc=$?"
du -sh "$D"
