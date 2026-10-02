#!/usr/bin/env bash
# runchip.sh PAGEURL TAG [CPU]: the chip diagram's flows A, H, K and the tour (part 1's run.sh, first part), one at a
# time, a warm profile, 1280x800 DPR 1: the chip's own camera at parity after part 2's changes to the shared files
PAGE=$1; TAG=$2; CPUF=${3:-1}; D=/home/yaroslavvb/claude/work/ladder/p2/motion
cd /home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion
export CHROME=$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome UDD=$D/udd-chip TMPDIR=/home/yaroslavvb/claude/work/ladder/p2/tmp REC=./recorder-chip.js STATE='window.__chipState()' STEPTXT="(document.getElementById('st-live')||{}).textContent"
export CPU=$CPUF
for f in 1:A 8:H b:K; do q=${f%%:*}; k=${f##*:}
  UNTIL='window.__chipState().done' node drive.mjs $PAGE "?flow=$q" $D/$TAG-$k.json 1280 800 1 150 2>$D/$TAG-$k.log
done
UNTIL='window.__chipState().tour === 16' node drive.mjs $PAGE "?tour=1" $D/$TAG-tour.json 1280 800 1 60 2>$D/$TAG-tour.log
for k in A H K tour; do [ -f $D/$TAG-$k.json ] && python3 summ.py $D/$TAG-$k.json; done > $D/$TAG-summ.txt 2>&1
for k in A H K tour; do echo "## $k"; python3 kink.py $D/$TAG-$k.json; done > $D/$TAG-kink.txt 2>&1
echo done >> $D/$TAG-summ.txt
