#!/usr/bin/env bash
# E131 (Q136): the registered passes on aifoundry1 card 1, run by session_e131.sh after the smoke gate has passed. A port of
# tools/claims-v3/e129/queue_e129.sh, each change marked E131:
#   1. passes 13110-13114 (four, then a fifth if it fits), each tools/claims-v3/e131/block_e131.sh, with V3_DEVICE=1 and E131_EXPN=e131;
#   2. the budget is anchored on E131_T0 (epoch seconds, the session's launch, just before its first config read): a pass starts only if
#      now + projected <= E131_T0 + E131_BUDGET_S - E131_RESERVE_S (2700 - 60: the 45 card-minutes, with the closing config read inside them) and
#      now + projected <= the deadline, 2026-11-02 15:50 PST (every run ends by 16:00 PST); projected is E131_FIRST_S (560 s: E95's longest pass on
#      aifoundry3, 537 s, plus a margin, as E112 registered it) until a pass ends, then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e131/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on the card or a
#      device process; rc 1 = the block failed, a registered stop included: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E131_T0=<anchor epoch> bash tools/claims-v3/e131/queue_e131.sh > build/e131/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E131_EXPN=e131
T0=${E131_T0:?E131_T0 - the session anchor, epoch seconds}
BUDGET_S=${E131_BUDGET_S:-2700}; RESERVE_S=${E131_RESERVE_S:-60}; longest=${E131_FIRST_S:-560}; GAP_S=${E131_GAP_S:-10}
BLOCK=${E131_BLOCK:-tools/claims-v3/e131/block_e131.sh}      # E131_BLOCK exists only for a stub self-test; session_e131.sh never sets it
PASSES=${E131_PASSES:-13110 13111 13112 13113 13114}          # E131_PASSES exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E131_DEADLINE:-2026-11-02 15:50 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e131
echo "$(date +%T) e131: passes ${PASSES}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in $PASSES; do
  if [ -e build/e131/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e131: done, $n passes, at $(rel "$(date +%s)")"
