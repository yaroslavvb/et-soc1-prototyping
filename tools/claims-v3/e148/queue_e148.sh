#!/usr/bin/env bash
# E148 (Q138): the registered passes on aifoundry1 card 1, run by session_e148.sh after the smoke gate has passed. A port of
# tools/claims-v3/e129/queue_e129.sh (itself a port of e124/queue_e124.sh), each change marked E148:
#   1. passes 14810-14819 (at most ten), each tools/claims-v3/e148/block_e148.sh, with V3_DEVICE=1 and E148_EXPN=e148;
#   2. the budget is anchored on E148_T0 (epoch seconds, the session's launch): a pass starts only if now + projected <= E148_T0 + E148_BUDGET_S -
#      E148_RESERVE_S (2400 - 150: the 40 card-minutes, with the closing config read inside them) and now + projected <= the deadline, 2026-11-02
#      23:45 PST (every run ends by 23:50 PST, Q138's gate); projected is E148_FIRST_S (600 s, E129's passes took 536-663 s) until a pass ends,
#      then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e148/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on the card or a
#      device process: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E148_T0=<anchor epoch> bash tools/claims-v3/e148/queue_e148.sh > build/e148/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E148_EXPN=e148
T0=${E148_T0:?E148_T0 - the session anchor, epoch seconds}
BUDGET_S=${E148_BUDGET_S:-2400}; RESERVE_S=${E148_RESERVE_S:-150}; longest=${E148_FIRST_S:-600}
BLOCK=${E148_BLOCK:-tools/claims-v3/e148/block_e148.sh}      # E148_BLOCK exists only for a stub self-test; session_e148.sh never sets it
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E148_DEADLINE:-2026-11-02 23:45 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e148
echo "$(date +%T) e148: passes 14810-14819; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in 14810 14811 14812 14813 14814 14815 14816 14817 14818 14819; do
  if [ -e build/e148/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e148: done, $n passes, at $(rel "$(date +%s)")"
