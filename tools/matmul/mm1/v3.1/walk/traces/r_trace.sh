#!/bin/bash
# v31-trace (Q217), run ON aifoundry3 (sent by a3_send.sh only while no lane books aifoundry3 and queue_state reads QUEUE OVER for e213a):
# ONE traced simulator run of a GEMM arm through trace_run.py (the host with --sysemu in bubblewrap with no /dev/et*, prlimit --as 4 GB,
# nice 19, a plain timeout; the log streamed through a FIFO into the summarizer, nothing of it kept). The summarizer itself runs at nice 19
# under its own 4 GB cap. One run at a time (trace_run.py refuses if a simulator run of ours is going).
#   bash r_trace.sh <name> <kernel rgm136.gemmL|rgm136.gemmLnc|rgm211.gemmLn> <arm e.g. gemmL2x4x16> <mask> <log-sel> [<log-sel> ...]
#   a log-sel is '<shire>,<64-bit hex mask of the shire's harts>' (sys_emu's -ls)
set -u
D="$HOME/claude/work/q217-v31-trace"; cd "$D" || exit 3
name=$1; kernel=$2; arm=$3; mask=$4; shift 4
case "$kernel" in
  rgm136.gemmL)   host=bin/rgm136/sparsity_host; elf=bin/rgm136/sparsity.elf ;;   # E136-E212's pairing
  rgm136.gemmLnc) host=bin/rgm211/sparsity_host; elf=bin/rgm136/sparsity.elf ;;   # E211's pairing for gemmLnc
  rgm211.gemmLn)  host=bin/rgm211/sparsity_host; elf=bin/rgm211/sparsity.elf ;;   # E211's pairing for gemmLn
  *) echo "unknown kernel $kernel"; exit 2 ;;
esac
args=()
for s in "$@"; do args+=(--log-sel "$s"); done
echo "start $(date '+%F %T %Z') run $name: $kernel $arm mask $mask; load $(cut -d' ' -f1-3 /proc/loadavg); free $(free -g | awk '/Mem:/{print $7}') GB"
nice -n 19 prlimit --as=4294967296 /usr/bin/python3 -I -B "$D/trace_run.py" run --name "$name" --host "$D/$host" --elf "$D/$elf" \
  --arm "$arm" --values-gen tiles --tile "$D/tiles/fp32/zeros.bin" --type fp32 --mask "$mask" "${args[@]}" --out "$D/runs/$name" --timeout 2400
rc=$?
echo "end $(date '+%F %T %Z') rc=$rc; summary $(stat -c %s "$D/runs/$name/summary.json.gz" 2>/dev/null) B; run dir $(du -sh "$D/runs/$name" 2>/dev/null | cut -f1); load $(cut -d' ' -f1-3 /proc/loadavg)"
ls "$D/runs/$name" 2>/dev/null | tr '\n' ' '; echo
exit $rc
