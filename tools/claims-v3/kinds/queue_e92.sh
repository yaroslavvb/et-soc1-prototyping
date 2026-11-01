#!/usr/bin/env bash
# E92 (Q132): run passes <first> .. <first>+<n>-1 of block_e92.sh on the local card, one after another, inside the
# registered card budget (E92.md, "Card budget"). A port of queue_e78.sh (sha256 0232c08c...) with block_e92.sh, E92's
# budget and deadline, and no tier-1 fallback (every E92 item runs in every pass; there is no shorter pass):
#
#   setsid nohup bash tools/claims-v3/kinds/queue_e92.sh <first-pass> <n-passes> > build/e92-queue.log 2>&1 < /dev/null &
#
# Before each pass it projects the pass's end from the longest measured pass so far (E92_FIRST_S, 620 s, until the
# first one ends) and starts the pass only if the projected end is inside E92_BUDGET_MIN card-minutes of the queue's start
# (default 41: with the smoke and the session's config reads, at most the registered 45) and before E92_DEADLINE
# (default 2026-11-01 06:45 PST: every run ends by 07:15 PST; a full date, because the clocks go back at 02:00 PDT tonight, a marked E92 change to E90's `today HH:MM`). A pass in flight is never cut. It stops before the next
# pass when build/claims-v3/STOP or build/kinds-STOP exists and after any pass that fails; after a pass that found
# another user on the card (exit 3) it waits 5 min and tries that pass once more, if that still fits.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
p=${1:?first pass}; n=${2:?number of passes}
BUDGET_MIN=${E92_BUDGET_MIN:-41}; DEADLINE=${E92_DEADLINE:-2026-11-01 06:45 PST}; longest=${E92_FIRST_S:-620}
t_start=$(date +%s); done_n=0
deadline=$(date -d "$DEADLINE" +%s 2>/dev/null || echo $((t_start + 3 * 3600)))
fits() { local now el; now=$(date +%s); el=$((now - t_start))
  [ $((el + longest)) -le $((BUDGET_MIN * 60)) ] && [ $((now + longest)) -le "$deadline" ]; }
echo "$(date +%T) queue: passes $p..$((p + n - 1)), budget ${BUDGET_MIN} card-min, deadline $DEADLINE, first-pass estimate ${longest} s"
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  if ! fits; then
    echo "$(date +%T) budget: stopping before p$i (elapsed $(( ($(date +%s) - t_start) / 60 )) min, longest pass $((longest / 60)) min, $done_n passes done)"
    exit 0
  fi
  echo "$(date +%T) p$i starts (elapsed $(( ($(date +%s) - t_start) / 60 )) card-min)"
  t0=$(date +%s)
  bash tools/claims-v3/kinds/block_e92.sh "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( ($(date +%s) - t0) / 60 )) min)"
  if [ $rc -eq 3 ]; then
    sleep 300
    if fits; then
      t0=$(date +%s)
      bash tools/claims-v3/kinds/block_e92.sh "$i" < /dev/null; rc=$?
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
echo "$(date +%T) queue done: $done_n passes, $(( ($(date +%s) - t_start) / 60 )) card-min"
