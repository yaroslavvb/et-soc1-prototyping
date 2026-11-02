#!/usr/bin/env bash
# E134 (Q136): run E134's blocks on aifoundry3 card 0, one after another, in the registered sequence and inside the
# registered card budget (README.md, "Card budget"). A port of tools/claims-v3/e130/queue_e130.sh (itself E127's queue with
# E102's fixed sequence of two kinds of block), with E134's pass numbers, sequence, estimates and budget:
#
#   E134_T0=<epoch> setsid nohup bash tools/claims-v3/e134/queue_e134.sh > build/e134-logs/e134-queue.log 2>&1 < /dev/null &
#
# The sequence is A B A B A B A B B A (13410 13420 13411 13421 13412 13422 13413 13423 13424 13414): every registered rule
# has its three kept blocks of each kind after the sixth; the fourth of each kind is the margin against a set-aside; a fifth
# B (E134-R4 is the rule short of precision) and then a fifth A buy resolution and run only if they fit. Before each block it projects that block's end from the longest
# measured block of its kind so far (until one has ended, the registered estimates: A 300 s, B 240 s) and starts it only if
# the projected end is inside E134_BUDGET_S seconds of E134_T0 (default 2340: with the session-end read, at most the
# registered 40 card-minutes) and before E134_DEADLINE (default 2026-11-02 15:50 PST: every run ends by 16:00 PST). A block
# in flight is never cut. It stops before the next block when build/claims-v3/STOP or build/kinds-STOP exists and after any
# block that fails; after a block that found another user on the card (exit 3) it waits 5 min and tries that block once
# more, if that still fits. When the queue ends it reads `ettelem config` once more under the card lock with timeout 10 (the
# session-end read), unless E134_NO_END_READ is set. Nothing here sends any other device command.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
SEQ=${E134_SEQ:-13410 13420 13411 13421 13412 13422 13413 13423 13424 13414}
BUDGET_S=${E134_BUDGET_S:-2340}; DEADLINE=${E134_DEADLINE:-2026-11-02 15:50 PST}
longest_A=${E134_FIRST_A_S:-300}; longest_B=${E134_FIRST_B_S:-240}; seen_A=; seen_B=
GAP_S=${E134_GAP_S:-2}   # E134: 2 s between blocks (E130's 5 s); each block already ends with its own 5 s settle
BLOCK=${E134_BLOCK:-tools/claims-v3/e134/block_e134.sh}
t_start=${E134_T0:-$(date +%s)}; done_n=0
deadline=$(date -d "$DEADLINE" +%s 2>/dev/null || echo $((t_start + 3 * 3600)))
kind_of() { case "$1" in 1341?) echo A ;; 1342?) echo B ;; *) echo X ;; esac; }
est_of() { case "$1" in A) echo "$longest_A" ;; B) echo "$longest_B" ;; *) echo 9999 ;; esac; }
fits() { local now el; now=$(date +%s); el=$((now - t_start))
  [ $((el + $1)) -le "$BUDGET_S" ] && [ $((now + $1)) -le "$deadline" ]; }
end_read() {
  [ -n "${E134_NO_END_READ:-}" ] && return 0
  mkdir -p build/e134-logs
  ( exec 9<>/run/lock/etsoc-shire0.lock && flock -w 60 9 &&
    LD_LIBRARY_PATH=/opt/et/lib timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 ) \
    > build/e134-logs/config-session-end.json
  date +%s > build/e134-logs/config-session-end.json.time
  echo "$(date +%T) session-end read: $(cat build/e134-logs/config-session-end.json)"
  command -v et-who > /dev/null && et-who 2>&1 | head -3 | sed "s/^/$(date +%T) et-who: /"
}
echo "$(date +%T) queue: blocks $SEQ, budget ${BUDGET_S} s from $(date -d @"$t_start" +%T), deadline $DEADLINE, first estimates A ${longest_A} s, B ${longest_B} s"
last=${SEQ##* }
for i in $SEQ; do
  for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; end_read; exit 0; }; done
  k=$(kind_of "$i"); e=$(est_of "$k")
  if ! fits "$e"; then
    echo "$(date +%T) budget: stopping before p$i (elapsed $(( $(date +%s) - t_start )) s, longest $k block $e s, $done_n blocks done)"
    end_read; exit 0
  fi
  echo "$(date +%T) p$i ($k) starts (elapsed $(( $(date +%s) - t_start )) s)"
  t0=$(date +%s)
  bash "$BLOCK" "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( $(date +%s) - t0 )) s)"
  if [ $rc -eq 3 ]; then
    sleep 300
    if fits "$e"; then
      t0=$(date +%s)
      bash "$BLOCK" "$i" < /dev/null; rc=$?
      echo "$(date +%T) p$i retry rc=$rc"
    else
      echo "$(date +%T) budget: no retry of p$i"; end_read; exit 3
    fi
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; end_read; exit "$rc"; }
  d=$(( $(date +%s) - t0 ))
  case "$k" in      # the registered estimate holds until the first block of its kind ends
    A) if [ -z "$seen_A" ] || [ "$d" -gt "$longest_A" ]; then longest_A=$d; fi; seen_A=1 ;;
    B) if [ -z "$seen_B" ] || [ "$d" -gt "$longest_B" ]; then longest_B=$d; fi; seen_B=1 ;;
  esac
  done_n=$((done_n + 1))
  [ "$i" != "$last" ] && sleep "$GAP_S"
done
echo "$(date +%T) queue done: $done_n blocks, $(( $(date +%s) - t_start )) s since the session start"
end_read
