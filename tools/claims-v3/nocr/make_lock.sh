#!/usr/bin/env bash
# nocr: freeze the pre-registration before validation (run once, after development, in the git checkout).
#
#   bash tools/claims-v3/nocr/make_lock.sh <nocroute.elf built from the frozen sources>
#
# Refuses unless PREREG.md says "Status: FROZEN". Writes, in tools/claims-v3/nocr/:
#   PREREG.sha256        sha256 of PREREG.md (quote it in the summary)
#   LOCK.sha256          every file a block runs or reads: this directory's code, params and sets, the nocroute
#                        sources, lib.sh and queue.sh (sha256sum -c format, paths from the tree root)
#   kernel-text.sha256   sha256 of the kernel's .text (the three hosts' toolchains differ only in .comment)
# Validation passes (block.sh 11-19) then refuse to start on any difference. Copy the three files to the validation
# host with deploy.sh, which checks every digest there.
set -eu
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
D=tools/claims-v3/nocr
elf=${1:?usage: make_lock.sh <nocroute.elf>}
grep -q '^Status: FROZEN' "$D/PREREG.md" || { echo "make_lock.sh: PREREG.md is not marked 'Status: FROZEN'" >&2; exit 2; }
python3 "$D/nocr.py" check-sets
sha256sum "$D/PREREG.md" | cut -c1-64 > "$D/PREREG.sha256"
files=("$D/block.sh" "$D/run.sh" "$D/nocr.py" "$D/reduce.py" "$D/params.json" "$D/sets.json" "$D/PREREG.md"
       "$D/make_lock.sh" "$D/deploy.sh" "$D/schedule-aifoundry3-smoke.txt" "$D/schedule-aifoundry3.txt"
       workloads/nocroute/meshmap.py workloads/nocroute/nocroute_args.h workloads/nocroute/CMakeLists.txt
       workloads/nocroute/host/CMakeLists.txt workloads/nocroute/host/Constants.h.in workloads/nocroute/host/main.cpp
       workloads/nocroute/kernel/CMakeLists.txt workloads/nocroute/kernel/crt.S workloads/nocroute/kernel/sections.ld
       workloads/nocroute/kernel/nocroute.c tools/claims-v3/lib.sh tools/claims-v3/queue.sh)
sha256sum "${files[@]}" > "$D/LOCK.sha256.new" && mv "$D/LOCK.sha256.new" "$D/LOCK.sha256"
python3 "$D/nocr.py" texthash "$elf" > "$D/kernel-text.sha256"
python3 "$D/nocr.py" lockcheck --kernel "$elf"
echo "PREREG.md sha256 $(cat "$D/PREREG.sha256"); LOCK.sha256 over ${#files[@]} files; kernel .text $(cut -c1-12 "$D/kernel-text.sha256")"
