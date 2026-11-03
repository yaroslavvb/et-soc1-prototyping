#!/usr/bin/env bash
# E115 (Q133): reduce every finished pass with E78's reduction (reduce_e140.py runs reduce_e78.py unchanged with E115's
# items), run the registered arms (leakage 0.1994 / 0.3803 / 0, dips removed, gates off), score E115's rules on the primary
# with every arm beside, and assemble the data directory. Desk compute: run it on the Intel over a copy of the raw passes,
# never on the card's host. A port of tools/claims-v3/kinds/collect_e95.sh:
#
#   PY=python3 nice -n 10 bash tools/claims-v3/e140/collect_e140.sh ['p140[1-9][0-9]'] <raw root>
#
# <raw root> holds kinds/, kinds-smoke/ and logs/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/ (only the
# p140* passes) and build/e140-logs/. Output: build/e140-out/2026-11-02-e140-blind4/ with e140.json, runs.csv,
# reduce.txt, the arms (e140-leak0.1994 / 0.3803 / 0, e140-nodips, e140-gatesoff: .json, .csv, .txt), scored.json,
# results.md, code.sha256, logs/, the smoke and every pass's raw data. Only passes whose block.json says "ok" are reduced; an
# `.attempt-*` directory is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
GLOB=${1:-p140[1-9][0-9]}
RAW=${2:?raw root}
OUT=$ROOT/build/e140-out/2026-11-02-e140-blind4
rm -rf "${ROOT:?}/build/e140-out"
mkdir -p "$OUT/aifoundry3/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

E=tools/claims-v3/e140
K=tools/claims-v3/kinds
"$PY" $E/reduce_e140.py "${ok[@]}" --out "$OUT/e140.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
ARMS=()
for k in 0.1994 0.3803 0; do   # E78's primary slope value on E78's runs, E71's idle slope, no correction
  "$PY" $E/reduce_e140.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e140-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--arm "leak$k=$OUT/e140-leak$k.json")
done
"$PY" $E/reduce_e140.py "${ok[@]}" --drop-dips --out "$OUT/e140-nodips.json" --csv "$OUT/runs-nodips.csv" \
  --txt "$OUT/reduce-nodips.txt" > "$OUT/reduce-nodips.log" 2>&1; echo "dips arm rc=$?"
ARMS+=(--arm "dips_removed=$OUT/e140-nodips.json")
"$PY" $E/reduce_e140.py "${ok[@]}" --gates-off --out "$OUT/e140-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
ARMS+=(--arm "gates_off=$OUT/e140-gatesoff.json")
"$PY" $E/score_e140.py --e140 "$OUT/e140.json" "${ARMS[@]}" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e140 failed"; tail -20 "$OUT/score.log"; }
# the registered fallback reading, labelled: the dips-removed arm scored alone (used only if the primary keeps < 2 passes)
"$PY" $E/score_e140.py --e140 "$OUT/e140-nodips.json" --md "$OUT/results-nodips.md" --json "$OUT/scored-nodips.json" \
  > "$OUT/score-nodips.log" 2>&1 && echo "results-nodips.md written" || echo "score of the dips arm failed"

( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $E/* $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json \
    $K/blind4/blind4.json $K/blind4/SHA256SUMS $K/blind4/tiles/*/*.bin 2>/dev/null || shasum -a 256 tools/claims-v3/lib.sh $E/* $K/e78_common.py $K/run_e78.py \
    $K/reduce_e78.py $K/kinds.json $K/blind4/blind4.json $K/blind4/SHA256SUMS $K/blind4/tiles/*/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done   # the pull puts the queue/dry logs and the session reads there
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/kinds/"; done
for d in "$RAW"/kinds/p140*.attempt-* "$RAW"/kinds-smoke/p140*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
