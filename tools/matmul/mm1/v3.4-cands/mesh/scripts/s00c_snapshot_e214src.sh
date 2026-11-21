#!/bin/bash
# mask-mesh s00c: E214's registered source (arms.json and its tiles), which MM1-v3.2's energy code opens at import (energy_v32.py: E214SRC),
# into the read-only snapshot at the same commit cfd7e641; needed by compose_af4.py (MM1-v3.2's energy side), not by the time fit.
set -u
W=<W>
LAB=<LAB>
L=$W/out/mask-mesh
C=cfd7e6415d0da2af17c8078ea68a7bac8acd5c5b
/usr/bin/flock -w 600 "$W/locks/lab-git.lock" git -C "$LAB" archive --format=tar "$C" tools/claims-v3/e214/proposal/src | tar -x -C "$L/work/lab"
echo "rc ${PIPESTATUS[0]}"
echo "path tools/claims-v3/e214/proposal/src (s00c, $(TZ=America/Los_Angeles date '+%F %T %Z'))" >> "$L/work/lab-SNAPSHOT.txt"
du -sh "$L/work/lab/tools/claims-v3/e214/proposal/src"
