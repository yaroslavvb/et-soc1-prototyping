cd ~/q126d/work/decks
NG="$HOME/q126d/ngspice/bin/ngspice"
for f in dev_25.sp dev_80.sp fo4_0p517.sp leak_25_0p517.sp leak_80_0p517.sp en_INVx1_0p517_0p0.sp en_INVx1_0p517_0p5.sp en_INVx1_0p517_1p0.sp en_INVx1_0p517_2p0.sp en_INVx1_0p517_4p0.sp en_INVx1_0p517_8p0.sp en_NAND2x1_0p517_0p0.sp en_NAND2x1_0p517_0p5.sp en_NAND2x1_0p517_1p0.sp en_NAND2x1_0p517_2p0.sp en_NAND2x1_0p517_4p0.sp en_NAND2x1_0p517_8p0.sp en_FAx1_0p517_0p0.sp en_FAx1_0p517_0p5.sp en_FAx1_0p517_1p0.sp en_FAx1_0p517_2p0.sp en_FAx1_0p517_4p0.sp en_FAx1_0p517_8p0.sp sc_0p517_1.sp sc_0p517_2.sp sc_0p517_5.sp sc_0p517_10.sp sc_0p517_20.sp sc_0p517_50.sp sc_0p517_100.sp sc_0p517_200.sp fo4_0p700.sp leak_25_0p700.sp leak_80_0p700.sp en_INVx1_0p700_0p0.sp en_INVx1_0p700_0p5.sp en_INVx1_0p700_1p0.sp en_INVx1_0p700_2p0.sp en_INVx1_0p700_4p0.sp en_INVx1_0p700_8p0.sp en_NAND2x1_0p700_0p0.sp en_NAND2x1_0p700_0p5.sp en_NAND2x1_0p700_1p0.sp en_NAND2x1_0p700_2p0.sp en_NAND2x1_0p700_4p0.sp en_NAND2x1_0p700_8p0.sp en_FAx1_0p700_0p0.sp en_FAx1_0p700_0p5.sp en_FAx1_0p700_1p0.sp en_FAx1_0p700_2p0.sp en_FAx1_0p700_4p0.sp en_FAx1_0p700_8p0.sp sc_0p700_1.sp sc_0p700_2.sp sc_0p700_5.sp sc_0p700_10.sp sc_0p700_20.sp sc_0p700_50.sp sc_0p700_100.sp sc_0p700_200.sp; do
  echo "===DECK $f"
  nice -n 15 "$NG" -b "$f" 2>&1
done
echo "===ALLDONE"
