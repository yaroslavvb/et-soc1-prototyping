#!/usr/bin/env bash
# E129 (Q136): the registered passes on aifoundry1 card 1, run by session_e129.sh after the smoke gate has passed. A port of
# tools/claims-v3/e124/queue_e124.sh, each change marked E129:
#   1. passes 12910-12919 (at most ten), each tools/claims-v3/e129/block_e129.sh, with V3_DEVICE=1 and E129_EXPN=e129;
#   2. the budget is anchored on E129_T0 (epoch seconds, the session's launch): a pass starts only if now + projected <= E129_T0 + E129_BUDGET_S -
#      E129_RESERVE_S (2100 - 150: the 35 card-minutes, with the closing config read inside them) and now + projected <= the deadline, 2026-11-02
#      15:50 PST (every run ends by 16:00 PST); projected is E129_FIRST_S (300 s) until a pass ends, then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e129/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on the card or a
#      device process: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E129_T0=<anchor epoch> bash tools/claims-v3/e129/queue_e129.sh > build/e129/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 E129_EXPN=e129
T0=${E129_T0:?E129_T0 - the session anchor, epoch seconds}
BUDGET_S=${E129_BUDGET_S:-2100}; RESERVE_S=${E129_RESERVE_S:-150}; longest=${E129_FIRST_S:-300}
BLOCK=${E129_BLOCK:-tools/claims-v3/e129/block_e129.sh}      # E129_BLOCK exists only for a stub self-test; session_e129.sh never sets it
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E129_DEADLINE:-2026-11-02 15:50 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e129
echo "$(date +%T) e129: passes 12910-12919; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in 12910 12911 12912 12913 12914 12915 12916 12917 12918 12919; do
  if [ -e build/e129/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e129: done, $n passes, at $(rel "$(date +%s)")"
