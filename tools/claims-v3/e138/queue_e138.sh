#!/usr/bin/env bash
# E130 (Q136): run E130's blocks on aifoundry3 card 0, one after another, in the registered sequence and inside the
# registered card budget (README.md, "Card budget"). A port of tools/claims-v3/e127/queue_e127.sh (the budget counted in
# SECONDS from the session's start, E138_T0, the epoch of the session-start config read; the session-end read) with
# queue_e102.sh's fixed sequence of two kinds of block and its per-kind estimates:
#
#   E138_T0=<epoch> setsid nohup bash tools/claims-v3/e138/queue_e138.sh > build/e138-logs/e138-queue.log 2>&1 < /dev/null &
#
# The sequence is B A B A B A B A B B (13810 13820 13811 13821 13812 13822 13813 13823 13814 13815): every registered rule
# has its three kept blocks of each kind after the sixth; the fourth A block is the A rules' margin against a set-aside, and
# the last two B blocks buy the B list's resolution (the last runs only if it fits). Before each block it
# projects that block's end from the longest measured block of its kind so far (until one has ended, the registered
# estimates: B 200 s, A 160 s) and starts it only if the projected end is inside E138_BUDGET_S seconds of E138_T0 (default
# 1740: with the session-end read, at most the registered 30 card-minutes) and before E138_DEADLINE (default 2026-11-02
# 15:50 PST: every run ends by 16:00 PST). A block in flight is never cut. It stops before the next block when
# build/claims-v3/STOP or build/kinds-STOP exists and after any block that fails; after a block that found another user
# on the card (exit 3) it waits 5 min and tries that block once more, if that still fits. When the queue ends it reads
# `ettelem config` once more under the card lock with timeout 10 (the session-end read), unless E138_NO_END_READ is set.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
SEQ=${E138_SEQ:-13810 13811 13812 13813 13814 13815 13816 13817 13818 13819}
BUDGET_S=${E138_BUDGET_S:-1740}; DEADLINE=${E138_DEADLINE:-2026-11-02 21:40 PST}
longest_B=${E138_FIRST_B_S:-200}; longest_A=${E138_FIRST_A_S:-160}; seen_B=; seen_A=
GAP_S=${E138_GAP_S:-5}
BLOCK=${E138_BLOCK:-tools/claims-v3/e138/block_e138.sh}
t_start=${E138_T0:-$(date +%s)}; done_n=0
deadline=$(date -d "$DEADLINE" +%s 2>/dev/null || echo $((t_start + 3 * 3600)))
kind_of() { case "$1" in 1381?) echo B ;; 1382?) echo A ;; *) echo X ;; esac; }
est_of() { case "$1" in B) echo "$longest_B" ;; A) echo "$longest_A" ;; *) echo 9999 ;; esac; }
fits() { local now el; now=$(date +%s); el=$((now - t_start))
  [ $((el + $1)) -le "$BUDGET_S" ] && [ $((now + $1)) -le "$deadline" ]; }
end_read() {
  [ -n "${E138_NO_END_READ:-}" ] && return 0
  mkdir -p build/e138-logs
  ( exec 9<>/run/lock/etsoc-shire0.lock && flock -w 60 9 &&
    LD_LIBRARY_PATH=/opt/et/lib timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 ) \
    > build/e138-logs/config-session-end.json
  date +%s > build/e138-logs/config-session-end.json.time
  echo "$(date +%T) session-end read: $(cat build/e138-logs/config-session-end.json)"
  command -v et-who > /dev/null && et-who 2>&1 | head -3 | sed "s/^/$(date +%T) et-who: /"
}
echo "$(date +%T) queue: blocks $SEQ, budget ${BUDGET_S} s from $(date -d @"$t_start" +%T), deadline $DEADLINE, first estimates B ${longest_B} s, A ${longest_A} s"
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
    B) if [ -z "$seen_B" ] || [ "$d" -gt "$longest_B" ]; then longest_B=$d; fi; seen_B=1 ;;
    A) if [ -z "$seen_A" ] || [ "$d" -gt "$longest_A" ]; then longest_A=$d; fi; seen_A=1 ;;
  esac
  done_n=$((done_n + 1))
  [ "$i" != "$last" ] && sleep "$GAP_S"
done
echo "$(date +%T) queue done: $done_n blocks, $(( $(date +%s) - t_start )) s since the session start"
end_read
