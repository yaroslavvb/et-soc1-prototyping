#!/usr/bin/env bash
# E170 box step 8, AT THE DESK on the Intel, after `box/step_e170.sh pull` has copied aifoundry1:nekko/build/e170/ into <raw> (bounded, through
# Q141(k)'s runner). It never reaches a box. At nice 10 with at most 2 jobs (section 28 of the round's brief: it needs this Mac's tree):
#   1. the harness at the desk is the committed one (check_e170.py --desk);
#   2. Q139(k)'s check of C on every session with a C log (stoptest-board, smoke, s1...), ccheck.py check --jobs 2;
#   3. the runs and the queue's logs into docs/reports/data/<E170_DATE>-e170-blind7-card0/ (aifoundry1-c0/, logs/), the ccheck outputs beside;
#   4. no other login enters the public repo: E164's scrubber (scrub_etwho_e164.py, generic over a directory) on the data directory with the owner's
#      login, then its --check, which must read OK (else exit 7 and nothing may be committed);
#   5. the telemetry, launches and C logs gzipped (as E160's and E165's);
#   6. the registered score, score_e170_a1.py (amendment A1 over score_e170.py), into results.json, results.md and score.txt. It prints
#      "results.md written" only when the scorer exited 0 and wrote it; any other ending is a non-zero exit.
#
#   E170_DATE=2026-11-04 bash tools/claims-v3/e170/collect_e170.sh build/e170-raw
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 1
RAW=${1:?usage: collect_e170.sh <the pulled copy, e.g. build/e170-raw>}
DAY=${E170_DATE:-2026-11-04}
D=docs/reports/data/$DAY-e170-blind7-card0
PY=${PY:-python3}
OWNER=${E170_OWNER:-yaroslavvb}
[ -d "$RAW/runs" ] || { echo "refused: no $RAW/runs (run box/step_e170.sh pull first)"; exit 2; }
[ -e "$D/aifoundry1-c0" ] && { echo "refused: $D/aifoundry1-c0 exists"; exit 2; }
$PY -B tools/claims-v3/e170/check_e170.py --desk | tail -1
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "refused: the desk tree is not E170's committed harness: nothing collected"; exit 6; }
mkdir -p "$D/aifoundry1-c0" "$D/logs" "$RAW/cc" || exit 2
for s in stoptest-board smoke s1 s2 s3 s4 s5 s6; do          # stoptest-die stops before any launch: no C log
  [ -f "$RAW/runs/$s/c-log.jsonl" ] || continue
  nice -n 10 $PY -B tools/claims-v3/ccheck/ccheck.py check "$RAW/runs/$s/c-log.jsonl" --out "$RAW/cc/ccheck-$s.json" --jobs 2 \
    > "$RAW/cc/ccheck-$s.txt" 2>&1 || echo "warning: ccheck of $s exited $?: read $RAW/cc/ccheck-$s.txt"
done
rsync -a "$RAW/runs/" "$D/aifoundry1-c0/" || exit 3
for f in queue.out slot.txt holders-at-launch.txt e170-preflight.txt; do [ -f "$RAW/$f" ] && cp "$RAW/$f" "$D/logs/"; done
cp "$RAW/cc/"ccheck-*.json "$D/" 2>/dev/null
$PY -B tools/claims-v3/e164/scrub_etwho_e164.py "$D" --owner "$OWNER" > "$D/logs/scrub.txt" 2>&1 || { echo "stopped: the scrub failed: nothing may be committed"; exit 7; }
$PY -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$D" --owner "$OWNER" >> "$D/logs/scrub.txt" 2>&1 \
  || { echo "stopped: the scrub's check is not OK (another login is left): nothing may be committed"; exit 7; }
find "$D/aifoundry1-c0" -path '*/tel/*.jsonl' -type f -exec gzip -n {} +
find "$D/aifoundry1-c0" \( -name launches.jsonl -o -name c-log.jsonl \) -type f -exec gzip -n {} +
SESS=$(for s in "$D"/aifoundry1-c0/s[0-9]*; do [ -f "$s/session.json" ] && printf '%s\n' "$s"; done)
[ -n "$SESS" ] || { echo "stopped: no session under $D/aifoundry1-c0 (the queue ended before s1: read $D/aifoundry1-c0/queue.jsonl and QUEUE-HALT): collected, not scored"; exit 4; }
CC=$(ls "$D"/ccheck-s[0-9]*.json 2>/dev/null)
nice -n 10 $PY -B tools/claims-v3/e170/score_e170_a1.py $SESS --ccheck $CC --out "$D/results.json" --md "$D/results.md" > "$D/score.txt" 2>&1; rc=$?
{ [ $rc -eq 0 ] && [ -s "$D/results.md" ]; } || { echo "stopped: the registered scorer failed (rc $rc; read $D/score.txt): collected, not scored"; exit 7; }
ls "$D"/ccheck-*.json > /dev/null 2>&1 && gzip -n -k "$D"/ccheck-*.json
echo "results.md written: $D/results.md"
head -3 "$D/score.txt"
