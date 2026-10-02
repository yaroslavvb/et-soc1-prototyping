#!/usr/bin/env bash
# motion-chip.sh VER BASEURL CPU REP : the chip diagram's runs of motion.sh only (A, H, K, up, dive, loop), for the fixed build
VER=$1; BASE=$2; CPUF=${3:-1}; REP=${4:-1}; TAG=$VER-c$CPUF-r$REP; D=/home/yaroslavvb/claude/work/ladder/final/motion
cd /home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion
export TMPDIR=$D/tmp CPU=$CPUF UDD=$D/udd-chip-$VER REC=./recorder-chip.js STATE='window.__chipState()' STEPTXT="(document.getElementById('st-live')||{}).textContent"
for f in 1:A 8:H b:K; do q=${f%%:*}; k=${f##*:}
  UNTIL='window.__chipState().done' node drive.mjs $BASE/chip.html "?flow=$q" $D/$TAG-$k.json 1280 800 1 150 2>$D/$TAG-$k.log
done
SI="shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma/vpu.lane.fma.tree/fma.tree.col/lib.cmp42/lib.fa/lib.xor/lib.finfet/lib.fin/lib.channel/lib.si"
UP=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(36) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1700})]))")
DIVE=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(36) for x in ({'key': '+'}, {'wait': 1900})]))")
SCEN="$UP" UNTIL='window.__chipState().depth === 0 && !window.__chipState().zooming' node drive.mjs $BASE/chip.html "?at=$SI" $D/$TAG-up.json 1280 800 1 100 2>$D/$TAG-up.log
SCEN="$DIVE" UNTIL="/lib\.si\$/.test(window.__chipState().path) && !window.__chipState().zooming" node drive.mjs $BASE/chip.html "?at=beyond" $D/$TAG-dive.json 1280 800 1 110 2>$D/$TAG-dive.log
LOOP=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(5) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1900})]))")
SCEN="$LOOP" UNTIL="window.__chipState().node === 'p.atom' && !window.__chipState().zooming" node drive.mjs $BASE/chip.html "?at=beyond" $D/$TAG-loop.json 1280 800 1 40 2>$D/$TAG-loop.log
for k in A H K up dive loop; do f=$D/$TAG-$k.json; [ -f $f ] && python3 summ.py $f; done > $D/$TAG-summ.txt 2>&1
for k in A H K up dive loop; do f=$D/$TAG-$k.json; [ -f $f ] && { echo "## $k"; python3 moves.py $f; }; done > $D/$TAG-moves.txt 2>&1
echo done >> $D/$TAG-summ.txt
