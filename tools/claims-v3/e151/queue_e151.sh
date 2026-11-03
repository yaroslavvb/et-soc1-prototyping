#!/usr/bin/env bash
# E151 (Q139): the registered blocks on aifoundry3 card 0, run by session_e151.sh after the stop-path test and the smoke gate have
# passed. A port of tools/claims-v3/e145/queue_e145.sh (the budget anchored on the session's T0, two kinds of block with per-kind
# estimates), each change marked E151:
#   1. the registered sequence (e151_common.SEQUENCE): 15110 ... 15119 (ten B blocks), 15130 (one A block, the in-session control),
#      then 15120 15131 15132 only if the budget still allows; each tools/claims-v3/e151/block_e151.sh, no V3_DEVICE;
#   2. the budget: a block starts only if now + projected <= E151_T0 + E151_BUDGET_S - E151_RESERVE_S (2100 - 45 s: the 35
#      card-minutes, with the closing config read and a margin inside them) and now + projected <= the deadline, 2026-11-03 11:25 PST
#      (every run ends by 11:30 PST); projected is the longest measured block of its kind, or until one has ended the registered
#      estimates, B 185 s and A 140 s (on this card E138's B blocks took 177-178 s and E130's A blocks 133-134 s);
#   3. it stops before the next block on build/e151/STOP, build/claims-v3/STOP or build/kinds-STOP, and after any block that fails
#      (rc 3 = another user on the card or a device process; rc 1 = the block failed, a registered stop included: never retried).
# A block in flight is never cut. No block is added after any reduction is read. Nothing is set.
#
#   E151_T0=<anchor epoch> bash tools/claims-v3/e151/queue_e151.sh > build/e151/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
T0=${E151_T0:?E151_T0 - the session anchor, epoch seconds}
BUDGET_S=${E151_BUDGET_S:-2100}; RESERVE_S=${E151_RESERVE_S:-45}; GAP_S=${E151_GAP_S:-5}
longest_B=${E151_FIRST_B_S:-185}; longest_A=${E151_FIRST_A_S:-140}; seen_B=; seen_A=
BLOCK=${E151_BLOCK:-tools/claims-v3/e151/block_e151.sh}      # E151_BLOCK exists only for a stub self-test; session_e151.sh never sets it
SEQ=${E151_SEQ:-$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e151_common as e; print(" ".join(map(str, e.SEQUENCE)))' tools/claims-v3/e151)}
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E151_DEADLINE:-2026-11-03 11:25 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
kind_of() { case "$1" in 1511?|1512?) echo B ;; 1513?) echo A ;; *) echo X ;; esac; }
est_of() { case "$1" in B) echo "$longest_B" ;; A) echo "$longest_A" ;; *) echo 99999 ;; esac; }
mkdir -p build/e151
echo "$(date +%T) e151: blocks ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimates B ${longest_B} s, A ${longest_A} s"
n=0; nB=0; nA=0
for p in $SEQ; do
  if [ -e build/e151/STOP ] || [ -e build/claims-v3/STOP ] || [ -e build/kinds-STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  k=$(kind_of "$p"); e=$(est_of "$k")
  now=$(date +%s)
  if [ $((now + e)) -gt "$limit" ] || [ $((now + e)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p ($k; now $(rel "$now"), projected ${e} s, would end $(rel $((now + e))) > $(rel "$limit") or the deadline)"
    break
  fi
  echo "$(date +%T) p$p ($k) starts at $(rel "$now") (projected ${e} s)"
  t0=$(date +%s)
  bash "$BLOCK" "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  case "$k" in      # the registered estimate holds until the first block of its kind ends
    B) if [ -z "$seen_B" ] || [ "$d" -gt "$longest_B" ]; then longest_B=$d; fi; seen_B=1; nB=$((nB + 1)) ;;
    A) if [ -z "$seen_A" ] || [ "$d" -gt "$longest_A" ]; then longest_A=$d; fi; seen_A=1; nA=$((nA + 1)) ;;
  esac
  n=$((n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) e151: done, $n blocks (B $nB, A $nA), at $(rel "$(date +%s)")"
