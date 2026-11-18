#!/bin/bash
# v31-counts step 4 (inner; inside W/slot.sh + W/nodev.sh): the bench's functional check (fcheck_all.sh: one txfma_top over 40,000 vectors in
# fp32 and fp16; whole TensorFMA ops in three formats; the zero gate), which must PASS before any count is quoted. JOBS=2.
set -u
. <W>/out/v31-counts/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
mkdir -p "$L/work/fcheck"
cd "$L/work/bench" || exit 2
echo "start $(ts); load $(load1)"
JOBS=2 PY=/usr/bin/python3 bash fcheck_all.sh "$L/work/fcheck"
rc=$?
echo "fcheck rc $rc; end $(ts)"
exit $rc
