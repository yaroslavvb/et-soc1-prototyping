#!/usr/bin/env bash
# E156 (Q139): copy E156's raw data and logs from aifoundry1's ~/nekko to the Intel's clone, read only on the box (rsync from it). A copy of
# tools/claims-v3/e155/collect_e155.sh with the names changed.
#
#   bash tools/claims-v3/e156/collect_e156.sh <data dir>      # docs/reports/data/2026-11-03-e156-memory-images-card1
#
# <data dir>/passes/p156<nn>/ (every pass's raw files, attempts included under their own names), passes/p15601 (the smoke) and passes/p15602 (the
# stop-path test), <data dir>/logs/ (the session's log, its two config reads, the queue, the preflight, binaries.sha256). Nothing on the box changes.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?data dir}
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
B=nekko/build/claims-v3/aifoundry1-c1
mkdir -p "$D/passes" "$D/logs"
timeout 300 rsync -a -e "$SSH" "aifoundry1:$B/e156/" "$D/passes/"; echo "passes rc=$?"
timeout 120 rsync -a -e "$SSH" "aifoundry1:$B/e156-smoke/" "$D/passes/"; echo "smoke rc=$?"
timeout 120 rsync -a -e "$SSH" "aifoundry1:$B/e156-stoptest/" "$D/passes/"; echo "stoptest rc=$?"
timeout 120 rsync -a -e "$SSH" --exclude stubtest aifoundry1:nekko/build/e156/ "$D/logs/"; echo "logs rc=$?"
ls "$D/passes" "$D/logs"
