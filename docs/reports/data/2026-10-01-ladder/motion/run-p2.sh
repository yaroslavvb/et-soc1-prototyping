#!/usr/bin/env bash
# run.sh PAGEURL TAG [CPU] [NEW]: the memory levels' motion runs, one at a time, a warm profile, 1280x800 DPR 1:
#   the access #dram/load (the levels' camera following an access), the level tabs (5, 2, 1, 3, 4: a cross-fade between
#   the maps, out and in between levels), and on the new page (NEW=1) the ladder: Up from the L3's map out to the rack
#   and + back in (the hand-over both ways), and + from the L2's cell to an atom and Up back (the inner scales)
PAGE=$1; TAG=$2; CPUF=${3:-1}; D=/home/yaroslavvb/claude/work/ladder/p2/motion
cd /home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion
export CHROME=$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome UDD=$D/udd TMPDIR=/home/yaroslavvb/claude/work/ladder/p2/tmp
export CPU=$CPUF
node drive.mjs $PAGE '#dram/load' $D/$TAG-load.json 1280 800 1 150 2>$D/$TAG-load.log
TABS='[{"wait":1500},{"key":"5"},{"wait":2600},{"key":"2"},{"wait":2600},{"key":"1"},{"wait":2600},{"key":"3"},{"wait":2600},{"key":"4"},{"wait":2600},{"key":"1"},{"wait":2600}]'
SCEN="$TABS" UNTIL='performance.now() > 20000 && !window.__memState().zooming' node drive.mjs $PAGE '#l1' $D/$TAG-tabs.json 1280 800 1 60 2>$D/$TAG-tabs.log
if [ -n "$NEW" ]; then
  UP=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(5) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1900})] + [x for i in range(5) for x in ({'eval': \"document.querySelector('#pmz [data-ci=plus]').click()\"}, {'wait': 1900})]))")
  REC=./recorder-mlchip.js SCEN="$UP" UNTIL="performance.now() > 22000 && !window.__memState().ladder.zooming && !window.__memState().ladder.on" node drive.mjs $PAGE '#l3' $D/$TAG-out.json 1280 800 1 60 2>$D/$TAG-out.log
  IN=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(5) for x in ({'eval': \"document.querySelector('#pmz [data-ci=plus]').click()\"}, {'wait': 1900})] + [x for i in range(5) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1900})]))")
  REC=./recorder-mlchip.js SCEN="$IN" UNTIL="performance.now() > 22000 && !window.__memState().ladder.zooming && !window.__memState().ladder.on" node drive.mjs $PAGE '#l2/cell' $D/$TAG-in.json 1280 800 1 60 2>$D/$TAG-in.log
fi
for k in load tabs out in; do [ -f $D/$TAG-$k.json ] && python3 summ.py $D/$TAG-$k.json; done > $D/$TAG-summ.txt 2>&1
for k in load tabs out in; do [ -f $D/$TAG-$k.json ] && { echo "## $k"; python3 kink.py $D/$TAG-$k.json; }; done > $D/$TAG-kink.txt 2>&1
echo done >> $D/$TAG-summ.txt
