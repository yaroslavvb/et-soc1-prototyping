#!/usr/bin/env bash
# E181 (M11's session 2): the collector, tools/claims-v3/e176/collect_e176_v2.sh (6b013ad9, which stays as committed) with E181's names and
# ONE change: it never runs the scorer (E176's runbook note 2, section 3, the code verifier's fault 2: "the scorer writes before the gates").
# It brings aifoundry3's E181 data and logs to the Intel's lab clone (read-only on the box; rsync bounded at 300 / 120 s), empties the data
# directory's ccheck/ first, runs Q139(k)'s C check on every C log (ccheck.py check, unchanged, --jobs 2) and names each pass whose C log is
# absent or empty. Step 22 (rb/s22_collect_e181.sh) then runs the gates (the check finished, every launch the marks record checked, the
# login scrub, the desk-path gate) and only after them the scorer (score_e181.sh), so nothing scored is written before the gates.
#   bash tools/claims-v3/e181/collect_e181.sh docs/reports/data/<YYYY-MM-DD>-e181-m11-session2-aifoundry3
# Run it from step 22, never alone.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: collect_e181.sh <data dir>}
PY=${PY:-/usr/bin/python3}
mkdir -p "$D/aifoundry3" "$D/logs" "$D/ccheck"
find "$D/ccheck" -mindepth 1 -maxdepth 1 -type f -delete
for f in scored-m11.json scored-m11.md scored-m11-lines.jsonl; do [ -e "$D/$f" ] && { echo "refusing: $D/$f exists before the gates (remove the data directory first)"; exit 3; }; done
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
for x in e181-smoke e181; do
  timeout 300 rsync -a -e "$SSH" --exclude 'telemetry.jsonl.raw' --exclude 'tiles/' aifoundry3:aifoundry/build/claims-v3/aifoundry3/$x/ "$D/aifoundry3/$x/" || echo "rsync $x rc=$?"
done
timeout 120 rsync -a -e "$SSH" aifoundry3:aifoundry/build/e181/ "$D/logs/" || echo "rsync logs rc=$?"
logs=()
for d in "$D"/aifoundry3/e181-smoke/p18101 "$D"/aifoundry3/e181/p18120; do
  if [ ! -s "$d/c-log.jsonl" ]; then echo "c-log $(basename "$d"): absent or empty (step 22's launch gate reads whether this pass must carry one)"; continue; fi
  cp "$d/c-log.jsonl" "$D/ccheck/c-log-$(basename "$d").jsonl"
  logs+=("$D/ccheck/c-log-$(basename "$d").jsonl")
done
if [ ${#logs[@]} -gt 0 ]; then
  nice -n 10 "$PY" tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$D/ccheck/ccheck-all.json" --jobs 2 > "$D/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$D/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
echo "collected (no score: step 22 scores after its gates)"
du -sh "$D"
