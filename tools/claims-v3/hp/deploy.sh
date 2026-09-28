#!/usr/bin/env bash
# Heat placement (HP): copy the hp code of this tree to a lab host's tree (~/nekko) and check every digest there.
#
#   bash tools/claims-v3/hp/deploy.sh <aifoundry1|aifoundry3> [--check] [--with-prereg]
#
# Refused (exit 2) while a queue, a block or a probe of the V3 claims framework runs on the host (any user): a running
# queue reads these files between blocks. Copies (tar over ssh) the hp code only: block.sh, probe.sh, hplib.sh,
# hplib.py, reduce.py, prereg.py, sptrace_events.py, placements.py, placements.json, run_queue.sh, run_a2.sh,
# deploy.sh, README.md, selftest/, ettelem-hp/. It never copies the frozen files (../lib.sh, ../queue.sh, a2/,
# tools/ettelem/flip_thermal_model.py): it checks that the host's copies equal this tree's and fails if not. params/
# (development decisions may be edited on the host) and prereg/ are compared and reported, and copied only with
# --with-prereg (prereg/* and params/params-val-aifoundry1-c1.json, after prereg.py --val); the schedules are copied
# only if their non-comment lines are the same on both sides. --check copies nothing.
# Exit 0: every copied and frozen file matches; 1: a mismatch (listed); 2: refused or the host could not be reached.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
host=${1:-}; shift || true
CHECK=; PREREG=
for a in "$@"; do case "$a" in --check) CHECK=1 ;; --with-prereg) PREREG=1 ;; *) echo "unknown option $a" >&2; exit 2 ;; esac; done
case "$host" in aifoundry1|aifoundry3) ;; *) echo "deploy.sh: usage: deploy.sh <aifoundry1|aifoundry3> [--check] [--with-prereg] (aifoundry2 runs this worktree itself)" >&2; exit 2 ;; esac
RT=nekko
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=20 "$host")
HPD=tools/claims-v3/hp
CODE=($HPD/block.sh $HPD/probe.sh $HPD/hplib.sh $HPD/hplib.py $HPD/reduce.py $HPD/prereg.py $HPD/sptrace_events.py
      $HPD/placements.py $HPD/placements.json $HPD/run_queue.sh $HPD/run_a2.sh $HPD/deploy.sh $HPD/README.md
      $HPD/selftest/run_selftest.py $HPD/selftest/synth_blocks.py $HPD/ettelem-hp/CMakeLists.txt $HPD/ettelem-hp/ettelem.cpp)
FROZEN=(tools/claims-v3/lib.sh tools/claims-v3/queue.sh tools/ettelem/flip_thermal_model.py $(find $HPD/a2 -maxdepth 1 -type f | sort))
KEPT=($(ls $HPD/params/*.json $HPD/prereg/* 2>/dev/null))
SCHED=($(ls tools/claims-v3/schedule-hp-*.txt))
for f in "${CODE[@]}" "${FROZEN[@]}"; do [ -f "$f" ] || { echo "deploy.sh: missing $f here" >&2; exit 2; }; done

# 1. nothing of the claims framework may run there (the [x] keeps pgrep from matching this command line itself)
busy=$("${SSH[@]}" "pgrep -af '[t]ools/claims-v3/(queue|hp/run_queue|hp/run_a2|[a-z0-9_/-]+/block|hp/probe)\.sh' || true") ||
  { echo "deploy.sh: cannot reach $host" >&2; exit 2; }
if [ -n "$busy" ]; then echo "deploy.sh: refused: a queue or block runs on $host:" >&2; echo "$busy" | cut -c1-200 >&2; exit 2; fi

remote_sha() { "${SSH[@]}" "cd ~/$RT && sha256sum $* 2>/dev/null; true"; }
# 2. copy the code (and, with --with-prereg, the PREREG files); schedules whose non-comment lines agree
if [ -z "$CHECK" ]; then
  cp_list=("${CODE[@]}")
  [ -n "$PREREG" ] && cp_list+=($(ls $HPD/prereg/* 2>/dev/null) $(ls $HPD/params/params-val-aifoundry1-c1.json 2>/dev/null))
  for s in "${SCHED[@]}"; do
    theirs=$("${SSH[@]}" "cd ~/$RT && grep -v '^\s*\(#\|\$\)' $s 2>/dev/null | md5sum" | cut -c1-32)
    ours=$(grep -v '^\s*\(#\|$\)' "$s" | md5sum | cut -c1-32)
    if [ "$theirs" = "$ours" ]; then cp_list+=("$s"); else echo "schedule $s: its non-comment lines differ on $host: not copied"; fi
  done
  tar cf - "${cp_list[@]}" | "${SSH[@]}" "cd ~/$RT && tar xf -" || { echo "deploy.sh: copy to $host failed" >&2; exit 2; }
  echo "copied ${#cp_list[@]} files to $host:~/$RT"
fi

# 3. every digest
declare -A R
while read -r h f; do R[$f]=$h; done < <(remote_sha "${CODE[@]}" "${FROZEN[@]}" "${KEPT[@]}" "${SCHED[@]}")
bad=0; warn=0
chk() {   # chk <class> <file>
  local l r; l=$(sha256sum "$2" | cut -c1-64); r=${R[$2]:-missing}
  if [ "$r" = "$l" ]; then printf 'same    %-9s %s %s\n' "$1" "${l:0:12}" "$2"
  elif [ "$1" = code ] || [ "$1" = frozen ]; then bad=1; printf 'DIFFERS %-9s %s %s (%s: %s)\n' "$1" "${l:0:12}" "$2" "$host" "${r:0:12}"
  else warn=1; printf 'differs %-9s %s %s (%s: %s)\n' "$1" "${l:0:12}" "$2" "$host" "${r:0:12}"; fi
}
for f in "${CODE[@]}"; do chk code "$f"; done
for f in "${FROZEN[@]}"; do chk frozen "$f"; done
for f in "${KEPT[@]}"; do chk kept "$f"; done
for f in "${SCHED[@]}"; do chk schedule "$f"; done
"${SSH[@]}" "cd ~/$RT && ls $HPD/prereg/ $HPD/params/ 2>/dev/null | grep -v '^$' | tr '\n' ' '" | sed 's/^/on the host: /'; echo
if [ $bad = 1 ]; then echo "deploy.sh: $host: code or frozen files DIFFER (above)"; exit 1; fi
echo "deploy.sh: $host: all ${#CODE[@]} code and ${#FROZEN[@]} frozen files match$([ $warn = 1 ] && echo "; params/prereg/schedules: see 'differs' lines")"
exit 0
