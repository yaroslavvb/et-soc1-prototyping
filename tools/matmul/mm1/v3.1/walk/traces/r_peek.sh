#!/bin/bash
# v31-trace (Q217), run ON aifoundry3: a read-only look at this lane's running trace (its processes' CPU time and RSS, the run folder).
set -u
D="$HOME/claude/work/q217-v31-trace"
ps -u "$(id -u)" -o pid,etime,time,rss,comm | grep -E 'sys_emu|sparsity_host|python3' | grep -v grep
ls -la "$D/runs/${1:-}" 2>/dev/null | head -20
tail -3 "$D/runs/${1:-}/err.log" 2>/dev/null | sed "s#$HOME#~#g" | cut -c1-200
echo "load $(cut -d' ' -f1-3 /proc/loadavg)"
