#!/usr/bin/env bash
# E184 (Q155), kit note 3 (KIT.md.dated-note-3.md section 2): collect_e184_v2.sh (v2, which stays as committed) with dated amendment A4's
# reducer and nothing else changed: each arm present is reduced by reduce_e184_v4.py (v2's reduction; A3-3's session gate with A4: a config
# read lacking tdp_w, temp_threshold_c or minion_mhz, or holding a null among them, is MISSING and replaced by runbook step 7's read; a
# complete read not as registered is MOVED; each edge checked on its own) into reduced-e184{s,b}-v4.json, and scored by score_e184_v3.py
# (unchanged). Each arm's T0 is kept in <out>/t0-<arm>.txt, as in v2. The runbook's step 11 v3 (rb/s22_collect_e184_v3.sh) runs it on the
# Intel. It reads no card and commits nothing.
#
#   E184_DATE=<YYYY-MM-DD> [E184_T0_S=<epoch>] [E184_T0_B=<epoch>] [PY=/usr/bin/python3] bash tools/claims-v3/e184/collect_e184_v3.sh <raw dir>
#   <raw dir>/<card>/{e184,e184-smoke,e184-stoptest}/p184NN/ and <raw dir>/<card>/logs/ (card: aifoundry3, aifoundry1-c1)
#   -> build/e184-out/<day>-e184-sensor-validation/{raw/<card>/..., reduced-e184s-v4.json, reduced-e184b-v4.json, scored-e184-v3.json, .md}
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
RAW=${1:?usage: collect_e184_v3.sh <raw dir>}
DAY=${E184_DATE:?E184_DATE - the card day, YYYY-MM-DD}
PY=${PY:-/usr/bin/python3}
OUT=build/e184-out/$DAY-e184-sensor-validation
mkdir -p "$OUT/raw"
args=()
for card in aifoundry3 aifoundry1-c1; do
  [ -d "$RAW/$card" ] || continue
  rsync -a --exclude '*.raw' --exclude images "$RAW/$card" "$OUT/raw/"
  if [ "$card" = aifoundry3 ]; then arm=S; lc=s; t0=${E184_T0_S:-}; else arm=B; lc=b; t0=${E184_T0_B:-}; fi
  # v2's rule (the verifier's nit (e) of kit note 1): an arm collected with its T0 keeps that T0 in the output, so collecting the other arm
  # later re-reduces this one with its own T0, not with the newest real log
  if [ -n "$t0" ]; then echo "$t0" > "$OUT/t0-$arm.txt"; else t0=$(cat "$OUT/t0-$arm.txt" 2>/dev/null); fi
  if [ -n "$t0" ]; then
    "$PY" -B tools/claims-v3/e184/reduce_e184_v4.py "$OUT/raw" --arm "$arm" --t0 "$t0" > "$OUT/reduced-e184$lc-v4.json" || { echo "reduce_e184_v4 $arm failed"; exit 1; }
  else
    "$PY" -B tools/claims-v3/e184/reduce_e184_v4.py "$OUT/raw" --arm "$arm" > "$OUT/reduced-e184$lc-v4.json" || { echo "reduce_e184_v4 $arm failed"; exit 1; }
  fi
  args+=(--$lc "$OUT/reduced-e184$lc-v4.json")
done
[ ${#args[@]} -gt 0 ] || { echo "no arm's raw copy under $RAW"; exit 1; }
"$PY" -B tools/claims-v3/e184/score_e184_v3.py "${args[@]}" --out "$OUT" > /dev/null || { echo "score_e184_v3 failed"; exit 1; }
[ -s "$OUT/scored-e184-v3.md" ] && echo "scored-e184-v3.md written: $OUT (reduce_e184_v4.py, A4)"
