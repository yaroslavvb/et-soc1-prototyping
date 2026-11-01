#!/usr/bin/env bash
# E102 (Q132): run E102's blocks on aifoundry1 card 1, one after another, inside the registered card budget (E102.md, "Card budget"). A port of
# queue_e94.sh with three kinds of block and a fixed sequence: G T T I, G T I, G T I, I, I. A T never follows an I, so a float train never starts on a cooled card; every
# registered rule needs at least three of each, and the sequence has them after its ninth block; the last two I blocks buy resolution and go first if time runs short.
#
#   setsid nohup bash tools/claims-v3/kinds/queue_e102.sh > build/e102-queue.log 2>&1 < /dev/null &
#
# Before each block it projects that block's end from the longest measured block of its kind so far (until one has ended, the registered estimates: G
# 440 s, T 320 s, I 150 s) and starts it only if the projected end is inside E102_BUDGET_S seconds of the queue's start (default 3400, about 57 min)
# and before the fixed deadline, 2026-11-01 07:00 PST (the run's window ends 07:15 PST; an epoch, so that the clock change cannot confuse it). A
# block in flight is never cut. It stops before the next block when build/claims-v3/STOP or build/kinds-STOP exists and after any block that fails; after
# a block that found another user on the card (exit 3) it waits 5 min and tries it once more, if that still fits.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
SEQ=${E102_SEQ:-10210 10220 10221 10230 10211 10222 10231 10212 10223 10232 10233 10234}
BUDGET_S=${E102_BUDGET_S:-3400}
longest_G=440; longest_T=320; longest_I=150
t_start=$(date +%s); done_n=0
deadline=$(date -d '2026-11-01 07:00 PST' +%s)
kind_of() { case "$1" in 1021?) echo G ;; 1022?) echo T ;; 1023?) echo I ;; *) echo X ;; esac; }
est_of() { case "$1" in G) echo "$longest_G" ;; T) echo "$longest_T" ;; I) echo "$longest_I" ;; *) echo 9999 ;; esac; }
fits() { local now el; now=$(date +%s); el=$((now - t_start))
  [ $((el + $1)) -le "$BUDGET_S" ] && [ $((now + $1)) -le "$deadline" ]; }
echo "$(date +%T) queue: blocks $SEQ, budget ${BUDGET_S} s, deadline 2026-11-01 07:00 PST"
for i in $SEQ; do
  for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  k=$(kind_of "$i"); e=$(est_of "$k")
  if ! fits "$e"; then
    echo "$(date +%T) budget: stopping before p$i (elapsed $(( $(date +%s) - t_start )) s, longest $k block $e s, $done_n blocks done)"
    exit 0
  fi
  echo "$(date +%T) p$i ($k) starts (elapsed $(( $(date +%s) - t_start )) s)"
  t0=$(date +%s)
  bash tools/claims-v3/kinds/block_e102.sh "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( $(date +%s) - t0 )) s)"
  if [ $rc -eq 3 ]; then
    sleep 300
    if fits "$e"; then
      t0=$(date +%s)
      bash tools/claims-v3/kinds/block_e102.sh "$i" < /dev/null; rc=$?
      echo "$(date +%T) p$i retry rc=$rc"
    else
      echo "$(date +%T) budget: no retry of p$i"; exit 3
    fi
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; exit "$rc"; }
  d=$(( $(date +%s) - t0 ))
  case "$k" in
    G) [ "$d" -gt "$longest_G" ] && longest_G=$d ;;
    T) [ "$d" -gt "$longest_T" ] && longest_T=$d ;;
    I) [ "$d" -gt "$longest_I" ] && longest_I=$d ;;
  esac
  done_n=$((done_n + 1))
  sleep 5
done
echo "$(date +%T) queue done: $done_n blocks, $(( $(date +%s) - t_start )) s"
