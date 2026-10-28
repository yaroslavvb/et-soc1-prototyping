#!/usr/bin/env bash
# E75's reduction, exactly as run on Wed 28 Oct 2026. Run it from the lab repo root; any python3 with numpy.
set -eu
D=docs/reports/data/2026-10-28-e75-memory-flip-ladder
for leak in auto 0.2936 0.3803; do
  out=$D/mf.json; csv=$D/runs.csv
  [ "$leak" = auto ] || { out=$D/mf-leak$leak.json; csv=; }
  python3 tools/claims-v3/mf/reduce_mf.py "$D"/passes/p75* --gen "$D/gen" \
    --pred tools/claims-v3/mf/predictions.json --leak "$leak" --out "$out" ${csv:+--csv "$csv"}
done
