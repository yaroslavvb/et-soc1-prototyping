#!/usr/bin/env bash
# E185 (M11's session 3): the score, run by step 22 (rb/s22_collect_e185.sh) only after every gate. M11's scorer v5
# (tools/claims-v3/m11/score_m11_v5.py): M11's registered readings on A10's reading (the chain over the smoke and the measured pass) for every
# aifoundry3 session it is given, with E176's and E181's committed passes named first (E176's refused G0 excludes it; E181 is read with its
# committed smoke pass, as A10-3 says the pooled readings read it), and E185.md section 6's rules on E185's pass. It writes scored-m11.json,
# scored-m11.md and scored-m11-lines.jsonl into the data directory and prints "score rc=<rc>".
#   bash tools/claims-v3/e185/score_e185.sh docs/reports/data/<YYYY-MM-DD>-e185-m11-session3-aifoundry3
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: score_e185.sh <data dir>}
PY=${PY:-/usr/bin/python3}
E176=${E185_E176_PASS:-docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176/p17620}
E181D=docs/reports/data/2026-11-06-e181-m11-session2-aifoundry3/aifoundry3
[ -e "$D/aifoundry3/e185/p18520/marks.jsonl" ] || { echo "no measured pass marks: nothing to score"; echo "score rc=3"; exit 0; }
SM=()
[ -d "$D/aifoundry3/e185-smoke/p18501" ] && SM=(--smoke "$D/aifoundry3/e185-smoke/p18501")
nice -n 10 "$PY" -B tools/claims-v3/m11/score_m11_v5.py score --a3 "$E176" --a3 "$E181D/e181/p18120" --smoke "$E181D/e181-smoke/p18101" \
  --a3 "$D/aifoundry3/e185/p18520" ${SM[@]+"${SM[@]}"} --host "$D/logs" --e185 "$D/aifoundry3/e185/p18520" \
  --lines "$D/scored-m11-lines.jsonl" --json "$D/scored-m11.json" --md "$D/scored-m11.md" > /dev/null; echo "score rc=$?"
