#!/bin/bash
# phase2.sh: the second half of the SP3 sweep (host CPU only; nothing here opens a card).
#   1. re-time the exhaustive scan where W >= 5 with the padded AVX-512 build (old records kept aside)
#   2. GF(2) elimination on random subsets (noisy labels), 3. the numpy GEMM form, 4. the MLP reference.
# Every step is niced, at most 4 threads, and waits while anyone holds an ET card (et-who --check).
# Usage: nice -n 19 ./phase2.sh RESULTS_DIR
set -u
OUT=${1:?results dir}
cd "$(dirname "$0")"

guard() {
    command -v et-who >/dev/null || return 0
    while ! et-who --check >/dev/null 2>&1; do
        echo "$(date +%T) phase2: card held, waiting" >> "$OUT/sweep.log"
        sleep 30
    done
}

python3 - "$OUT" <<'EOF'
import json, os, sys
out = sys.argv[1]
p = os.path.join(out, "exh.jsonl")
keep, old = [], []
for line in open(p):
    d = json.loads(line)
    (old if d["W"] >= 5 else keep).append(line)
if old:
    with open(os.path.join(out, "exh_unpadded.jsonl"), "a") as f:
        f.writelines(old)
    with open(p + ".tmp", "w") as f:
        f.writelines(keep)
    os.replace(p + ".tmp", p)
print(f"moved {len(old)} exh records with W >= 5 to exh_unpadded.jsonl")
EOF

guard; python3 sweep.py exh --out "$OUT" --budget-s 1500 --threads 4 --exh-threaded-cap-cpu-s 400
guard; python3 sweep.py gers --out "$OUT" --budget-s 900 --threads 1
guard; OPENBLAS_NUM_THREADS=1 python3 sweep.py gemm --out "$OUT" --budget-s 900 --threads 1
for cfg in "20 3 0 1,2,3" "30 3 0 1,2,3" "50 3 0 1,2,3" "50 3 0.1 1,2" "20 4 0 1,2,3" "32 4 0 1,2" "64 3 0 1,2"; do
    set -- $cfg
    guard
    OPENBLAS_NUM_THREADS=1 python3 mlp.py --n $1 --k $2 --eta $3 --seeds $4 --max-s 90 --out "$OUT/mlp.jsonl" > /dev/null
done
echo "$(date +%T) phase2 done" >> "$OUT/sweep.log"
