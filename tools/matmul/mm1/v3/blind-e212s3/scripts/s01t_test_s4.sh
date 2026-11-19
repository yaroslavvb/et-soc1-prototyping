#!/bin/bash
# blind-v3-e212s3 step 1 (desk test, before any S3 datum): the declared scorer s03_score.py run on E212 a2c0-S4 (MM1-v3's vendored copy of
# the committed data-e212-a2c0-S4.json, sha256 2e2ed24e...), which must reproduce MM1-v3's README section 5 and postcheck_twins.json's S4 split.
# THE CPU RULE: inside slot.sh, single-threaded, waiting while the 1-minute load is above 6.
set -u
W=<W>
L=$W/out/blind-v3-e212s3
V3=$L/work/lab-b149/tools/matmul/mm1/v3
ts() { TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'; }
end=$(( $(date +%s) + 480 ))
while :; do
  l1=$(cut -d' ' -f1 /proc/loadavg)
  if awk -v l="$l1" 'BEGIN{exit !(l <= 6.0)}'; then break; fi
  [ "$(date +%s)" -ge "$end" ] && { echo "load still $l1 at $(ts): not run"; exit 3; }
  sleep 20
done
echo "load $l1 at $(ts); scorer sha256 $(sha256sum "$L/scripts/s03_score.py" | cut -d' ' -f1)"
mkdir -p "$L/work/test-s4"
bash "$W/slot.sh" env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  /usr/bin/python3 -I -B "$L/scripts/s03_score.py" --v3 "$V3" --data "$V3/inputs/e212-unread/a2c0-S4__data-e212-a2c0-S4.json" \
  --session a2c0-S4 --label TEST-S4 --out "$L/work/test-s4"
echo "rc $? at $(ts)"
