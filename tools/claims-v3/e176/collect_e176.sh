#!/usr/bin/env bash
# E176 (Q143(k)): bring aifoundry3's E176 data and logs to the Intel's lab clone (run on the Intel; read-only on the box), then the desk steps
# with the registered code: Q139(k)'s C check on every C log (ccheck.py check, unchanged, --jobs 2) and M11's scorer
# (tools/claims-v3/m11/score_m11.py score) on the measured pass, with every earlier M11 aifoundry3 session named after the data directory
# (REGISTRATION.md section 3: HM-LG and HM-CAL read a card kind's M11 sessions together). E166's collect_e166.sh (c75bc460) with E176's
# names and two changes: (1) the data directory's ccheck/ is emptied first, so a check of C from an earlier try is never read as this one's
# (v3.1's note on collect_e166.sh); (2) the scorer is M11's, writing scored-m11.json and scored-m11.md.
#   bash tools/claims-v3/e176/collect_e176.sh docs/reports/data/<YYYY-MM-DD>-e176-m11-holds-aifoundry3 [<an earlier M11 pass dir> ...]
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: collect_e176.sh <data dir> [<an earlier M11 aifoundry3 pass dir> ...]}
shift
PY=${PY:-/usr/bin/python3}
mkdir -p "$D/aifoundry3" "$D/logs" "$D/ccheck"
find "$D/ccheck" -mindepth 1 -maxdepth 1 -type f -delete
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
for x in e176-smoke e176; do
  timeout 300 rsync -a -e "$SSH" --exclude 'telemetry.jsonl.raw' --exclude 'tiles/' aifoundry3:aifoundry/build/claims-v3/aifoundry3/$x/ "$D/aifoundry3/$x/" || echo "rsync $x rc=$?"
done
timeout 120 rsync -a -e "$SSH" aifoundry3:aifoundry/build/e176/ "$D/logs/" || echo "rsync logs rc=$?"
logs=()
for d in "$D"/aifoundry3/e176-smoke/p17601 "$D"/aifoundry3/e176/p17620; do
  [ -s "$d/c-log.jsonl" ] || continue
  cp "$d/c-log.jsonl" "$D/ccheck/c-log-$(basename "$d").jsonl"
  logs+=("$D/ccheck/c-log-$(basename "$d").jsonl")
done
if [ ${#logs[@]} -gt 0 ]; then
  nice -n 10 "$PY" tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$D/ccheck/ccheck-all.json" --jobs 2 > "$D/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$D/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
if [ -e "$D/aifoundry3/e176/p17620/marks.jsonl" ]; then
  earlier=()
  for p in "$@"; do earlier+=(--a3 "$p"); done
  nice -n 10 "$PY" -B tools/claims-v3/m11/score_m11.py score ${earlier[@]+"${earlier[@]}"} --a3 "$D/aifoundry3/e176/p17620" \
    --json "$D/scored-m11.json" --md "$D/scored-m11.md" > /dev/null; echo "score rc=$?"
fi
du -sh "$D"
