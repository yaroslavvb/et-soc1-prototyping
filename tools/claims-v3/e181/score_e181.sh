#!/usr/bin/env bash
# E181 (M11's session 2): the score, run by step 22 (rb/s22_collect_e181.sh) only AFTER its gates (the check of C finished, every launch the
# marks record checked, the login scrub and the desk-path gate). M11's scorer v3 (tools/claims-v3/m11/score_m11_v3.py: v2 unchanged, plus
# A6-A8's precedence, the start gate read whole, and FL5(c) in both coordinates, reported) on the measured pass, with E176's committed pass
# named first as the earlier M11 aifoundry3 session (REGISTRATION.md section 3: HM-LG, HM-CAL, HM-CAL-I8 and A5's readings read a card
# kind's sessions together; E176's refused G0 excludes it with its own reason). It writes scored-m11.json, scored-m11.md and the lines file
# scored-m11-lines.jsonl into the data directory and prints "score rc=<rc>".
#   bash tools/claims-v3/e181/score_e181.sh docs/reports/data/<YYYY-MM-DD>-e181-m11-session2-aifoundry3
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: score_e181.sh <data dir>}
PY=${PY:-/usr/bin/python3}
E176=${E181_EARLIER_PASS:-docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176/p17620}
[ -e "$D/aifoundry3/e181/p18120/marks.jsonl" ] || { echo "no measured pass marks: nothing to score"; echo "score rc=3"; exit 0; }
nice -n 10 "$PY" -B tools/claims-v3/m11/score_m11_v3.py score --a3 "$E176" --a3 "$D/aifoundry3/e181/p18120" \
  --lines "$D/scored-m11-lines.jsonl" --json "$D/scored-m11.json" --md "$D/scored-m11.md" > /dev/null; echo "score rc=$?"
