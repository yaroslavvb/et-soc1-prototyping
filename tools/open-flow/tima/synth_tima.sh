#!/bin/bash
# Q133(a): core-et's tima_top (the int8 multiply-add: four 9x9 signed products, their sum, and the 32-bit add of C; two
# per vector lane) elaborated with yosys-slang and mapped onto ASAP7 RVT, TT corner, with tools/open-flow/txfma/synth.sh's
# recipe: the same liberty files, the same dont-use list, the same abc period (1250 ps), the same tie cells.
#   SCRATCH=<setup_darwin.sh's dir> bash tools/open-flow/tima/synth_tima.sh
#
# The RTL writes the products as `$signed(f2_in1_part[i]) * $signed(f2_in2_part[i])` (tima_top.v:89) and the sums as `+`
# (tima_top.v:94, tima_adder.v:17): the gates are the synthesis tool's choice, not the RTL's. So this writes one netlist per
# architecture the open tools offer, all flattened (the netlist a normal flow hands on; txfma/synth.sh's `flat`):
#   plain       synth -flatten                     the open flow exactly as txfma/synth.sh runs it (no Booth pass)
#   booth       synth -flatten -booth              radix-4 Booth products, the sums as yosys's alumacc/maccmap leaves them
#   booth_tree  synth -flatten -booth -arith_tree  radix-4 Booth products, and the sums as carry-save adder trees
#   booth_swap  booth_tree on a copy of tima_top.v whose product reads in2 * in1: the same function, with the Booth
#               recoding moved to the other operand (yosys recodes a fixed operand position; see recoded_operand.txt)
# Writes $SCRATCH/work/tima/syn/tima_<arm>.{v,json}, stat_<arm>.txt, and the uncompressed liberty files in work/lib.
set -u
S=${SCRATCH:?set SCRATCH}
W=$S/work
T=$W/tima
R=$S/core-et/rtl
P=$S/orfs/flow/platforms/asap7
Y=$S/oss-cad-suite/bin/yosys
PERIOD=${PERIOD:-1250}
ARMS=${ARMS:-plain booth booth_tree booth_swap}
mkdir -p "$T/syn" "$W/lib"
LOG=$T/syn/synth.log
: > "$LOG"

LIBARGS=""
for g in "$P"/lib/NLDM/asap7sc7p5t_{AO,INVBUF,OA,SIMPLE}_RVT_TT_nldm_*.lib.gz; do
  [ -e "$g" ] || continue
  o=$W/lib/$(basename "$g" .gz); [ -s "$o" ] || gzip -dc "$g" > "$o"; LIBARGS="$LIBARGS -liberty $o"
done
for f in "$P"/lib/NLDM/asap7sc7p5t_SEQ_RVT_TT_nldm_*.lib; do
  [ -e "$f" ] || continue
  o=$W/lib/$(basename "$f"); [ -s "$o" ] || cp "$f" "$o"; LIBARGS="$LIBARGS -liberty $o"
done
DU="-dont_use *x1p*_ASAP7* -dont_use *xp*_ASAP7* -dont_use SDF* -dont_use ICG*"

# The swapped copy: one textual change, checked to have happened exactly once.
SWAP=$T/syn/tima_top_swap.v
sed 's/\$signed(f2_in1_part\[i\])\*\$signed(f2_in2_part\[i\])/$signed(f2_in2_part[i])*$signed(f2_in1_part[i])/' \
  "$R/shire/minion/vpu/tima/tima_top.v" > "$SWAP"
[ "$(diff "$R/shire/minion/vpu/tima/tima_top.v" "$SWAP" | grep -c '^>')" = 1 ] || { echo "swap edit failed"; exit 1; }

synth_one() {   # synth_one <arm> <top file> <synth flags>
  local arm=$1 top=$2 flags=$3
  { echo "plugin -i slang"
    printf 'read_slang --std 1800-2017 --single-unit --compat vcs --allow-use-before-declare'
    printf ' --relax-enum-conversions --top tima_top -I %s -I %s \\\n' "$R/inc" "$R"
    printf '  %s \\\n' "$top" "$R/shire/minion/vpu/tima/tima_adder.v"
    echo "  --error-limit=200"
    echo "hierarchy -check -top tima_top"
    echo "synth -top tima_top -flatten $flags"
    echo "opt -purge"
    echo "dfflibmap $LIBARGS $DU"
    echo "opt"
    echo "abc $LIBARGS -D $PERIOD $DU"
    echo "setundef -zero"
    echo "opt_clean -purge"
    echo "hilomap -singleton -hicell TIEHIx1_ASAP7_75t_R H -locell TIELOx1_ASAP7_75t_R L"
    echo "tee -o $T/syn/stat_$arm.txt stat $LIBARGS"
    echo "write_verilog -noattr -noexpr -nohex -nodec $T/syn/tima_$arm.v"
    echo "write_json $T/syn/tima_$arm.json"
  } > "$T/syn/syn_$arm.ys"
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) $arm period=${PERIOD}ps flags='$flags' ===" >> "$LOG"
  nice -n 10 "$Y" -s "$T/syn/syn_$arm.ys" >> "$LOG" 2>&1
  echo "rc=$? $arm" >> "$LOG"
}

for arm in $ARMS; do
  case $arm in
    plain)      synth_one plain      "$R/shire/minion/vpu/tima/tima_top.v" "" ;;
    booth)      synth_one booth      "$R/shire/minion/vpu/tima/tima_top.v" "-booth" ;;
    booth_tree) synth_one booth_tree "$R/shire/minion/vpu/tima/tima_top.v" "-booth -arith_tree" ;;
    booth_swap) synth_one booth_swap "$SWAP"                               "-booth -arith_tree" ;;
  esac
done
grep "^rc=" "$LOG"
for arm in $ARMS; do
  printf '%-11s ' "$arm"; grep -m1 "Chip area for top module\|Chip area for module" "$T/syn/stat_$arm.txt" | sed 's/^ *//'
  grep -E "^ +[0-9]+ +cells$|Number of cells" "$T/syn/stat_$arm.txt" | head -1
done
