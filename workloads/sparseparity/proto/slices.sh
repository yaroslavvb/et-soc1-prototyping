#!/bin/bash
# slices.sh: timing samples of scans too large to run whole (host CPU only; nothing here opens a card).
# One thread, every S-th outer task (spbits exh slice=S); the per-subset rate then projects the full scan.
# Waits while anyone holds an ET card. Usage: nice -n 19 ./slices.sh RESULTS_DIR
OUT=${1:?results dir}
cd "$(dirname "$0")"
for cfg in "512 5 0.2 218 32" "512 5 0.3 521 32" "512 5 0.4 2151 32" "1024 5 0.3 575 2048" \
           "1024 5 0.4 2373 2048" "1024 4 0.4 2032 64"; do
    set -- $cfg
    if command -v et-who >/dev/null; then
        while ! et-who --check >/dev/null 2>&1; do
            echo "$(date +%T) slices: card held, waiting" >> "$OUT/sweep.log"; sleep 30
        done
    fi
    nice -n 19 ./spbits exh n=$1 k=$2 eta=$3 m=$4 seed=1 threads=1 slice=$5 >> "$OUT/exh_slice.jsonl"
done
echo "$(date +%T) slices done" >> "$OUT/sweep.log"
