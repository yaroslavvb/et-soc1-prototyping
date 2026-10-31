#!/usr/bin/env bash
# E78 (Q130): reduce every finished pass, run the registered leakage arms, score, and assemble the data directory.
# Run on the box from the tree that holds the binaries (numpy from lib.sh's .venv), or on the Intel over a copy:
#
#   bash tools/claims-v3/kinds/collect_e78.sh [<pass glob, default p78[1-9][0-9]>] [<raw root>]
#
# Output: build/e78-out/2026-10-31-e78-kinds-energy-matrix/ with e78.json, runs.csv, reduce.txt, the two leakage
# arms (e78-leak0.3803.json, e78-leak0.json and their csv/txt), the rail-lag arms (e78-tau0.80/1.10.json), scored.json, results.md, code.sha256, logs/, the
# smoke and every pass's raw data. Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory is
# never read, and no pass is chosen after the fact (E78.md, "Pre-registered analysis").
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p78[1-9][0-9]}
RAW=${2:-$ROOT/build/claims-v3/aifoundry3}
OUT=$ROOT/build/e78-out/2026-10-31-e78-kinds-energy-matrix
rm -rf "${ROOT:?}/build/e78-out"
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
"$PY" $K/reduce_e78.py "${ok[@]}" --out "$OUT/e78.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
for k in 0.3803 0; do   # the registered leakage arms: E71's measured idle slope, and no correction
  "$PY" $K/reduce_e78.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e78-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
done
for tau in 0.80 1.10; do   # the registered rail-lag arms (the rail is reported, never scored)
  "$PY" $K/reduce_e78.py "${ok[@]}" --tau "$tau" --no-refit --out "$OUT/e78-tau$tau.json" > "$OUT/reduce-tau$tau.log" 2>&1
  echo "rail-tau arm $tau rc=$?"
done
"$PY" $K/score_e78.py --e78 "$OUT/e78.json" --e78-arm "leak0.3803=$OUT/e78-leak0.3803.json" \
  --e78-arm "leak0=$OUT/e78-leak0.json" --md "$OUT/results.md" --json "$OUT/scored.json" > "$OUT/score.log" 2>&1 \
  && echo "results.md written" || { echo "score_e78 failed"; tail -20 "$OUT/score.log"; }

( sha256sum tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/predictions-e78.json $K/kinds.json ) > "$OUT/code.sha256" 2>/dev/null
for f in e78-queue.log e78-dry.log; do [ -f "$ROOT/build/$f" ] && cp "$ROOT/build/$f" "$OUT/logs/$f"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/kinds/"; done
for d in "$RAW"/kinds/p78*.attempt-* "$RAW"/kinds-smoke/p78*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
