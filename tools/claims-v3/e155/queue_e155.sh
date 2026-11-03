#!/usr/bin/env bash
# E155 (Q139): the registered passes on aifoundry1 card 1, run by session_e155.sh after the smoke gate has passed. A copy of
# tools/claims-v3/e148/queue_e148.sh, each change marked E155:
#   1. passes 15510-15519 (at most ten), each tools/claims-v3/e155/block_e155.sh, with V3_DEVICE=1 and E155_EXPN=e155;
#   2. the budget is anchored on E155_T0 (epoch seconds, the session's launch): a pass starts only if now + projected <= E155_T0 + E155_BUDGET_S -
#      E155_RESERVE_S (2400 - 150: the 40 card-minutes, with the closing config read inside them) and now + projected <= the deadline, 2026-11-03
#      11:20 PST (every run ends by 11:30 PST, Q139's gate); projected is E155_FIRST_S (600 s: E129's cool-morning passes on this card took
#      522-650 s, E148's warm evening ones 170-206 s) until a pass ends, then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e155/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on the card or a
#      device process: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E155_T0=<anchor epoch> bash tools/claims-v3/e155/queue_e155.sh > build/e155/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E155_EXPN=e155
T0=${E155_T0:?E155_T0 - the session anchor, epoch seconds}
BUDGET_S=${E155_BUDGET_S:-2400}; RESERVE_S=${E155_RESERVE_S:-150}; longest=${E155_FIRST_S:-600}
BLOCK=${E155_BLOCK:-tools/claims-v3/e155/block_e155.sh}      # E155_BLOCK exists only for a stub self-test; session_e155.sh never sets it
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E155_DEADLINE:-2026-11-03 11:20 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e155
echo "$(date +%T) e155: passes 15510-15519; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in 15510 15511 15512 15513 15514 15515 15516 15517 15518 15519; do
  if [ -e build/e155/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
  sleep 10
done
echo "$(date +%T) e155: done, $n passes, at $(rel "$(date +%s)")"
