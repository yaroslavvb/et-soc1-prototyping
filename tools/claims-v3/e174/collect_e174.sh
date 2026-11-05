#!/usr/bin/env bash
# E174 (Q142(kg)), AT THE DESK on the Intel, after `box/step_e174.sh pull` has copied aifoundry1:nekko/build/e174/ into <raw> (bounded, through the
# runbook's runner). It never reaches a box. E170's collect_e170.sh with E174's names and two changes, written before any E174 data:
#   1. the harness at the desk is the committed one (check_e174.py --desk), else exit 6;
#   2. Q139(k)'s check of C on EVERY session directory with a C log, then THE C-LOG LIST (cclist_q142kg.py; the Q142 critic's fault 3): every
#      session the registration requires to carry one (smoke, stoptest-board, every BURST session s1-s6 the queue started that ran a work launch)
#      must hold a C log, else nothing is scored (exit 8);
#   3. the runs and logs into docs/reports/data/<E174_DATE>-e174-blind8-card0/ (aifoundry1-c0/, logs/), the ccheck outputs beside;
#   4. no other login enters the public repo: E164's scrubber with the owner's login, then its --check (else exit 7: nothing may be committed);
#   5. the telemetry, launches and C logs gzipped (as E160's, E165's and E170's);
#   6. the registered score, score_e174.py (the predictor's python, numpy), into results.json and score.txt; its exit 5 (a listed session with no
#      check of C given) is this collector's exit 8, any other non-zero its exit 7. It prints "results written" only when the scorer exited 0.
#
#   E174_DATE=<the run's date> bash tools/claims-v3/e174/collect_e174.sh build/e174-raw
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 1
RAW=${1:?usage: collect_e174.sh <the pulled copy, e.g. build/e174-raw>}
DAY=${E174_DATE:?E174_DATE=<YYYY-MM-DD, the date of the run> is required}
D=docs/reports/data/$DAY-e174-blind8-card0
PY=${PY:-/usr/bin/python3}
OWNER=${E174_OWNER:-yaroslavvb}
[ -d "$RAW/runs" ] || { echo "refused: no $RAW/runs (run box/step_e174.sh pull first)"; exit 2; }
[ -e "$D/aifoundry1-c0" ] && { echo "refused: $D/aifoundry1-c0 exists"; exit 2; }
"$PY" -B tools/claims-v3/e174/check_e174.py --desk | tail -1
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "refused: the desk tree is not E174's committed harness: nothing collected"; exit 6; }
mkdir -p "$D/aifoundry1-c0" "$D/logs" "$RAW/cc" || exit 2
for sd in "$RAW"/runs/*/; do
  s=$(basename "$sd")
  [ -f "$sd/c-log.jsonl" ] || continue
  nice -n 10 "$PY" -B tools/claims-v3/ccheck/ccheck.py check "$sd/c-log.jsonl" --out "$RAW/cc/ccheck-$s.json" --jobs 2 > "$RAW/cc/ccheck-$s.txt" 2>&1
  echo "ccheck $s rc=$?"
done
"$PY" -B tools/claims-v3/q142kg-runbook/cclist_q142kg.py "$RAW/runs" "$RAW/cc" | tee "$RAW/cc/cclist.txt"
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "stopped: a session the registration requires to carry a C log has none (cclist above): nothing scored"; exit 8; }
rsync -a "$RAW/runs/" "$D/aifoundry1-c0/" || exit 3
for f in queue.out slot.txt holders-at-launch.txt e174-preflight.txt; do [ -f "$RAW/$f" ] && cp "$RAW/$f" "$D/logs/"; done
cp "$RAW/cc/cclist.txt" "$D/logs/"
cp "$RAW/cc/"ccheck-*.json "$D/" 2>/dev/null
"$PY" -B tools/claims-v3/e164/scrub_etwho_e164.py "$D" --owner "$OWNER" > "$D/logs/scrub.txt" 2>&1 || { echo "stopped: the scrub failed: nothing may be committed"; exit 7; }
"$PY" -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$D" --owner "$OWNER" >> "$D/logs/scrub.txt" 2>&1 \
  || { echo "stopped: the scrub's check is not OK (another login is left): nothing may be committed"; exit 7; }
find "$D/aifoundry1-c0" -path '*/tel/*.jsonl' -type f -exec gzip -n {} +
find "$D/aifoundry1-c0" \( -name launches.jsonl -o -name c-log.jsonl \) -type f -exec gzip -n {} +
SESS=$(for s in "$D"/aifoundry1-c0/s[0-9]*; do [ -f "$s/session.json" ] && printf '%s\n' "$s"; done)
[ -n "$SESS" ] || { echo "stopped: no session under $D/aifoundry1-c0 (the queue ended before s1: read its queue.jsonl and QUEUE-HALT): collected, not scored"; exit 4; }
CC=$(ls "$D"/ccheck-*.json 2>/dev/null)
nice -n 10 "$PY" -B tools/claims-v3/e174/score_e174.py $SESS --ccheck $CC --out "$D/results.json" > "$D/score.txt" 2>&1; rc=$?
[ $rc -eq 5 ] && { cat "$D/score.txt"; echo "stopped: the scorer refused: a listed session has no check of C (exit 5): collected, not scored"; exit 8; }
[ $rc -eq 0 ] || { echo "stopped: the registered scorer failed (rc $rc; read $D/score.txt): collected, not scored"; exit 7; }
ls "$D"/ccheck-*.json > /dev/null 2>&1 && gzip -n -k "$D"/ccheck-*.json
echo "results written: $D/results.json"
head -3 "$D/score.txt"
