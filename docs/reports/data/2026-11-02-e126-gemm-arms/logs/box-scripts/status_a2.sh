#!/bin/bash
# quick status (no wait): one line per fact
R=~/claude/et-soc1-prototyping/build/e126/runs
date '+%T %Z'
cat $R/status.json 2>/dev/null; echo
grep -o '"kind": "[a-z_0-9]*"' $R/queue.jsonl | tr '\n' ' '; echo
for s in smoke s1 s2; do [ -f $R/$s.out ] && { echo "== $s"; grep -E "^\S+ \[[0-9]+/[0-9]+\]|NOT ADMITTED|session ends|exit |cap cuts|safety|other_user|e105_peak_lock|refused" $R/$s.out | tail -3; }; done
[ -f $R/QUEUE-HALT ] && cat $R/QUEUE-HALT
[ -f $R/s1/skipped.jsonl ] && cat $R/s1/skipped.jsonl
true
