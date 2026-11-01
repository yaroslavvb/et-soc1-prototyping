#!/bin/bash
# E97 run control, not part of any measurement. It opens no device. The queue and run_e97b.py already stop by 07:13 PST on their own clocks; this is the backstop, on the box, needing no ssh.
# At 07:14:00 PST: the STOP files (the runners read them at their next check). At 07:15:20 PST: SIGTERM to the block if it still runs (its trap stops the runner, then the sampler with SIGTERM, and writes block.json).
cd "$HOME/aifoundry" || exit 9
T1=$(date -d "2026-11-01 07:14:00 PST" +%s); T2=$(date -d "2026-11-01 07:15:20 PST" +%s)
echo "$(date -Is) watchdog up: STOP at $T1, SIGTERM at $T2"
while [ "$(date +%s)" -lt "$T1" ]; do
  pgrep -f 'queue_e97[.]sh' > /dev/null || { echo "$(date -Is) the queue is gone: nothing to do"; exit 0; }
  sleep 30
done
echo "$(date -Is) the deadline: STOP files"
touch build/e97-STOP
for p in 9710 9711 9720; do d=build/claims-v3/aifoundry3/e97/p$p; if [ -d "$d" ] && [ ! -e "$d/block.json" ]; then echo "the watchdog at the deadline" >> "$d/STOP"; fi; done
while [ "$(date +%s)" -lt "$T2" ]; do
  pgrep -f 'queue_e97[.]sh' > /dev/null || { echo "$(date -Is) the queue ended"; exit 0; }
  sleep 5
done
echo "$(date -Is) SIGTERM to the block"
pkill -TERM -f 'block_e97[.]sh'
