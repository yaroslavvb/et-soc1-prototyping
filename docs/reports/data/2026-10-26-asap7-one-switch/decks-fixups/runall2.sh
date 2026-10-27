cd ~/q126d/work/decks2
NG="$HOME/q126d/ngspice/bin/ngspice"
for f in fa_noc_0p517_0p0.sp fa_noc_0p517_0p5.sp fa_noc_0p517_1p0.sp fa_noc_0p517_2p0.sp fa_noc_0p517_4p0.sp fa_noc_0p517_8p0.sp fa_cc_0p517_2p0.sp fa_st_0p517_B0CI0.sp fa_st_0p517_B0CI1.sp fa_st_0p517_B1CI0.sp fa_st_0p517_B1CI1.sp nand_B1_0p517.sp xor_B0_0p517.sp xor_B1_0p517.sp fa_noc_0p700_0p0.sp fa_noc_0p700_0p5.sp fa_noc_0p700_1p0.sp fa_noc_0p700_2p0.sp fa_noc_0p700_4p0.sp fa_noc_0p700_8p0.sp fa_cc_0p700_2p0.sp fa_st_0p700_B0CI0.sp fa_st_0p700_B0CI1.sp fa_st_0p700_B1CI0.sp fa_st_0p700_B1CI1.sp nand_B1_0p700.sp xor_B0_0p700.sp xor_B1_0p700.sp; do
  echo "===DECK $f"
  nice -n 15 "$NG" -b "$f" 2>&1
done
echo "===ALLDONE"
