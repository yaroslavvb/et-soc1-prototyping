#!/usr/bin/env bash
# E132: the registered passes on aifoundry3, run by session_e132.sh after the smoke gate passed. Passes 13210-13216, each E75's
# mf/block.sh unchanged (MF_GEN=build/e132-gen, MF_EXPN=e132, MF_ENERCAT = E99's host). 13210 is the registered warm-up.
# It stops before the next pass on build/e132-STOP or build/mf-STOP, after any pass that fails, or when the pass would end past
# E132_DEADLINE_S (epoch seconds; session_e132.sh sets it to the session's start + 36 min, so the smoke, the passes and both config
# reads stay inside the brief's 40 card-minutes). A pass in flight is never cut. The longest pass so far is the estimate (first 240 s).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ITEMS=${E132_ITEMS:-anchor_pi,dp_zeros,dm_,ab_,eh_,el_,wl_,vl_,c3_}
export MF_GEN=$PWD/build/e132-gen MF_EXPN=e132 MF_ENERCAT=build/enercat-e99/host/enercat_host
t_start=$(date +%s); deadline=${E132_DEADLINE_S:-$((t_start + 30 * 60))}; longest=${E132_LONGEST_S:-240}
echo "$(date +%T) e132 queue: start, deadline in $(( (deadline - t_start) / 60 )) min, items $ITEMS"
for p in 13210 13211 13212 13213 13214 13215 13216; do
  for f in build/e132-STOP build/mf-STOP build/claims-v3/STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$p"; exit 0; }; done
  now=$(date +%s)
  if [ $((now + longest)) -gt "$deadline" ]; then echo "$(date +%T) deadline: stopping before p$p (longest pass $longest s)"; break; fi
  echo "$(date +%T) p$p starts"
  t0=$(date +%s)
  bash tools/claims-v3/mf/block.sh "$p" "$ITEMS" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  [ "$d" -gt "$longest" ] && longest=$d
  sleep 15
done
echo "$(date +%T) e132 queue: done"
