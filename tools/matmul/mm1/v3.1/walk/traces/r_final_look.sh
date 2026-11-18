#!/bin/bash
# v31-trace (Q217), run ON aifoundry3: read-only end-of-lane look: this lane's folder size, any log file left in it, any simulator process
# of this user still running, et-who, load.
set -u
D="$HOME/claude/work/q217-v31-trace"
du -sh "$D" | sed "s#$HOME#~#g"
find "$D" -name '*.log' -size +1M -printf '%s %p\n' | sed "s#$HOME#~#g" | head
find "$D" -name 'sysemu.log*' -printf '%s %p\n' | sed "s#$HOME#~#g" | head
pgrep -u "$(id -u)" -fa 'sparsity_host --sysemu' | cut -c1-80 || echo "no simulator host of this user running"
command -v et-who >/dev/null && timeout 20 et-who 2>&1 | head -2
echo "load $(cut -d' ' -f1-3 /proc/loadavg)"
