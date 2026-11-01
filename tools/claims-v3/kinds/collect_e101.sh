#!/usr/bin/env bash
# E101 (Q132): reduce every finished pass with E78's reduction (reduce_e101.py runs reduce_e78.py unchanged with E101's items), run the registered leakage arms, score E101's power rules, and assemble the data
# directory's power part. Desk compute: run it on the Intel over a copy of the raw passes (as E78's A1 says), never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/kinds/collect_e101.sh ['p101[1-9][0-9]'] <raw root>
#
# <raw root> holds kinds/ and kinds-smoke/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/ (only the p101* passes). Output: build/e101-out/2026-11-01-e101-real-matmul/ with e101.json, runs.csv, reduce.txt,
# the leakage arms (e101-leak0.1994 / 0.3803 / 0 .json, csv, txt), scored.json, results.md, code.sha256, logs/, the smoke and every pass's raw data. Only passes whose block.json says "ok" are reduced; an `.attempt-*`
# directory is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-/usr/bin/python3}
GLOB=${1:-p101[1-9][0-9]}
RAW=${2:-$ROOT/build/claims-v3/aifoundry3}
OUT=$ROOT/build/e101-out/2026-11-01-e101-real-matmul
rm -rf "${ROOT:?}/build/e101-out"
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
"$PY" $K/reduce_e101.py "${ok[@]}" --out "$OUT/e101.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -3 "$OUT/reduce.log" | cut -c1-200
ARMS=()
for k in 0.1994 0.3803 0; do   # E78's primary slope value on E78's runs, E71's idle slope, no correction
  "$PY" $K/reduce_e101.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e101-leak$k.json" --csv "$OUT/runs-leak$k.csv" --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--arm "leak$k=$OUT/e101-leak$k.json")
done
"$PY" $K/score_e101.py --e101 "$OUT/e101.json" "${ARMS[@]}" --raw "${ok[@]}" --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1; echo "score rc=$?"; tail -30 "$OUT/score.log" | cut -c1-220
for d in "${ok[@]}"; do cp -R "$d" "$OUT/aifoundry3/kinds/"; done
[ -d "$RAW/kinds-smoke" ] && cp -R "$RAW/kinds-smoke" "$OUT/aifoundry3/" 2>/dev/null
( shasum -a 256 $K/e78_common.py $K/run_e78.py $K/reduce_e78.py tools/claims-v3/lib.sh $K/e101_common.py $K/run_e101.py $K/reduce_e101.py $K/score_e101.py $K/block_e101.sh $K/queue_e101.sh $K/run_e101.sh $K/collect_e101.sh $K/predictions-e101.json \
    tools/claims-v3/rgm/host/main.cpp tools/claims-v3/rgm/kernel/sparsity.c tools/claims-v3/rgm/sparsity_args.h ) > "$OUT/code.sha256"
du -sh "$OUT"
