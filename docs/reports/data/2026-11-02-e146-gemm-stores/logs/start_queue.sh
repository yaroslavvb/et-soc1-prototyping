#!/bin/bash
cd ~/claude/et-soc1-prototyping || exit 9
setsid nohup python3 tools/claims-v3/e146/queue_e146.py --slots ~/claude/work/q138-a2-e146-slot.txt --runs build/e146/runs --cap 40 --cap-margin-s 150 > build/e146/queue.out 2>&1 < /dev/null &
echo "queue pid $!"
