#!/bin/bash
# mask-ceiling (Q238 track C) s02: E224 arm B's measured side for this lane's points, made exactly as E224's kit's step 13 makes it
# (tools/claims-v3/e224/rb/s24_score_e224b.sh): E208's registered reducer reduce_mms.py (b9e32618...) with mms_common.py (c3fc7883...), run from
# the lane's scratch clone at its committed path, on the COMMITTED session folder of docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry2/
# (data commit 087f9baa). Writes only work/e224b/. No device, no score. Desk; /usr/bin/python3 3.12.3 -I -B, single-threaded, run in a slot.
set -u
LANE="${MASK_CEILING_LANE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$LANE/work/lab" || exit 10
DD=docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry2
R8=tools/claims-v3/e208/proposal/src
C=$(git log --diff-filter=A --format=%H -- "$DD/SHA256SUMS" | tail -n 1)
echo "data commit of $DD: $C"
[ -n "$C" ] || exit 10
[ -z "$(git status --porcelain -- "$DD")" ] || { echo "the data directory differs from its commit"; exit 10; }
[ "$(sha256sum $R8/reduce_mms.py | cut -c1-64)" = b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5 ] || { echo "reduce_mms.py not the registered one"; exit 10; }
[ "$(sha256sum $R8/mms_common.py | cut -c1-64)" = c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c ] || { echo "mms_common.py not the registered one"; exit 10; }
mkdir -p "$LANE/work/e224b"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
prlimit --as=4294967296 /usr/bin/python3 -I -B "$R8/reduce_mms.py" "$DD/session" --out "$LANE/work/e224b/data-e224b.json" --txt "$LANE/work/e224b/reduce-e224b.txt" > "$LANE/work/e224b/reduce.out" 2>&1
rc=$?
echo "reduce_mms.py rc $rc"
tail -5 "$LANE/work/e224b/reduce.out"
sha256sum "$LANE/work/e224b/data-e224b.json" "$LANE/work/e224b/reduce-e224b.txt" 2>/dev/null
exit $rc
