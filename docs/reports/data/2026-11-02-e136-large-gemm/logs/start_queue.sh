#!/bin/bash
cd ~/claude/et-soc1-prototyping || exit 9
setsid nohup python3 tools/claims-v3/e136/queue_e136.py --slots ~/claude/work/q137-a2-e136-slot.txt --runs build/e136/runs --cap 45 --cap-margin-s 150 > build/e136/queue.out 2>&1 < /dev/null &
echo "queue pid $!"
