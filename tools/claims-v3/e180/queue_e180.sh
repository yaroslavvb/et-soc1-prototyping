#!/usr/bin/env bash
# E180 (Q146(f), the kit): the registered passes on aifoundry3 card 0, run by session_e180.sh after the stop-path test and the smoke
# gate have passed. tools/claims-v3/e178/queue_e178.sh's form (the budget anchored on the session's T0), with E180's plan:
#   1. the plan (E180_PLAN, E180.md section 7): FULL 18010-18015 (budget 3,000 s: the 50 card-minute cap); TWO 18010 18011 (1,200 s,
#      the 20 card-minute cap); each item block_e180.sh;
#   2. an item starts only if now + projected <= E180_T0 + the budget - E180_RESERVE_S (60 s, the closing config read inside the
#      budget) and now + projected <= E180_DEADLINE (required); projected is 420 s (plan-e180.json first_pass_estimate_s) until a pass
#      ends, then the longest measured; a pass in flight is never cut;
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e180/STOP or
#      build/claims-v3/STOP, and after any item that does not end ok (rc 3 another user or a device process; rc 5 a live stop; rc 1
#      the block failed): never retried.
# Nothing is set. No item is added after any reduction is read.
#
#   E180_T0=<anchor epoch> E180_DEADLINE='<date>' [E180_PLAN=FULL|TWO] bash tools/claims-v3/e180/queue_e180.sh > build/e180/queue.out 2>&1 < /dev/null
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E180_T0:?E180_T0 - the session anchor, epoch seconds}
DL=${E180_DEADLINE:?E180_DEADLINE - the latest end of any item, a date string}
PLAN=${E180_PLAN:-FULL}
case "$PLAN" in
  FULL) SEQ="18010 18011 18012 18013 18014 18015"; BUDGET_S=3000 ;;
  TWO)  SEQ="18010 18011"; BUDGET_S=1200 ;;
  *) echo "E180_PLAN=$PLAN: only FULL or TWO"; exit 2 ;;
esac
SEQ=${E180_SEQ:-$SEQ}                # E180_SEQ, E180_BUDGET_S and E180_BLOCK exist only for the dry pass's stub test
BUDGET_S=${E180_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E180_RESERVE_S:-60}; GAP_S=${E180_GAP_S:-10}
BLOCK=${E180_BLOCK:-tools/claims-v3/e180/block_e180.sh}
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E180_DEADLINE '$DL' is not a date"; exit 2; }
est=${E180_FIRST_PASS_S:-420}; seen=0
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e180
echo "$(date +%T) e180: plan $PLAN, items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T'); first estimate ${est} s"
n=0
for p in $SEQ; do
  if [ -e build/e180/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  now=$(date +%s)
  if [ $((now + est)) -gt "$limit" ] || [ $((now + est)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p (now $(rel "$now"), projected ${est} s, would end $(rel $((now + est))) > $(rel "$limit") or the deadline)"
    break
  fi
  echo "$(date +%T) p$p starts at $(rel "$now") (projected ${est} s)"
  t0=$(date +%s)
  bash "$BLOCK" "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  if [ "$seen" -eq 0 ] || [ "$d" -gt "$est" ]; then est=$d; fi     # the first estimate holds until a pass ends
  seen=1
  n=$((n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) e180: done, $n items, at $(rel "$(date +%s)")"
