#!/bin/bash
# one compact status line for the monitor (no wait on the box)
R=~/claude/et-soc1-prototyping/build/e126/runs
st=$(python3 -c "import json;print(json.load(open('$R/status.json')).get('state'))" 2>/dev/null)
last=$(grep -hE "^\S+ \[[0-9]+/[0-9]+\]" $R/s*.out 2>/dev/null | tail -1 | sed -E 's/^(\S+) \[([0-9]+)\/([0-9]+)\] ([A-Z])-[0-9]+-([^:]*):.*/\1 run \2\/\3 block \4 \5/')
alerts=$(grep -hE "NOT ADMITTED|session ends|safety|other_user|e105_peak_lock|refused|error" $R/s*.out 2>/dev/null | tail -2 | tr '\n' ' ')
halt=$([ -f $R/QUEUE-HALT ] && echo HALT)
echo "state=$st | $last | alerts: ${alerts:-none} $halt"
