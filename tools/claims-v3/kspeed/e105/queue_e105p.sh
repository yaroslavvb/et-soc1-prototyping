#!/usr/bin/env bash
# E105 amendment A1: the power arm, on aifoundry3 at its pinned 600 MHz. E101 session 1's own block_e101.sh and run_e101.py, unchanged, with the layout set by E101_GEMM and the binary by E101_SPARSITY (both of them block_e101.sh's own switches): E78's frame, E78's anchors, the same reducer.
# gemm1 and gemm16 items keep their names in the records, so which layout a pass ran is its directory: kinds-e105c holds E101_GEMM=gemmc, kinds-e105v holds E101_GEMM=gemmv. tenb, mm16, gemmnc1 and mmp64 are dropped: E101 session 1 has them. A pass in flight is never cut.
#
#   setsid nohup bash tools/claims-v3/kspeed/e105/queue_e105p.sh > build/e105/queue-p.out 2>&1 < /dev/null &
#
# It stops before the next pass on build/e105/STOP-P, after any failed pass, or if a pass would end past E105P_DEADLINE_S (epoch seconds, default its start plus 50 min).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export E101_SPARSITY=build/e105/host/sparsity_host E101_DROP_ARMS=tenb,mm16,gemmnc1,mmp64
t_start=$(date +%s); deadline=${E105P_DEADLINE_S:-$((t_start + 50 * 60))}; longest=600
sha256sum build/e105/host/sparsity_host build/e105/kernel/sparsity.elf > build/e105/binaries-p.sha256
echo "$(date +%T) e105p: start, deadline in $(( (deadline - t_start) / 60 )) min"
for spec in "10520 gemmc e105c" "10521 gemmv e105v" "10522 gemmc e105c" "10523 gemmv e105v"; do
  set -- $spec; p=$1; arm=$2; exp=$3
  [ -e build/e105/STOP-P ] && { echo "$(date +%T) STOP-P: stopping before p$p"; break; }
  now=$(date +%s)
  if [ $((now + longest)) -gt "$deadline" ]; then echo "$(date +%T) deadline: stopping before p$p (longest pass $longest s)"; break; fi
  echo "$(date +%T) p$p starts: E101_GEMM=$arm E78_EXPN=kinds-$exp"
  t0=$(date +%s)
  E101_GEMM=$arm E78_EXPN=kinds-$exp bash tools/claims-v3/kinds/block_e101.sh "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  [ "$d" -gt "$longest" ] && longest=$d
  sleep 15
done
echo "$(date +%T) e105p: done"
