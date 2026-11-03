#!/usr/bin/env bash
# E152 (Q139): run passes <first> .. <first>+<n>-1 of block_e152.sh on aifoundry3 card 0, one after another, inside the
# registered card budget (README.md, "Card budget"). A port of tools/claims-v3/e127/queue_e127.sh with block_e152.sh, the
# budget counted in SECONDS from the session's start (E152_T0, the epoch of the session-start config read), and E152's
# deadline:
#
#   E152_T0=<epoch> setsid nohup bash tools/claims-v3/e152/queue_e152.sh <first-pass> <n-passes> > build/e152-logs/e152-queue.log 2>&1 < /dev/null &
#
# Before each pass it projects the pass's end from the longest measured pass so far (E152_FIRST_S, 360 s, until the first
# one ends) and starts the pass only if the projected end is inside E152_BUDGET_S seconds of E152_T0 (default 2160: with
# the session-end read and the release, at most the registered 40 card-minutes) and before E152_DEADLINE (default
# 2026-11-03 11:20 PST: every run ends by 11:30 PST). A pass in flight is never cut. It stops before the next pass when
# build/claims-v3/STOP or build/kinds-STOP exists and after any pass that fails; after a pass that found another user on
# the card (exit 3) it waits 5 min and tries that pass once more, if that still fits. When the queue ends it reads
# `ettelem config` once more under the card lock with timeout 10, through E128's guard (the session-end read), unless
# E152_NO_END_READ is set.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
p=${1:?first pass}; n=${2:?number of passes}
BUDGET_S=${E152_BUDGET_S:-2160}; DEADLINE=${E152_DEADLINE:-2026-11-03 11:20 PST}; longest=${E152_FIRST_S:-360}
GAP_S=${E152_GAP_S:-15}
BLOCK=${E152_BLOCK:-tools/claims-v3/e152/block_e152.sh}
t_start=${E152_T0:-$(date +%s)}; done_n=0
deadline=$(date -d "$DEADLINE" +%s 2>/dev/null || echo $((t_start + 3 * 3600)))
fits() { local now el; now=$(date +%s); el=$((now - t_start))
  [ $((el + longest)) -le "$BUDGET_S" ] && [ $((now + longest)) -le "$deadline" ]; }
end_read() {
  [ -n "${E152_NO_END_READ:-}" ] && return 0
  mkdir -p build/e152-logs
  ( exec 9<>/run/lock/etsoc-shire0.lock && flock -w 60 9 &&
    LD_LIBRARY_PATH=/opt/et/lib timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1 ) \
    > build/e152-logs/config-session-end.json
  date +%s > build/e152-logs/config-session-end.json.time
  echo "$(date +%T) session-end read: $(cat build/e152-logs/config-session-end.json)"
  command -v et-who > /dev/null && et-who 2>&1 | head -3 | sed "s/^/$(date +%T) et-who: /"
}
echo "$(date +%T) queue: passes $p..$((p + n - 1)), budget ${BUDGET_S} s from $(date -d @"$t_start" +%T), deadline $DEADLINE, first-pass estimate ${longest} s"
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; end_read; exit 0; }; done
  if ! fits; then
    echo "$(date +%T) budget: stopping before p$i (elapsed $(( $(date +%s) - t_start )) s, longest pass ${longest} s, $done_n passes done)"
    end_read; exit 0
  fi
  echo "$(date +%T) p$i starts (elapsed $(( $(date +%s) - t_start )) s)"
  t0=$(date +%s)
  bash "$BLOCK" "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( $(date +%s) - t0 )) s)"
  if [ $rc -eq 3 ]; then
    sleep 300
    if fits; then
      t0=$(date +%s)
      bash "$BLOCK" "$i" < /dev/null; rc=$?
      echo "$(date +%T) p$i retry rc=$rc"
    else
      echo "$(date +%T) budget: no retry of p$i"; end_read; exit 3
    fi
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; end_read; exit "$rc"; }
  d=$(( $(date +%s) - t0 ))
  if [ "$done_n" -eq 0 ] || [ $d -gt $longest ]; then longest=$d; fi   # the estimate holds until the first pass ends
  done_n=$((done_n + 1))
  [ "$i" -lt $((p + n - 1)) ] && sleep "$GAP_S"
done
echo "$(date +%T) queue done: $done_n passes, $(( $(date +%s) - t_start )) s since the session start"
end_read
