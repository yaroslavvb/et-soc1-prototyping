#!/bin/bash
# mask-posimb (Q238) a02: E224 arm B's committed session (087f9baa, docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry2/session) reduced
# by E208's REGISTERED reducer (tools/claims-v3/e208/proposal/src/reduce_mms.py b9e32618..., mms_common.py c3fc7883..., the reducer E224's
# runbook step 13 names for arm B), read only, from the lane's clone; output in the lane's work/e224b/ only. Desk; single-threaded; in a slot.
set -u
W=${ROUND_W:?the round folder}
LANE=$W/out/mask-posimb
LAB=$LANE/work/lab
R8=$LAB/tools/claims-v3/e208/proposal/src
DD=$LAB/docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry2
OUT=$LANE/work/e224b
mkdir -p "$OUT"
[ "$(sha256sum "$R8/reduce_mms.py" | cut -c1-64)" = b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5 ] || { echo "reduce_mms.py not the registered one"; exit 10; }
[ "$(sha256sum "$R8/mms_common.py" | cut -c1-64)" = c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c ] || { echo "mms_common.py not the registered one"; exit 10; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd "$OUT" || exit 10
bash "$W/slot.sh" nice -n 10 timeout 900 /usr/bin/python3 -I -B "$R8/reduce_mms.py" "$DD/session" --out "$OUT/data-e224b.json" --txt "$OUT/reduce-e224b.txt" > "$OUT/reduce.out" 2>&1
rc=$?
echo "reduce_mms.py rc $rc"
tail -3 "$OUT/reduce.out"
sha256sum "$OUT/data-e224b.json" "$OUT/reduce-e224b.txt" 2>/dev/null
git -C "$LAB" status --short | head -3
