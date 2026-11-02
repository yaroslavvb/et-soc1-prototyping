#!/usr/bin/env bash
# E128 (Q136): reduce every finished pass with E78's reduction (reduce_e128.py: tools/claims-v3/kinds/reduce_e78.py unchanged with E128's items, card 1's
# config gate and its meter dips removed, leakage frozen at E82's 0.2414), run the registered arms (dips kept; pass gates opened; leakage auto, 0.1994,
# 0.3803, 0.545, 0), score E128's rules and assemble the data directory. A port of tools/claims-v3/signloc/collect_e108.sh.
# Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e128/collect_e128.sh ['p128[1-9][0-9]'] <raw root>
#
# <raw root> holds e128/, e128-smoke/ and e128-readback/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/ (only the p128* passes)
# and logs/. Output: build/e128-out/2026-11-02-e128-fp16-signs/ with e128.json, runs.csv, reduce.txt, the arms (e128-dipskept, e128-gatesoff, e128-auto,
# e128-leak<k> .json/.csv/.txt), scored.json, results.md, code.sha256, logs/, the smoke and every pass's raw data. Only passes whose block.json says "ok" are
# reduced; an `.attempt-*` directory is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p128[1-9][0-9]}
RAW=${2:-$ROOT/build/claims-v3/aifoundry1-c1}
OUT=$ROOT/build/e128-out/2026-11-02-e128-fp16-signs
rm -rf "${ROOT:?}/build/e128-out"
mkdir -p "$OUT/aifoundry1-c1/e128" "$OUT/logs"

ok=()
for d in "$RAW"/e128/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

K=tools/claims-v3/e128
KD=tools/claims-v3/kinds
"$PY" $K/reduce_e128.py "${ok[@]}" --leak 0.2414 --out "$OUT/e128.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
ARMS=()
"$PY" $K/reduce_e128.py "${ok[@]}" --keep-dips --leak 0.2414 --no-refit --out "$OUT/e128-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
ARMS+=(--arm "dips_kept=$OUT/e128-dipskept.json")
"$PY" $K/reduce_e128.py "${ok[@]}" --gates-off --leak 0.2414 --no-refit --out "$OUT/e128-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
ARMS+=(--arm "gates_off=$OUT/e128-gatesoff.json")
"$PY" $K/reduce_e128.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e128-auto.json" --csv "$OUT/runs-auto.csv" \
  --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
ARMS+=(--arm "auto=$OUT/e128-auto.json")
for k in 0.1994 0.3803 0.545 0; do   # E78's fit (Q130(n)'s D scope), E71's idle slope, card 1's idle slope (E82), none
  "$PY" $K/reduce_e128.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e128-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--arm "leak$k=$OUT/e128-leak$k.json")
done
RB=$RAW/e128-readback/p12802/readback.jsonl
"$PY" $K/score_e128.py --e128 "$OUT/e128.json" --readback "$RB" "${ARMS[@]}" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e128 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { shasum -a 256 tools/claims-v3/lib.sh $KD/e78_common.py $KD/run_e78.py $KD/reduce_e78.py $KD/make_kinds.py $KD/make_e104.py \
    $K/*e128*.* $K/E128.md $K/predictions-e128.json $K/ettelem_guard.sh $KD/kinds.json $K/e128/e128.json $K/e128/tiles/*/*.bin 2>/dev/null ||
  sha256sum tools/claims-v3/lib.sh $KD/e78_common.py $KD/run_e78.py $KD/reduce_e78.py $KD/make_kinds.py $KD/make_e104.py \
    $K/*e128*.* $K/E128.md $K/predictions-e128.json $K/ettelem_guard.sh $KD/kinds.json $K/e128/e128.json $K/e128/tiles/*/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry1-c1/e128/"; done
for d in "$RAW"/e128-readback/p128*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/e128/readback-$(basename "$d")"; done
for d in "$RAW"/e128/p128*.attempt-* "$RAW"/e128-smoke/p128*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/e128/$(basename "$(dirname "$d")")-$(basename "$d")"
done
for d in "$RAW"/e128/p128*; do   # a pass whose block did not end ok is kept beside, never reduced
  case "$d" in *.attempt-*) continue ;; esac
  [ -d "$d" ] && [ ! -d "$OUT/aifoundry1-c1/e128/$(basename "$d")" ] && cp -r "$d" "$OUT/aifoundry1-c1/e128/notok-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
