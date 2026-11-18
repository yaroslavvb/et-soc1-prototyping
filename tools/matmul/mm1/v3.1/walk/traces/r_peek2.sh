#!/bin/bash
# v31-trace (Q217), run ON aifoundry3: read-only: this user's processes under the lane's run (tree, CPU, RSS).
set -u
ps -u "$(id -u)" -o pid,ppid,etime,time,rss,args --sort=start_time | grep -v 'ps -u' | sed "s#$HOME#~#g" | cut -c1-220 | tail -12
