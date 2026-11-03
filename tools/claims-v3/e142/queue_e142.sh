#!/usr/bin/env bash
# E142 (Q138): the registered passes on aifoundry1 card 1, run by session_e142.sh after the stop-path test and the smoke gate have
# passed. A port of tools/claims-v3/e131/queue_e131.sh (E78-frame passes on this card, the budget anchored on the session's T0), each
# change marked E142:
#   1. passes 14210-14213, then 14214 if it fits, each tools/claims-v3/e142/block_e142.sh with V3_DEVICE=1;
#   2. the budget: a pass starts only if now + projected <= E142_T0 + E142_BUDGET_S - E142_RESERVE_S (3000 - 60 s: the 50
#      card-minutes, with the closing config read inside them) and now + projected <= the deadline, 2026-11-02 23:40 PST (every run
#      ends by 23:50 PST); projected is E142_FIRST_S (720 s: E131's slowest pass on this card, 652 s for 53 runs from a cool die,
#      scaled to 56 runs, plus a margin) until a pass ends, then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e142/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on
#      the card or a device process; rc 1 = the block failed, a registered stop included: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E142_T0=<anchor epoch> bash tools/claims-v3/e142/queue_e142.sh > build/e142/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
T0=${E142_T0:?E142_T0 - the session anchor, epoch seconds}
BUDGET_S=${E142_BUDGET_S:-3000}; RESERVE_S=${E142_RESERVE_S:-60}; longest=${E142_FIRST_S:-720}; GAP_S=${E142_GAP_S:-10}
BLOCK=${E142_BLOCK:-tools/claims-v3/e142/block_e142.sh}      # E142_BLOCK exists only for a stub self-test; session_e142.sh never sets it
PASSES=${E142_PASSES:-14210 14211 14212 14213 14214}          # E142_PASSES exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E142_DEADLINE:-2026-11-02 23:40 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e142
echo "$(date +%T) e142: passes ${PASSES}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in $PASSES; do
  if [ -e build/e142/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e142: done, $n passes, at $(rel "$(date +%s)")"
