#!/usr/bin/env bash
# E110's reduction, exactly as registered: tools/claims-v3/e110/reduce_e110.py and predictions.json as frozen at 52b5fc46. Run it from the
# lab repo root; any python3 with numpy. The primary arm is the passes with the board meter's dip samples removed by E82 A2's definition
# (dp/posthoc_dips.py), as E99's reduce.sh did; the warm-up pass 11010 is in the glob, and the reducer keeps it out of the headline by the
# registered rule. The smoke (p11001) is not reduced. WORK holds the filtered copies, and is not committed.
set -eu
D=docs/reports/data/2026-11-01-e110-memory-width
PY=${PY:-python3}
WORK=${WORK:-build/e110-dipwork}
$PY tools/claims-v3/dp/posthoc_dips.py "$D"/passes/p1101? --work "$WORK" --out "$D/dips.json"
for leak in auto 0.2936 0.3803; do
  out=$D/e110.json; csv=$D/runs.csv
  [ "$leak" = auto ] || { out=$D/e110-leak$leak.json; csv=; }
  $PY tools/claims-v3/e110/reduce_e110.py "$WORK"/p1101? --gen "$D/gen" --pred tools/claims-v3/e110/predictions.json \
    --leak "$leak" --out "$out" ${csv:+--csv "$csv"}
done
$PY tools/claims-v3/e110/reduce_e110.py "$D"/passes/p1101? --gen "$D/gen" --pred tools/claims-v3/e110/predictions.json --out "$D/e110-unfiltered.json"
