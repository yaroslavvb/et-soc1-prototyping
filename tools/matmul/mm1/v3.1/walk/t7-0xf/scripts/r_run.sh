#!/bin/bash
# t7-0xf (Q221), run ON aifoundry3 by a3.sh run (only while no lane books aifoundry3, no claim file stands and queue_state reads
# QUEUE OVER for aifoundry3's recent chains): this lane's ONE traced simulator run, in the form of verify-v31trace's u1 (its r_run.sh,
# b480ea7e...) with only these changes: the mask 0xf (E212's compact layout at n 4, t7's point), the run name u2-gemmL-1x1x16-0xf-allchip
# and its folder runs/u2, this lane's own remote folder, and the excerpts: harts 0 (shire 0 minion 0), 1 (its hart 1) and 254 (shire 3
# minion 31, hart 0: an enabled shire at 0xf, in place of u1's 830), and every line of shires 4 and 31 (both outside 0xf, in place of u1's
# 1 and 31). rgm136's gemmL 1x1x16, fp32 zeros; every hart (all 64) of EVERY compute shire 0-31 logged, so this run alone meets trace
# criterion (a)'s minimum log set at 0xf: (i) all 64 harts of the 4 enabled shires 0-3 and (ii) all 64 harts of all 28 shires outside
# the mask. The runner is verify-v31trace's vt_run.py, unchanged (sha256 bd7f945b...): the host in bubblewrap with no /dev/et*,
# prlimit --as 4 GB, nice 19, plain timeout 1500 (never -k); the reader at nice 19 under its own 4 GB cap. One run.
set -u
D="$HOME/claude/work/q221-t7-0xf"; cd "$D" || exit 3
want=bd7f945b88085daa8fe40a6f173eb7beade4dd78028254d76fafa56803cb0022
got=$(sha256sum "$D/vt_run.py" | cut -d' ' -f1)
[ "$got" = "$want" ] || { echo "vt_run.py hash $got is not the desk's $want: not running"; exit 4; }
sel=()
for s in $(seq 0 31); do sel+=(--log-sel "$s,ffffffffffffffff"); done
echo "start $(date '+%F %T %Z'); load $(cut -d' ' -f1-3 /proc/loadavg); mem avail $(free -g | awk '/Mem:/{print $7}') GB"
nice -n 19 prlimit --as=4294967296 /usr/bin/python3 -I -B "$D/vt_run.py" --name u2-gemmL-1x1x16-0xf-allchip \
  --host "$D/bin/rgm136/sparsity_host" --elf "$D/bin/rgm136/sparsity.elf" --tile "$D/tiles/fp32/zeros.bin" --arm gemmL1x1x16 \
  --mask 0xf "${sel[@]}" --excerpt-hart 0 --excerpt-hart 1 --excerpt-hart 254 --excerpt-shire 4 --excerpt-shire 31 \
  --trace-run "$D/trace_run_v31.py" --out "$D/runs/u2" --timeout 1500
rc=$?
echo "end $(date '+%F %T %Z') rc=$rc; load $(cut -d' ' -f1-3 /proc/loadavg)"
ls -la "$D/runs/u2" 2>/dev/null
du -sh "$D/runs/u2" 2>/dev/null
echo "sim runs of this user now: $(pgrep -u "$(id -u)" -f 'sparsity_host --sysemu' | wc -l)"
timeout 20 et-who 2>&1 | head -2
exit $rc
