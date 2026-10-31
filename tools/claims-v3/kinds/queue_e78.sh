#!/usr/bin/env bash
# E78 (Q130): run passes <first> .. <first>+<n>-1 of block_e78.sh on the local card, one after another, inside the
# registered card budget (E78.md, "Card budget"). A port of tools/claims-v3/hlp/queue_hlp.sh with the kinds paths,
# its own STOP file and the budget rule:
#
#   setsid nohup bash tools/claims-v3/kinds/queue_e78.sh <first-pass> <n-passes> > build/e78-queue.log 2>&1 < /dev/null &
#
# Before each pass it projects the pass's end from the longest pass so far (11 min before the first one ends):
#   - it starts a full pass (tiers 1 and 2) only if the projected end is inside E78_BUDGET_MIN card-minutes of the
#     queue's start (default 85; the smoke's ~2 min makes the registered 90) and before E78_DEADLINE (default 19:15
#     local time; card runs must end by ~19:30);
#   - if a full pass does not fit and fewer than E78_MIN_PASSES (4) passes are done, it runs a tier-1-only pass
#     (44 runs, ~0.7 of a full one) if THAT fits inside 88 card-minutes and the deadline; otherwise it stops.
# It stops before the next pass when build/claims-v3/STOP or build/kinds-STOP exists, after any pass that fails,
# and after a pass that found another user on the card (exit 3) it waits 10 min and tries that pass once more.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
p=${1:?first pass}; n=${2:?number of passes}
BUDGET_MIN=${E78_BUDGET_MIN:-85}; HARD_MIN=${E78_HARD_MIN:-88}; MIN_PASSES=${E78_MIN_PASSES:-4}
DEADLINE=${E78_DEADLINE:-19:15}
t_start=$(date +%s); longest=660; done_n=0
deadline=$(date -d "today $DEADLINE" +%s 2>/dev/null || echo $((t_start + 6 * 3600)))
echo "$(date +%T) queue: passes $p..$((p + n - 1)), budget ${BUDGET_MIN} card-min (hard ${HARD_MIN}), deadline $DEADLINE"
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  now=$(date +%s); el=$((now - t_start)); tiers=1,2
  if [ $((el + longest)) -gt $((BUDGET_MIN * 60)) ] || [ $((now + longest)) -gt "$deadline" ]; then
    short=$((longest * 7 / 10))
    if [ "$done_n" -lt "$MIN_PASSES" ] && [ $((el + short)) -le $((HARD_MIN * 60)) ] && [ $((now + short)) -le "$deadline" ]; then
      tiers=1
      echo "$(date +%T) budget: a full pass would end past the budget (elapsed $((el / 60)) min, longest pass $((longest / 60)) min); p$i runs tier 1 only"
    else
      echo "$(date +%T) budget: stopping before p$i (elapsed $((el / 60)) min, longest pass $((longest / 60)) min, $done_n passes done)"
      exit 0
    fi
  fi
  echo "$(date +%T) p$i starts (tiers $tiers, elapsed $((el / 60)) card-min)"
  t0=$(date +%s)
  E78_TIERS=$tiers bash tools/claims-v3/kinds/block_e78.sh "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( ($(date +%s) - t0) / 60 )) min)"
  if [ $rc -eq 3 ]; then
    sleep 600
    t0=$(date +%s)
    E78_TIERS=$tiers bash tools/claims-v3/kinds/block_e78.sh "$i" < /dev/null; rc=$?
    echo "$(date +%T) p$i retry rc=$rc"
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; exit "$rc"; }
  d=$(( $(date +%s) - t0 )); [ "$tiers" = 1 ] && d=$((d * 10 / 7)); [ $d -gt $longest ] && longest=$d
  done_n=$((done_n + 1))
  sleep 15
done
echo "$(date +%T) queue done: $done_n passes, $(( ($(date +%s) - t_start) / 60 )) card-min"
