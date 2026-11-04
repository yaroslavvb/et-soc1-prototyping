#!/usr/bin/env bash
# E164 (Q141(b)): the registered passes on aifoundry1 card 1, run by session_e164.sh after the stop-path test and the smoke gate have
# passed. A port of tools/claims-v3/e157/queue_e157.sh, each change marked E164:
#   1. passes 16410-16413 (four planned), then 16414 if it fits, each tools/claims-v3/e164/block_e164.sh with V3_DEVICE=1;
#   2. the budget: a pass starts only if now + projected <= E164_T0 + E164_BUDGET_S - E164_RESERVE_S (3900 - 60 s: the 65
#      card-minutes, with the closing config read inside them) and now + projected <= the deadline E164_DEADLINE, which the launch
#      MUST set (a GNU date string, the round's time gate less 10 minutes; there is no default, the day is the go's); projected is
#      E164_FIRST_S (900 s: E157's slowest pass on this card, 675 s for 78 launches, scaled to 98, 848 s, plus a margin for a first
#      pass from a cool die) until a pass ends, then the longest measured pass; exact integer seconds;
#   3. it stops before the next pass on build/e164/STOP or build/claims-v3/STOP, and after any pass that fails (rc 3 = another user on
#      the card or a device process; rc 1 = the block failed, a registered stop included: never retried).
# A pass in flight is never cut. No pass is added after any reduction is read. Nothing is set.
#
#   E164_T0=<anchor epoch> E164_DEADLINE='<YYYY-MM-DD HH:MM PST>' bash tools/claims-v3/e164/queue_e164.sh > build/e164/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
T0=${E164_T0:?E164_T0 - the session anchor, epoch seconds}
DL=${E164_DEADLINE:?E164_DEADLINE - the last end of a pass, the round time gate less 10 minutes (no default)}         # E164 change 2
BUDGET_S=${E164_BUDGET_S:-3900}; RESERVE_S=${E164_RESERVE_S:-60}; longest=${E164_FIRST_S:-900}; GAP_S=${E164_GAP_S:-10}
BLOCK=${E164_BLOCK:-tools/claims-v3/e164/block_e164.sh}      # E164_BLOCK exists only for a stub self-test; session_e164.sh never sets it
PASSES=${E164_PASSES:-16410 16411 16412 16413 16414}          # E164_PASSES exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "$(date +%T) e164: E164_DEADLINE '$DL' is not a date: no pass runs"; exit 2; }
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e164
echo "$(date +%T) e164: passes ${PASSES}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s; E164_DROP_P2=${E164_DROP_P2:-0}"
n=0
for p in $PASSES; do
  if [ -e build/e164/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e164: done, $n passes, at $(rel "$(date +%s)")"
