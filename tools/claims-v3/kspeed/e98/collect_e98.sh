#!/bin/bash
# E98: copy the night's raw sessions from aifoundry2 into the lab clone's data directory, and the three boxes' own 5 s history for the night, numbers
# only (t, cpu, mem, load, temps, cards[n, ok, held, die, max, w]). Telemetry and launches gzipped, as E64-E87 did. Run from the Intel, read-only on the boxes.
#     bash collect_e98.sh <data dir> <from epoch s> <to epoch s>
set -u
DST="${1:?data dir}"; A="${2:?from}"; B="${3:?to}"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
REMOTE=claude/et-soc1-prototyping/build/e98
mkdir -p "$DST/history"
rsync -a -e "$SSH" --exclude='STOP' "aifoundry2:$REMOTE/runs/" "$DST/" || exit 3
rsync -a -e "$SSH" "aifoundry2:$REMOTE/smoke/" "$DST/smoke/" || exit 3
rsync -a -e "$SSH" "aifoundry2:$REMOTE/smoke.out" "$DST/smoke/run.out" || exit 3
for f in schedule.json slots.txt queue.out; do rsync -a -e "$SSH" "aifoundry2:$REMOTE/$f" "$DST/$f" || exit 3; done
for f in "$DST"/*/tel/*.jsonl "$DST"/*/launches.jsonl; do [ -f "$f" ] && gzip -9 -n -f "$f"; done
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for box in aifoundry1 aifoundry2 aifoundry3; do
  # UTC days the night covers; the file a box writes is named by the UTC date
  $SSH "$box" 'cat ~/live/history/2026-11-01.jsonl' > "$DST/history/$box.raw" || exit 3
  python3 "$HERE/thin_history.py" "$DST/history/$box.raw" "$A" "$B" | gzip -9 -n > "$DST/history/$box-2026-11-01.jsonl.gz" || exit 3
  rm -f "$DST/history/$box.raw"
done
du -sh "$DST"/* | tail -20
