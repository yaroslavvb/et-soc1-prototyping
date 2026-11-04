#!/usr/bin/env bash
# E157 (Q139): the registered passes on aifoundry1 card 1, run by session_e157.sh after the stop-path test and the smoke gate have
# passed. A port of tools/claims-v3/e142/queue_e142.sh, each change marked E157:
#   1. passes 15710-15713, then 15714 if it fits, each tools/claims-v3/e157/block_e157.sh with V3_DEVICE=1;
#   2. the budget: a pass starts only if now + projected <= E157_T0 + E157_BUDGET_S - E157_RESERVE_S (3300 - 60 s: the 55
#      card-minutes, with the closing config read inside them) and now + projected <= the deadline, 2026-11-03 21:50 PST (every run
#      ends by 22:00 PST, section 23 of the round's brief); projected is E157_FIRST_S (780 s: E142's slowest pass on this card, 525 s for 56 runs, scaled to 76 runs,
#      712 s, plus a margin for the C log's DMA and a first pass from a cool die) until a pass ends, then the longest measured pass;
#      exact integer seconds;
#   3. it stops before the next pass on build/e157/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on
#      the card or a device process; rc 1 = the block failed, a registered stop included: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E157_T0=<anchor epoch> bash tools/claims-v3/e157/queue_e157.sh > build/e157/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
T0=${E157_T0:?E157_T0 - the session anchor, epoch seconds}
BUDGET_S=${E157_BUDGET_S:-3300}; RESERVE_S=${E157_RESERVE_S:-60}; longest=${E157_FIRST_S:-780}; GAP_S=${E157_GAP_S:-10}
BLOCK=${E157_BLOCK:-tools/claims-v3/e157/block_e157.sh}      # E157_BLOCK exists only for a stub self-test; session_e157.sh never sets it
PASSES=${E157_PASSES:-15710 15711 15712 15713 15714}          # E157_PASSES exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E157_DEADLINE:-2026-11-03 21:50 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e157
echo "$(date +%T) e157: passes ${PASSES}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in $PASSES; do
  if [ -e build/e157/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  now=$(date +%s)
  if [ $((now + longest)) -gt "$limit" ] || [ $((now + longest)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p (now $(rel "$now"), projected ${longest} s, would end $(rel $((now + longest))) > $(rel "$limit") or the deadline)"
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
echo "$(date +%T) e157: done, $n passes, at $(rel "$(date +%s)")"
