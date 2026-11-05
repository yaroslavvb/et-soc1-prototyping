#!/usr/bin/env bash
# E175 (Q143(g)): the dry pass on the Intel, E173's drypass_intel_e173.sh (lab 5a2a9ba0) with E175's names, and a stand-in ssh and rsync first
# on PATH that log any call (none is expected). The whole queue (queue_e175.py --dry)
# on run_hpl.py's toy card: no device is opened, no lock is taken,
# no ssh is run, nothing is read from a box. The smoke, the two dry stop-path tests (board 30 W on three samples; die 30 C), then s1 with
# protocol-dry.json (the dry twin's short order: 22 runs of 1.5 s bursts, passes 1-2), the watcher fix installed (its record in s1/e175.json). Then
# the registered scorer (score_e175.py) reads the dry s1: on the toy card no C log exists, so complete runs count (dry), and at 3 governed and 3
# pinned tiles (each group's minimum is 8) every governed and pinned rule reads NOT SCORED, as registered; the code path runs end to end. Every
# scratch path in the summary is <scratch>.
#
#   bash tools/claims-v3/e175/drypass_intel_e175.sh <a new empty scratch dir> > tools/claims-v3/e175/logs/drypass-intel.txt
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 1
S=${1:?usage: drypass_intel_e175.sh <a new empty scratch dir>}
[ -d "$S" ] && [ -n "$(ls -A "$S" 2>/dev/null)" ] && { echo "refused: $S is not empty"; exit 2; }
mkdir -p "$S/runs" "$S/bin" || exit 2
# a stand-in ssh and rsync first on PATH (the kits' verifier's fault 6 for E173): each logs its call and fails, so any reach for a box shows here
for t in ssh rsync; do
  printf '#!/bin/bash\necho "$(date +%%s) %s $*" >> "%s/standin-calls.log"\nexit 97\n' "$t" "$S" > "$S/bin/$t"
  chmod +x "$S/bin/$t"
done
: > "$S/standin-calls.log"
export PATH="$S/bin:$PATH"
QPY=${QPY:-python3}               # the queue and the runner: the desk's python3, as E165's and E170's dry passes ran them
SPY=${SPY:-/usr/bin/python3}      # the scorer: the predictor's python (numpy 1.26)
export PYTHONDONTWRITEBYTECODE=1
now=$(date +%s)
echo "SLOT E175: start $now (dry) end $((now + 2400)) " > "$S/slot.txt"
t0=$(date +%s)
nice -n 10 "$QPY" tools/claims-v3/e175/queue_e175.py --slots "$S/slot.txt" --runs "$S/runs" --dry --protocol tools/claims-v3/e175/protocol-dry.json \
  --stoptest-board tools/claims-v3/e175/protocol-stoptest-board-dry.json --stoptest-die tools/claims-v3/e175/protocol-stoptest-die-dry.json --cap 12 \
  > "$S/queue.out" 2>&1
qrc=$?
echo "E175 dry pass on the Intel ($("$QPY" --version 2>&1)): queue rc $qrc in $(( $(date +%s) - t0 )) s (the toy card; no device, no lock, no ssh)"
"$QPY" -B - "$S/runs/queue.jsonl" <<'EOP'
import json, sys
for ln in open(sys.argv[1]):
    d = json.loads(ln)
    k = d["kind"]
    if k in ("queue_start", "before_first_launch", "card_free", "status"):
        continue
    keep = {x: d[x] for x in ("name", "rc", "bad", "why", "stop", "trip_after_line_ms", "launch_end_after_trip_ms", "lines", "skipped") if x in d}
    if "end" in d and isinstance(d["end"], dict):
        keep["end"] = {x: d["end"].get(x) for x in ("exit", "reason", "card_min")}
    print(f"  {k:18s} {json.dumps(keep)}")
EOP
echo "  s1: $(wc -l < "$S/runs/s1/runs.jsonl" 2>/dev/null | tr -d ' ') runs recorded; the watcher: $("$QPY" -B -c 'import json,sys; w=json.load(open(sys.argv[1]))["watcher"]; print(w["watcher"], w["watcher_sha256"][:12], "installed", w["installed"])' "$S/runs/s1/e175.json" 2>&1)"
nice -n 10 "$SPY" -B tools/claims-v3/e175/score_e175.py "$S/runs/s1" --out "$S/results-dry.json" > "$S/score-dry.txt" 2>&1
echo "score_e175.py on the dry s1: rc $?"
sed "s#$S#<scratch>#g" "$S/score-dry.txt" | cut -c1-400 | sed 's/^/  /'
echo "stand-in ssh and rsync calls during the dry pass: $(wc -l < "$S/standin-calls.log" | tr -d ' ') (their first lines: $(head -n 2 "$S/standin-calls.log" | sed "s#$S#<scratch>#g" | cut -c1-120 | tr '\n' ' '))"
