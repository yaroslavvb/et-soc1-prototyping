#!/usr/bin/env bash
# nocr: copy the experiment to a lab host's tree (~/nekko), build the workload there, and check every digest.
#
#   bash tools/claims-v3/nocr/deploy.sh <ssh target of aifoundry1 or aifoundry3> [--check] [--no-build]
#
# Run from a checkout (aifoundry2's, or a laptop's). Refused (exit 2): aifoundry2 itself (its checkout is the tree, and
# DV2 runs there), a host where any claims-v3 queue, nocr run.sh or block runs (any user), a host without et-who, and a
# host whose et-who --check shows a holder. Copies with tar over ssh (never over a running script: a tar --unlink-first writes new files):
# tools/claims-v3/nocr/ and workloads/nocroute/ only; builds build/nocroute (a directory no other block uses) with
# nice -n 10 and -j4 through scripts/deploy-lab.sh's commands; checks that the host's lib.sh and queue.sh equal this
# tree's (they are never copied). --check copies and builds nothing. Exit 0: every file matches; 1: a mismatch.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
host=${1:-}; shift || true
CHECK=; BUILD=1
for a in "$@"; do case "$a" in --check) CHECK=1 ;; --no-build) BUILD= ;; *) echo "unknown option $a" >&2; exit 2 ;; esac; done
[ -n "$host" ] || { echo "usage: deploy.sh <host> [--check] [--no-build]" >&2; exit 2; }
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=20 "$host")
name=$("${SSH[@]}" hostname) || { echo "deploy.sh: cannot reach $host" >&2; exit 2; }
case "$name" in aifoundry1|aifoundry3) ;; *) echo "deploy.sh: $host is $name: only aifoundry1 and aifoundry3" >&2; exit 2 ;; esac
busy=$("${SSH[@]}" "pgrep -af '[t]ools/claims-v3/(queue|[a-z0-9_]+/run_queue|[a-z0-9_]+/run|[a-z0-9_/-]+/block)\.sh' || true")
if [ -n "$busy" ]; then echo "deploy.sh: refused: a queue or block runs on $name:" >&2; echo "$busy" | cut -c1-200 >&2; exit 2; fi
held=$("${SSH[@]}" "command -v et-who > /dev/null && { et-who --check; echo rc=\$?; } || echo rc=none")
case "$held" in
  *rc=0) ;;
  *rc=none) echo "deploy.sh: refused: et-who is not installed on $name" >&2; exit 2 ;;
  *) echo "deploy.sh: refused: et-who on $name: $held" >&2; exit 2 ;;
esac
D=tools/claims-v3/nocr
W=workloads/nocroute
CODE=($(ls $D/*.sh $D/*.py $D/*.json $D/*.txt $D/*.md $D/*.sha256 2>/dev/null)
      $W/meshmap.py $W/nocroute_args.h $W/CMakeLists.txt $W/README.md $W/host/CMakeLists.txt $W/host/Constants.h.in
      $W/host/main.cpp $W/kernel/CMakeLists.txt $W/kernel/crt.S $W/kernel/sections.ld $W/kernel/nocroute.c)
FROZEN=(tools/claims-v3/lib.sh tools/claims-v3/queue.sh)
if [ -z "$CHECK" ]; then
  "${SSH[@]}" "mkdir -p ~/nekko/$D ~/nekko/$W/host ~/nekko/$W/kernel" || exit 2
  tar cf - "${CODE[@]}" | "${SSH[@]}" "cd ~/nekko && tar xf - --unlink-first" || { echo "deploy.sh: copy failed" >&2; exit 2; }
  "${SSH[@]}" "cd ~/nekko && chmod +x $D/*.sh $D/*.py"
  echo "copied ${#CODE[@]} files to $name:~/nekko"
  if [ -n "$BUILD" ]; then
    # scripts/deploy-lab.sh's build, into build/nocroute; --clean-first because tar keeps the source's mtimes
    "${SSH[@]}" "set -e; cd ~/nekko
      nice -n 10 cmake -S $W -B build/nocroute -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build-nocroute.log 2>&1 ||
        { tail -30 build-nocroute.log; exit 1; }
      nice -n 10 cmake --build build/nocroute -j4 --clean-first >> build-nocroute.log 2>&1 || { tail -30 build-nocroute.log; exit 1; }
      grep -E 'warning:' build-nocroute.log || true; rm -f build-nocroute.log
      ls -l build/nocroute/host/nocroute_host build/nocroute/kernel/nocroute.elf
      python3 $D/nocr.py texthash build/nocroute/kernel/nocroute.elf" || { echo "deploy.sh: build failed" >&2; exit 1; }
  fi
fi
declare -A R
while read -r h f; do R[$f]=$h; done < <("${SSH[@]}" "cd ~/nekko && sha256sum ${CODE[*]} ${FROZEN[*]} 2>/dev/null; true")
bad=0
for f in "${CODE[@]}" "${FROZEN[@]}"; do
  l=$(sha256sum "$f" | cut -c1-64); r=${R[$f]:-missing}
  if [ "$r" = "$l" ]; then printf 'same    %s %s\n' "${l:0:12}" "$f"; else bad=1; printf 'DIFFERS %s %s (%s: %s)\n' "${l:0:12}" "$f" "$name" "${r:0:12}"; fi
done
for b in build/ettelem/ettelem build/nocroute/host/nocroute_host build/nocroute/kernel/nocroute.elf; do
  "${SSH[@]}" "test -e ~/nekko/$b" || { bad=1; echo "MISSING $b on $name"; }
done
[ $bad = 1 ] && { echo "deploy.sh: $name: files DIFFER or are missing (above)"; exit 1; }
echo "deploy.sh: $name: all ${#CODE[@]} nocr files and ${#FROZEN[@]} shared files match"
