#!/bin/bash
# E135: rebuild every derived file in this directory from logs/, with Python 3 and no third-party modules.
# Run from this directory: bash rebuild.sh
set -eu
T=../../../../tools/gpu/e135
python3 "$T/reduce_e135.py" logs/e135-20261102-r1 --preds "$T/predictions-e135.json" --json results.json > reduce.txt
python3 "$T/posthoc_e135.py" logs/e135-20261102-r1 --preds "$T/predictions-e135.json" --json posthoc.json > posthoc.txt
python3 "$T/reduce_e135.py" logs/e135-20261102-smoke1 --preds "$T/predictions-e135.json" > smoke-reduce.txt
echo "rebuilt: results.json reduce.txt posthoc.json posthoc.txt smoke-reduce.txt"
