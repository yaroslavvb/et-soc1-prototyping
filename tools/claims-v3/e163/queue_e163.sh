#!/usr/bin/env bash
# E163 (Q141): the registered passes and blocks on aifoundry3 card 0, run by session_e163.sh after the stop-path test and the smoke gate
# have passed. A copy of tools/claims-v3/e153/queue_e153.sh (the budget anchored on the session's T0), each change marked E163:
#   1. the plan (E163_PLAN, E163.md "What runs"): FULL 16310 16311 16312, then the E151 block 16350 16351 16352, then 16313 (budget
#      4,200 s: the 70 card-minutes); TWO 16310 16311 (2,280 s); SHORT 16320 16321 (1,800 s); each item tools/claims-v3/e163/block_e163.sh;
#   2. the budget: an item starts only if now + projected <= E163_T0 + the plan's budget - E163_RESERVE_S (60 s, the closing config read
#      inside the budget) and now + projected <= E163_DEADLINE (required: set at his go from the round's time gate); projected is the
#      item kind's first estimate (a 97-run kinds pass 1,000 s; a 77-run SHORT pass 820 s; an E151 block 190 s) until an item of that
#      kind ends, then the longest measured of that kind; exact integer seconds;
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e163/STOP or
#      build/claims-v3/STOP, and after any item that fails (rc 3 = another user on the card or a device process; rc 1 = the block
#      failed, a registered stop included: never retried).
# An item in flight is never cut. No item is added after any reduction is read. Nothing is set.
#
#   E163_T0=<anchor epoch> E163_DEADLINE='<date>' [E163_PLAN=FULL|TWO|SHORT] bash tools/claims-v3/e163/queue_e163.sh > build/e163/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E163_T0:?E163_T0 - the session anchor, epoch seconds}
DL=${E163_DEADLINE:?E163_DEADLINE - the latest end of any item, from the time gate of the round, a date string}
PLAN=${E163_PLAN:-FULL}
case "$PLAN" in
  FULL)  SEQ="16310 16311 16312 16350 16351 16352 16313"; BUDGET_S=4200 ;;
  TWO)   SEQ="16310 16311"; BUDGET_S=2280 ;;
  SHORT) SEQ="16320 16321"; BUDGET_S=1800 ;;
  *) echo "E163_PLAN=$PLAN: only FULL, TWO or SHORT"; exit 2 ;;
esac
SEQ=${E163_SEQ:-$SEQ}                # E163_SEQ exists only for the stub self-test (dry_intel_e163.sh); session_e163.sh never sets it
BUDGET_S=${E163_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E163_RESERVE_S:-60}; GAP_S=${E163_GAP_S:-10}
BLOCK=${E163_BLOCK:-tools/claims-v3/e163/block_e163.sh}      # E163_BLOCK exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E163_DEADLINE '$DL' is not a date"; exit 2; }
kind() { case "$1" in 1631[0-9]) echo kinds ;; 1632[0-9]) echo short ;; 1635[0-9]) echo e151 ;; *) echo other ;; esac; }
est_kinds=${E163_FIRST_KINDS_S:-1000}; est_short=${E163_FIRST_SHORT_S:-820}; est_e151=${E163_FIRST_E151_S:-190}
seen_kinds=0; seen_short=0; seen_e151=0
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e163
echo "$(date +%T) e163: plan $PLAN, items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T'); first estimates kinds ${est_kinds} s, short ${est_short} s, e151 ${est_e151} s"
n=0
for p in $SEQ; do
  if [ -e build/e163/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  k=$(kind "$p")
  eval "proj=\$est_$k"
  now=$(date +%s)
  if [ $((now + proj)) -gt "$limit" ] || [ $((now + proj)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p ($k; now $(rel "$now"), projected ${proj} s, would end $(rel $((now + proj))) > $(rel "$limit") or the deadline)"
    break
  fi
  echo "$(date +%T) p$p ($k) starts at $(rel "$now") (projected ${proj} s)"
  t0=$(date +%s)
  bash "$BLOCK" "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  eval "seen=\$seen_$k"
  if [ "$seen" -eq 0 ] || [ "$d" -gt "$proj" ]; then eval "est_$k=$d"; fi   # the first estimate holds until an item of its kind ends
  eval "seen_$k=1"
  n=$((n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) e163: done, $n items, at $(rel "$(date +%s)")"
