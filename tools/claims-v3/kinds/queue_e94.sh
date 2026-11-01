#!/usr/bin/env bash
# E94 (Q132): run passes <first> .. <first>+<n>-1 of block_e94.sh on aifoundry1 card 1, one after another, inside the
# registered card budget (E94.md, "Card budget"). A port of queue_e93.sh with block_e94.sh, the budget in SECONDS. Every E94 item runs in every
# pass; there is no shorter pass.
#
#   setsid nohup bash tools/claims-v3/kinds/queue_e94.sh <first-pass> <n-passes> > build/e94-queue.log 2>&1 < /dev/null &
#
# Before each pass it projects the pass's end from the longest measured pass so far (E94_FIRST_S, 730 s, until the first
# one ends) and starts the pass only if the projected end is inside E94_BUDGET_S seconds of the queue's start (default
# 2400: with the smoke, the claim and the release, the registered card budget) and before the fixed deadline,
# 2026-11-01 07:00 PST (the run's window ends 07:15 PST; an epoch, so that the clock change at 02:00 PDT cannot confuse it).
# A pass in flight is never cut. It stops before the next pass when build/claims-v3/STOP or build/kinds-STOP exists and
# after any pass that fails; after a pass that found another user on the card (exit 3) it waits 5 min and tries that pass
# once more, if that still fits.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
p=${1:?first pass}; n=${2:?number of passes}
BUDGET_S=${E94_BUDGET_S:-2400}; longest=${E94_FIRST_S:-730}
t_start=$(date +%s); done_n=0
deadline=$(date -d '2026-11-01 07:00 PST' +%s)
fits() { local now el; now=$(date +%s); el=$((now - t_start))
  [ $((el + longest)) -le "$BUDGET_S" ] && [ $((now + longest)) -le "$deadline" ]; }
echo "$(date +%T) queue: passes $p..$((p + n - 1)), budget ${BUDGET_S} s, deadline 2026-11-01 07:00 PST, first-pass estimate ${longest} s"
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  if ! fits; then
    echo "$(date +%T) budget: stopping before p$i (elapsed $(( $(date +%s) - t_start )) s, longest pass ${longest} s, $done_n passes done)"
    exit 0
  fi
  echo "$(date +%T) p$i starts (elapsed $(( $(date +%s) - t_start )) s)"
  t0=$(date +%s)
  bash tools/claims-v3/kinds/block_e94.sh "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( $(date +%s) - t0 )) s)"
  if [ $rc -eq 3 ]; then
    sleep 300
    if fits; then
      t0=$(date +%s)
      bash tools/claims-v3/kinds/block_e94.sh "$i" < /dev/null; rc=$?
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
