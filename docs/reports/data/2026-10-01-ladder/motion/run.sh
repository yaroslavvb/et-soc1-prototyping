#!/usr/bin/env bash
# run.sh PAGEURL TAG [CPU] : the chip diagram's motion runs, one at a time, a warm profile, 1280x800 DPR 1:
#   flows 1 (A), 8 (H), B (K) and the tour (parity with bb0eb78), Up from the silicon crystal to the top (the base's
#   deepest scale), the dive (+ from the top to the silicon crystal), and on the ladder's page also Up from the Planck
#   length to the top and round the ring (the wrap) and in again
PAGE=$1; TAG=$2; CPUF=${3:-1}; D=/home/yaroslavvb/claude/work/ladder/motion
cd /home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion
export CHROME=$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome UDD=$D/udd REC=./recorder-chip.js STATE='window.__chipState()' STEPTXT="(document.getElementById('st-live')||{}).textContent"
export CPU=$CPUF
for f in 1:A 8:H b:K; do q=${f%%:*}; k=${f##*:}
  UNTIL='window.__chipState().done' node drive.mjs $PAGE "?flow=$q" $D/$TAG-$k.json 1280 800 1 150 2>$D/$TAG-$k.log
done
UNTIL='window.__chipState().tour === 16' node drive.mjs $PAGE "?tour=1" $D/$TAG-tour.json 1280 800 1 60 2>$D/$TAG-tour.log
SI="shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma/vpu.lane.fma.tree/fma.tree.col/lib.cmp42/lib.fa/lib.xor/lib.finfet/lib.fin/lib.channel/lib.si"
UP=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(36) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1700})]))")
DIVE=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(36) for x in ({'key': '+'}, {'wait': 1900})]))")
SCEN="$UP" UNTIL='window.__chipState().depth === 0 && !window.__chipState().zooming' node drive.mjs $PAGE "?at=$SI" $D/$TAG-up.json 1280 800 1 100 2>$D/$TAG-up.log
SCEN="$DIVE" UNTIL="/lib\.si\$/.test(window.__chipState().path) && !window.__chipState().zooming" node drive.mjs $PAGE "?at=beyond" $D/$TAG-dive.json 1280 800 1 110 2>$D/$TAG-dive.log
if [ -n "$LADDER" ]; then
  # the wrap: Up from the Planck length to the top, round the ring, in again at the Planck length and up to the die
  WR=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(62) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1700})]))")
  SCEN="$WR" UNTIL="window.__chipState().node === 'die' && window.__chipState().depth > 25 && !window.__chipState().zooming" node drive.mjs $PAGE "?at=$SI/p.atom/p.nucleus/p.nucleon/p.quark/p.planck" $D/$TAG-wrap.json 1280 800 1 140 2>$D/$TAG-wrap.log
fi
for k in A H K tour up dive wrap; do [ -f $D/$TAG-$k.json ] && python3 summ.py $D/$TAG-$k.json; done > $D/$TAG-summ.txt 2>&1
for k in A H K tour; do echo "## $k"; python3 kink.py $D/$TAG-$k.json; done > $D/$TAG-kink.txt 2>&1
echo done >> $D/$TAG-summ.txt
