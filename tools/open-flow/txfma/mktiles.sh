#!/bin/bash
# Q126(e): every operand file the gate-level bench runs, with the exact flags they were made
# with. Without this the flow is not reproducible from the repo: the seed, the --iters-before
# warm-up and the --from-bin step all change the stimulus, and so every energy number.
#
#   SCRATCH=$HOME/scratch-q126-e LAB=<et-soc1-prototyping checkout> bash mktiles.sh
#
# Writes $SCRATCH/work/tiles/<pattern>.hex  (768 hex words: A, B, and the C the accumulators
# hold after --iters-before ops), and $SCRATCH/work/hl/ (V3-HL's own tiles and manifest).
set -u
S=${SCRATCH:?set SCRATCH}
L=${LAB:-$S/et-soc1-prototyping}
W=$S/work
PY=${PY:-python3}
ITERS=${ITERS:-1000}      # the accumulator state the measured op starts from
SEED=${SEED:-1}           # the 21 Sep random tile's seed; do not change it without saying so
mkdir -p "$W/tiles" "$W/hl"

# 1. The built-in value patterns of 21 Sep (sparsity_host --values): the random tile every
#    toggle count in this project is quoted against, and the two anchors.
for p in randn ones zeros; do
  [ -s "$W/tiles/$p.hex" ] && { echo "have $p"; continue; }
  ( cd "$L" && $PY -I rtl-sim/fma_toggle/tiles.py "$p" "$W/tiles/$p.hex" \
      --seed "$SEED" --iters-before "$ITERS" ) && echo "ok $p"
done

# 2. The Hamming ladder (V3-HL, the operand files E60 ran on the cards): tiles/ and manifest.json.
#    lq_* hold the partner quiet (A = 1.0), lb_* busy (A = pi); h is the designed number of
#    B-mantissa bits that flip from one multiply-add to the next.
[ -s "$W/hl/manifest.json" ] || ( cd "$L" && $PY -I tools/claims-v3/hl/make_hl.py "$W/hl" >/dev/null ) \
  && echo "ok hl ($(ls "$W/hl/tiles" | wc -l) items)"

# 3. The ladder rungs the bench actually runs, converted from V3-HL's raw 2 x 1024-byte tiles.
#    The pattern argument is ignored when --from-bin is given; it still has to be a valid name.
for p in ${RUNGS:-lq_h0 lq_h1 lq_h2 lq_h4 lq_h8 lb_h0 lb_h1 lb_h2 lb_h4 lb_h8}; do
  [ -s "$W/tiles/$p.hex" ] && { echo "have $p"; continue; }
  [ -s "$W/hl/tiles/$p.bin" ] || { echo "no $p.bin"; continue; }
  ( cd "$L" && $PY -I rtl-sim/fma_toggle/tiles.py randn "$W/tiles/$p.hex" \
      --from-bin "$W/hl/tiles/$p.bin" --iters-before "$ITERS" ) && echo "ok $p"
done

ls -la "$W/tiles" | tail -n +2
