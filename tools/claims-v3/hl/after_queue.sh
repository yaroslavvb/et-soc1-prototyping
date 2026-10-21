#!/usr/bin/env bash
# V3-HL: wait until no queue_hl.sh of ours runs on this host, then run queue_hl.sh with the given arguments.
#   HL_GEN=... setsid -f bash tools/claims-v3/hl/after_queue.sh <first-pass> <n-passes> <items> > build/hl-queue-<card>-2.log 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
me=$$
while pgrep -u "$(id -u)" -f 'tools/claims-v3/hl/queue_hl.sh' | grep -vx "$me" > /dev/null; do sleep 20; done
echo "$(date +%T) previous queue done; starting passes $1.. with HL_GEN=${HL_GEN:-build/hl-gen}"
exec bash tools/claims-v3/hl/queue_hl.sh "$@"
