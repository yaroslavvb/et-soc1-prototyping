#!/usr/bin/env bash
# motion.sh VER BASEURL CPU REP : the final check's motion runs, one at a time, a warm profile per version (VER = bb0 or head),
# 1280x800 DPR 1. Chip: flows 1 (A), 8 (H) and B (K); Up from the silicon crystal to the top (36 presses); + from the top
# down to the silicon crystal (36 presses). Memory levels: the access #dram/load; the level tabs 5 2 1 3 4 1.
# Head only: the chip's loop (Up from beyond: round to the Planck length, then a quark, a proton, the nucleus, the atom);
# the memory levels' out (Up x5 from the L3's map to "?", + x5 back) and in (+ x5 from the L2's cell, Up x5 back).
VER=$1; BASE=$2; CPUF=${3:-1}; REP=${4:-1}; TAG=$VER-c$CPUF-r$REP; D=/home/yaroslavvb/claude/work/ladder/final/motion
mkdir -p $D $D/tmp
cd /home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion
export TMPDIR=$D/tmp CPU=$CPUF
export UDD=$D/udd-chip-$VER REC=./recorder-chip.js STATE='window.__chipState()' STEPTXT="(document.getElementById('st-live')||{}).textContent"
for f in 1:A 8:H b:K; do q=${f%%:*}; k=${f##*:}
  UNTIL='window.__chipState().done' node drive.mjs $BASE/chip.html "?flow=$q" $D/$TAG-$k.json 1280 800 1 150 2>$D/$TAG-$k.log
done
SI="shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma/vpu.lane.fma.tree/fma.tree.col/lib.cmp42/lib.fa/lib.xor/lib.finfet/lib.fin/lib.channel/lib.si"
UP=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(36) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1700})]))")
DIVE=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(36) for x in ({'key': '+'}, {'wait': 1900})]))")
SCEN="$UP" UNTIL='window.__chipState().depth === 0 && !window.__chipState().zooming' node drive.mjs $BASE/chip.html "?at=$SI" $D/$TAG-up.json 1280 800 1 100 2>$D/$TAG-up.log
SCEN="$DIVE" UNTIL="/lib\.si\$/.test(window.__chipState().path) && !window.__chipState().zooming" node drive.mjs $BASE/chip.html "?at=beyond" $D/$TAG-dive.json 1280 800 1 110 2>$D/$TAG-dive.log
if [ "$VER" = head ]; then
  LOOP=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(5) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1900})]))")
  SCEN="$LOOP" UNTIL="window.__chipState().node === 'p.atom' && !window.__chipState().zooming" node drive.mjs $BASE/chip.html "?at=beyond" $D/$TAG-loop.json 1280 800 1 40 2>$D/$TAG-loop.log
fi
unset REC STATE STEPTXT
export UDD=$D/udd-ml-$VER
node drive.mjs $BASE/ml.html '#dram/load' $D/$TAG-load.json 1280 800 1 150 2>$D/$TAG-load.log
TABS='[{"wait":1500},{"key":"5"},{"wait":2600},{"key":"2"},{"wait":2600},{"key":"1"},{"wait":2600},{"key":"3"},{"wait":2600},{"key":"4"},{"wait":2600},{"key":"1"},{"wait":2600}]'
SCEN="$TABS" UNTIL='performance.now() > 20000 && !window.__memState().zooming' node drive.mjs $BASE/ml.html '#l1' $D/$TAG-tabs.json 1280 800 1 60 2>$D/$TAG-tabs.log
if [ "$VER" = head ]; then
  OUT=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(5) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1900})] + [x for i in range(5) for x in ({'eval': \"document.querySelector('#pmz [data-ci=plus]').click()\"}, {'wait': 1900})]))")
  REC=./recorder-mlchip.js SCEN="$OUT" UNTIL="performance.now() > 22000 && !window.__memState().ladder.zooming && !window.__memState().ladder.on" node drive.mjs $BASE/ml.html '#l3' $D/$TAG-out.json 1280 800 1 60 2>$D/$TAG-out.log
  IN=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(5) for x in ({'eval': \"document.querySelector('#pmz [data-ci=plus]').click()\"}, {'wait': 1900})] + [x for i in range(5) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1900})]))")
  REC=./recorder-mlchip.js SCEN="$IN" UNTIL="performance.now() > 22000 && !window.__memState().ladder.zooming && !window.__memState().ladder.on" node drive.mjs $BASE/ml.html '#l2/cell' $D/$TAG-in.json 1280 800 1 60 2>$D/$TAG-in.log
fi
for k in A H K up dive loop load tabs out in; do f=$D/$TAG-$k.json; [ -f $f ] && python3 summ.py $f; done > $D/$TAG-summ.txt 2>&1
for k in A H K up dive loop load tabs out in; do f=$D/$TAG-$k.json; [ -f $f ] && { echo "## $k"; python3 moves.py $f; }; done > $D/$TAG-moves.txt 2>&1
for k in A H K load; do f=$D/$TAG-$k.json; [ -f $f ] && { echo "## $k"; python3 kink.py $f; }; done > $D/$TAG-kink.txt 2>&1
echo done >> $D/$TAG-summ.txt
