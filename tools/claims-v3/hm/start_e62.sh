#!/usr/bin/env bash
# E62: start the card session detached from the ssh connection, as the lab's start_card.sh starts its
# queues (setsid nohup, stdin from /dev/null). Usage, on aifoundry2 from build/e62/code:
#   bash start_e62.sh <rundir> [--dry]
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
out=${1:?usage: start_e62.sh <rundir> [--dry]}
mode=${2:-}
if [ -e "$out/session.json" ] || [ -e "$out/run.out" ]; then
  echo "refusing: $out already has a session"
  exit 2
fi
mkdir -p "$out"
if [ "$mode" = --dry ]; then
  setsid nohup python3 run_hm.py --protocol protocol.json --out "$out" --dry > "$out/run.out" 2>&1 < /dev/null &
else
  setsid nohup python3 run_hm.py --protocol protocol.json --out "$out" > "$out/run.out" 2>&1 < /dev/null &
fi
echo "started pid $! -> $out/run.out"
