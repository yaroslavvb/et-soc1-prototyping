#!/usr/bin/env bash
# E184 (Q153), kit note 1 (KIT.md.dated-note-1.md section 2): the desk collection of an arm's session copied back from its box (the runbook's
# step 11, rb/s22_collect_e184.sh, runs it), on the Intel. It copies the raw tree into the day's output, reduces each arm present with
# reduce_e184_v2.py (the pass gate, the session gate for the arm's T0, A2-5's refresh rule) and scores whatever is reduced with score_e184_v2.py
# (A2's readings, no rule of an arm whose session gate fails). It reads no card and commits nothing.
#
#   E184_DATE=<YYYY-MM-DD> [E184_T0_S=<epoch>] [E184_T0_B=<epoch>] [PY=/usr/bin/python3] bash tools/claims-v3/e184/collect_e184.sh <raw dir>
#   <raw dir>/<card>/{e184,e184-smoke,e184-stoptest}/p184NN/ and <raw dir>/<card>/logs/ (card: aifoundry3, aifoundry1-c1)
#   -> build/e184-out/<day>-e184-sensor-validation/{raw/<card>/..., reduced-e184s-v2.json, reduced-e184b-v2.json, scored-e184-v2.json, .md}
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
RAW=${1:?usage: collect_e184.sh <raw dir>}
DAY=${E184_DATE:?E184_DATE - the card day, YYYY-MM-DD}
PY=${PY:-/usr/bin/python3}
OUT=build/e184-out/$DAY-e184-sensor-validation
mkdir -p "$OUT/raw"
args=()
for card in aifoundry3 aifoundry1-c1; do
  [ -d "$RAW/$card" ] || continue
  rsync -a --exclude '*.raw' --exclude images "$RAW/$card" "$OUT/raw/"
  if [ "$card" = aifoundry3 ]; then arm=S; lc=s; t0=${E184_T0_S:-}; else arm=B; lc=b; t0=${E184_T0_B:-}; fi
  if [ -n "$t0" ]; then
    "$PY" -B tools/claims-v3/e184/reduce_e184_v2.py "$OUT/raw" --arm "$arm" --t0 "$t0" > "$OUT/reduced-e184$lc-v2.json" || { echo "reduce_e184_v2 $arm failed"; exit 1; }
  else
    "$PY" -B tools/claims-v3/e184/reduce_e184_v2.py "$OUT/raw" --arm "$arm" > "$OUT/reduced-e184$lc-v2.json" || { echo "reduce_e184_v2 $arm failed"; exit 1; }
  fi
  args+=(--$lc "$OUT/reduced-e184$lc-v2.json")
done
[ ${#args[@]} -gt 0 ] || { echo "no arm's raw copy under $RAW"; exit 1; }
"$PY" -B tools/claims-v3/e184/score_e184_v2.py "${args[@]}" --out "$OUT" > /dev/null || { echo "score_e184_v2 failed"; exit 1; }
[ -s "$OUT/scored-e184-v2.md" ] && echo "scored-e184-v2.md written: $OUT"
