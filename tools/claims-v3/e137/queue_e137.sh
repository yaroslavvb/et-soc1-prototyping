#!/usr/bin/env bash
# E137 (Q137): the registered passes on aifoundry1 card 1, run by session_e137.sh after the smoke gate has passed. A port of
# tools/claims-v3/e131/queue_e131.sh, each change marked E137:
#   1. passes 13710-13716 (seven at most; four kept are what the rules need), each tools/claims-v3/e137/block_e137.sh, with V3_DEVICE=1;
#   2. the budget is anchored on E137_T0 (epoch seconds, the session's launch, just before its first config read): a pass starts only if
#      now + projected <= E137_T0 + E137_BUDGET_S - E137_RESERVE_S (3420 - 60: 57 of the 60 card-minutes, with the closing config read inside them)
#      and now + projected <= the deadline, 2026-11-02 21:30 PST (every run ends by 21:45 PST); projected is E137_FIRST_S (700 s: E128's slowest
#      pass on this card, 958 s for 39 runs, scaled to 28 runs, plus a margin) until a pass ends, then the longest measured pass;
#   3. it stops before the next pass on build/e137/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on the card or a
#      device process; rc 1 = the block failed, a registered stop included: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E137_T0=<anchor epoch> bash tools/claims-v3/e137/queue_e137.sh > build/e137/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
T0=${E137_T0:?E137_T0 - the session anchor, epoch seconds}
BUDGET_S=${E137_BUDGET_S:-3420}; RESERVE_S=${E137_RESERVE_S:-60}; longest=${E137_FIRST_S:-700}; GAP_S=${E137_GAP_S:-10}
BLOCK=${E137_BLOCK:-tools/claims-v3/e137/block_e137.sh}      # E137_BLOCK exists only for a stub self-test; session_e137.sh never sets it
PASSES=${E137_PASSES:-13710 13711 13712 13713 13714 13715 13716}
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E137_DEADLINE:-2026-11-02 21:30 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e137
echo "$(date +%T) e137: passes ${PASSES}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in $PASSES; do
  if [ -e build/e137/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  now=$(date +%s)
  if [ $((now + longest)) -gt "$limit" ] || [ $((now + longest)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p (now $(rel "$now"), projected ${longest} s, would end $(rel $((now + longest))) > $(rel "$limit"))"
    break
  fi
  echo "$(date +%T) p$p starts at $(rel "$now") (projected ${longest} s)"
  t0=$(date +%s)
  bash "$BLOCK" "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  if [ "$n" -eq 0 ] || [ "$d" -gt "$longest" ]; then longest=$d; fi   # the first estimate holds until a pass ends
  n=$((n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) e137: done, $n passes, at $(rel "$(date +%s)")"
