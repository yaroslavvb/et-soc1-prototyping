#!/usr/bin/env bash
# E74's reduction, exactly as run on Wed 28 Oct 2026. Run it from the lab repo root; any python3 with numpy.
# The leakage line: `auto` is reduce_hl.py's own within-run estimator (what E60/E61/E65 used, and what
# predictions.json's rule 4 means by the default); the two fixed values are the registered sensitivity
# (E66, aifoundry2, 0.2936 W/C) and aifoundry3's own measured idle slope over this launch band (E71, 0.3803).
set -eu
D=docs/reports/data/2026-10-28-e74-register-file-cells
for leak in auto 0.2936 0.3803; do
  out=$D/rf.json; csv=$D/runs.csv
  [ "$leak" = auto ] || { out=$D/rf-leak$leak.json; csv=; }
  python3 tools/claims-v3/rf/reduce_rf.py "$D"/passes/p74* --gen "$D/gen" \
    --pred tools/claims-v3/rf/predictions.json --leak "$leak" --out "$out" ${csv:+--csv "$csv"}
done
