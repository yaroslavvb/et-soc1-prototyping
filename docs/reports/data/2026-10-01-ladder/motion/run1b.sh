#!/usr/bin/env bash
# run1b.sh PAGEURL TAG [CPU] : part 1b's motion runs, one at a time, a warm profile, 1280x800 DPR 1: the flows A, H and K
# (parity), the vector add (as part 1), and part 1b's new paths by Enter on a part and Backspace back out: a PCIe lane down
# to an atom (lane, its CTLE, the pair, the fin, the channel, the crystal, an atom), the card's core regulator down to an
# atom (buck converter, power transistor, crystal, atom) and the wiring down to a copper atom
PAGE=$1; TAG=$2; CPUF=${3:-1}; D=/home/yaroslavvb/claude/work/ladder/p1b/motion
cd /home/yaroslavvb/claude/et-soc1-ladder/tools/pagemotion
export CHROME=$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome UDD=/home/yaroslavvb/claude/work/ladder/motion/udd REC=./recorder-chip.js STATE='window.__chipState()' STEPTXT="(document.getElementById('st-live')||{}).textContent"
export CPU=$CPUF TMPDIR=/home/yaroslavvb/claude/work/ladder/tmp
for f in 1:A 8:H b:K; do q=${f%%:*}; k=${f##*:}
  UNTIL='window.__chipState().done' node drive.mjs $PAGE "?flow=$q" $D/$TAG-c$CPUF-$k.json 1280 800 1 150 2>$D/$TAG-c$CPUF-$k.log
done
ent() { python3 -c "import json,sys; ks=sys.argv[1].split(','); n=int(sys.argv[2]); print(json.dumps([{'wait': 1500}] + [x for k in ks for x in ({'eval': \"[...document.querySelectorAll('#chip > g.lay')].filter(l => l.style.display !== 'none').pop().querySelector('.comp[data-comp=\\\"%s\\\"]').focus()\" % k}, {'key': 'Enter'}, {'wait': 1900})] + [x for i in range(n) for x in ({'key': 'Backspace'}, {'wait': 1700})]))" "$1" "$2"; }
FA="shire:0/minion:0.0.0/vpu/vpu.lane:0/vpu.lane.fma"
SCEN="$(ent fmaadd,pfx1,onefet,devring,thefin,lattice,oneatom 7)" UNTIL="/vpu\.lane\.fma\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 25000" node drive.mjs $PAGE "?at=$FA" $D/$TAG-c$CPUF-vadd.json 1280 800 1 90 2>$D/$TAG-c$CPUF-vadd.log
if [ -n "$NEW" ]; then
  SCEN="$(ent pcie.lane,ctle,pair,devring,thefin,lattice,oneatom 7)" UNTIL="/pcie\.phy\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 25000" node drive.mjs $PAGE "?at=pcie/pcie.phy" $D/$TAG-c$CPUF-lane.json 1280 800 1 90 2>$D/$TAG-c$CPUF-lane.log
  SCEN="$(ent vrm,hs,cell,oneatom 4)" UNTIL="/card:board\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 15000" node drive.mjs $PAGE "?at=card:board" $D/$TAG-c$CPUF-reg.json 1280 800 1 90 2>$D/$TAG-c$CPUF-reg.log
  SCEN="$(ent wires,cu,free 3)" UNTIL="/die\.metal\$/.test(window.__chipState().path) && !window.__chipState().zooming && performance.now() > 12000" node drive.mjs $PAGE "?at=die.metal" $D/$TAG-c$CPUF-wire.json 1280 800 1 90 2>$D/$TAG-c$CPUF-wire.log
fi
for k in A H K vadd lane reg wire; do [ -f $D/$TAG-c$CPUF-$k.json ] && python3 summ.py $D/$TAG-c$CPUF-$k.json; done > $D/$TAG-c$CPUF-summ.txt 2>&1
for k in A H K vadd lane reg wire; do [ -f $D/$TAG-c$CPUF-$k.json ] && { echo "## $k"; python3 kink.py $D/$TAG-c$CPUF-$k.json; }; done > $D/$TAG-c$CPUF-kink.txt 2>&1
echo done >> $D/$TAG-c$CPUF-summ.txt
