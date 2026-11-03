#!/bin/bash
cd ~/claude/et-soc1-prototyping || exit 9
setsid nohup python3 tools/claims-v3/e159/queue_e159.py --slots ~/claude/work/q139-a2-e159-slot.txt --runs build/e159/runs --cap 30 --cap-margin-s 150 > build/e159/queue.out 2>&1 < /dev/null &
echo "queue pid $!"
