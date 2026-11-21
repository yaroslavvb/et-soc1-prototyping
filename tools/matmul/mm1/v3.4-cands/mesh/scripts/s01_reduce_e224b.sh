#!/bin/bash
# mask-mesh s01: E224 arm B's measured side by E208's registered reducer (reduce_mms.py b9e32618..., mms_common.py c3fc7883...: the
# reducer E224's runbook step 13 names) on the COMMITTED session folder (the snapshot of cfd7e641), output in this lane's work/ only.
# Desk, reads only; single-threaded inside the round's CPU slots; a plain timeout (never -k).
set -u
W=<W>
L=$W/out/mask-mesh
S=$L/work/lab/tools/claims-v3/e208/proposal/src
D=$L/work/lab/docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry2/session
O=$L/work/e224b
mkdir -p "$O"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
bash "$W/slot.sh" timeout 900 /usr/bin/python3 -I -B "$S/reduce_mms.py" "$D" --out "$O/data-e224b.json" --txt "$O/reduce-e224b.txt" > "$O/reduce.out" 2>&1
rc=$?
echo "reduce rc $rc"
tail -n 5 "$O/reduce.out"
sha256sum "$O/data-e224b.json" 2>/dev/null
exit $rc
