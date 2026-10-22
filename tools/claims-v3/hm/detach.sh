#!/usr/bin/env bash
# Run a command detached from the ssh connection (setsid nohup, stdin from /dev/null), logging to a file.
# Usage, on aifoundry2: bash detach.sh <log file> <command> [args...]
set -u
log=${1:?usage: detach.sh <log> <command> [args...]}
shift
setsid nohup "$@" > "$log" 2>&1 < /dev/null &
echo "detached pid $! -> $log"
