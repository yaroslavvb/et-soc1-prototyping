#!/bin/bash
# blind-v3-e212s3: desk test of s02_order.py on the committed E212 a2c0-S4 folder (its own time records), before any S3 datum.
set -u
W=<W>
L=$W/out/blind-v3-e212s3
LAB=<LAB>
H=$(git -C "$LAB" rev-parse HEAD)
T=$L/work/test-order
if [ -e "$T" ]; then echo "test dir exists: stop"; exit 4; fi
mkdir -p "$T"
git -C "$LAB" archive --format=tar "$H" docs/reports/data/2026-11-17-e212-mmsweep2-a2c0-S4 | tar -x -C "$T"
/usr/bin/python3 -I -B "$L/scripts/s02_order.py" --folder "$T/docs/reports/data/2026-11-17-e212-mmsweep2-a2c0-S4" --lab "$LAB" --main "$H" \
  --declared '2026-11-17 15:00:00' --out "$T/order-s4.json"
echo "rc $?"
