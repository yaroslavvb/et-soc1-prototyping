#!/usr/bin/env bash
# E76's probe reduction, exactly as run on Wed 28 Oct 2026. Run it from the lab repo root.
set -eu
D=docs/reports/data/2026-10-28-e76-trapped-instructions
python3 tools/claims-v3/tr/reduce_tr.py "$D"/passes/p76* --gen "$D/gen" \
  --pred tools/claims-v3/tr/predictions.json --out "$D/tr.json" --csv "$D/runs.csv"
