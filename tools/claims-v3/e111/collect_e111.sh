#!/bin/bash
# E111 (Q133): copy the afternoon's sessions from aifoundry2 into the lab clone's data directory, read-only on the boxes, and the three
# boxes' own 5 s history over the session, numbers only (E98's thin_history.py: t, cpu, mem, load, temps, cards[n, ok, held, die, max,
# w]). Telemetry and launches gzipped, as E64-E98 did. The camera's raw stream and reduced frame cube stay on aifoundry2 (as E62, E63,
# E73 and E85's do); their sha256 go in left-on-aifoundry2.sha256. Any other user's login a runner's mark recorded is replaced with
# `<another lab user>` first (scrub_logins_e111.py), as E98 did. Run from the Intel:
#     bash tools/claims-v3/e111/collect_e111.sh <data dir> <from epoch s> <to epoch s> [<runs dir on the box, default build/e111/runs>]
set -u
DST="${1:?data dir}"; A="${2:?from}"; B="${3:?to}"; RUNS="${4:-build/e111/runs}"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
REMOTE="claude/et-soc1-prototyping/$RUNS"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$DST/history"
rsync -a -e "$SSH" --exclude='STOP' --exclude='CAMSTOP' --exclude='*.p3rec' --exclude='frames.npz' --exclude='CAM/logs/' \
  "aifoundry2:$REMOTE/" "$DST/" || exit 3
rsync -a -e "$SSH" "aifoundry2:$(dirname "$REMOTE")/schedule.json" "aifoundry2:$(dirname "$REMOTE")/queue.out" "$DST/" 2>/dev/null
$SSH aifoundry2 "cd $REMOTE && find CAM CAM-RED -type f \( -name '*.p3rec' -o -name 'frames.npz' -o -path 'CAM/logs/*' \) -print0 2>/dev/null | xargs -0 -r sha256sum" \
  > "$DST/left-on-aifoundry2.sha256" || true
python3 "$HERE/scrub_logins_e111.py" "$DST" || { echo "a login is still in a file: stop"; exit 4; }
for f in "$DST"/*/tel/*.jsonl "$DST"/*/launches.jsonl "$DST"/CAM/tel.jsonl "$DST"/CAM-RED/tel.jsonl; do [ -f "$f" ] && gzip -9 -n -f "$f"; done
for box in aifoundry1 aifoundry2 aifoundry3; do
  for day in $(python3 -c "import time,sys; a,b=int(sys.argv[1]),int(sys.argv[2]); print(' '.join(sorted({time.strftime('%Y-%m-%d', time.gmtime(t)) for t in range(a, b + 1, 3600)} | {time.strftime('%Y-%m-%d', time.gmtime(b))})))" "$A" "$B"); do
    $SSH "$box" "cat ~/live/history/$day.jsonl" > "$DST/history/$box.raw" 2>/dev/null || { rm -f "${DST:?}/history/$box.raw"; continue; }
    python3 "$HERE/../kspeed/e98/thin_history.py" "$DST/history/$box.raw" "$A" "$B" | gzip -9 -n > "$DST/history/$box-$day.jsonl.gz"
    rm -f "${DST:?}/history/$box.raw"
  done
done
du -sh "$DST"/* | tail -30
