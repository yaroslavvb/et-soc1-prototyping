#!/usr/bin/env bash
# vrun.sh : the keyboard-zoom motion runs only (vtree on both pages, vadd on the ladder's), CPU 1x and 4x
D=/home/yaroslavvb/claude/work/ladder/motion; R=/home/yaroslavvb/claude/et-soc1-ladder/docs/reports/data/2026-10-01-ladder/motion/run.sh
cd /home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion
export CHROME=$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome UDD=$D/udd REC=./recorder-chip.js STATE='window.__chipState()' STEPTXT="(document.getElementById('st-live')||{}).textContent"
eval "$(grep '^FA=\|^VT=' $R)"; eval "$(grep '^  VA=' $R | sed 's/^  //')"
for C in 1 4; do export CPU=$C
  for P in base u2e; do
    SCEN="$VT" UNTIL="/vpu\.lane\.fma\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 22000" node drive.mjs http://127.0.0.1:8765/$P/chip.html "?at=$FA" $D/$P-c$C-vtree.json 1280 800 1 90 2>$D/$P-c$C-vtree.log
  done
  SCEN="$VA" UNTIL="/vpu\.lane\.fma\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 25000" node drive.mjs http://127.0.0.1:8765/u2e/chip.html "?at=$FA" $D/u2e-c$C-vadd.json 1280 800 1 90 2>$D/u2e-c$C-vadd.log
done
for f in base-c1-vtree u2e-c1-vtree u2e-c1-vadd base-c4-vtree u2e-c4-vtree u2e-c4-vadd; do python3 summ.py $D/$f.json; done > $D/vrun-summ.txt 2>&1
echo VDONE >> $D/vrun-summ.txt
