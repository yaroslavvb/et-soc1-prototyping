#!/usr/bin/env bash
# E73: reduce and analyse one run directory, ON aifoundry2 (the raw frames are ~2 GB and stay there).
#   bash reduce_e73.sh <rundir>
set -u
RUN=${1:?usage: reduce_e73.sh <rundir>}
CODE="$HOME/claude/et-soc1-prototyping/build/e73/code"
cd "$CODE" || exit 1
RED="$RUN-RED"; ANA="$RUN-ANA"
echo "== reduce =="; python3 reduce_hm.py "$RUN" --out "$RED" || exit 1
echo "== fpa =="; python3 fpa_trace.py "$RUN" --out "$RED/fpa.npz" || exit 1
echo "== lockin =="
python3 lockin_hlf.py "$RED" --protocol protocol-e73.json --template prereg/e62_bloom_dt.npy \
    --scene-ref prereg/e62_scene.npy --fpa "$RED/fpa.npz" --out "$ANA" || exit 1
echo "== fit =="
python3 fit_hlf.py "$ANA/lockin.json" --protocol protocol-e73.json --predictions predictions.json \
    --out "$ANA/fit.json" --md "$ANA/fit.txt" || exit 1
if [ -f dips_hlc.py ]; then
  echo "== dips =="; python3 dips_hlc.py "$RED" --out "$ANA/dips.json" 2>&1 | tail -5
fi
echo "done: $ANA"
