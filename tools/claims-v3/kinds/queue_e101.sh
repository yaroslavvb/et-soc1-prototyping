#!/usr/bin/env bash
# E101 (Q132): run passes <first> .. <first>+<n>-1 of block_e101.sh on the local card, one after another, inside the registered card budget (E101.md, "Card budget").
# A port of queue_e78.sh with block_e101.sh, E101's budget and deadline (a full date, because the clocks go back at 02:00 PDT tonight) and E78's tier-1 fallback:
#
#   setsid nohup bash tools/claims-v3/kinds/queue_e101.sh <first-pass> <n-passes> > build/e101-queue.log 2>&1 < /dev/null &
#
# Before each pass it projects the pass's end from the longest measured pass so far (E101_FIRST_S, 800 s, until the first one ends):
#   - it starts a full pass (tiers 1 and 2) only if the projected end is inside E101_BUDGET_MIN card-minutes of the queue's start and before E101_DEADLINE;
#   - if a full pass does not fit and fewer than E101_MIN_PASSES (3) passes are done, it runs a tier-1-only pass (62 runs against 78) if THAT fits; otherwise it stops.
# A pass in flight is never cut. It stops before the next pass when build/claims-v3/STOP or build/kinds-STOP exists and after any pass that fails; after a pass that found
# another user on the card (exit 3) it waits 5 min and tries that pass once more, if that still fits.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
p=${1:?first pass}; n=${2:?number of passes}
BUDGET_MIN=${E101_BUDGET_MIN:-44}; MIN_PASSES=${E101_MIN_PASSES:-3}; DEADLINE=${E101_DEADLINE:-2026-11-01 06:45 PST}; longest=${E101_FIRST_S:-800}
t_start=$(date +%s); done_n=0
deadline=$(date -d "$DEADLINE" +%s 2>/dev/null || echo $((t_start + 3 * 3600)))
echo "$(date +%T) queue: passes $p..$((p + n - 1)), budget ${BUDGET_MIN} card-min, deadline $DEADLINE, first-pass estimate ${longest} s"
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  now=$(date +%s); el=$((now - t_start)); tiers=1,2
  if [ $((el + longest)) -gt $((BUDGET_MIN * 60)) ] || [ $((now + longest)) -gt "$deadline" ]; then
    short=$((longest * 62 / 78))
    if [ "$done_n" -lt "$MIN_PASSES" ] && [ $((el + short)) -le $((BUDGET_MIN * 60)) ] && [ $((now + short)) -le "$deadline" ]; then
      tiers=1
      echo "$(date +%T) budget: a full pass would end past the budget (elapsed $((el / 60)) min, longest pass $((longest / 60)) min); p$i runs tier 1 only"
    else
      echo "$(date +%T) budget: stopping before p$i (elapsed $((el / 60)) min, longest pass $((longest / 60)) min, $done_n passes done)"
      exit 0
    fi
  fi
  echo "$(date +%T) p$i starts (tiers $tiers, elapsed $((el / 60)) card-min)"
  t0=$(date +%s)
  E78_TIERS=$tiers bash tools/claims-v3/kinds/block_e101.sh "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( ($(date +%s) - t0) / 60 )) min)"
  if [ $rc -eq 3 ]; then
    sleep 300
    t0=$(date +%s)
    E78_TIERS=$tiers bash tools/claims-v3/kinds/block_e101.sh "$i" < /dev/null; rc=$?
    echo "$(date +%T) p$i retry rc=$rc"
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; exit "$rc"; }
  d=$(( $(date +%s) - t0 )); [ "$tiers" = 1 ] && d=$((d * 78 / 62))
  if [ "$done_n" -eq 0 ] || [ $d -gt $longest ]; then longest=$d; fi   # the estimate holds until the first pass ends
  done_n=$((done_n + 1))
  sleep 15
done
echo "$(date +%T) queue done: $done_n passes, $(( ($(date +%s) - t_start) / 60 )) card-min"
