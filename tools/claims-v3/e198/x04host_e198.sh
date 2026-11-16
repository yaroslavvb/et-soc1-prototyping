#!/usr/bin/env bash
# E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): the runner's --host. It runs THE BUILT HOST UNCHANGED (E198_HOST,
# today's x04clock_host, its sha256 checked by the session against the build record) with the runner's own arguments, its standard output
# to a raw file of its own (E198_RAWDIR/<seq>.stdout: the host writes to a regular file, as it wrote to the runner's file on aifoundry3),
# then writes that output to its own standard output (the runner's device-stdout.txt) with every runtime line `Opening device <n>`
# removed by dropruntime_e198.py (E198.md 3 and 18.4: a runtime line inside an X04 line never reaches the runner's json.loads), and exits
# with the host's status. Its stderr is the host's (the runner's device-stderr.txt). Signals: the runner's `timeout -k 1 10` sends
# SIGTERM to its whole process group, this file and the host alike; this file has a handler (not an ignore, so the host starts with the
# default dispositions), waits for the host, writes what the host wrote, and then dies of the same signal the host died of, so `timeout`
# and the runner read the status they would have read without it; `-k 1` still kills the group a second later. A raw directory that
# cannot be written stops the host before it starts (exit 1: the runner's "device process exit 1" stop).
#   E198_HOST=<host> E198_RAWDIR=<dir> E198_KIT=<kit folder> <E198 root>/tools/claims-v3/e198/x04host_e198.sh <the host's options>
# SPDX-License-Identifier: Apache-2.0
set -u
H=${E198_HOST:?E198_HOST is the built host}; RAW=${E198_RAWDIR:?E198_RAWDIR is the raw output folder}; K=${E198_KIT:?E198_KIT}
mkdir -p "$RAW" || exit 1
n=$(find "$RAW" -maxdepth 1 -name '*.stdout' | wc -l)
seq=$(printf '%05d' $((n + 1)))
f=$RAW/$seq.stdout
trap ':' TERM INT HUP
"$H" "$@" > "$f"
rc=$?
env -u LD_LIBRARY_PATH python3 -I -B "$K/dropruntime_e198.py" filter "$f" "$RAW/index.jsonl" "$seq" "$rc"
trap - TERM INT HUP
if [ "$rc" -gt 128 ] && [ "$rc" -lt 160 ]; then kill -s "$(kill -l $((rc - 128)))" "$$"; fi
exit "$rc"
