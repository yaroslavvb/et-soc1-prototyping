#!/usr/bin/env bash
# E139's registered reduction (README § 4): E132's reducer and frozen constants UNCHANGED (tools/claims-v3/e132/reduce_e132.py and
# predictions.json, sha256 in predictions-e139.json), with --warmup 13910. Run from the lab repo root with any python3 that has numpy:
#   PY=python3 bash tools/claims-v3/e139/reduce_e139.sh <E139 data dir> [<E132 data dir>]
# Primary: E139's passes alone (p1391?), the board meter's dips removed (dp/posthoc_dips.py), leakage auto -> <D>/e139.json, runs.csv.
# Arms: leakage 0.2936 and 0.3803 W/C; unfiltered. Registered secondary: E132's headline passes (p13211-p13216) with E139's, dips
# removed, leakage auto -> <D>/e139-pooled.json. The smoke (p13901) and both warm-ups (13210 is not passed in; 13910 by --warmup) stay out.
set -eu
D=${1:?E139 data dir}; D132=${2:-docs/reports/data/2026-11-02-e132-memory-split}
PY=${PY:-python3}; WORK=${WORK:-build/e139-dipwork}; WORK132=${WORK132:-build/e139-dipwork-e132}
R=tools/claims-v3/e132/reduce_e132.py; P=tools/claims-v3/e132/predictions.json; G=$D132/gen; WU=${E139_WARMUP:-13910}
GLOB=${E139_GLOB:-p1391?}
$PY tools/claims-v3/dp/posthoc_dips.py "$D"/passes/$GLOB --work "$WORK" --out "$D/dips.json"
for leak in auto 0.2936 0.3803; do
  out=$D/e139.json; csv=$D/runs.csv
  [ "$leak" = auto ] || { out=$D/e139-leak$leak.json; csv=; }
  $PY $R "$WORK"/$GLOB --gen "$G" --pred $P --warmup "$WU" --leak "$leak" --out "$out" ${csv:+--csv "$csv"}
done
$PY $R "$D"/passes/$GLOB --gen "$G" --pred $P --warmup "$WU" --out "$D/e139-unfiltered.json"
$PY tools/claims-v3/dp/posthoc_dips.py "$D132"/passes/p1321[1-6] --work "$WORK132" --out "$D/dips-e132-pooled.json"
$PY $R "$WORK132"/p1321[1-6] "$WORK"/$GLOB --gen "$G" --pred $P --warmup "$WU" --out "$D/e139-pooled.json"
