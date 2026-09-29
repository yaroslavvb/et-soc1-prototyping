#!/bin/bash
# mlp_more.sh: larger MLP reference points (host CPU only). Usage: nice -n 19 ./mlp_more.sh RESULTS_DIR
OUT=${1:?results dir}
cd "$(dirname "$0")"
for cfg in "128 3 0 1,2 60" "50 3 0.2 1,2 60" "20 5 0 1,2 60" "64 4 0 1 120"; do
    set -- $cfg
    if command -v et-who >/dev/null; then
        while ! et-who --check >/dev/null 2>&1; do sleep 30; done
    fi
    OPENBLAS_NUM_THREADS=1 python3 mlp.py --n $1 --k $2 --eta $3 --seeds $4 --max-s $5 --max-steps 2000000 \
        --out "$OUT/mlp.jsonl" > /dev/null
done
echo "$(date +%T) mlp_more done" >> "$OUT/sweep.log"
