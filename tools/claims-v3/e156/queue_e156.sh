#!/usr/bin/env bash
# E156 (Q139): the registered passes on aifoundry1 card 1, run by session_e156.sh after the smoke gate has passed. A copy of
# tools/claims-v3/e155/queue_e155.sh, each change marked E156:
#   1. passes 15610-15619 (15610 the registered warm-up, as E132's 13210 and E139's 13910), each tools/claims-v3/e156/block_e156.sh, with
#      V3_DEVICE=1, MF_EXPN=e156 and E156's images and host;
#   2. the budget is anchored on E156_T0 (epoch seconds, the session's launch): a pass starts only if now + projected <= E156_T0 + E156_BUDGET_S -
#      E156_RESERVE_S (2400 - 150: the 40 card-minutes, with the closing config read inside them) and now + projected <= the deadline, 2026-11-03
#      11:20 PST (every run ends by 11:30 PST, Q139's gate); projected is E156_FIRST_S (330 s: E139's 24-run passes took 201-230 s on aifoundry3,
#      E155's 14-run passes 215-239 s on this card, about 12.5 s a run here, and an E156 pass is 20 runs) until a pass ends, then the longest
#      measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e156/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on the card or a
#      device process: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E156_T0=<anchor epoch> bash tools/claims-v3/e156/queue_e156.sh > build/e156/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1 MF_EXPN=e156 MF_GEN=$PWD/build/e156-gen MF_ENERCAT=build/enercat-e99/host/enercat_host MF_MAX_C=70
T0=${E156_T0:?E156_T0 - the session anchor, epoch seconds}
BUDGET_S=${E156_BUDGET_S:-2400}; RESERVE_S=${E156_RESERVE_S:-150}; longest=${E156_FIRST_S:-330}
BLOCK=${E156_BLOCK:-tools/claims-v3/e156/block_e156.sh}      # E156_BLOCK exists only for a stub self-test; session_e156.sh never sets it
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E156_DEADLINE:-2026-11-03 11:20 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e156
echo "$(date +%T) e156: passes 15610-15619 (15610 the warm-up); budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
n=0
for p in 15610 15611 15612 15613 15614 15615 15616 15617 15618 15619; do
  if [ -e build/e156/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e156: done, $n passes, at $(rel "$(date +%s)")"
