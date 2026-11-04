#!/bin/bash
# E161 (Q139): E144b's collect_e144b.sh with E161's names: copy the evening's session from aifoundry2 into the lab clone's data directory, read-only on the boxes, and the three
# boxes' own 5 s history over the session, numbers only (E98's thin_history.py), as E111's collect_e111.sh did (no camera here). Any
# other user's login a runner's mark recorded is replaced with `<another lab user>` first (E111's scrub_logins_e111.py). Telemetry and
# launches gzipped, as E64-E111 did. Run from the Intel, at the top of the lab clone:
#     bash tools/claims-v3/e161/collect_e161.sh <data dir> <from epoch s> <to epoch s> [<runs dir on the box, default build/e161/runs>]
# The C logs (<step>/c-log.jsonl) are gzipped too; ccheck.py reads them back with gunzip at the desk.
set -u
DST="${1:?data dir}"; A="${2:?from}"; B="${3:?to}"; RUNS="${4:-build/e161/runs}"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
REMOTE="claude/et-soc1-prototyping/$RUNS"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$DST/history"
rsync -a -e "$SSH" --exclude='STOP' "aifoundry2:$REMOTE/" "$DST/" || exit 3
rsync -a -e "$SSH" "aifoundry2:$(dirname "$REMOTE")/schedule.json" "aifoundry2:$(dirname "$REMOTE")/queue.out" "$DST/" 2>/dev/null
python3 "$HERE/../e111/scrub_logins_e111.py" "$DST" || { echo "a login is still in a file: stop"; exit 4; }
for f in "$DST"/*/tel/*.jsonl "$DST"/*/launches.jsonl "$DST"/*/c-log.jsonl; do [ -f "$f" ] && gzip -9 -n -f "$f"; done
for box in aifoundry1 aifoundry2 aifoundry3; do
  for day in $(python3 "$HERE/../e133/utc_days_e133.py" "$A" "$B"); do
    $SSH "$box" "cat ~/live/history/$day.jsonl" > "$DST/history/$box.raw" 2>/dev/null || { rm -f "${DST:?}/history/$box.raw"; continue; }
    python3 "$HERE/../kspeed/e98/thin_history.py" "$DST/history/$box.raw" "$A" "$B" | gzip -9 -n > "$DST/history/$box-$day.jsonl.gz"
    rm -f "${DST:?}/history/$box.raw"
  done
done
du -sh "$DST"/* | tail -30
