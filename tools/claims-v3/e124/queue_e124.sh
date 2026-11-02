#!/usr/bin/env bash
# E124 (Q134): the registered passes on aifoundry1 card 1, run by session_e124.sh after the smoke gate has passed. A port of
# tools/claims-v3/e109/queue_e109.sh with E112's budget rule (tools/claims-v3/e112/queue_e112.sh), each change marked E124:
#   1. passes 12410-12414, each tools/claims-v3/e109/block_e109.sh UNCHANGED, with V3_DEVICE=1 and E109_EXPN=e124;
#   2. the budget is anchored on E124_T0 (epoch seconds; since amendment A1 the session's launch, before it the claim post): a pass starts only if
#      now + projected <= E124_T0 + E124_BUDGET_S -
#      E124_RESERVE_S (1800 - 150, so that the closing config read and the release fit inside the 30 card-minutes) and now + projected <= the deadline,
#      2026-11-01 23:15 PST; projected is E124_FIRST_S (360 s) until a pass ends, then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e124/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on the card or a
#      device process: never retried).
# A pass in flight is never cut. Nothing is set.
#
#   E124_T0=<anchor epoch> bash tools/claims-v3/e124/queue_e124.sh > build/e124/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E109_EXPN=e124
T0=${E124_T0:?E124_T0 - the session anchor, epoch seconds}
BUDGET_S=${E124_BUDGET_S:-1800}; RESERVE_S=${E124_RESERVE_S:-150}; longest=${E124_FIRST_S:-360}
BLOCK=${E124_BLOCK:-tools/claims-v3/e109/block_e109.sh}      # E124_BLOCK exists only for a stub self-test; session_e124.sh never sets it
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E124_DEADLINE:-2026-11-01 23:15 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e124
echo "$(date +%T) e124: passes 12410-12414; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in 12410 12411 12412 12413 12414; do
  if [ -e build/e124/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
  sleep 15
done
echo "$(date +%T) e124: done, $n passes, at $(rel "$(date +%s)")"
