#!/bin/bash
cd ~/claude/et-soc1-prototyping || exit 9
setsid nohup python3 tools/claims-v3/e143/queue_e143.py --slots ~/claude/work/q138-a2-e143-slot.txt --runs build/e143/runs --cap 38 --cap-margin-s 150 > build/e143/queue.out 2>&1 < /dev/null &
echo "queue pid $!"
