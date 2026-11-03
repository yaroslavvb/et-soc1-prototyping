#!/usr/bin/env bash
# E141 (Q138): the registered passes on aifoundry3 card 0 (E141), run by session_e141.sh after the stop-path test and the smoke gate have
# passed. A copy of tools/claims-v3/e142/queue_e142.sh (a port of e131/queue_e131.sh, the budget anchored on the session's T0), each
# change marked E141 (E142's, with aifoundry3's card and first-pass estimate):
#   1. passes 14110-14113, then 14114 if it fits, each tools/claims-v3/e141/block_e141.sh (aifoundry3: no V3_DEVICE);
#   2. the budget: a pass starts only if now + projected <= E141_T0 + E141_BUDGET_S - E141_RESERVE_S (3000 - 60 s: the 50
#      card-minutes, with the closing config read inside them) and now + projected <= the deadline, 2026-11-02 23:40 PST (every run
#      ends by 23:50 PST); projected is E141_FIRST_S (620 s: E140's slowest pass on this card, 469 s for 45 runs, scaled to 56 runs,
#      584 s, plus a margin) until a pass ends, then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e141/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on
#      the card or a device process; rc 1 = the block failed, a registered stop included: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E141_T0=<anchor epoch> bash tools/claims-v3/e141/queue_e141.sh > build/e141/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E141_T0:?E141_T0 - the session anchor, epoch seconds}
BUDGET_S=${E141_BUDGET_S:-3000}; RESERVE_S=${E141_RESERVE_S:-60}; longest=${E141_FIRST_S:-620}; GAP_S=${E141_GAP_S:-10}
BLOCK=${E141_BLOCK:-tools/claims-v3/e141/block_e141.sh}      # E141_BLOCK exists only for a stub self-test; session_e141.sh never sets it
PASSES=${E141_PASSES:-14110 14111 14112 14113 14114}          # E141_PASSES exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E141_DEADLINE:-2026-11-02 23:40 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e141
echo "$(date +%T) e141: passes ${PASSES}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in $PASSES; do
  if [ -e build/e141/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e141: done, $n passes, at $(rel "$(date +%s)")"
