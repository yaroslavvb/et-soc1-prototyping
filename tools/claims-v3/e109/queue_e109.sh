#!/usr/bin/env bash
# E109: the registered passes on aifoundry3, detached on the box, after the smoke (block_e109.sh 10901 --smoke) has passed:
#
#   setsid nohup bash tools/claims-v3/e109/queue_e109.sh > build/e109/queue.out 2>&1 < /dev/null &
#
# Passes 10910-10913, each block_e109.sh unchanged. It stops before the next pass on build/e109/STOP, after any failed pass, or if a pass would end past
# E109_DEADLINE_S (epoch seconds; default its start plus 23 min, so that the smoke, the passes and both config reads stay inside the 25 card-minutes the
# brief allows: a pass is 34 device runs, 2 burn-in and 32 registered, about 330 s). A pass in flight is never cut by the deadline. A port of queue_e107.sh without its watcher: no E109 item is expected above E78's own
# random fp32 anchor (about 26 W of S at the pinned 600 MHz).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
t_start=$(date +%s); deadline=${E109_DEADLINE_S:-$((t_start + 23 * 60))}; longest=${E109_LONGEST_S:-330}
mkdir -p build/e109
sha256sum build/e109/host/sparsity_host build/e109/kernel/sparsity.elf > build/e109/binaries.sha256
echo "$(date +%T) e109: start, deadline in $(( (deadline - t_start) / 60 )) min"
for p in 10910 10911 10912 10913; do
  [ -e build/e109/STOP ] && { echo "$(date +%T) STOP: stopping before p$p"; break; }
  now=$(date +%s)
  if [ $((now + longest)) -gt "$deadline" ]; then echo "$(date +%T) deadline: stopping before p$p (longest pass $longest s)"; break; fi
  echo "$(date +%T) p$p starts"
  t0=$(date +%s)
  bash tools/claims-v3/e109/block_e109.sh "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  [ "$d" -gt "$longest" ] && longest=$d
  sleep 15
done
echo "$(date +%T) e109: done"
