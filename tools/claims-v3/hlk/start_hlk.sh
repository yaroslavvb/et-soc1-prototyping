#!/usr/bin/env bash
# E85: start the card session detached from the ssh connection, as E63's start_hlc.sh does (setsid nohup,
# stdin from /dev/null), with run_hlk.py (E63's runner plus a per-set --type) in place of run_hlc.py.
# Usage, on aifoundry2 from build/e85/code:
#   bash start_hlk.sh <rundir> [--dry] [protocol.json]
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
out=${1:?usage: start_hlk.sh <rundir> [--dry] [protocol.json]}
mode=${2:-}
proto=${3:-protocol-e85.json}
if [ -e "$out/session.json" ] || [ -e "$out/run.out" ]; then
  echo "refusing: $out already has a session"
  exit 2
fi
mkdir -p "$out"
if [ "$mode" = --dry ]; then
  setsid nohup python3 run_hlk.py --protocol "$proto" --out "$out" --dry > "$out/run.out" 2>&1 < /dev/null &
else
  setsid nohup python3 run_hlk.py --protocol "$proto" --out "$out" > "$out/run.out" 2>&1 < /dev/null &
fi
echo "started pid $! -> $out/run.out"
