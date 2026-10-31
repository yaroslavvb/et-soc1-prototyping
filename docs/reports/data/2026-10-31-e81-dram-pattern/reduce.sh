#!/usr/bin/env bash
# E81's reduction, exactly as registered: tools/claims-v3/dp/reduce_dp.py and predictions.json as frozen at 14f219ef.
# Run it from the lab repo root; any python3 with numpy. The warm-up pass 8110 is in the glob; the reducer keeps it
# out of the headline by the registered rule. The smoke (p8101) is not reduced.
set -eu
D=docs/reports/data/2026-10-31-e81-dram-pattern
PY=${PY:-python3}
for leak in auto 0.2936 0.3803; do
  out=$D/dp.json; csv=$D/runs.csv
  [ "$leak" = auto ] || { out=$D/dp-leak$leak.json; csv=; }
  "$PY" tools/claims-v3/dp/reduce_dp.py "$D"/passes/p811? --gen "$D/gen" --pred tools/claims-v3/dp/predictions.json \
    --leak "$leak" --out "$out" ${csv:+--csv "$csv"}
done
