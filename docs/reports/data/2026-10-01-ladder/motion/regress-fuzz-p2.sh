#!/bin/bash
# regress-fuzz.sh <page.html> <label>: regress.sh's third stream only (the fuzzers, the leak test, the phone suite and the
# smoke tests), for a change that touches only the hand-over; results in res/<label>/
F=/home/yaroslavvb/claude/work/ladder/p2/mlreg; P=$1; L=$2; O=$F/res/$L; mkdir -p $O
run() { local d=$1 n=$2; shift 2; (cd $F/$d && timeout 1500 node "$@" > $O/$n.txt 2>&1; echo "$n exit $?" >> $O/done.txt); }
for s in 1 2 3; do run portc/review fuzz-$s fuzz.mjs $P $s 12; done
for s in 1 2 3; do run desk fuzzkb-$s fuzzkb.mjs $P $s 14; done
for s in 11 22 33; do run phone fuzzp-$s fuzz.mjs $P $s 390 844 4; done
run code fuzz2-d fuzz2.mjs $P 11 12; run code fuzz2-p fuzz2.mjs $P 21 12 phone; run code fuzz3-d fuzz3.mjs $P 31 12; run code fuzz3-p fuzz3.mjs $P 32 12 phone
run code leak t_leak.mjs $P 4 40; run portc phone phone.mjs $P 4; run portc smoke-d smoke.mjs $P desktop; run portc smoke-p smoke.mjs $P phone
echo ALLDONE >> $O/done.txt
