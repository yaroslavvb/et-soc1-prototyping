#!/usr/bin/env bash
# E128 (Q136): run passes <first> .. <first>+<n>-1 of block_e128.sh on aifoundry1 card 1, one after another, inside the registered card budget (E128.md,
# "Card budget"). A port of tools/claims-v3/signloc/queue_e108.sh with block_e128.sh and E128's deadline. Every E128 item runs in every pass; there is no
# shorter pass.
#
#   setsid nohup bash tools/claims-v3/e128/queue_e128.sh <first-pass> <n-passes> > build/e128-queue.log 2>&1 < /dev/null &
#
# Before each pass it projects the pass's end from the longest measured pass so far (E128_FIRST_S, 420 s, until the first one ends) and starts the pass only
# if the projected end is inside E128_BUDGET_S seconds of the queue's start (default 2040: with the smoke, the read-back and the claim, the registered card
# budget of 40 card-minutes) and before the fixed deadline, 2026-11-02 15:50 PST (Q136's "every run ends by 16:00 PST", less a margin; an epoch). A pass in
# flight is never cut. It stops before the next pass when build/claims-v3/STOP or build/e128-STOP exists and after any pass that fails; after a pass that
# found another user on the card (exit 3) it waits 5 min and tries that pass once more, if that still fits.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
p=${1:?first pass}; n=${2:?number of passes}
BUDGET_S=${E128_BUDGET_S:-2040}; longest=${E128_FIRST_S:-420}
t_start=$(date +%s); done_n=0
deadline=$(date -d '2026-11-02 15:50 PST' +%s)
fits() { local now el; now=$(date +%s); el=$((now - t_start))
  [ $((el + longest)) -le "$BUDGET_S" ] && [ $((now + longest)) -le "$deadline" ]; }
echo "$(date +%T) queue: passes $p..$((p + n - 1)), budget ${BUDGET_S} s, deadline 2026-11-02 15:50 PST, first-pass estimate ${longest} s"
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/e128-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  if ! fits; then
    echo "$(date +%T) budget: stopping before p$i (elapsed $(( $(date +%s) - t_start )) s, longest pass ${longest} s, $done_n passes done)"
    exit 0
  fi
  echo "$(date +%T) p$i starts (elapsed $(( $(date +%s) - t_start )) s)"
  t0=$(date +%s)
  bash tools/claims-v3/e128/block_e128.sh "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( $(date +%s) - t0 )) s)"
  if [ $rc -eq 3 ]; then
    sleep 300
    if fits; then
      t0=$(date +%s)
      bash tools/claims-v3/e128/block_e128.sh "$i" < /dev/null; rc=$?
      echo "$(date +%T) p$i retry rc=$rc"
    else
      echo "$(date +%T) budget: no retry of p$i"; exit 3
    fi
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; exit "$rc"; }
  d=$(( $(date +%s) - t0 ))
  if [ "$done_n" -eq 0 ] || [ $d -gt $longest ]; then longest=$d; fi   # the estimate holds until the first pass ends
  done_n=$((done_n + 1))
  sleep 15
done
echo "$(date +%T) queue done: $done_n passes, $(( $(date +%s) - t_start )) s"
