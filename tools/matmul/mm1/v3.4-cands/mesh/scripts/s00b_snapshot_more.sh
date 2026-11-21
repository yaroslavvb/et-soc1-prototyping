#!/bin/bash
# mask-mesh s00b: one more file into the read-only snapshot (E208's mms_common.py, the registered reducer's helper), same commit.
set -u
W=<W>
LAB=<LAB>
L=$W/out/mask-mesh
C=cfd7e6415d0da2af17c8078ea68a7bac8acd5c5b
/usr/bin/flock -w 600 "$W/locks/lab-git.lock" git -C "$LAB" archive --format=tar "$C" tools/claims-v3/e208/proposal/src/mms_common.py | tar -x -C "$L/work/lab"
echo "rc ${PIPESTATUS[0]}"
echo "path tools/claims-v3/e208/proposal/src/mms_common.py (s00b, $(TZ=America/Los_Angeles date '+%F %T %Z'))" >> "$L/work/lab-SNAPSHOT.txt"
sha256sum "$L/work/lab/tools/claims-v3/e208/proposal/src/reduce_mms.py" "$L/work/lab/tools/claims-v3/e208/proposal/src/mms_common.py"
