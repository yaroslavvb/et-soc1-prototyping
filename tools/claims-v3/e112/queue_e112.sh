#!/usr/bin/env bash
# E112 (Q133): run the session's measured passes on aifoundry1 card 1 in the registered order, one after another, inside the
# registered card budget IN SECONDS (E112.md, "Card budget"). A port of tools/claims-v3/signloc/queue_e108.sh (itself a port of
# tools/claims-v3/kinds/queue_e86.sh, the queue E91 ran) with these changes, each marked E112:
#   1. two kinds of pass: "a:<pass>" runs tools/claims-v3/kinds/block_e86.sh (E86's pass, the one E91 registered) and
#      "b:<pass>" runs tools/claims-v3/kinds/block_e95.sh (E95's pass); both blocks are unchanged;
#   2. the budget is anchored on the claim's own time, E112_T0 (epoch seconds), not on the queue's start: an entry starts
#      only if now + projected <= E112_T0 + E112_BUDGET_S - E112_RESERVE_S (3600 - 120) and now + projected <= the deadline,
#      2026-11-01 18:45 PST; projected is the longest measured pass OF THAT KIND so far, or the kind's first estimate
#      (E112_FIRST_A_S 390, E112_FIRST_B_S 560) until one has ended; exact integer seconds, no rounding;
#   3. an entry that does not fit is skipped and logged, and the queue tries the next entry (the order is the priority);
#   4. after the last entry it reads the card's static configuration once more, read only, under card 1's lock with
#      `timeout 10` (the session-end read), unless another process holds the card.
# A pass in flight is never cut. It stops before the next entry when build/claims-v3/STOP or build/e112-STOP exists and after
# any pass that fails; after a pass that found another user on the card (exit 3) it waits 5 min and tries that pass once more,
# if that still fits.
#
#   E112_T0=<claim epoch> setsid nohup bash tools/claims-v3/e112/queue_e112.sh a:11210 ... b:11253 > build/e112-queue.log 2>&1 < /dev/null &
#
# E112_BLOCK_A / E112_BLOCK_B / E112_GAP_S / E112_NO_END_READ exist only for selftest_e112.py's stub run; run_e112.sh never
# sets them. No knob is written: no governor, TDP, threshold or clock set, no reset, no --reset-ms.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
T0=${E112_T0:?E112_T0 - the time of the claim post, epoch seconds}
BUDGET_S=${E112_BUDGET_S:-3600}; RESERVE_S=${E112_RESERVE_S:-120}; GAP_S=${E112_GAP_S:-15}
BLOCK_A=${E112_BLOCK_A:-tools/claims-v3/kinds/block_e86.sh}; BLOCK_B=${E112_BLOCK_B:-tools/claims-v3/kinds/block_e95.sh}
la=${E112_FIRST_A_S:-390}; lb=${E112_FIRST_B_S:-560}; na=0; nb=0; done_n=0; skipped=0
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E112_DEADLINE:-2026-11-01 18:45 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
echo "$(date +%T) queue: $*; budget ${BUDGET_S} s from the claim ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimates a ${la} s, b ${lb} s"
for e in "$@"; do
  kind=${e%%:*}; p=${e#*:}
  case "$kind:$p" in a:[0-9]*) blk=$BLOCK_A; proj=$la ;; b:[0-9]*) blk=$BLOCK_B; proj=$lb ;;
    *) echo "$(date +%T) bad entry $e"; exit 2 ;; esac
  for f in build/claims-v3/STOP build/e112-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before $e"; break 2; }; done
  now=$(date +%s)
  if [ $((now + proj)) -gt "$limit" ] || [ $((now + proj)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: skipping $e (now $(rel "$now"), projected ${proj} s, ends $(rel $((now + proj))) > $(rel "$limit"))"
    skipped=$((skipped + 1)); continue
  fi
  echo "$(date +%T) $e starts at $(rel "$now") (projected ${proj} s, end by $(rel $((now + proj))))"
  t0=$(date +%s)
  bash "$blk" "$p" < /dev/null; rc=$?
  echo "$(date +%T) $e rc=$rc ($(( $(date +%s) - t0 )) s)"
  if [ $rc -eq 3 ]; then
    sleep 300
    now=$(date +%s)
    if [ $((now + proj)) -le "$limit" ] && [ $((now + proj)) -le "$deadline" ]; then
      t0=$(date +%s)
      bash "$blk" "$p" < /dev/null; rc=$?
      echo "$(date +%T) $e retry rc=$rc"
    else
      echo "$(date +%T) budget: no retry of $e"; break
    fi
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after $e (rc $rc)"; break; }
  d=$(( $(date +%s) - t0 ))
  if [ "$kind" = a ]; then { [ "$na" -eq 0 ] || [ $d -gt "$la" ]; } && la=$d; na=$((na + 1)); fi   # the estimate holds until the first pass of its kind ends
  if [ "$kind" = b ]; then { [ "$nb" -eq 0 ] || [ $d -gt "$lb" ]; } && lb=$d; nb=$((nb + 1)); fi
  done_n=$((done_n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) passes done: $done_n (a $na, b $nb), skipped $skipped, at $(rel "$(date +%s)")"
# E112 change 4: the session-end read of the card's static configuration (read only: `ettelem config` has no setter)
if [ -z "${E112_NO_END_READ:-}" ] && [ -z "${V3_DRY:-}" ]; then
  mkdir -p build/e112-logs
  w=$(timeout 20 et-who 2>&1 | head -5)
  echo "$(date +%T) et-who: $w"
  if printf '%s' "$w" | grep -q 'No process holds'; then
    ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 build/ettelem/ettelem config 2>/dev/null < /dev/null |
      grep '^{' | tail -1 > build/e112-logs/config-session-end.json
    date -Iseconds > build/e112-logs/config-session-end.json.time
    echo "$(date +%T) session-end config: $(cat build/e112-logs/config-session-end.json)"
  else
    echo "$(date +%T) session-end config: not read (the card is not free)"
  fi
fi
echo "$(date +%T) queue done at $(rel "$(date +%s)")"
