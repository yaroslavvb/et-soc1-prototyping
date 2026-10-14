#!/usr/bin/env bash
# measure.sh: one energy measurement on an ET-SoC-1 card, made the way the lab's agents make them.
#
#   idle (6 s)  ->  the workload (one process, capped at 10 s)  ->  idle (8 s)
#
# with the card's power meter read 10 times a second the whole time. The idle stretches on both
# sides are the baseline: energy = (power during the work - idle power) x time.
#
# Hold the card's lock for the whole measurement, so nobody else starts on the card meanwhile:
#   flock -n /run/lock/etsoc-shire0.lock ./measure.sh OUT_DIR -- <workload command ...>
#   python3 energy.py OUT_DIR
#
# ETTELEM points at the sampler (default build/ettelem/ettelem); IDLE_BEFORE and IDLE_AFTER are seconds.
set -u
OUT=$1; shift; [ "${1:-}" = "--" ] && shift
ETTELEM=${ETTELEM:-build/ettelem/ettelem}
IDLE_BEFORE=${IDLE_BEFORE:-6}
IDLE_AFTER=${IDLE_AFTER:-8}
mkdir -p "$OUT"

# 1. Start the sampler. About one start in three fails right after another sampler exits, so retry.
SAMPLER=
for attempt in 1 2 3 4; do
  "$ETTELEM" sample --seconds 120 --every-ms 100 > "$OUT/power.jsonl" 2> "$OUT/sampler.err" < /dev/null &
  SAMPLER=$!
  for i in $(seq 1 40); do
    sleep 0.25
    grep -q '^{' "$OUT/power.jsonl" && break 2
  done
  kill -TERM "$SAMPLER"; wait "$SAMPLER"; SAMPLER=; sleep 2
done
[ -n "$SAMPLER" ] || { echo "the sampler did not start (is the card free? et-who)" >&2; exit 1; }
# Stop it with a plain kill (SIGTERM): the request in flight completes. Never kill -9 a card tool.
trap 'kill -TERM "$SAMPLER" 2>/dev/null; wait "$SAMPLER"' EXIT

# 2. Idle, the work, idle.
sleep "$IDLE_BEFORE"
date +%s.%N > "$OUT/t_start"
timeout 10 "$@" > "$OUT/workload.out" 2>&1 < /dev/null
echo $? > "$OUT/exit_code"
date +%s.%N > "$OUT/t_end"
sleep "$IDLE_AFTER"
echo "done: $OUT (workload exit code $(cat "$OUT/exit_code"))"
