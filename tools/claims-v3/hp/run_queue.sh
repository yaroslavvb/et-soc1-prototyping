#!/usr/bin/env bash
# Heat placement (HP): the only way to start a queue of an hp schedule. It checks what ../queue.sh cannot (queue.sh and
# lib.sh are frozen in the PREREG locks, and a queue on aifoundry3 runs their deployed copies), then execs queue.sh:
#
#   setsid nohup tools/claims-v3/hp/run_queue.sh tools/claims-v3/schedule-hp-aifoundry3.txt \
#       > build/claims-v3/queue-hp-aifoundry3.log 2>&1 < /dev/null &
#   V3_DEVICE=1 [HP_PREREG_SHA256=<the recorded sha256>] setsid nohup tools/claims-v3/hp/run_queue.sh \
#       tools/claims-v3/schedule-hp-aifoundry1-c1.txt > build/claims-v3/queue-hp-aifoundry1-c1.log 2>&1 < /dev/null &
#
# Refused (exit 2, recorded in build/claims-v3[-dry]/hp-refused.jsonl, before queue.sh runs at all):
#  - aifoundry1 with V3_DEVICE anything but 1 (card 0 is never used: queue.sh would read card 0's die temperature
#    before every block, and wait on it for up to 30 min, before each block.sh refused; review low, 27 Sep), or with
#    ET_DEVICES set to anything but 1; aifoundry3 with V3_DEVICE set; any other host (aifoundry2 runs only
#    tools/claims-v3/hp/run_a2.sh, by hand);
#  - V3_FORCE without V3_DRY=1 (a re-run into a finished block's directory);
#  - a schedule line other than "hp <pass>", "sleep <s>", "end" (this wrapper starts hp schedules only);
#  - a schedule with validation passes (hp 9xxx) and no HP_PREREG_SHA256 (64 hex digits) outside V3_DRY: every
#    validation block refuses without it (hplib.py vallock), so the queue would only fail them one by one.
# The schedule is checked when the queue starts; lines appended later are checked by block.sh itself (which refuses
# card 0, V3_FORCE and a missing HP_PREREG_SHA256 on its own).
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
host=$(hostname)
LOGF=$ROOT/build/claims-v3/hp-refused.jsonl; [ -n "${V3_DRY:-}" ] && LOGF=$ROOT/build/claims-v3-dry/hp-refused.jsonl
refuse() {
  mkdir -p "$(dirname "$LOGF")"
  python3 -c 'import json,sys,time; print(json.dumps({"t_ms": int(time.time()*1000), "who": "run_queue.sh", "host": sys.argv[1],
    "v3_device": sys.argv[2], "schedule": sys.argv[3], "why": sys.argv[4], "dry": bool(sys.argv[5])}))' \
    "$host" "${V3_DEVICE-<unset>}" "${1:-}" "$2" "${V3_DRY:-}" >> "$LOGF" 2>/dev/null || true
  echo "$(date +%FT%T) run_queue.sh: $2: refused" >&2
  exit 2
}
sched=${1:-}
[ -n "$sched" ] || refuse "" "usage: run_queue.sh <schedule file>"
case "$host" in
  aifoundry1)
    [ "${V3_DEVICE-}" = 1 ] || refuse "$sched" "aifoundry1 runs hp work on card 1 only: V3_DEVICE must be 1 (got '${V3_DEVICE-<unset>}'; card 0 is never used, not even for queue.sh's die reading)"
    [ -z "${ET_DEVICES+x}" ] || [ "$ET_DEVICES" = 1 ] || refuse "$sched" "ET_DEVICES='$ET_DEVICES' names another card than V3_DEVICE=1" ;;
  aifoundry3)
    [ -z "${V3_DEVICE+x}" ] || refuse "$sched" "aifoundry3 has one card: V3_DEVICE must be unset (got '$V3_DEVICE')" ;;
  *) refuse "$sched" "hp schedules run on aifoundry1 card 1 and aifoundry3 only (this is $host; aifoundry2's session is tools/claims-v3/hp/run_a2.sh)" ;;
esac
[ -n "${V3_FORCE:-}" ] && [ -z "${V3_DRY:-}" ] && refuse "$sched" "V3_FORCE is honoured only under V3_DRY=1 (it would re-run a finished block into its own directory)"
case "$sched" in /*) ;; *) sched=$PWD/$sched ;; esac
[ -f "$sched" ] || refuse "$sched" "no schedule file $sched"
bad=$(grep -v '^\s*\(#\|$\)' "$sched" | awk '!(($1 == "hp" && $2 ~ /^[0-9]+$/ && NF == 2) || ($1 == "sleep" && $2 ~ /^[0-9]+$/ && NF == 2) || ($1 == "end" && NF == 1))' | head -n 3)
[ -z "$bad" ] || refuse "$sched" "not an hp schedule: $(echo "$bad" | tr '\n' ';')"
if grep -v '^\s*\(#\|$\)' "$sched" | awk '$1 == "hp" && $2 >= 9000 && $2 < 10000 {f=1} END {exit !f}'; then
  if [ -z "${V3_DRY:-}" ] && ! [[ "${HP_PREREG_SHA256:-}" =~ ^[0-9a-f]{64}$ ]]; then
    refuse "$sched" "validation passes need HP_PREREG_SHA256=<PREREG.md's sha256 as recorded when prereg.py --val printed it>"
  fi
fi
echo "$(date +%FT%T) run_queue.sh: $host${V3_DEVICE:+ card $V3_DEVICE}, $sched: checks passed; exec queue.sh"
exec bash "$ROOT/tools/claims-v3/queue.sh" "$sched"
