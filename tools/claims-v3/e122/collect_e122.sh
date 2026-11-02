#!/usr/bin/env bash
# E122 (Q134): reduce every finished pass with E108's reduction, unchanged (tools/claims-v3/signloc/reduce_e108.py:
# reduce_e78.py with E108's items; dips removed by E82 A2's definition; on aifoundry3 its card-1 config substitution never
# fires, because the card reads 0/65, which E78's gate accepts as it stands), with the leakage slope frozen at E78's own
# fit on this card, 0.1994 W/C; run the registered arms (dips kept and gates off at 0.1994; leakage auto, 0.2414 (E108's),
# 0.3803, 0.545, 0); score E122's rules (score_e122.py) on the reduction and the read-back; assemble the data directory.
# A port of tools/claims-v3/signloc/collect_e108.sh. Desk compute: run it on the Intel over a copy of the raw passes,
# never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e122/collect_e122.sh ['p122[1-9][0-9]'] <raw root>
#
# <raw root> holds signloc/, signloc-smoke/ and signloc-readback/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/
# (only the p122* passes) and logs/. Output: build/e122-out/2026-11-01-e122-signs-replicate/ with e122.json, runs.csv,
# reduce.txt, the arms (e122-<arm> .json/.csv/.txt), scored.json, results.md, code.sha256, logs/, the smoke, the read-back
# and every pass's raw data. Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never read;
# no pass is chosen after the fact. reduce_e108.py writes "experiment": "E108" into each reduction and an "E108:" header
# into reduce.txt: that is E108's unchanged code speaking.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p122[1-9][0-9]}
RAW=${2:?raw root (holds signloc/, signloc-smoke/, signloc-readback/, logs/)}
OUT=$ROOT/build/e122-out/2026-11-01-e122-signs-replicate
rm -rf "${ROOT:?}/build/e122-out"
mkdir -p "$OUT/aifoundry3/signloc" "$OUT/logs"

ok=()
for d in "$RAW"/signloc/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

SL=tools/claims-v3/signloc
KD=tools/claims-v3/kinds
E=tools/claims-v3/e122
"$PY" $SL/reduce_e108.py "${ok[@]}" --leak 0.1994 --out "$OUT/e122.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
ARMS=()
"$PY" $SL/reduce_e108.py "${ok[@]}" --keep-dips --leak 0.1994 --no-refit --out "$OUT/e122-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
ARMS+=(--arm "dips_kept=$OUT/e122-dipskept.json")
"$PY" $SL/reduce_e108.py "${ok[@]}" --gates-off --leak 0.1994 --no-refit --out "$OUT/e122-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
ARMS+=(--arm "gates_off=$OUT/e122-gatesoff.json")
"$PY" $SL/reduce_e108.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e122-auto.json" --csv "$OUT/runs-auto.csv" \
  --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
ARMS+=(--arm "auto=$OUT/e122-auto.json")
for k in 0.2414 0.3803 0.545 0; do   # E108's primary (E82's fit on card 1), E71's idle slope, card 1's idle slope (E82), none
  "$PY" $SL/reduce_e108.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e122-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--arm "leak$k=$OUT/e122-leak$k.json")
done
RB=$(ls "$RAW"/signloc-readback/p12202/readback.jsonl 2>/dev/null)
"$PY" $E/score_e122.py --e122 "$OUT/e122.json" ${RB:+--readback "$RB"} "${ARMS[@]}" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e122 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { shasum -a 256 tools/claims-v3/lib.sh $KD/e78_common.py $KD/run_e78.py $KD/reduce_e78.py $KD/kinds.json \
    $SL/e108_common.py $SL/run_e108.py $SL/block_e108.sh $SL/readback_e108.py $SL/reduce_e108.py $SL/score_e108.py \
    $SL/predictions-e108.json $SL/e108/e108.json $SL/e108/tiles/*/*.bin $E/*.py $E/*.sh $E/*.json $E/*.md 2>/dev/null ||
  sha256sum tools/claims-v3/lib.sh $KD/e78_common.py $KD/run_e78.py $KD/reduce_e78.py $KD/kinds.json \
    $SL/e108_common.py $SL/run_e108.py $SL/block_e108.sh $SL/readback_e108.py $SL/reduce_e108.py $SL/score_e108.py \
    $SL/predictions-e108.json $SL/e108/e108.json $SL/e108/tiles/*/*.bin $E/*.py $E/*.sh $E/*.json $E/*.md; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/signloc/"; done
for d in "$RAW"/signloc-readback/p122*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/signloc/readback-$(basename "$d")"; done
for d in "$RAW"/signloc/p122*.attempt-* "$RAW"/signloc-smoke/p122*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/signloc/$(basename "$(dirname "$d")")-$(basename "$d")"
done
for d in "$RAW"/signloc/p122*; do   # a pass whose block did not end ok is kept beside, never reduced
  case "$d" in *.attempt-*) continue ;; esac
  [ -d "$d" ] && [ ! -d "$OUT/aifoundry3/signloc/$(basename "$d")" ] && cp -r "$d" "$OUT/aifoundry3/signloc/notok-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
