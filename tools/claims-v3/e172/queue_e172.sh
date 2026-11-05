#!/usr/bin/env bash
# E172 (Q142(k6), tools/claims-v3/e172/E172.md): pool 8 in E164's form on aifoundry1 card 1: the registered passes on aifoundry1 card 1, run by session_e172.sh after the stop-path test and the smoke gate
# have passed. A port of tools/claims-v3/e164/queue_e164.sh, unchanged but for E172's names, its passes (17210-17214: four planned as the
# budget allows; a fifth does not fit) and its first estimate (800 s, E164's 900 s scaled to 86 launches): a pass starts only if now +
# projected <= E172_T0 + 3,900 s - 60 s and <= E172_DEADLINE (required, the round's time gate less 10 minutes); projected is 800 s until a
# pass ends, then the longest measured; it stops at the first pass that does not fit, before the next pass on build/e172/STOP or
# build/claims-v3/STOP, and after any pass that fails. A pass in flight is never cut. Nothing is set.
#
#   E172_T0=<anchor epoch> E172_DEADLINE='<date>' bash tools/claims-v3/e172/queue_e172.sh > build/e172/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
T0=${E172_T0:?E172_T0 - the session anchor, epoch seconds}
DL=${E172_DEADLINE:?E172_DEADLINE - the last end of a pass, the round time gate less 10 minutes (no default)}         # E172 change 2
BUDGET_S=${E172_BUDGET_S:-3900}; RESERVE_S=${E172_RESERVE_S:-60}; longest=${E172_FIRST_S:-800}; GAP_S=${E172_GAP_S:-10}   # E172: 800 s for an 86-launch pass
BLOCK=${E172_BLOCK:-tools/claims-v3/e172/block_e172.sh}      # E172_BLOCK exists only for a stub self-test; session_e172.sh never sets it
PASSES=${E172_PASSES:-17210 17211 17212 17213 17214}          # E172_PASSES exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "$(date +%T) e172: E172_DEADLINE '$DL' is not a date: no pass runs"; exit 2; }
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e172
echo "$(date +%T) e172: passes ${PASSES}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s; E172_DROP_P2=${E172_DROP_P2:-0}"
n=0
for p in $PASSES; do
  if [ -e build/e172/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e172: done, $n passes, at $(rel "$(date +%s)")"
