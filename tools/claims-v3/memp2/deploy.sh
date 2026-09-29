#!/usr/bin/env bash
# memp2: copy memp2's code to a lab host's tree (~/nekko), optionally build build/memprobe2 there, and check digests.
#
#   bash tools/claims-v3/memp2/deploy.sh <aifoundry1|aifoundry3> [--build] [--check] [--print]
#
# Refused (exit 2) while a queue, block, memp2 series or memp2 sysemu check of the V3 framework runs on the host (any
# user), or while et-who --check there shows any holder. Copies (tar over ssh; tar unlinks each file first, so a running script's bytes are never
# overwritten) tools/claims-v3/memp2/ and workloads/memprobe's sources (CMake files, memprobe_args.h, kernel/, host/,
# gen_ops2.py, README.md), never gen_ops.py (the OH lock pins it: the host's copy must already equal this tree's).
# --build: cmake into build/memprobe2 only (-DMEMPROBE_EXT=ON, nice, -j4, --clean-first because tar keeps the
# sources' times), never build/memprobe or build/memprobe-v3. Then it checks that the host's copy of every file
# memp2 runs equals this tree's. --check: copy and build nothing. --print: print the ssh commands, run nothing.
# aifoundry2 runs from its own checkout: build there with the cmake lines in README.md, after DV2 ends.
# Exit: 0 every file matches (and the build, if asked, succeeded); 1 a mismatch or a failed build; 2 refused.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
host=${1:-}; shift || true
BUILD=; CHECK=; PRINT=
for a in "$@"; do case "$a" in --build) BUILD=1 ;; --check) CHECK=1 ;; --print) PRINT=1 ;;
  *) echo "unknown option $a" >&2; exit 2 ;; esac; done
case "$host" in aifoundry1|aifoundry3) ;; *) echo "deploy.sh: usage: deploy.sh <aifoundry1|aifoundry3> [--build] [--check] [--print]" >&2; exit 2 ;; esac
RT=nekko
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=20 "$host")
run() { if [ -n "$PRINT" ]; then printf '%q ' "${SSH[@]}" "$@"; echo; else "${SSH[@]}" "$@"; fi; }
MD=tools/claims-v3/memp2
CODE=($(ls $MD/*.sh $MD/*.py $MD/*.txt $MD/*.md 2>/dev/null) $(ls $MD/prereg/* 2>/dev/null) $(ls $MD/LOCK.sha256 2>/dev/null)
      workloads/memprobe/CMakeLists.txt workloads/memprobe/memprobe_args.h workloads/memprobe/gen_ops2.py
      workloads/memprobe/README.md $(ls workloads/memprobe/kernel/* workloads/memprobe/host/*))
SHARED=(tools/claims-v3/lib.sh tools/claims-v3/queue.sh tools/claims-v3/cat/run_catalogue_t10.py tools/claims-v3/cat/catlib.py
        workloads/enercat/run_catalogue.py workloads/enercat/analyze_catalogue.py workloads/memprobe/gen_ops.py)
BUILDCMD="cd ~/$RT && nice -n 10 cmake -S workloads/memprobe -B build/memprobe2 -DCMAKE_PREFIX_PATH=/opt/et -DMEMPROBE_EXT=ON -Wno-dev > build-memprobe2.log 2>&1 && nice -n 10 cmake --build build/memprobe2 -j4 --clean-first >> build-memprobe2.log 2>&1; rc=\$?; grep -E 'warning:|error:' build-memprobe2.log | head -20; tail -2 build-memprobe2.log; exit \$rc"

if [ -z "$PRINT" ]; then
  busy=$("${SSH[@]}" "pgrep -af '[t]ools/claims-v3/(queue|oh/run_queue|hp/run_queue|[a-z0-9_/-]+/(block|series|sysemu))\.sh' || true") ||
    { echo "deploy.sh: cannot reach $host" >&2; exit 2; }
  if [ -n "$busy" ]; then echo "deploy.sh: refused: a queue or block runs on $host:" >&2; echo "$busy" | cut -c1-200 >&2; exit 2; fi
  held=$("${SSH[@]}" "et-who --check 2>&1; echo rc=\$?") || { echo "deploy.sh: et-who on $host failed" >&2; exit 2; }
  case "$held" in *rc=0) ;; *) echo "deploy.sh: refused: et-who --check on $host: ${held//$'\n'/; }" >&2; exit 2 ;; esac
else
  run "pgrep -af '[t]ools/claims-v3/(queue|oh/run_queue|hp/run_queue|[a-z0-9_/-]+/(block|series|sysemu))\.sh'; et-who --check"
fi
if [ -z "$CHECK" ]; then
  if [ -n "$PRINT" ]; then echo "tar cf - ${CODE[*]} | $(printf '%q ' "${SSH[@]}")'cd ~/$RT && tar xf - --unlink-first'"
  else
    run "mkdir -p ~/$RT/$MD/prereg ~/$RT/workloads/memprobe/kernel ~/$RT/workloads/memprobe/host" || exit 2
    tar cf - --exclude=__pycache__ "${CODE[@]}" | "${SSH[@]}" "cd ~/$RT && tar xf - --unlink-first" ||
      { echo "deploy.sh: copy to $host failed" >&2; exit 2; }
    run "cd ~/$RT && chmod +x $MD/*.sh"
    echo "copied ${#CODE[@]} files to $host:~/$RT"
  fi
  if [ -n "$BUILD" ]; then
    run "$BUILDCMD" || { echo "deploy.sh: the build of build/memprobe2 on $host failed" >&2; exit 1; }
  fi
fi
[ -n "$PRINT" ] && { run "cd ~/$RT && sha256sum ${CODE[*]} ${SHARED[*]}"; exit 0; }
declare -A R
while read -r h f; do R[$f]=$h; done < <("${SSH[@]}" "cd ~/$RT && sha256sum ${CODE[*]} ${SHARED[*]} 2>/dev/null; true")
bad=0
for f in "${CODE[@]}" "${SHARED[@]}"; do
  l=$(sha256sum "$f" | cut -c1-64); r=${R[$f]:-missing}
  if [ "$r" = "$l" ]; then printf 'same    %s %s\n' "${l:0:12}" "$f"; else bad=1; printf 'DIFFERS %s %s (%s: %s)\n' "${l:0:12}" "$f" "$host" "${r:0:12}"; fi
done
[ $bad = 1 ] && { echo "deploy.sh: $host: files DIFFER (above)"; exit 1; }
echo "deploy.sh: $host: all ${#CODE[@]} memp2 files and ${#SHARED[@]} shared files match"
