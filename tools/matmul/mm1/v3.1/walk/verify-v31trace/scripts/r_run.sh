#!/bin/bash
# verify-v31trace (Q217), run ON aifoundry3 by a3.sh run (only while no lane books aifoundry3, no claim file stands and queue_state reads
# QUEUE OVER for e213a): this lane's ONE traced simulator run. rgm136's gemmL 1x1x16, fp32 zeros, mask 0x1111 (E212's spread layout at n 4,
# t8's point), every hart (all 64) of EVERY compute shire 0-31 logged, so this run alone meets trace criterion (a)'s minimum log set at
# this mask: (i) all 64 harts of the 4 enabled shires and (ii) all 64 harts of all 28 shires outside the mask. Raw excerpts kept (gzip):
# harts 0 (shire 0 minion 0), 1 (its hart 1) and 830 (shire 12 minion 31), and every line of shires 1 and 31. The host in bubblewrap with
# no /dev/et*, prlimit --as 4 GB, nice 19, plain timeout 1500 (never -k); the reader at nice 19 under its own 4 GB cap. One run.
set -u
D="$HOME/claude/work/q217-verify-v31trace"; cd "$D" || exit 3
want=bd7f945b88085daa8fe40a6f173eb7beade4dd78028254d76fafa56803cb0022
got=$(sha256sum "$D/vt_run.py" | cut -d' ' -f1)
[ "$got" = "$want" ] || { echo "vt_run.py hash $got is not the desk's $want: not running"; exit 4; }
sel=()
for s in $(seq 0 31); do sel+=(--log-sel "$s,ffffffffffffffff"); done
echo "start $(date '+%F %T %Z'); load $(cut -d' ' -f1-3 /proc/loadavg); mem avail $(free -g | awk '/Mem:/{print $7}') GB"
nice -n 19 prlimit --as=4294967296 /usr/bin/python3 -I -B "$D/vt_run.py" --name u1-gemmL-1x1x16-0x1111-allchip \
  --host "$D/bin/rgm136/sparsity_host" --elf "$D/bin/rgm136/sparsity.elf" --tile "$D/tiles/fp32/zeros.bin" --arm gemmL1x1x16 \
  --mask 0x1111 "${sel[@]}" --excerpt-hart 0 --excerpt-hart 1 --excerpt-hart 830 --excerpt-shire 1 --excerpt-shire 31 \
  --trace-run "$D/trace_run_v31.py" --out "$D/runs/u1" --timeout 1500
rc=$?
echo "end $(date '+%F %T %Z') rc=$rc; load $(cut -d' ' -f1-3 /proc/loadavg)"
ls -la "$D/runs/u1" 2>/dev/null
du -sh "$D/runs/u1" 2>/dev/null
echo "sim runs of this user now: $(pgrep -u "$(id -u)" -f 'sparsity_host --sysemu' | wc -l)"
timeout 20 et-who 2>&1 | head -2
exit $rc
