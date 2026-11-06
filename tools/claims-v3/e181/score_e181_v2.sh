#!/usr/bin/env bash
# E181 (M11's session 2): the score v2, tools/claims-v3/e181/score_e181.sh (33cdccf6, which stays as committed) with M11's scorer v4 in v3's
# place (tools/claims-v3/m11/score_m11_v4.py; the kit's README.md.dated-note-1.md): v3's readings unchanged; nothing written before the
# start_gate marks are read, and the lines file staged and renamed only after the whole score succeeds (the kit verifier's fault 4); A9's
# reported arm on E181's measured pass with its smoke pass named (p18101: the chain over both passes, M11's amendment A9, cd5bed77); A6-5's
# host windows read from the collected logs/ (host-start.out, host-end.out: step 12's); A6-3's pattern edge flagged. E176's committed pass is
# named first, as v1 named it (its refused G0 excludes it with its own reason; the arm is not read there). Step 22 v2
# (rb/s22_collect_e181_v2.sh) runs it only after every gate. It writes scored-m11.json, scored-m11.md and scored-m11-lines.jsonl into the data
# directory and prints "score rc=<rc>".
#   bash tools/claims-v3/e181/score_e181_v2.sh docs/reports/data/<YYYY-MM-DD>-e181-m11-session2-aifoundry3
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: score_e181_v2.sh <data dir>}
PY=${PY:-/usr/bin/python3}
E176=${E181_EARLIER_PASS:-docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176/p17620}
[ -e "$D/aifoundry3/e181/p18120/marks.jsonl" ] || { echo "no measured pass marks: nothing to score"; echo "score rc=3"; exit 0; }
SM=()
[ -d "$D/aifoundry3/e181-smoke/p18101" ] && SM=(--smoke "$D/aifoundry3/e181-smoke/p18101")
nice -n 10 "$PY" -B tools/claims-v3/m11/score_m11_v4.py score --a3 "$E176" --a3 "$D/aifoundry3/e181/p18120" ${SM[@]+"${SM[@]}"} --host "$D/logs" \
  --lines "$D/scored-m11-lines.jsonl" --json "$D/scored-m11.json" --md "$D/scored-m11.md" > /dev/null; echo "score rc=$?"
