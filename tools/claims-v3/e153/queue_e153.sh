#!/usr/bin/env bash
# E153 (Q139): the registered passes on aifoundry3 card 0, run by session_e153.sh after the stop-path test and the smoke gate have
# passed. A copy of tools/claims-v3/e141/queue_e141.sh (E141's, itself E142's port of e131/queue_e131.sh, the budget anchored on the
# session's T0), each change marked E153:
#   1. passes 15310-15312, then 15313 if it fits, each tools/claims-v3/e153/block_e153.sh (aifoundry3: no V3_DEVICE);
#   2. the budget: a pass starts only if now + projected <= E153_T0 + E153_BUDGET_S - E153_RESERVE_S (3300 - 60 s: the 55
#      card-minutes, with the closing config read inside them) and now + projected <= the deadline, 2026-11-03 21:50 PST (every run
#      ends by 22:00 PST); projected is E153_FIRST_S (880 s: E141's slowest pass on this card, 623 s for 56 runs, scaled to 76 runs,
#      846 s, plus a margin) until a pass ends, then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e153/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on
#      the card or a device process; rc 1 = the block failed, a registered stop included: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E153_T0=<anchor epoch> bash tools/claims-v3/e153/queue_e153.sh > build/e153/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E153_T0:?E153_T0 - the session anchor, epoch seconds}
BUDGET_S=${E153_BUDGET_S:-3300}; RESERVE_S=${E153_RESERVE_S:-60}; longest=${E153_FIRST_S:-880}; GAP_S=${E153_GAP_S:-10}
BLOCK=${E153_BLOCK:-tools/claims-v3/e153/block_e153.sh}      # E153_BLOCK exists only for a stub self-test; session_e153.sh never sets it
PASSES=${E153_PASSES:-15310 15311 15312 15313}          # E153_PASSES exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E153_DEADLINE:-2026-11-03 21:50 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e153
echo "$(date +%T) e153: passes ${PASSES}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in $PASSES; do
  if [ -e build/e153/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e153: done, $n passes, at $(rel "$(date +%s)")"
