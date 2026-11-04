#!/usr/bin/env bash
# E157: the registered scorer, exactly as collect_e157.sh step 5 runs it, now with E153's committed primary reduction of pool 6 (X1, X2, S1, S2),
# run from the committed data directory (it writes build/e157-x/; this lane copied scored-e153.json, results-e153.md and score-e153.log beside it).
#   bash docs/reports/data/2026-11-03-e157-blind6-card1/posthoc/score_with_e153.sh [<E153's C-excluded tiles, comma-joined>]
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." || exit 1     # the repository root
D=docs/reports/data/2026-11-03-e157-blind6-card1
E153=docs/reports/data/2026-11-03-e153-blind6-aifoundry3/e153.json
DROP=${1:-}
git log -1 --format='%h %ci' -- "$E153" || exit 2
mkdir -p build/e157-x
gzip -dc $D/ccheck/ccheck-session.json.gz > build/e157-x/ccheck-session.json
RJ=()
for p in $D/aifoundry1-c1/e157/p157* $D/aifoundry1-c1/e157-smoke-p15701; do [ -s "$p/runs.jsonl" ] && RJ+=(--runs-jsonl "$p/runs.jsonl"); done
ARMS=(--arm "e142_footing=$D/e157-e142footing.json" --arm "session_own_slope=$D/e157-auto.json" --arm "dips_kept=$D/e157-dipskept.json"
      --arm "leak0.2955=$D/e157-leak0.2955.json" --arm "leak0.3320=$D/e157-leak0.3320.json" --arm "relaxed=$D/e157-relaxed.json")
python3 tools/claims-v3/e157/score_e157.py --e157 $D/e157.json --k1-e142 $D/e157-e142footing.json --runs $D/runs.csv "${ARMS[@]}" \
  --ccheck build/e157-x/ccheck-session.json "${RJ[@]}" --e153 "$E153" --e153-drop "$DROP" \
  --json build/e157-x/scored-e153.json --md build/e157-x/results-e153.md > build/e157-x/score-e153.log 2>&1; echo "rc=$?"
cat build/e157-x/score-e153.log
