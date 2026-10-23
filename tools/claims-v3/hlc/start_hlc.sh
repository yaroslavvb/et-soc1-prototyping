#!/usr/bin/env bash
# E63: start the card session detached from the ssh connection, as E62's start_e62.sh does (setsid nohup,
# stdin from /dev/null). Usage, on aifoundry2 from build/e63/code:
#   bash start_hlc.sh <rundir> [--dry] [protocol.json]
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
out=${1:?usage: start_hlc.sh <rundir> [--dry] [protocol.json]}
mode=${2:-}
proto=${3:-protocol.json}
if [ -e "$out/session.json" ] || [ -e "$out/run.out" ]; then
  echo "refusing: $out already has a session"
  exit 2
fi
mkdir -p "$out"
if [ "$mode" = --dry ]; then
  setsid nohup python3 run_hlc.py --protocol "$proto" --out "$out" --dry > "$out/run.out" 2>&1 < /dev/null &
else
  setsid nohup python3 run_hlc.py --protocol "$proto" --out "$out" > "$out/run.out" 2>&1 < /dev/null &
fi
echo "started pid $! -> $out/run.out"
