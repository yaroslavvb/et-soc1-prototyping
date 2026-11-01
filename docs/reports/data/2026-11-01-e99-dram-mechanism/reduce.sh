#!/usr/bin/env bash
# E99's reduction, exactly as registered: tools/claims-v3/dm/reduce_dm.py and predictions.json as frozen at 590f9b7e. Run it from the
# lab repo root; any python3 with numpy. The primary arm is the passes with the board meter's dip samples removed by E82 A2's
# definition (dp/posthoc_dips.py); the warm-up pass 9910 is in the glob, and the reducer keeps it out of the headline by the registered
# rule. The smoke (p9901) is not reduced. WORK holds the filtered copies, and is not committed.
set -eu
D=docs/reports/data/2026-11-01-e99-dram-mechanism
PY=${PY:-python3}
WORK=${WORK:-build/e99-dipwork}
$PY tools/claims-v3/dp/posthoc_dips.py "$D"/passes/p991? --work "$WORK" --out "$D/dips.json"
for leak in auto 0.2936 0.3803; do
  out=$D/dm.json; csv=$D/runs.csv
  [ "$leak" = auto ] || { out=$D/dm-leak$leak.json; csv=; }
  $PY tools/claims-v3/dm/reduce_dm.py "$WORK"/p991? --gen "$D/gen" --pred tools/claims-v3/dm/predictions.json \
    --leak "$leak" --out "$out" ${csv:+--csv "$csv"}
done
$PY tools/claims-v3/dm/reduce_dm.py "$D"/passes/p991? --gen "$D/gen" --pred tools/claims-v3/dm/predictions.json --out "$D/dm-unfiltered.json"
