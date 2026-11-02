#!/usr/bin/env bash
# E124 (Q134): copy E124's raw data and logs from aifoundry1's ~/nekko to the Intel's clone, read only on the box (rsync from it).
#
#   bash tools/claims-v3/e124/collect_e124.sh <data dir>      # e.g. docs/reports/data/2026-11-01-e124-int8-zeros-replicate
#
# <data dir>/aifoundry1-c1/e124/p124<nn>/ and e124-smoke/p12401/ (every pass's raw files, attempts included under their own names),
# <data dir>/logs/ (the session's log, its two config reads, the queue, the box build and desk logs, binaries.sha256). Nothing on the box is changed.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?data dir}
mkdir -p "$D/aifoundry1-c1" "$D/logs"
timeout 300 rsync -a aifoundry1:nekko/build/claims-v3/aifoundry1-c1/e124 aifoundry1:nekko/build/claims-v3/aifoundry1-c1/e124-smoke "$D/aifoundry1-c1/"
echo "raw rc=$?"
timeout 120 rsync -a --exclude stubtest --exclude stub_block.sh aifoundry1:nekko/build/e124/ "$D/logs/"
echo "logs rc=$?"
ls "$D/aifoundry1-c1/e124" "$D/logs"
