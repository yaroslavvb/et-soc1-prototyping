#!/usr/bin/env bash
# all-p2.sh NEWTAG: part 2's motion runs, one at a time on a quiet machine, a warm profile each page, 1280x800 DPR 1, at
# CPU 1x and 4x: the memory levels (run.sh: the access #dram/load, the level tabs; on the new page the ladder out from the
# L3's map to the rack and back in, and in from the L2's cell to an atom and back out) against the committed page, and
# the chip diagram's flows A, H, K and the tour (runchip.sh) against the committed page; then the first load (a phone
# at 4x, five interleaved runs each)
# (in the repository: run-p2.sh and runchip-p2.sh are the work directory's run.sh and runchip.sh; regress-p2.sh is its mlreg/regress.sh)
T=${1:-p2m}; D=/home/yaroslavvb/claude/work/ladder/p2/motion; U=http://127.0.0.1:8766
cd $D
for c in 1 4; do
  ./run-p2.sh $U/mlbase/ml.html mlbase-c$c $c
  NEW=1 ./run-p2.sh $U/$T/ml.html ml$T-c$c $c
  ./runchip-p2.sh $U/chipbase/chip.html chipbase-c$c $c
  ./runchip-p2.sh $U/$T/chip.html chip$T-c$c $c
done
export TMPDIR=/home/yaroslavvb/claude/work/ladder/p2/tmp
node ../firstload.mjs $U/mlbase/ml.html $U/$T/ml.html 5 > $D/firstload-ml.txt 2>&1
node ../firstload.mjs $U/chipbase/chip.html $U/$T/chip.html 5 > $D/firstload-chip.txt 2>&1
echo ALLDONE > $D/all-done.txt
