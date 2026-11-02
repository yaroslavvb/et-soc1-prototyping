#!/usr/bin/env bash
# E123 (Q134): reduce every finished pass with E78's reduction (reduce_e123.py runs tools/claims-v3/kinds/reduce_e78.py
# unchanged with E123's items; dips removed by E82 A2's definition), with the leakage slope frozen at E78's own fit on this
# card, 0.1994 W/C; run the registered arms (dips kept at 0.1994; E78's pass gates opened; leakage auto, 0.2414, 0.3803,
# 0.545, 0); score E123's rules (score_e123.py) and assemble the data directory. A port of tools/claims-v3/e121/collect_e121.sh.
# Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e123/collect_e123.sh ['p123[1-9][0-9]'] <raw root>
#
# <raw root> holds kinds/ and kinds-smoke/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/ (only the p123*
# passes) and logs/. Output: build/e123-out/2026-11-01-e123-tile-spread-rest/ with e123.json, runs.csv, reduce.txt, the arms
# (e123-dipskept, e123-gatesoff, e123-auto, e123-leak<k> .json/.csv/.txt), scored.json, results.md, code.sha256, logs/, the
# smoke and every pass's raw data. Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never
# read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p123[1-9][0-9]}
RAW=${2:?raw root (holds kinds/, kinds-smoke/, logs/)}
OUT=$ROOT/build/e123-out/2026-11-01-e123-tile-spread-rest
rm -rf "${ROOT:?}/build/e123-out"
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
E=tools/claims-v3/e123
"$PY" $E/reduce_e123.py "${ok[@]}" --leak 0.1994 --out "$OUT/e123.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
ARMS=()
"$PY" $E/reduce_e123.py "${ok[@]}" --keep-dips --leak 0.1994 --no-refit --out "$OUT/e123-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
ARMS+=(--arm "dips_kept=$OUT/e123-dipskept.json")
"$PY" $E/reduce_e123.py "${ok[@]}" --gates-off --leak 0.1994 --no-refit --out "$OUT/e123-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
ARMS+=(--arm "gates_off=$OUT/e123-gatesoff.json")
"$PY" $E/reduce_e123.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e123-auto.json" --csv "$OUT/runs-auto.csv" \
  --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
ARMS+=(--arm "auto=$OUT/e123-auto.json")
for k in 0.2414 0.3803 0.545 0; do   # E93/E94's primary (E82's fit on card 1), E71's idle slope, card 1's idle slope (E82), none
  "$PY" $E/reduce_e123.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e123-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--arm "leak$k=$OUT/e123-leak$k.json")
done
"$PY" $E/score_e123.py --e123 "$OUT/e123.json" "${ARMS[@]}" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e123 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json \
    $K/score_e94.py $E/*.py $E/*.sh $E/*.json $E/*.md $E/tiles/*/*.bin 2>/dev/null ||
  sha256sum tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json \
    $K/score_e94.py $E/*.py $E/*.sh $E/*.json $E/*.md $E/tiles/*/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/kinds/"; done
for d in "$RAW"/kinds/p123*.attempt-* "$RAW"/kinds-smoke/p123*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
for d in "$RAW"/kinds/p123*; do   # a pass whose block did not end ok is kept beside, never reduced
  case "$d" in *.attempt-*) continue ;; esac
  [ -d "$d" ] && [ ! -d "$OUT/aifoundry3/kinds/$(basename "$d")" ] && cp -r "$d" "$OUT/aifoundry3/kinds/notok-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
