#!/usr/bin/env bash
# E137 (Q137): reduce every finished pass with E78's reduction (reduce_e137.py: tools/claims-v3/kinds/reduce_e78.py unchanged with E137's items,
# card 1's config gate and its meter dips removed, leakage frozen at E82's 0.2414), the set-aside rule's relaxed reading, the registered arms (dips
# kept; pass gates opened; leakage auto, 0.1994, 0.3803, 0.545, 0), score E137's rules and assemble the data directory. A port of
# tools/claims-v3/e128/collect_e128.sh. Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e137/collect_e137.sh ['p137[1-9][0-9]'] <raw root>
#
# <raw root> holds e137/ and e137-smoke/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/ and logs/ (the session's files from
# build/e137/). Output: build/e137-out/2026-11-02-e137-fp16-sign-rest/. Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory
# is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p137[1-9][0-9]}
RAW=${2:-$ROOT/build/claims-v3/aifoundry1-c1}
OUT=$ROOT/build/e137-out/2026-11-02-e137-fp16-sign-rest
rm -rf "${ROOT:?}/build/e137-out"
mkdir -p "$OUT/aifoundry1-c1/e137" "$OUT/logs"

ok=()
for d in "$RAW"/e137/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

K=tools/claims-v3/e137
KD=tools/claims-v3/kinds
"$PY" $K/reduce_e137.py "${ok[@]}" --leak 0.2414 --out "$OUT/e137.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
"$PY" $K/reduce_e137.py "${ok[@]}" --relax-anchors --leak 0.2414 --no-refit --out "$OUT/e137-relaxed.json" --csv "$OUT/runs-relaxed.csv" \
  --txt "$OUT/reduce-relaxed.txt" > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed (set-aside reading) rc=$?"
ARMS=()
"$PY" $K/reduce_e137.py "${ok[@]}" --keep-dips --leak 0.2414 --no-refit --out "$OUT/e137-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
ARMS+=(--arm "dips_kept=$OUT/e137-dipskept.json")
"$PY" $K/reduce_e137.py "${ok[@]}" --gates-off --leak 0.2414 --no-refit --out "$OUT/e137-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
ARMS+=(--arm "gates_off=$OUT/e137-gatesoff.json")
"$PY" $K/reduce_e137.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e137-auto.json" --csv "$OUT/runs-auto.csv" \
  --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
ARMS+=(--arm "auto=$OUT/e137-auto.json")
for k in 0.1994 0.3803 0.545 0; do
  "$PY" $K/reduce_e137.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e137-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--arm "leak$k=$OUT/e137-leak$k.json")
done
"$PY" $K/score_e137.py --primary "$OUT/e137.json" --relaxed "$OUT/e137-relaxed.json" "${ARMS[@]}" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e137 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && sha256sum tools/claims-v3/lib.sh $KD/e78_common.py $KD/run_e78.py $KD/reduce_e78.py $KD/kinds.json \
    $K/*.py $K/*.sh $K/E137.md $K/predictions-e137.json tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/e128/e128/e128.json \
    tools/claims-v3/e128/e128/tiles/*/*.bin ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry1-c1/e137/"; done
for d in "$RAW"/e137/p137*.attempt-* "$RAW"/e137-smoke/p137*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/e137/$(basename "$(dirname "$d")")-$(basename "$d")"
done
for d in "$RAW"/e137/p137*; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -d "$d" ] && [ ! -d "$OUT/aifoundry1-c1/e137/$(basename "$d")" ] && cp -r "$d" "$OUT/aifoundry1-c1/e137/notok-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
