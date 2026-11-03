#!/usr/bin/env bash
# E145 (Q138): the registered blocks on aifoundry1 card 1, run by session_e145.sh after the stop-path test and the smoke gate have
# passed. A port of tools/claims-v3/e137/queue_e137.sh (the budget anchored on the session's T0, card 1) with
# tools/claims-v3/e138/queue_e138.sh's two kinds of block and their per-kind estimates, each change marked E145:
#   1. the registered sequence (e145_common.SEQUENCE): 14510 14530 14511 14512 14513 14531 14514 14515 14516 14532 14517 ... 14523,
#      A blocks (the control) second, sixth and tenth, B blocks everywhere else, each tools/claims-v3/e145/block_e145.sh with
#      V3_DEVICE=1;
#   2. the budget: a block starts only if now + projected <= E145_T0 + E145_BUDGET_S - E145_RESERVE_S (3000 - 90 s: the 50
#      card-minutes, with the closing config read and a margin inside them) and now + projected <= the deadline, 2026-11-02 23:30 PST
#      (every run ends by 23:50 PST); projected is the longest measured block of its kind, or until one has ended the registered
#      estimates, B 200 s and A 160 s (E138's B blocks took 177-178 s on aifoundry3; card 1's runs take about 4.6 s, E137);
#   3. it stops before the next block on build/e145/STOP, build/claims-v3/STOP or build/kinds-STOP, and after any block that fails
#      (rc 3 = another user on the card or a device process; rc 1 = the block failed, a registered stop included: never retried).
# A block in flight is never cut. No block is added after any reduction is read. Nothing is set.
#
#   E145_T0=<anchor epoch> bash tools/claims-v3/e145/queue_e145.sh > build/e145/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
T0=${E145_T0:?E145_T0 - the session anchor, epoch seconds}
BUDGET_S=${E145_BUDGET_S:-3000}; RESERVE_S=${E145_RESERVE_S:-90}; GAP_S=${E145_GAP_S:-5}
longest_B=${E145_FIRST_B_S:-200}; longest_A=${E145_FIRST_A_S:-160}; seen_B=; seen_A=
BLOCK=${E145_BLOCK:-tools/claims-v3/e145/block_e145.sh}      # E145_BLOCK exists only for a stub self-test; session_e145.sh never sets it
SEQ=${E145_SEQ:-$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e145_common as e; print(" ".join(map(str, e.SEQUENCE)))' tools/claims-v3/e145)}
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E145_DEADLINE:-2026-11-02 23:30 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
kind_of() { case "$1" in 1451?|1452?) echo B ;; 1453?) echo A ;; *) echo X ;; esac; }
est_of() { case "$1" in B) echo "$longest_B" ;; A) echo "$longest_A" ;; *) echo 99999 ;; esac; }
mkdir -p build/e145
echo "$(date +%T) e145: blocks ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimates B ${longest_B} s, A ${longest_A} s"
n=0; nB=0; nA=0
for p in $SEQ; do
  if [ -e build/e145/STOP ] || [ -e build/claims-v3/STOP ] || [ -e build/kinds-STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e145: done, $n blocks (B $nB, A $nA), at $(rel "$(date +%s)")"
