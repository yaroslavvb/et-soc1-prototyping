#!/bin/bash
# one bounded wait (<= WAIT_S, default 500 s) on E126's queue on aifoundry2: returns early when the queue ends or halts; prints a short status
R=~/claude/et-soc1-prototyping/build/e126/runs
end=$(( $(date +%s) + ${WAIT_S:-500} ))
while [ $(date +%s) -lt $end ]; do
  if grep -q '"state": "ended"\|"state": "halted"' $R/status.json 2>/dev/null; then break; fi
  sleep 10
done
date '+%T %Z'
cat $R/status.json; echo
grep -o '"kind": "[a-z_0-9]*"' $R/queue.jsonl | tr '\n' ' '; echo
for s in smoke s1 s2 s3; do [ -f $R/$s.out ] && { echo "== $s"; grep -E "^\S+ \[[0-9]+/[0-9]+\]|NOT ADMITTED|session ends|exit |cap cuts|safety|other_user|e105_peak_lock|refused" $R/$s.out | tail -4; }; done
[ -f $R/QUEUE-HALT ] && cat $R/QUEUE-HALT
[ -f $R/s1/skipped.jsonl ] && cat $R/s1/skipped.jsonl
python3 - <<'PY'
import json, glob, os
R = os.path.expanduser("~/claude/et-soc1-prototyping/build/e126/runs")
mx = (0, None, 0)
for p in glob.glob(os.path.join(R, "s*/tel/*.jsonl")):
    for ln in open(p):
        if ln.startswith("{"):
            try:
                d = json.loads(ln)
            except ValueError:
                continue
            w = d.get("board_w") or 0
            ms = (d.get("temp_c") or {}).get("minshire") or [0, 0, 0]
            if w > mx[0]:
                mx = (w, os.path.basename(p), mx[2])
            mx = (mx[0], mx[1], max(mx[2], ms[2] or 0))
print("peak board W so far", mx[0], "in", mx[1], "| hottest die sensor so far", mx[2])
PY
