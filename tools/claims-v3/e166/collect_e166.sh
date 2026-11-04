#!/usr/bin/env bash
# E166 (Q141(h)): bring aifoundry3's E166 data and logs to the Intel's lab clone (run on the Intel; read-only on the box), then the desk steps
# with the registered code: Q139(k)'s C check on every C log (ccheck.py check, unchanged, --jobs 2) and the scorer (score_e166.py) on the
# measured pass. E154's collect_e154.sh with E166's names; the data directory is an argument (the card day sets its date).
#   bash tools/claims-v3/e166/collect_e166.sh docs/reports/data/<YYYY-MM-DD>-e166-heat-replicate-aifoundry3
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: collect_e166.sh <data dir>}
PY=${PY:-/usr/bin/python3}
mkdir -p "$D/aifoundry3" "$D/logs" "$D/ccheck"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
for x in e166-smoke e166; do
  timeout 300 rsync -a -e "$SSH" --exclude 'telemetry.jsonl.raw' --exclude 'tiles/' aifoundry3:aifoundry/build/claims-v3/aifoundry3/$x/ "$D/aifoundry3/$x/" || echo "rsync $x rc=$?"
done
timeout 120 rsync -a -e "$SSH" aifoundry3:aifoundry/build/e166/ "$D/logs/" || echo "rsync logs rc=$?"
logs=()
for d in "$D"/aifoundry3/e166-smoke/p16601 "$D"/aifoundry3/e166/p16620; do
  [ -s "$d/c-log.jsonl" ] || continue
  cp "$d/c-log.jsonl" "$D/ccheck/c-log-$(basename "$d").jsonl"
  logs+=("$D/ccheck/c-log-$(basename "$d").jsonl")
done
if [ ${#logs[@]} -gt 0 ]; then
  nice -n 10 "$PY" tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$D/ccheck/ccheck-all.json" --jobs 2 > "$D/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$D/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
if [ -e "$D/aifoundry3/e166/p16620/marks.jsonl" ]; then
  nice -n 10 "$PY" tools/claims-v3/e166/score_e166.py "$D/aifoundry3/e166/p16620" --json "$D/scored.json" > /dev/null; echo "score rc=$?"
fi
du -sh "$D"
