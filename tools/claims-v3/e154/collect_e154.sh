#!/usr/bin/env bash
# E154 (Q139): bring aifoundry3's E154 data and logs to the Intel's lab clone (run on the Intel; read-only on the box), then the desk steps with
# the registered code: Q139(k)'s C check on every C log (ccheck.py check, unchanged, --jobs 6) and the scorer (score_e154.py) on the measured
# pass. Heavy compute stays on the Intel (nice -n 10).
#   bash tools/claims-v3/e154/collect_e154.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3
PY=${PY:-/usr/bin/python3}
mkdir -p "$D/aifoundry3" "$D/logs" "$D/ccheck"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
for x in e154-smoke e154; do
  timeout 300 rsync -a -e "$SSH" --exclude 'telemetry.jsonl.raw' --exclude 'tiles/' aifoundry3:aifoundry/build/claims-v3/aifoundry3/$x/ "$D/aifoundry3/$x/" || echo "rsync $x rc=$?"
done
timeout 120 rsync -a -e "$SSH" aifoundry3:aifoundry/build/e154/ "$D/logs/" || echo "rsync logs rc=$?"
logs=()
for d in "$D"/aifoundry3/e154-smoke/p15401 "$D"/aifoundry3/e154/p15420; do
  [ -s "$d/c-log.jsonl" ] || continue
  cp "$d/c-log.jsonl" "$D/ccheck/c-log-$(basename "$d").jsonl"
  logs+=("$D/ccheck/c-log-$(basename "$d").jsonl")
done
if [ ${#logs[@]} -gt 0 ]; then
  nice -n 10 "$PY" tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$D/ccheck/ccheck-all.json" --jobs 6 > "$D/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$D/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
if [ -e "$D/aifoundry3/e154/p15420/marks.jsonl" ]; then
  nice -n 10 "$PY" tools/claims-v3/e154/score_e154.py "$D/aifoundry3/e154/p15420" --json "$D/scored.json" > /dev/null; echo "score rc=$?"
fi
du -sh "$D"
