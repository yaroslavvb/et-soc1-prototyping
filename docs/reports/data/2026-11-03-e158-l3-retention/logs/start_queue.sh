#!/bin/bash
cd ~/claude/et-soc1-prototyping || exit 9
setsid nohup python3 tools/claims-v3/e158/queue_e158.py --slots ~/claude/work/q139-a2-e158-slot.txt --runs build/e158/runs --cap 30 --cap-margin-s 150 > build/e158/queue.out 2>&1 < /dev/null &
echo "queue pid $!"
