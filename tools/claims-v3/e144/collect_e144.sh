#!/usr/bin/env bash
# E144 (Q138): bring aifoundry3's E144 data and logs to the Intel's lab clone (run on the Intel; read-only on the box).
#   bash tools/claims-v3/e144/collect_e144.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=docs/reports/data/2026-11-02-e144-heat-minutes
mkdir -p "$D/aifoundry3" "$D/logs"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
for x in e144-smoke e144; do
  timeout 120 rsync -a -e "$SSH" --exclude 'telemetry.jsonl.raw' --exclude 'tiles/' aifoundry3:aifoundry/build/claims-v3/aifoundry3/$x/ "$D/aifoundry3/$x/" || echo "rsync $x rc=$?"
done
timeout 60 rsync -a -e "$SSH" aifoundry3:aifoundry/build/e144/ "$D/logs/" || echo "rsync logs rc=$?"
du -sh "$D"
