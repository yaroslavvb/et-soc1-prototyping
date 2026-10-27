#!/bin/bash
# Q126(e): elaborate core-et's txfma_top with yosys-slang and map it onto ASAP7 RVT, TT corner.
#   SCRATCH=$HOME/scratch-open-flow [PERIOD=1250] bash tools/open-flow/txfma/synth.sh
# Writes $SCRATCH/work/syn/txfma_keep.{v,json}   hierarchy kept, for the per-block census
#        $SCRATCH/work/syn/txfma_flat.{v,json}   flattened, the netlist a normal flow would hand on
#        $SCRATCH/work/syn/txfma_mixed.{v,json}  flattened EXCEPT the four multiplier blocks, so
#                                                the multiplier's cell count can be compared with
#                                                a tape-out flow's without the hierarchy penalty
set -u
S=${SCRATCH:?set SCRATCH}
W=$S/work
R=$S/core-et/rtl
P=$S/orfs/flow/platforms/asap7
Y=$S/oss-cad-suite/bin/yosys
PERIOD=${PERIOD:-1250}          # ps. ASAP7's liberty time unit is 1 ps; 1250 ps = 800 MHz
mkdir -p "$W/syn" "$W/lib"
LOG=$W/syn/synth.log
: > "$LOG"

# One uncompressed liberty per ASAP7 cell group. Yosys reads ONE library() group per -liberty
# file, so these must stay separate: concatenating them hides the flip-flops.
LIBARGS=""
for g in "$P"/lib/NLDM/asap7sc7p5t_{AO,INVBUF,OA,SIMPLE}_RVT_TT_nldm_*.lib.gz; do
  [ -e "$g" ] || continue
  o=$W/lib/$(basename "$g" .gz); [ -s "$o" ] || zcat "$g" > "$o"; LIBARGS="$LIBARGS -liberty $o"
done
for f in "$P"/lib/NLDM/asap7sc7p5t_SEQ_RVT_TT_nldm_*.lib; do
  [ -e "$f" ] || continue
  o=$W/lib/$(basename "$f"); [ -s "$o" ] || cp "$f" "$o"; LIBARGS="$LIBARGS -liberty $o"
done

# ORFS's own dont-use list for asap7: the sub-unit drives, the scan flops, the clock gates
# (ORFS's asap7 flow does not insert ICGs, so the RTL's own et_clk_gate becomes a latch + gate).
DU="-dont_use *x1p*_ASAP7* -dont_use *xp*_ASAP7* -dont_use SDF* -dont_use ICG*"

# The file list: txfma_top.v FIRST (it is the only file that includes soc.vh, and the rest of the
# unit depends on one compilation unit for its types), then the rest, then the libs it instantiates.
FL=$W/syn/files.txt
: > "$FL"
echo "$R/shire/minion/vpu/txfma_7s/txfma_top.v" >> "$FL"
for f in "$R"/shire/minion/vpu/txfma_7s/*.v; do
  [ "$f" = "$R/shire/minion/vpu/txfma_7s/txfma_top.v" ] || echo "$f" >> "$FL"
done
for d in rf_latches compressors floating_point fixed_point registers; do
  for f in "$R/libs/$d"/*.v; do [ -e "$f" ] && echo "$f" >> "$FL"; done
done

# The four blocks the per-block census needs by name. slang mangles a kept module's name to
# <module>$<instance path>, which is what `setattr -mod` has to match; txfma_adder is used in
# more than one place, so the product adder is named by its full instance path.
KEEPMODS='txfma_booth_ppg_32r4$* txfma_wallace1$* txfma_wallace2$* txfma_adder$txfma_top.txfmafrac0_top.txfma0_f2.prod_adder_64b'

synth_one() {   # synth_one <tag> <slang hierarchy flag or empty> [extra synth flags] [keep-mods]
  local tag=$1 hier=$2
  { echo "plugin -i slang"
    printf 'read_slang --std 1800-2017 --single-unit --compat vcs --allow-use-before-declare'
    printf ' --relax-enum-conversions %s --top txfma_top -I %s -I %s \\\n' "$hier" "$R/inc" "$R"
    while read -r f; do printf '  %s \\\n' "$f"; done < "$FL"
    echo "  --error-limit=200"
    echo "hierarchy -check -top txfma_top"
    # flatten honours the keep_hierarchy attribute, so `mixed` gets cross-boundary optimisation
    # everywhere except the four blocks the census has to report separately.
    [ -n "${4:-}" ] && echo "setattr -mod -set keep_hierarchy 1 $4"
    echo "synth -top txfma_top${3:-}"
    echo "opt -purge"
    echo "dfflibmap $LIBARGS $DU"
    echo "opt"
    echo "abc $LIBARGS -D $PERIOD $DU"
    echo "setundef -zero"
    echo "opt_clean -purge"
    # Tie cells. Without them TritonRoute refuses the design: a bare 1'b0 net comes through as
    # a GROUND net, and detailed routing stops with DRT-0305.
    echo "hilomap -singleton -hicell TIEHIx1_ASAP7_75t_R H -locell TIELOx1_ASAP7_75t_R L"
    echo "tee -o $W/syn/stat_$tag.txt stat $LIBARGS"
    echo "write_verilog -noattr -noexpr -nohex -nodec $W/syn/txfma_$tag.v"
    echo "write_json $W/syn/txfma_$tag.json"
  } > "$W/syn/syn_$tag.ys"
  echo "=== $(date -Is) $tag period=${PERIOD}ps ===" >> "$LOG"
  nice -n 19 "$Y" -s "$W/syn/syn_$tag.ys" >> "$LOG" 2>&1
  echo "rc=$? $tag" >> "$LOG"
}

synth_one keep  "--keep-hierarchy" ""
synth_one flat  ""                 " -flatten"
synth_one mixed "--keep-hierarchy" " -flatten" "$KEEPMODS"
grep "^rc=" "$LOG"
grep -A2 "Chip area for top module\|Chip area for module ..txfma_top" "$W/syn/stat_keep.txt" | tail -4
