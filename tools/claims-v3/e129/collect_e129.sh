#!/usr/bin/env bash
# E129 (Q136): copy E129's raw data and logs from aifoundry1's ~/nekko to the Intel's clone, read only on the box (rsync from it).
#
#   bash tools/claims-v3/e129/collect_e129.sh <data dir>      # e.g. docs/reports/data/2026-11-02-e129-int8-noissue
#
# <data dir>/aifoundry1-c1/e129/p129<nn>/ and e129-smoke/p12901/ (every pass's raw files, attempts included under their own names),
# <data dir>/logs/ (the session's log, its two config reads, the queue, the preflight, binaries.sha256). Nothing on the box is changed.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?data dir}
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
mkdir -p "$D/aifoundry1-c1" "$D/logs"
timeout 300 rsync -a -e "$SSH" aifoundry1:nekko/build/claims-v3/aifoundry1-c1/e129 aifoundry1:nekko/build/claims-v3/aifoundry1-c1/e129-smoke "$D/aifoundry1-c1/"
echo "raw rc=$?"
timeout 120 rsync -a -e "$SSH" --exclude stubtest --exclude stub_block.sh aifoundry1:nekko/build/e129/ "$D/logs/"
echo "logs rc=$?"
ls "$D/aifoundry1-c1/e129" "$D/logs"
