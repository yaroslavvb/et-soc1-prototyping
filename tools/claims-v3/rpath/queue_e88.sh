#!/usr/bin/env bash
# E88 (Q130): run passes <first> .. <first>+<n>-1 of block_e88.sh on the local card, one after another, inside the
# registered card budget (E88.md, "Card budget"). queue_e78.sh's rule without its tier-1 fallback (E88 has one tier):
#
#   setsid nohup bash tools/claims-v3/rpath/queue_e88.sh <first-pass> <n-passes> > build/e88-queue.log 2>&1 < /dev/null &
#
# Before each pass it projects the pass's end from the longest pass so far (6 min before the first one ends) and
# starts it only if that end is inside E88_BUDGET_MIN card-minutes of the queue's start (default 41; with the smoke
# and the two config reads that keeps the session inside the registered 45) and before E88_DEADLINE (default 22:15
# local time; every evening run ends by 22:30). It stops before the next pass when build/claims-v3/STOP or
# build/rpath-STOP exists, after any pass that fails, and after a pass that found another user on the card (exit 3)
# it waits 10 min and tries that pass once more.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
p=${1:?first pass}; n=${2:?number of passes}
BUDGET_MIN=${E88_BUDGET_MIN:-41}; DEADLINE=${E88_DEADLINE:-22:15}
t_start=$(date +%s); longest=360; done_n=0
deadline=$(date -d "today $DEADLINE" +%s 2>/dev/null || echo $((t_start + 3 * 3600)))
echo "$(date +%T) queue: passes $p..$((p + n - 1)), budget ${BUDGET_MIN} card-min, deadline $DEADLINE"
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/rpath-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  now=$(date +%s); el=$((now - t_start))
  if [ $((el + longest)) -gt $((BUDGET_MIN * 60)) ] || [ $((now + longest)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$i (elapsed $((el / 60)) min, longest pass $((longest / 60)) min, $done_n passes done)"
    exit 0
  fi
  echo "$(date +%T) p$i starts (elapsed $((el / 60)) card-min)"
  t0=$(date +%s)
  bash tools/claims-v3/rpath/block_e88.sh "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( ($(date +%s) - t0) / 60 )) min)"
  if [ $rc -eq 3 ]; then
    sleep 600
    t0=$(date +%s)
    bash tools/claims-v3/rpath/block_e88.sh "$i" < /dev/null; rc=$?
    echo "$(date +%T) p$i retry rc=$rc"
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; exit "$rc"; }
  d=$(( $(date +%s) - t0 )); [ $d -gt $longest ] && longest=$d
  done_n=$((done_n + 1))
  sleep 10
done
echo "$(date +%T) queue done: $done_n passes, $(( ($(date +%s) - t_start) / 60 )) card-min"
