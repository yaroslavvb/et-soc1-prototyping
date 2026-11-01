#!/usr/bin/env bash
# E97 (Q132): reduce the finished passes and assemble the data directory. Desk compute: on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e97/collect_e97.sh <raw root> [<history root>]
#
# <raw root> holds e97/ and e97-smoke/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/, and logs/ (queue, dry and session reads). <history root> holds aifoundry1/, aifoundry2/ and aifoundry3/ with
# the boxes' ~/live/history files for the night. Output: build/e97-out/2026-11-01-e97-heat-low-power-steady/. Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never read; no pass
# is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?raw root}
HIST=${2:-}
OUT=$ROOT/build/e97-out/2026-11-01-e97-heat-low-power-steady
rm -rf "${ROOT:?}/build/e97-out"
mkdir -p "$OUT/aifoundry3/e97" "$OUT/logs"
A=()
for p in 9710 9711; do
  d=$RAW/e97/p$p
  [ -e "$d/block.json" ] || { echo "absent: $d"; continue; }
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  A+=("$d")
done
echo "Part A passes reduced: ${#A[@]}"
[ ${#A[@]} -gt 0 ] || { echo "no finished Part A pass" >&2; exit 1; }
"$PY" tools/claims-v3/e97/reduce_e97.py "${A[@]}" --out "$OUT" > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"
H=()
if [ -e "$RAW/e97/p9720/marks.jsonl" ]; then H=(--holds "$RAW/e97/p9720"); fi
"$PY" tools/claims-v3/e97/score_e97.py "${A[@]}" --out "$OUT" ${H[@]+"${H[@]}"} > "$OUT/score.log" 2>&1; echo "score rc=$?"; tail -2 "$OUT/score.log" | cut -c1-400
if [ -n "$HIST" ] && [ -e "$RAW/e97/p9720/marks.jsonl" ]; then "$PY" tools/claims-v3/e97/room_e97.py "$HIST" "$RAW/e97/p9720" > "$OUT/room.txt" 2>&1; echo "room rc=$?"; fi
( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh tools/claims-v3/e89/*.py tools/claims-v3/e89/*.sh tools/claims-v3/e97/*.py tools/claims-v3/e97/*.sh tools/claims-v3/e97/*.md tools/claims-v3/e97/*.json 2>/dev/null ||
    shasum -a 256 tools/claims-v3/lib.sh tools/claims-v3/e89/*.py tools/claims-v3/e89/*.sh tools/claims-v3/e97/*.py tools/claims-v3/e97/*.sh tools/claims-v3/e97/*.md tools/claims-v3/e97/*.json; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
for d in "${A[@]}"; do cp -r "$d" "$OUT/aifoundry3/e97/"; done
[ -d "$RAW/e97/p9720" ] && cp -r "$RAW/e97/p9720" "$OUT/aifoundry3/e97/"
for d in "$RAW"/e97/p97*.attempt-* "$RAW"/e97-smoke/p97*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
