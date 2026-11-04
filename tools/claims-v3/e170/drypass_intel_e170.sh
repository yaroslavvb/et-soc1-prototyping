#!/usr/bin/env bash
# E170 (Q141(w)): the dry pass on the Intel. The whole queue (queue_e170.py --dry) on run_hpl.py's toy card: no device is opened, no lock is taken,
# no ssh is run, nothing is read from a box. The state gate is skipped and recorded as such under --dry; the two stop-path tests run their dry twins
# (the toy card idles near 23 W, so its board twin's line is 30 W); the ramped smoke; then s1 with protocol-dry.json (passes 1 and 4, 1.5 s bursts).
# Then the scorer of record (score_e170_a1.py) reads the dry s1. Every scratch path in the summary is replaced by <scratch>.
#
#   bash tools/claims-v3/e170/drypass_intel_e170.sh <a new empty scratch dir> > tools/claims-v3/e170/logs/drypass-intel.txt
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 1
S=${1:?usage: drypass_intel_e170.sh <a new empty scratch dir>}
[ -d "$S" ] && [ -n "$(ls -A "$S" 2>/dev/null)" ] && { echo "refused: $S is not empty"; exit 2; }
mkdir -p "$S/runs" || exit 2
export ET_DEVICES=0 V3_DEVICE=0 PYTHONDONTWRITEBYTECODE=1
now=$(date +%s)
echo "SLOT E170: start $now (dry) end $((now + 2400)) " > "$S/slot.txt"
t0=$(date +%s)
nice -n 10 python3 tools/claims-v3/e170/queue_e170.py --slots "$S/slot.txt" --runs "$S/runs" --dry --protocol tools/claims-v3/e170/protocol-dry.json \
  --stoptest-board tools/claims-v3/e170/protocol-stoptest-board-dry.json --stoptest-die tools/claims-v3/e170/protocol-stoptest-die-dry.json --cap 12 \
  > "$S/queue.out" 2>&1
qrc=$?
echo "E170 dry pass on the Intel: queue rc $qrc in $(( $(date +%s) - t0 )) s (the toy card; no device, no lock, no ssh)"
python3 -B - "$S/runs/queue.jsonl" <<'EOP'
import json, sys
for ln in open(sys.argv[1]):
    d = json.loads(ln)
    k = d["kind"]
    if k in ("queue_start", "before_first_launch", "card_free", "status"):
        continue
    keep = {x: d[x] for x in ("name", "rc", "verdict", "bad", "why", "stop", "trip_after_line_ms", "launch_end_after_trip_ms", "lines", "board_max_w",
                              "die_max_c", "under_590", "over_stop", "skipped") if x in d}
    if "end" in d and isinstance(d["end"], dict):
        keep["end"] = {x: d["end"].get(x) for x in ("exit", "reason", "card_min")}
    print(f"  {k:18s} {json.dumps(keep)}")
EOP
echo "  s1: $(wc -l < "$S/runs/s1/runs.jsonl" 2>/dev/null) runs recorded; state gate: $(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("skipped"))' "$S/runs/state-gate.json")"
nice -n 10 python3 -B tools/claims-v3/e170/score_e170_a1.py "$S/runs/s1" --out "$S/results-dry.json" --md "$S/results-dry.md" > "$S/score-dry.txt" 2>&1
echo "score_e170_a1.py on the dry s1: rc $?"
sed "s#$S#<scratch>#g" "$S/score-dry.txt" | cut -c1-400 | sed 's/^/  /'
