#!/usr/bin/env bash
# outin.sh PAGEURL TAG [CPU]: only the new page's two ladder flows of run.sh (out from the L3's map and back; in from the
# L2's cell and back), to check the hand-over's first frames
PAGE=$1; TAG=$2; CPUF=${3:-1}; D=/home/yaroslavvb/claude/work/ladder/p2/motion
cd /home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion
export CHROME=$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome UDD=$D/udd TMPDIR=/home/yaroslavvb/claude/work/ladder/p2/tmp CPU=$CPUF
UP=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(5) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1900})] + [x for i in range(5) for x in ({'eval': \"document.querySelector('#pmz [data-ci=plus]').click()\"}, {'wait': 1900})]))")
REC=./recorder-mlchip.js SCEN="$UP" UNTIL="performance.now() > 22000 && !window.__memState().ladder.zooming && !window.__memState().ladder.on" node drive.mjs $PAGE '#l3' $D/$TAG-out.json 1280 800 1 60 2>$D/$TAG-out.log
IN=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(5) for x in ({'eval': \"document.querySelector('#pmz [data-ci=plus]').click()\"}, {'wait': 1900})] + [x for i in range(5) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1900})]))")
REC=./recorder-mlchip.js SCEN="$IN" UNTIL="performance.now() > 22000 && !window.__memState().ladder.zooming && !window.__memState().ladder.on" node drive.mjs $PAGE '#l2/cell' $D/$TAG-in.json 1280 800 1 60 2>$D/$TAG-in.log
for k in out in; do python3 summ.py $D/$TAG-$k.json; done > $D/$TAG-summ.txt 2>&1
for k in out in; do echo "## $k"; python3 kink.py $D/$TAG-$k.json; done > $D/$TAG-kink.txt 2>&1
