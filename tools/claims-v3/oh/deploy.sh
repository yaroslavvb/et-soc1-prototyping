#!/usr/bin/env bash
# OH (E53): copy the OH code of this tree to a lab host's tree (~/nekko) and check every digest there.
#
#   bash tools/claims-v3/oh/deploy.sh <aifoundry1|aifoundry3> [--check]
#
# Refused (exit 2) while a queue or a block of the V3 claims framework runs on the host (any user). Copies (tar over
# ssh) tools/claims-v3/oh/ only (code, params, battery, schedules, prereg/, README). It never copies the shared files
# the blocks use (../lib.sh, ../queue.sh, workloads/memprobe/gen_ops.py): it checks that the host's copies equal this
# tree's and fails if not. --check copies nothing. Exit 0: every file matches; 1: a mismatch (listed); 2: refused.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
host=${1:-}; shift || true
CHECK=
for a in "$@"; do case "$a" in --check) CHECK=1 ;; *) echo "unknown option $a" >&2; exit 2 ;; esac; done
case "$host" in aifoundry1|aifoundry3) ;; *) echo "deploy.sh: usage: deploy.sh <aifoundry1|aifoundry3> [--check]" >&2; exit 2 ;; esac
RT=nekko
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=20 "$host")
OD=tools/claims-v3/oh
CODE=($(ls $OD/*.sh $OD/*.py $OD/*.json $OD/*.txt $OD/*.md 2>/dev/null) $(ls $OD/prereg/* 2>/dev/null))
FROZEN=(tools/claims-v3/lib.sh tools/claims-v3/queue.sh workloads/memprobe/gen_ops.py)
busy=$("${SSH[@]}" "pgrep -af '[t]ools/claims-v3/(queue|oh/run_queue|hp/run_queue|[a-z0-9_/-]+/block)\.sh' || true") ||
  { echo "deploy.sh: cannot reach $host" >&2; exit 2; }
if [ -n "$busy" ]; then echo "deploy.sh: refused: a queue or block runs on $host:" >&2; echo "$busy" | cut -c1-200 >&2; exit 2; fi
if [ -z "$CHECK" ]; then
  "${SSH[@]}" "mkdir -p ~/$RT/$OD/prereg" || exit 2
  # into place with a rename per file (tar writes a new file, never over a running script's bytes)
  tar cf - "${CODE[@]}" | "${SSH[@]}" "cd ~/$RT && tar xf - --unlink-first" || { echo "deploy.sh: copy to $host failed" >&2; exit 2; }
  "${SSH[@]}" "cd ~/$RT && chmod +x $OD/*.sh"
  echo "copied ${#CODE[@]} files to $host:~/$RT"
fi
declare -A R
while read -r h f; do R[$f]=$h; done < <("${SSH[@]}" "cd ~/$RT && sha256sum ${CODE[*]} ${FROZEN[*]} 2>/dev/null; true")
bad=0
for f in "${CODE[@]}" "${FROZEN[@]}"; do
  l=$(sha256sum "$f" | cut -c1-64); r=${R[$f]:-missing}
  if [ "$r" = "$l" ]; then printf 'same    %s %s\n' "${l:0:12}" "$f"; else bad=1; printf 'DIFFERS %s %s (%s: %s)\n' "${l:0:12}" "$f" "$host" "${r:0:12}"; fi
done
[ $bad = 1 ] && { echo "deploy.sh: $host: files DIFFER (above)"; exit 1; }
echo "deploy.sh: $host: all ${#CODE[@]} OH files and ${#FROZEN[@]} shared files match"
