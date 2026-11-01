#!/usr/bin/env bash
# E107: the registered passes on aifoundry3, detached on the box, after the smoke (block_e107.sh 10701 --smoke) has passed:
#
#   setsid nohup bash tools/claims-v3/e107/queue_e107.sh > build/e107/queue.out 2>&1 < /dev/null &
#
# Passes 10710, 10711, 10712, each block_e107.sh unchanged. It stops before the next pass on build/e107/STOP, after any failed pass, or if a pass would end
# past E107_DEADLINE_S (epoch seconds; default its start plus 54 min, so that the smoke, the passes and both config reads stay inside the 60 card-minutes
# the brief allows). A pass in flight is never cut by the deadline. watch_e107.py ends a pass at 80 W on three board samples in a row (none is expected
# above about 60 W at the pinned 600 MHz).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
t_start=$(date +%s); deadline=${E107_DEADLINE_S:-$((t_start + 54 * 60))}; longest=${E107_LONGEST_S:-1080}
sha256sum build/e107/host/sparsity_host build/e107/kernel/sparsity.elf > build/e107/binaries.sha256
python3 tools/claims-v3/e107/watch_e107.py --root "build/claims-v3/$(hostname)/e107" --stop build/e107/STOP --watts 80 --samples 3 > build/e107/watch.out 2>&1 &
WATCH=$!
echo "$(date +%T) e107: start, deadline in $(( (deadline - t_start) / 60 )) min, watcher $WATCH"
for p in 10710 10711 10712; do
  [ -e build/e107/STOP ] && { echo "$(date +%T) STOP: stopping before p$p"; break; }
  now=$(date +%s)
  if [ $((now + longest)) -gt "$deadline" ]; then echo "$(date +%T) deadline: stopping before p$p (longest pass $longest s)"; break; fi
  echo "$(date +%T) p$p starts"
  t0=$(date +%s)
  bash tools/claims-v3/e107/block_e107.sh "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  [ "$d" -gt "$longest" ] && longest=$d
  sleep 15
done
kill -TERM "$WATCH" 2>/dev/null
echo "$(date +%T) e107: done"
