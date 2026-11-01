#!/usr/bin/env bash
# E97 (Q132): the card session on the local card, inside the registered budget (E97.md, "Card budget"). A port of
# tools/claims-v3/e89/queue_e89.sh with a full-date deadline (the clocks go back at 02:00 PDT tonight), Part B after Part A, and E95's
# one retry after finding another user on the card:
#
#   setsid nohup bash tools/claims-v3/e97/queue_e97.sh > build/e97-queue.log 2>&1 < /dev/null &
#
# Part A, passes 9710 and 9711: each starts only if its projected end, from the longest pass so far (E97_FIRST_S, 4,260 s, until the first
# one ends), is before the deadline. Then Part B, pass 9720, with whatever time is left; run_e97b.py's frozen plan decides what fits. So the
# steady holds are cut first and Part A's second pass next, the brief's order. It stops before the next pass when build/claims-v3/STOP or
# build/e97-STOP exists, after a pass that fails, and after a second finding of another user on the card.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export E97_DEADLINE=${E97_DEADLINE:-2026-11-01 07:13 PST}
longest=${E97_FIRST_S:-4260}
PASSES=${E97_PASSES:-"9710 9711"}
t_start=$(date +%s); done_n=0
deadline=$(date -d "$E97_DEADLINE" +%s 2>/dev/null || echo $((t_start + 5 * 3600)))
echo "$(date +%T) queue: Part A passes $PASSES, then Part B 9720; deadline $E97_DEADLINE ($deadline); first-pass estimate ${longest} s"
stopfile() { for f in build/claims-v3/STOP build/e97-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before $1"; return 0; }; done; return 1; }
for i in $PASSES; do
  stopfile "p$i" && exit 0
  now=$(date +%s)
  if [ $((now + longest)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: no p$i (elapsed $(( (now - t_start) / 60 )) min, longest pass $((longest / 60)) min, $done_n passes done); on to Part B"
    break
  fi
  echo "$(date +%T) p$i starts (elapsed $(( (now - t_start) / 60 )) min)"
  t0=$(date +%s)
  bash tools/claims-v3/e97/block_e97.sh "$i" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc ($(( ($(date +%s) - t0) / 60 )) min)"
  if [ $rc -eq 3 ]; then
    sleep 300
    if [ $(( $(date +%s) + longest )) -le "$deadline" ]; then
      t0=$(date +%s)
      bash tools/claims-v3/e97/block_e97.sh "$i" < /dev/null; rc=$?
      echo "$(date +%T) p$i retry rc=$rc"
    else
      echo "$(date +%T) budget: no retry of p$i"; exit 3
    fi
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; exit "$rc"; }
  d=$(( $(date +%s) - t0 ))
  if [ "$done_n" -eq 0 ] || [ $d -gt $longest ]; then longest=$d; fi
  done_n=$((done_n + 1))
done
stopfile p9720 && exit 0
echo "$(date +%T) p9720 (the holds) starts (elapsed $(( ($(date +%s) - t_start) / 60 )) min, $(( (deadline - $(date +%s)) / 60 )) min left)"
t0=$(date +%s)
bash tools/claims-v3/e97/block_e97.sh 9720 --holds < /dev/null; rc=$?
echo "$(date +%T) p9720 rc=$rc ($(( ($(date +%s) - t0) / 60 )) min)"
echo "$(date +%T) queue done: $done_n Part A passes, Part B rc $rc, $(( ($(date +%s) - t_start) / 60 )) min"
exit "$rc"
