#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# E141, post hoc after verification (Mon 2 Nov 2026, written after the data and after the verifier's read; never a verdict).
# E141's frozen reducer (tools/claims-v3/e141/reduce_e141.py: reduce_e78.py unchanged, E78's gates) run with the leakage slope
# fixed (--no-refit) at the footing of M7's 247 aifoundry3 float training rows, three ways of averaging their sessions' slopes
# (corrections-numbers.py, C1): 0.2104 W/C counted by rows (the verifier's value), 0.2163 weighted by each row's D, 0.2217
# weighted by D squared; each with the board meter's dips kept (as the registered primary and 154 of those rows) and removed
# (E82 A2's definition, as the other 93 rows: E121-E123 and E127). Over the same four committed passes the primary reduced; each
# reduction is scored ALONE by the frozen scorer (tools/claims-v3/e141/score_e141.py), as the dips-removed arm is. Desk compute
# on the committed raw passes, no device.
#
#   PY=<python with numpy> nice -n 10 bash docs/reports/data/2026-11-02-e141-blind5-aifoundry3/posthoc-after-verification/run_posthoc.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE/../../../../.." || exit 1
PY=${PY:-python3}
DD=docs/reports/data/2026-11-02-e141-blind5-aifoundry3
E=tools/claims-v3/e141
P=( $DD/aifoundry3/e141/p14110 $DD/aifoundry3/e141/p14111 $DD/aifoundry3/e141/p14112 $DD/aifoundry3/e141/p14113 )
for k in 0.2104 0.2163 0.2217; do
  for dips in kept removed; do
    if [ "$dips" = kept ]; then tag=leak$k; flag=(); else tag=nodips-leak$k; flag=(--drop-dips); fi
    "$PY" -B $E/reduce_e141.py "${P[@]}" ${flag[@]+"${flag[@]}"} --leak $k --no-refit --out "$HERE/e141-$tag.json" --csv "$HERE/runs-$tag.csv" \
      --txt "$HERE/reduce-$tag.txt" > "$HERE/reduce-$tag.log" 2>&1; echo "reduce $tag rc=$?"
    "$PY" -B $E/score_e141.py --e141 "$HERE/e141-$tag.json" --runs "$HERE/runs-$tag.csv" --json "$HERE/scored-$tag.json" \
      --md "$HERE/results-$tag.md" > "$HERE/score-$tag.log" 2>&1; echo "score $tag rc=$?"
    paste -sd' ' "$HERE/score-$tag.log"
  done
done
