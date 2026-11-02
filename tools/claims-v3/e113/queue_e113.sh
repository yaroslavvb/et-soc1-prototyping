#!/usr/bin/env bash
# E113 (Q133): the registered passes on aifoundry3, run by session_e113.sh after the smoke gate passed. Passes 1131-1137, each
# hl/block.sh unchanged (HL_GEN=build/hl-gen6-e113, HL_EXPN=e113: E67's and E70's protocol, launch at 58 C after 59 C, 4 s runs,
# two burn-in runs, anchor_pi first and last, the rest shuffled with the pass number). It stops before the next pass on
# build/e113-STOP, build/hl-STOP or build/claims-v3/STOP, after any pass that fails, or when the pass would end past
# E113_DEADLINE_S. A pass in flight is never cut. The longest pass so far is the estimate (first 300 s).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
. tools/claims-v3/e113/items_e113.sh
export HL_GEN=$PWD/build/hl-gen6-e113 HL_EXPN=e113
t_start=$(date +%s); deadline=${E113_DEADLINE_S:-$((t_start + 30 * 60))}; longest=${E113_LONGEST_S:-300}
echo "$(date +%T) e113 queue: start, deadline in $(( (deadline - t_start) / 60 )) min, items $E113_ITEMS"
for p in $E113_PASSES; do
  for f in build/e113-STOP build/hl-STOP build/claims-v3/STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$p"; exit 0; }; done
  now=$(date +%s)
  if [ $((now + longest)) -gt "$deadline" ]; then echo "$(date +%T) deadline: stopping before p$p (longest pass $longest s)"; break; fi
  echo "$(date +%T) p$p starts"
  t0=$(date +%s)
  bash tools/claims-v3/hl/block.sh "$p" "$E113_ITEMS" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  [ "$d" -gt "$longest" ] && longest=$d
  sleep 15
done
echo "$(date +%T) e113 queue: done"
