#!/bin/bash
cd ~/claude/et-soc1-prototyping || exit 9
setsid nohup python3 tools/claims-v3/e126/queue_e126.py --slots ~/claude/work/q136-a2-e126-slot.txt --runs build/e126/runs --cap 44 --cap-margin-s 150 > build/e126/queue.out 2>&1 < /dev/null &
echo "queue pid $!"
