#!/usr/bin/env bash
# DV2 Z1's host log (DESIGN §6 Z1: "the host logs sensors -j every 60 s"; a covariate only): no card access.
#   setsid nohup bash tools/claims-v3/dv2/hostlog.sh [until HH:MM, default 08:15] > /dev/null 2>&1 < /dev/null &
# Appends {t_ms, sensors} lines to build/claims-v3/<card>/dv2/host-sensors.jsonl every 60 s until the time given, or
# until build/claims-v3/STOP or build/claims-v3/<card>/dv2/NIGHT-STOP exists. Stop it early with a plain kill.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
CARD=$(hostname)
D=$ROOT/build/claims-v3/$CARD/dv2
[ -n "${V3_DRY:-}" ] && D=$ROOT/build/claims-v3-dry/$CARD/dv2
mkdir -p "$D"
UNTIL=${1:-08:15}
end=$(date -d "$UNTIL" +%s); [ "$end" -lt "$(date +%s)" ] && end=$(date -d "tomorrow $UNTIL" +%s)
n=0
while [ "$(date +%s)" -lt "$end" ]; do
  [ -e "$ROOT/build/claims-v3/STOP" ] && break
  [ -e "$D/NIGHT-STOP" ] && break
  s=$(timeout 20 sensors -j 2>/dev/null | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin), separators=(",", ":")))' 2>/dev/null || echo null)
  echo "{\"t_ms\":$(date +%s%3N),\"sensors\":$s}" >> "$D/host-sensors.jsonl"
  n=$(( n + 1 ))
  [ -n "${HOSTLOG_ONCE:-}" ] && break
  sleep 60
done
