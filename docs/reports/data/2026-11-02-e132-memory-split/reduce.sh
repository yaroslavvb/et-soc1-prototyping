#!/usr/bin/env bash
# E132's reduction, exactly as registered: tools/claims-v3/e132/reduce_e132.py and predictions.json as frozen at 34ec50b8. Run it from the
# lab repo root; any python3 with numpy. The primary arm is the passes with the board meter's dip samples removed by E82 A2's definition
# (dp/posthoc_dips.py), as E99's and E110's reduce.sh did; the warm-up pass 13210 is in the glob, and the reducer keeps it out of the
# headline by the registered rule. The smoke (p13201) is not reduced. WORK holds the filtered copies, and is not committed.
set -eu
D=docs/reports/data/2026-11-02-e132-memory-split
PY=${PY:-python3}
WORK=${WORK:-build/e132-dipwork}
$PY tools/claims-v3/dp/posthoc_dips.py "$D"/passes/p1321? --work "$WORK" --out "$D/dips.json"
for leak in auto 0.2936 0.3803; do
  out=$D/e132.json; csv=$D/runs.csv
  [ "$leak" = auto ] || { out=$D/e132-leak$leak.json; csv=; }
  $PY tools/claims-v3/e132/reduce_e132.py "$WORK"/p1321? --gen "$D/gen" --pred tools/claims-v3/e132/predictions.json \
    --leak "$leak" --out "$out" ${csv:+--csv "$csv"}
done
$PY tools/claims-v3/e132/reduce_e132.py "$D"/passes/p1321? --gen "$D/gen" --pred tools/claims-v3/e132/predictions.json --out "$D/e132-unfiltered.json"
