#!/usr/bin/env bash
# E152 (Q139): reduce every finished pass with E78's reduction (reduce_e152.py runs reduce_e78.py unchanged with E152's
# items) on the registered primary (dips removed, leakage auto), run the registered arms (dips kept; leakage 0.1994 /
# 0.3803 / 0; gates off), score E152's rules on the primary with every arm beside, and assemble the data directory. Desk
# compute: run it on the Intel over a copy of the raw passes, never on the card's host. A port of
# tools/claims-v3/e127/collect_e127.sh:
#
#   PY=<python with numpy> nice -n 10 bash tools/claims-v3/e152/collect_e152.sh ['p152[1-9][0-9]'] <raw root>
#
# <raw root> holds kinds/, kinds-smoke/, kinds-stoptest/ and logs/ as copied from aifoundry3:aifoundry/build/claims-v3/
# aifoundry3/ (only the p152* passes) and build/e152-logs/. Output: build/e152-out/2026-11-03-e152-gate-dose/ with e152.json,
# runs.csv, reduce.txt, the arms (e152-dipskept, e152-leak0.1994 / 0.3803 / 0, e152-gatesoff: .json, .csv, .txt),
# scored.json, results.md, code.sha256, logs/, the smoke, the stop tests and every pass's raw data. Only passes whose
# block.json says "ok" are reduced; an `.attempt-*` directory is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
GLOB=${1:-p152[1-9][0-9]}
RAW=${2:?raw root}
OUT=$ROOT/build/e152-out/2026-11-03-e152-gate-dose
rm -rf "${ROOT:?}/build/e152-out"
mkdir -p "$OUT/aifoundry3/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

E=tools/claims-v3/e152
K=tools/claims-v3/kinds
# the registered primary: dips removed (E82 A2's definition, E127's primary on this card), leakage auto; the arms: dips
# kept, leakage 0.1994 / 0.3803 / 0 and gates off (each on the dips-removed reduction)
"$PY" $E/reduce_e152.py "${ok[@]}" --drop-dips --out "$OUT/e152.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce (primary, dips removed) rc=$?"; tail -5 "$OUT/reduce.log"
"$PY" $E/reduce_e152.py "${ok[@]}" --out "$OUT/e152-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
ARMS=(--arm "dips_kept=$OUT/e152-dipskept.json")
for k in 0.1994 0.3803 0; do   # E78's primary slope value on E78's runs, E71's idle slope, no correction
  "$PY" $E/reduce_e152.py "${ok[@]}" --drop-dips --leak "$k" --no-refit --out "$OUT/e152-leak$k.json" \
    --csv "$OUT/runs-leak$k.csv" --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--arm "leak$k=$OUT/e152-leak$k.json")
done
"$PY" $E/reduce_e152.py "${ok[@]}" --drop-dips --gates-off --out "$OUT/e152-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
ARMS+=(--arm "gates_off=$OUT/e152-gatesoff.json")
"$PY" $E/score_e152.py --e152 "$OUT/e152.json" "${ARMS[@]}" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e152 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $E/SHA256SUMS $E/tiles/*/*.bin \
    $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json tools/claims-v3/e127/tiles/fp32/q_steady.bin \
    tools/claims-v3/e127/tiles/fp32/q_chk.bin 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $E/SHA256SUMS $E/tiles/*/*.bin \
    $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json tools/claims-v3/e127/tiles/fp32/q_steady.bin \
    tools/claims-v3/e127/tiles/fp32/q_chk.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done   # the pull puts the queue/dry logs and the session reads there
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/kinds/"; done
for d in "$RAW"/kinds/p152*.attempt-* "$RAW"/kinds-smoke/p152* "$RAW"/kinds-stoptest/p152*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
