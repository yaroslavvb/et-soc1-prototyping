#!/usr/bin/env bash
# PCIE2: copy this experiment's directory to a lab host's tree (~/nekko) and check every digest there.
#
#   bash tools/claims-v3/pcie2/deploy.sh <aifoundry1|aifoundry3> [--check]
#
# Refused (exit 2) while a queue or a block of the V3 framework runs on the host, or while et-who --check shows anyone
# on a card there. Copies tools/claims-v3/pcie2/ only (tar over ssh, each file replaced by a new one, never written
# over a running script's bytes). The probe itself is built separately with scripts/deploy-lab.sh <host>
# workloads/pciebench, which also carries run_pcie.sh and schedule.sh. Then compares, host against this tree:
# every pcie2 file and the probe's sources (must match: exit 1 if not), and lib.sh and queue.sh (reported only: the
# lab trees keep their own copies, and each pass records their sha256). --check copies nothing. That the build in
# ~/nekko/build/pciebench is of these sources is block.sh's check (its --preflight mode, files only).
# Never aifoundry2: its checkout runs the DV2 validation until about 17:00 PDT on 29 September.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
host=${1:-}; shift || true
CHECK=
for a in "$@"; do case "$a" in --check) CHECK=1 ;; *) echo "deploy.sh: unknown option $a" >&2; exit 2 ;; esac; done
case "$host" in aifoundry1|aifoundry3) ;; *) echo "deploy.sh: usage: deploy.sh <aifoundry1|aifoundry3> [--check]" >&2; exit 2 ;; esac
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=20 "$host")
D=tools/claims-v3/pcie2
CODE=($(ls $D/*.sh $D/*.py $D/*.md $D/*.txt $D/*.sha256 2>/dev/null))
PROBE=(workloads/pciebench/host/main.cpp workloads/pciebench/kernel/touch.c workloads/pciebench/touch_args.h
       workloads/pciebench/kernel/empty.c workloads/pciebench/kernel/crt.S workloads/pciebench/kernel/sections.ld
       workloads/pciebench/CMakeLists.txt workloads/pciebench/host/CMakeLists.txt
       workloads/pciebench/host/Constants.h.in workloads/pciebench/kernel/CMakeLists.txt
       workloads/pciebench/run_pcie.sh workloads/pciebench/schedule.sh)
SHARED=(tools/claims-v3/lib.sh tools/claims-v3/queue.sh)
busy=$("${SSH[@]}" "pgrep -af '[t]ools/claims-v3/([a-z0-9_/-]+/)?(queue|run_queue|run_passes|block)\.sh' || true; et-who --check > /dev/null 2>&1 || echo 'et-who --check: a card is in use (or the check failed)'") ||
  { echo "deploy.sh: cannot reach $host" >&2; exit 2; }
if [ -n "$busy" ]; then echo "deploy.sh: refused: $host is busy:" >&2; echo "$busy" | cut -c1-200 >&2; exit 2; fi
if [ -z "$CHECK" ]; then
  "${SSH[@]}" "mkdir -p ~/nekko/$D" || exit 2
  tar cf - "${CODE[@]}" | "${SSH[@]}" "cd ~/nekko && tar xf - --unlink-first && chmod +x $D/*.sh $D/*.py" ||
    { echo "deploy.sh: copy to $host failed" >&2; exit 2; }
  echo "copied ${#CODE[@]} files to $host:~/nekko/$D"
fi
declare -A R
while read -r h f; do R[$f]=$h; done < <("${SSH[@]}" "cd ~/nekko && sha256sum ${CODE[*]} ${PROBE[*]} ${SHARED[*]} 2>/dev/null; true")
bad=0
for f in "${CODE[@]}" "${PROBE[@]}" "${SHARED[@]}"; do
  l=$(sha256sum "$f" | cut -c1-64); r=${R[$f]:-missing}
  if [ "$r" = "$l" ]; then printf 'same    %s %s\n' "${l:0:12}" "$f"
  else
    printf 'DIFFERS %s %s (%s: %s)\n' "${l:0:12}" "$f" "$host" "${r:0:12}"
    case " ${SHARED[*]} " in *" $f "*) ;; *) bad=1 ;; esac
  fi
done
[ $bad = 1 ] && { echo "deploy.sh: $host: pcie2 or probe files DIFFER (above; the probe: scripts/deploy-lab.sh $host workloads/pciebench)"; exit 1; }
echo "deploy.sh: $host: every pcie2 and probe file matches"
