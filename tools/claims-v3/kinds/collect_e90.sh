#!/usr/bin/env bash
# E90 (Q130): reduce every finished pass with E78's reduction (reduce_e90.py runs reduce_e78.py unchanged with E90's
# items), run the registered leakage arms, score E90's rules, and assemble the data directory. Desk compute: run it on
# the Intel over a copy of the raw passes (as E78's A1 says), never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/kinds/collect_e90.sh ['p90[1-9][0-9]'] <raw root>
#
# <raw root> holds kinds/ and kinds-smoke/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/ (only the
# p90* passes). Output: build/e90-out/2026-10-31-e90-signs-spread/ with e90.json, runs.csv, reduce.txt, the
# leakage arms (e90-leak0.1994 / 0.3803 / 0 .json, csv, txt), scored.json, results.md, code.sha256, logs/, the smoke
# and every pass's raw data. Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never
# read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p90[1-9][0-9]}
RAW=${2:-$ROOT/build/claims-v3/aifoundry3}
OUT=$ROOT/build/e90-out/2026-10-31-e90-signs-spread
rm -rf "${ROOT:?}/build/e90-out"
mkdir -p "$OUT/aifoundry3/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

K=tools/claims-v3/kinds
"$PY" $K/reduce_e90.py "${ok[@]}" --out "$OUT/e90.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
ARMS=()
for k in 0.1994 0.3803 0; do   # E78's primary slope value on E78's runs, E71's idle slope, no correction
  "$PY" $K/reduce_e90.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e90-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--e90-arm "leak$k=$OUT/e90-leak$k.json")
done
"$PY" $K/score_e90.py --e90 "$OUT/e90.json" "${ARMS[@]}" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e90 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/E90.md $K/predictions-e78.json \
    $K/predictions-e90.json $K/kinds.json $K/e90/e90.json \
    $K/e90/tiles/*/*.bin 2>/dev/null || shasum -a 256 tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/E90.md \
    $K/predictions-e78.json $K/predictions-e90.json $K/kinds.json $K/e90/e90.json \
    $K/e90/tiles/*/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done   # the pull puts the queue/dry logs and ident reads there
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/kinds/"; done
for d in "$RAW"/kinds/p90*.attempt-* "$RAW"/kinds-smoke/p90*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
