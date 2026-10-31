#!/usr/bin/env bash
# E82 (Q130): reduce every finished card-1 pass with E78's reduction (reduce_e82.py runs reduce_e78.py unchanged),
# run the registered leakage and rail arms, score E78's rules and the cross-card rules, and assemble the data
# directory. Desk compute: run it on the Intel over a copy of the raw passes (as E78's A1 does):
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/kinds/collect_e82.sh ['p82[1-9][0-9]'] [<raw root>]
#   E78DIR=<E78's data dir> ...      # default docs/reports/data/2026-10-31-e78-kinds-energy-matrix (scored if present)
#
# <raw root> holds kinds/ and kinds-smoke/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/.
# Output: build/e82-out/2026-10-31-e82-kinds-aifoundry1/ with e82.json, runs.csv, reduce.txt, the leakage arms
# (e82-leak0.545 / 0.3803 / 0 .json, csv, txt), the rail-lag arms (e82-tau0.80/1.10.json), scored.json, results.md,
# code.sha256, logs/, the smoke and every pass's raw data. Only passes whose block.json says "ok" are reduced; an
# `.attempt-*` directory is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p82[1-9][0-9]}
RAW=${2:-$ROOT/build/claims-v3/aifoundry1-c1}
E78DIR=${E78DIR:-$ROOT/docs/reports/data/2026-10-31-e78-kinds-energy-matrix}
OUT=$ROOT/build/e82-out/2026-10-31-e82-kinds-aifoundry1
rm -rf "${ROOT:?}/build/e82-out"
mkdir -p "$OUT/aifoundry1-c1/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

K=tools/claims-v3/kinds
"$PY" $K/reduce_e82.py "${ok[@]}" --out "$OUT/e82.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
for k in 0.545 0.3803 0; do   # the registered leakage arms: card 1's E44 idle slope, E78's arm, no correction
  "$PY" $K/reduce_e82.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e82-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
done
for tau in 0.80 1.10; do   # the registered rail-lag arms (the rail is reported, never scored)
  "$PY" $K/reduce_e82.py "${ok[@]}" --tau "$tau" --no-refit --out "$OUT/e82-tau$tau.json" > "$OUT/reduce-tau$tau.log" 2>&1
  echo "rail-tau arm $tau rc=$?"
done
E78ARG=()
if [ -f "$E78DIR/e78.json" ]; then E78ARG=(--e78-dir "$E78DIR"); echo "cross-card: against $E78DIR"; else echo "cross-card: E78 data not present ($E78DIR)"; fi
"$PY" $K/score_e82.py --e82 "$OUT/e82.json" --e82-arm "leak0.545=$OUT/e82-leak0.545.json" \
  --e82-arm "leak0.3803=$OUT/e82-leak0.3803.json" --e82-arm "leak0=$OUT/e82-leak0.json" ${E78ARG[@]+"${E78ARG[@]}"} \
  --md "$OUT/results.md" --json "$OUT/scored.json" > "$OUT/score.log" 2>&1 \
  && echo "results.md written" || { echo "score_e82 failed"; tail -20 "$OUT/score.log"; }

( sha256sum tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/E82.md $K/predictions-e78.json $K/predictions-e82.json \
    $K/kinds.json 2>/dev/null || shasum -a 256 tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/E82.md \
    $K/predictions-e78.json $K/predictions-e82.json $K/kinds.json ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done   # the pull puts the queue/dry logs and ident reads there
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry1-c1/kinds/"; done
for d in "$RAW"/kinds/p82*.attempt-* "$RAW"/kinds-smoke/p82*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
