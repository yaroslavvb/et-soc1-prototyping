#!/usr/bin/env bash
# E176 (Q143(k)), the collector v2 (Q143(k)'s fix pass, Thu 5 Nov 2026, before any E176 data): collect_e176.sh (lab 03582d2f, which stays as
# committed) with two changes, nothing else:
#   (1) the scorer is M11's v2, tools/claims-v3/m11/score_m11_v2.py score (lab ebdbb35c), which imports score_m11.py unchanged and adds A5's
#       readings (lab 9b084c66), A4-3's two NOT SCORED reasons and the lines written first: it writes scored-m11.json, scored-m11.md and the
#       lines file scored-m11-lines.jsonl;
#   (2) each pass whose C log is absent or empty is named ("c-log <pass>: absent or empty"), so the step's gate can be read beside it.
#       The C-log requirement and the count of checked launches against the marks are the gate's (../q143k-runbook/cclaunch_q143k.py, run
#       by step 22 v2, s22_collect_q143k_v2.sh): this collector, like v1, checks every C log it finds and goes on.
# Everything else is v1's, line for line: bring aifoundry3's E176 data and logs to the Intel's lab clone (read-only on the box; rsync bounded
# at 300 / 120 s), empty the data directory's ccheck/ first, Q139(k)'s C check on every C log (ccheck.py check, unchanged, --jobs 2), then
# the scorer on the measured pass with every earlier M11 aifoundry3 session named after the data directory (REGISTRATION.md section 3).
#   bash tools/claims-v3/e176/collect_e176_v2.sh docs/reports/data/<YYYY-MM-DD>-e176-m11-holds-aifoundry3 [<an earlier M11 pass dir> ...]
# Run it from step 22 v2, never alone: the step reads the scorer's rc, the check's end, the C logs' requirement and the counts.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: collect_e176_v2.sh <data dir> [<an earlier M11 aifoundry3 pass dir> ...]}
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
  if [ ! -s "$d/c-log.jsonl" ]; then echo "c-log $(basename "$d"): absent or empty (step 22 v2's gate reads whether this pass must carry one)"; continue; fi
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
  nice -n 10 "$PY" -B tools/claims-v3/m11/score_m11_v2.py score ${earlier[@]+"${earlier[@]}"} --a3 "$D/aifoundry3/e176/p17620" \
    --lines "$D/scored-m11-lines.jsonl" --json "$D/scored-m11.json" --md "$D/scored-m11.md" > /dev/null; echo "score rc=$?"
fi
du -sh "$D"
