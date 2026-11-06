#!/usr/bin/env bash
# E178 (Q146, the kit): the registered passes on aifoundry3 card 0, run by session_e178.sh after the stop-path test and the smoke gate have
# passed. A copy of tools/claims-v3/e171/queue_e171.sh (the budget anchored on the session's T0), each change marked E178:
#   1. the plan (E178_PLAN, E178.md section 7, "The plans"): FULL 17810 17811 17812 17813, the fourth only if the budget rule admits it
#      (budget 3,600 s: the 60 card-minute cap); TWO 17810 17811 (1,920 s: the 32 card-minute cap); each item block_e178.sh;
#   2. the budget: an item starts only if now + projected <= E178_T0 + the plan's budget - E178_RESERVE_S (60 s, the closing config read
#      inside the budget) and now + projected <= E178_DEADLINE (required: set at his go from the round's time gate); projected is the
#      first estimate (a 76-run pass, 800 s: E178.md section 7, "its projected end (800 s)") until a pass ends, then the longest measured;
#      exact integer seconds;
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e178/STOP or
#      build/claims-v3/STOP, and after any item that fails (rc 3 = another user on the card or a device process; rc 1 = the block
#      failed, a registered stop included: never retried).
# An item in flight is never cut. No item is added after any reduction is read. Nothing is set.
#
#   E178_T0=<anchor epoch> E178_DEADLINE='<date>' [E178_PLAN=FULL|TWO] bash tools/claims-v3/e178/queue_e178.sh > build/e178/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E178_T0:?E178_T0 - the session anchor, epoch seconds}
DL=${E178_DEADLINE:?E178_DEADLINE - the latest end of any item, from the time gate of the round, a date string}
PLAN=${E178_PLAN:-FULL}
case "$PLAN" in
  FULL)  SEQ="17810 17811 17812 17813"; BUDGET_S=3600 ;;
  TWO)   SEQ="17810 17811"; BUDGET_S=1920 ;;
  *) echo "E178_PLAN=$PLAN: only FULL or TWO"; exit 2 ;;
esac
SEQ=${E178_SEQ:-$SEQ}                # E178_SEQ exists only for the stub self-test (dry_intel_e178.sh); session_e178.sh never sets it
BUDGET_S=${E178_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E178_RESERVE_S:-60}; GAP_S=${E178_GAP_S:-10}
BLOCK=${E178_BLOCK:-tools/claims-v3/e178/block_e178.sh}      # E178_BLOCK exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E178_DEADLINE '$DL' is not a date"; exit 2; }
kind() { case "$1" in 1781[0-9]) echo kinds ;; *) echo other ;; esac; }
est_kinds=${E178_FIRST_KINDS_S:-800}; est_other=1000000
seen_kinds=0; seen_other=0
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e178
echo "$(date +%T) e178: plan $PLAN, items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T'); first estimate kinds ${est_kinds} s"
n=0
for p in $SEQ; do
  if [ -e build/e178/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e178: done, $n items, at $(rel "$(date +%s)")"
