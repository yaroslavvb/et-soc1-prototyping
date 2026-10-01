#!/usr/bin/env bash
# run.sh PAGEURL TAG [CPU] : the chip diagram's motion runs, one at a time, a warm profile, 1280x800 DPR 1:
#   flows 1 (A), 8 (H), B (K) and the tour (parity with bb0eb78), Up from the silicon crystal to the top (the base's
#   deepest scale), the dive (+ from the top to the silicon crystal), and on the ladder's page also the loop (Up from
#   the atom where the ring lands, round the ring and in again as the same atom, to the die), a vector add (Enter down
#   from the multiply-add through a textbook adder to an atom, Backspace back out) and the sideways links to a memory
#   shire and back (since the owner's second update of 1 Oct)
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
# zooms by Enter on a part, on both pages (the parity for the vector add below): from the multiply-add into its tree, a
# column, a 4:2 compressor, a full adder, an XOR gate and a transistor, then Backspace back out
FA="shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma"
VT=$(python3 -c "import json; ks=['fmatree','treecol','colc42','fa1','xor1','onefet']; print(json.dumps([{'wait': 1500}] + [x for k in ks for x in ({'eval': \"[...document.querySelectorAll('#chip > g.lay')].filter(l => l.style.display !== 'none').pop().querySelector('.comp[data-comp=\\\"%s\\\"]').focus()\" % k}, {'key': 'Enter'}, {'wait': 1900})] + [x for i in range(6) for x in ({'key': 'Backspace'}, {'wait': 1700})]))")
SCEN="$VT" UNTIL="/vpu\.lane\.fma\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 22000" node drive.mjs $PAGE "?at=$FA" $D/$TAG-vtree.json 1280 800 1 90 2>$D/$TAG-vtree.log
if [ -n "$LADDER" ]; then
  # the loop (the owner's second update, 1 Oct 09:00): Up from the atom where the ring lands (in a transistor of lane 0's
  # multiply-add) to the die, out to the top, round the ring, in as the same atom and up to the die again: 52 presses
  WR=$(python3 -c "import json; print(json.dumps([{'wait': 1500}] + [x for i in range(52) for x in ({'eval': \"document.getElementById('up').click()\"}, {'wait': 1700})]))")
  SCEN="$WR" UNTIL="window.__chipState().node === 'die' && window.__chipTest.wrapin() === null && window.__chipState().depth > 25 && !window.__chipState().zooming" node drive.mjs $PAGE "?at=$SI/p.atom" $D/$TAG-wrap.json 1280 800 1 140 2>$D/$TAG-wrap.log
  # a vector add (the owner's case): from the multiply-add, Enter on the adder, a carry cell, a transistor, the fin, the
  # channel, the crystal and an atom; then Backspace back out to the multiply-add
  VA=$(python3 -c "import json; ks=['fmaadd','pfx1','onefet','devring','thefin','lattice','oneatom']; print(json.dumps([{'wait': 1500}] + [x for k in ks for x in ({'eval': \"[...document.querySelectorAll('#chip > g.lay')].filter(l => l.style.display !== 'none').pop().querySelector('.comp[data-comp=\\\"%s\\\"]').focus()\" % k}, {'key': 'Enter'}, {'wait': 1900})] + [x for i in range(7) for x in ({'key': 'Backspace'}, {'wait': 1700})]))")
  SCEN="$VA" UNTIL="/vpu\.lane\.fma\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 25000" node drive.mjs $PAGE "?at=$FA" $D/$TAG-vadd.json 1280 800 1 90 2>$D/$TAG-vadd.log
  # sideways and back: shire 24 west to memory shire 0, its south link to memory shire 1 and back north, and east back to
  # shire 24 (each by its link, Enter)
  NB=$(python3 -c "import json; L=['Go to memory shire 0, west','Go to memory shire 1, south','Go to memory shire 0, north','Go to shire 24, east']; print(json.dumps([{'wait': 1500}] + [x for l in L for x in ({'eval': \"[...document.querySelectorAll('#chip .nbr')].filter(g => g.getClientRects().length).find(g => g.getAttribute('aria-label') === '%s').focus()\" % l}, {'key': 'Enter'}, {'wait': 1600})]))")
  SCEN="$NB" UNTIL="/die\/shire:24\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 9000" node drive.mjs $PAGE "?at=shire:24" $D/$TAG-side.json 1280 800 1 60 2>$D/$TAG-side.log
fi
for k in A H K tour up dive vtree wrap vadd side; do [ -f $D/$TAG-$k.json ] && python3 summ.py $D/$TAG-$k.json; done > $D/$TAG-summ.txt 2>&1
for k in A H K tour; do echo "## $k"; python3 kink.py $D/$TAG-$k.json; done > $D/$TAG-kink.txt 2>&1
echo done >> $D/$TAG-summ.txt
