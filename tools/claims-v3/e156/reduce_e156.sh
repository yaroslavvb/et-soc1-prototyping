#!/usr/bin/env bash
# E156's registered reduction (README "Rules"): run from the lab repo root with any python3 that has numpy:
#   PY=python3 bash tools/claims-v3/e156/reduce_e156.sh <E156 data dir>
# Primary: E156's passes p15610-p15619 (15610 the registered warm-up, never in the headline), the board meter's dips removed (dp/posthoc_dips.py,
# E82 A2's rule, as E139's primary), leakage auto (E139's), -> <D>/e156.json, runs.csv. Arms (reported): leakage 0.2936 and 0.3803 W/C (E139's arms),
# 0.3134 W/C (Q139(u)'s frozen idle slope for this card, footing.json), and the dips kept. The smoke (p15601) and the stop test (p15602) stay out.
set -eu
D=${1:?E156 data dir}
PY=${PY:-python3}; WORK=${WORK:-build/e156-dipwork}
R=tools/claims-v3/e156/reduce_e156.py; P=tools/claims-v3/e156/predictions-e156.json; G=$D/gen; WU=15610
GLOB=${E156_GLOB:-p1561[0-9]}
$PY tools/claims-v3/dp/posthoc_dips.py "$D"/passes/$GLOB --work "$WORK" --out "$D/dips.json"
for leak in auto 0.2936 0.3803 0.3134; do
  out=$D/e156.json; csv=$D/runs.csv
  [ "$leak" = auto ] || { out=$D/e156-leak$leak.json; csv=; }
  $PY $R "$WORK"/$GLOB --gen "$G" --pred $P --warmup "$WU" --leak "$leak" --out "$out" ${csv:+--csv "$csv"}
done
$PY $R "$D"/passes/$GLOB --gen "$G" --pred $P --warmup "$WU" --out "$D/e156-unfiltered.json"
