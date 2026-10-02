#!/bin/bash
# regress.sh <page.html> <label>: the reviewers' and the porter's suites on one page, in three streams; results in res/<label>/
F=/home/yaroslavvb/claude/work/ladder/p2/mlreg; P=$1; L=$2; O=$F/res/$L; mkdir -p $O
run() { local d=$1 n=$2; shift 2; (cd $F/$d && timeout 1500 node "$@" > $O/$n.txt 2>&1; echo "$n exit $?" >> $O/done.txt); }
# stream 1: the phone at 4x (tabs, parts at both sizes, the bar, swipes)
( run phone tabs390 tabs.mjs $P 390 844 4 $L-p390c4; run phone parts390 parts.mjs $P 390 844 4 $L-p390c4; run phone parts360 parts.mjs $P 360 740 4 $L-p360c4;
  run phone bar bar.mjs $P 390 844 4; run phone bar2 bar2.mjs $P 390 844 4; run phone swipe swipe.mjs $P 390 844 4; run phone tabs360 tabs.mjs $P 360 740 4 $L-p360c4 ) &
# stream 2: the desktop: the porter's keyboard script, accesses, races; the desktop review's suites
( run portc/review kb kb.mjs $P $O/kb.json; for lv in l1 l2 l3 scp dram; do run portc/review acc-$lv acc.mjs $P $lv $O/acc-$lv.json; done
  for s in race race2 race3; do run portc/review $s $s.mjs $P; done
  for k in Escape Backspace -; do run portc/review escesc-$k escesc.mjs $P '#scp/remote-load/4' $k; done
  run desk during during.mjs $P $O/during.json; run desk tour tour.mjs $P $O/tour.json; run desk bar-desk bar.mjs $P $O/bar-desk.json
  run desk newpa newpa.mjs $P $O/newpa.json; run portc misc misc.mjs $P; run portc remote remote.mjs $P; run portc keypace keypace.mjs $P ) &
# stream 3: fuzzers and the leak test
( for s in 1 2 3; do run portc/review fuzz-$s fuzz.mjs $P $s 12; done
  for s in 1 2 3; do run desk fuzzkb-$s fuzzkb.mjs $P $s 14; done
  for s in 11 22 33; do run phone fuzzp-$s fuzz.mjs $P $s 390 844 4; done
  run code fuzz2-d fuzz2.mjs $P 11 12; run code fuzz2-p fuzz2.mjs $P 21 12 phone; run code fuzz3-d fuzz3.mjs $P 31 12; run code fuzz3-p fuzz3.mjs $P 32 12 phone
  run code leak t_leak.mjs $P 4 40; run portc phone phone.mjs $P 4; run portc smoke-d smoke.mjs $P desktop; run portc smoke-p smoke.mjs $P phone ) &
wait
echo ALLDONE >> $O/done.txt
