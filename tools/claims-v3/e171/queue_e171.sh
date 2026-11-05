#!/usr/bin/env bash
# E171 (Q142(k6)): the registered passes on aifoundry3 card 0, run by session_e171.sh after the stop-path test and the smoke gate have
# passed. A copy of tools/claims-v3/e163/queue_e163.sh (the budget anchored on the session's T0), each change marked E171:
#   1. the plan (E171_PLAN, E171.md "The session plan"): FULL 17110 17111 17112 17113, the fourth only if the budget rule admits it
#      (budget 4,200 s: the 70 card-minutes); TWO 17110 17111 (2,280 s); SHORT 17120 17121 (1,800 s); each item block_e171.sh;
#   2. the budget: an item starts only if now + projected <= E171_T0 + the plan's budget - E171_RESERVE_S (60 s, the closing config read
#      inside the budget) and now + projected <= E171_DEADLINE (required: set at his go from the round's time gate); projected is the
#      item kind's first estimate (an 84-run kinds pass 900 s; a 75-run SHORT pass 820 s) until an item of that kind ends, then the
#      longest measured of that kind; exact integer seconds;
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e171/STOP or
#      build/claims-v3/STOP, and after any item that fails (rc 3 = another user on the card or a device process; rc 1 = the block
#      failed, a registered stop included: never retried).
# An item in flight is never cut. No item is added after any reduction is read. Nothing is set.
#
#   E171_T0=<anchor epoch> E171_DEADLINE='<date>' [E171_PLAN=FULL|TWO|SHORT] bash tools/claims-v3/e171/queue_e171.sh > build/e171/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E171_T0:?E171_T0 - the session anchor, epoch seconds}
DL=${E171_DEADLINE:?E171_DEADLINE - the latest end of any item, from the time gate of the round, a date string}
PLAN=${E171_PLAN:-FULL}
case "$PLAN" in
  FULL)  SEQ="17110 17111 17112 17113"; BUDGET_S=4200 ;;
  TWO)   SEQ="17110 17111"; BUDGET_S=2280 ;;
  SHORT) SEQ="17120 17121"; BUDGET_S=1800 ;;
  *) echo "E171_PLAN=$PLAN: only FULL, TWO or SHORT"; exit 2 ;;
esac
SEQ=${E171_SEQ:-$SEQ}                # E171_SEQ exists only for the stub self-test (dry_intel_e171.sh); session_e171.sh never sets it
BUDGET_S=${E171_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E171_RESERVE_S:-60}; GAP_S=${E171_GAP_S:-10}
BLOCK=${E171_BLOCK:-tools/claims-v3/e171/block_e171.sh}      # E171_BLOCK exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E171_DEADLINE '$DL' is not a date"; exit 2; }
kind() { case "$1" in 1711[0-9]) echo kinds ;; 1712[0-9]) echo short ;; *) echo other ;; esac; }
est_kinds=${E171_FIRST_KINDS_S:-900}; est_short=${E171_FIRST_SHORT_S:-820}; est_other=1000000
seen_kinds=0; seen_short=0; seen_other=0
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e171
echo "$(date +%T) e171: plan $PLAN, items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T'); first estimates kinds ${est_kinds} s, short ${est_short} s"
n=0
for p in $SEQ; do
  if [ -e build/e171/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e171: done, $n items, at $(rel "$(date +%s)")"
