#!/usr/bin/env bash
# all.sh NEWTAG : the motion runs of run.sh, the baseline (bb0eb78) and the ladder's page interleaved, at CPU 1 and 4
D=/home/yaroslavvb/claude/work/ladder/motion; N=${1:-fin2}
bash $D/run.sh http://127.0.0.1:8765/base/chip.html base-c1 1 > $D/all.log 2>&1
LADDER=1 bash $D/run.sh http://127.0.0.1:8765/$N/chip.html $N-c1 1 >> $D/all.log 2>&1
bash $D/run.sh http://127.0.0.1:8765/base/chip.html base-c4 4 >> $D/all.log 2>&1
LADDER=1 bash $D/run.sh http://127.0.0.1:8765/$N/chip.html $N-c4 4 >> $D/all.log 2>&1
python3 $D/compare.py base-c1 $N-c1 base-c4 $N-c4 > $D/compare-$N.txt 2>&1
echo ALLDONE >> $D/all.log
