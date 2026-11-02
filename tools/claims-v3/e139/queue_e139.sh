#!/usr/bin/env bash
# E139 (Q137): the registered passes on aifoundry3 card 0, run by session_e139.sh after the smoke gate passed. A port of
# tools/claims-v3/e132/queue_e132.sh; marked changes: passes 13910-13918 (13910 the registered warm-up), MF_GEN=build/e139-gen
# (E132's images byte for byte, gen.sha256), MF_EXPN=e139, MF_MAX_C=70 (die stop lowered from 78), build/e139-STOP (written also by
# watch_e139.py, the board-power stop). It stops before the next pass on build/e139-STOP, build/mf-STOP or build/claims-v3/STOP,
# after any pass that fails, or when the pass would end past E139_DEADLINE_S (epoch seconds; session_e139.sh sets it to the session's
# start + 42 min, and never later than 21:40 PST). A pass in flight is never cut by the budget. The longest pass so far is the
# estimate (first 270 s, E132's longest pass 268 s).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ITEMS=${E139_ITEMS:-anchor_pi,dp_zeros,dm_,ab_,eh_,el_,wl_,vl_,c3_}
export MF_GEN=$PWD/build/e139-gen MF_EXPN=e139 MF_ENERCAT=build/enercat-e99/host/enercat_host MF_MAX_C=${MF_MAX_C:-70}
t_start=$(date +%s); deadline=${E139_DEADLINE_S:-$((t_start + 30 * 60))}; longest=${E139_LONGEST_S:-270}
echo "$(date +%T) e139 queue: start, deadline $(date -d @"$deadline" +%T), items $ITEMS, die stop $MF_MAX_C C"
for p in ${E139_PASSES:-13910 13911 13912 13913 13914 13915 13916 13917 13918}; do
  for f in build/e139-STOP build/mf-STOP build/claims-v3/STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$p"; exit 0; }; done
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
echo "$(date +%T) e139 queue: done"
