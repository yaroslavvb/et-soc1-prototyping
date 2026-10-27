#!/bin/bash
# Q129: elaborate q129_scope_top (the lane's register files, operand bus, result path and
# per-lane control) with yosys-slang and map it onto ASAP7 RVT, TT - the same recipe
# tools/open-flow/txfma/synth.sh uses for the arithmetic, so the two netlists are priced on
# the same library at the same corner.
#
#   SCRATCH=$HOME/scratch-q129-scope LAB=<checkout> [PERIOD=1250] bash synth.sh
#
# Writes $SCRATCH/work-scope/syn/scope_keep.{v,json}  every boundary kept (the per-block census)
#        $SCRATCH/work-scope/syn/scope_mixed.{v,json} flattened EXCEPT the eight scope blocks -
#        the netlist a normal flow would hand on, with just enough hierarchy to read per block.
#        Quote `mixed`, as Q126(e) trap 5 says.
set -u
S=${SCRATCH:?set SCRATCH}
L=${LAB:-$HOME/claude/et-soc1-prototyping}
W=$S/work-scope
R=$S/core-et/rtl
P=$S/orfs/flow/platforms/asap7
Y=$S/oss-cad-suite/bin/yosys
PERIOD=${PERIOD:-1250}          # ps. ASAP7's liberty time unit is 1 ps; 1250 ps = 800 MHz
mkdir -p "$W/syn" "$W/lib"
LOG=$W/syn/synth.log
: > "$LOG"

# One uncompressed liberty per ASAP7 cell group (Q126(e) trap 2: yosys reads one library()
# group per -liberty file, so they must stay separate).
LIBARGS=""
for g in "$P"/lib/NLDM/asap7sc7p5t_{AO,INVBUF,OA,SIMPLE}_RVT_TT_nldm_*.lib.gz; do
  [ -e "$g" ] || continue
  o=$W/lib/$(basename "$g" .gz); [ -s "$o" ] || zcat "$g" > "$o"; LIBARGS="$LIBARGS -liberty $o"
done
for f in "$P"/lib/NLDM/asap7sc7p5t_SEQ_RVT_TT_nldm_*.lib; do
  [ -e "$f" ] || continue
  o=$W/lib/$(basename "$f"); [ -s "$o" ] || cp "$f" "$o"; LIBARGS="$LIBARGS -liberty $o"
done
DU="-dont_use *x1p*_ASAP7* -dont_use *xp*_ASAP7* -dont_use SDF* -dont_use ICG*"

# The file list. q129_scope_top.v FIRST: it is the only file that includes soc.vh, and
# vpu_bypass.v / the libs rely on one compilation unit for the macros and the types
# (Q126(e) trap 1). Then the core-et modules the scope instantiates, then the libraries.
FL=$W/syn/files.txt
: > "$FL"
echo "$L/tools/open-flow/scope/q129_scope_top.v" >> "$FL"
for f in vpu_bypass.v vpu_tensora_rf.v vpu_tensorb_rf.v vpu_tensortmp_rf.v; do
  echo "$R/shire/minion/vpu/$f" >> "$FL"
done
for d in rf_latches registers; do
  for f in "$R/libs/$d"/*.v; do [ -e "$f" ] && echo "$f" >> "$FL"; done
done

# The eight blocks the per-block census reports. slang mangles a kept module's name to
# <module>$<instance path>, which is what `setattr -mod` has to match.
KEEPMODS='q129_vpu_rf_model$* rf_latch_3r_2w$* vpu_tensora_rf$* vpu_tensorb_rf$* vpu_tensortmp_rf$* q129_tenc_rf_model$* rf_latch_1r_1w$* vpu_bypass$* q129_lane_ctl$*'

synth_one() {   # synth_one <tag> <slang hier flag> <extra synth flags> [keep-mods]
  local tag=$1 hier=$2
  { echo "plugin -i slang"
    printf 'read_slang --std 1800-2017 --single-unit --compat vcs --allow-use-before-declare'
    printf ' --relax-enum-conversions %s --top q129_scope_top -I %s -I %s \\\n' "$hier" "$R/inc" "$R"
    while read -r f; do printf '  %s \\\n' "$f"; done < "$FL"
    echo "  --error-limit=200"
    echo "hierarchy -check -top q129_scope_top"
    [ -n "${4:-}" ] && echo "setattr -mod -set keep_hierarchy 1 $4"
    echo "synth -top q129_scope_top${3:-}"
    echo "opt -purge"
    echo "dfflibmap $LIBARGS $DU"
    echo "opt"
    echo "abc $LIBARGS -D $PERIOD $DU"
    echo "setundef -zero"
    echo "opt_clean -purge"
    echo "hilomap -singleton -hicell TIEHIx1_ASAP7_75t_R H -locell TIELOx1_ASAP7_75t_R L"
    echo "tee -o $W/syn/stat_$tag.txt stat $LIBARGS"
    echo "write_verilog -noattr -noexpr -nohex -nodec $W/syn/scope_$tag.v"
    echo "write_json $W/syn/scope_$tag.json"
  } > "$W/syn/syn_$tag.ys"
  echo "=== $(date -Is) $tag period=${PERIOD}ps ===" >> "$LOG"
  nice -n 19 "$Y" -s "$W/syn/syn_$tag.ys" >> "$LOG" 2>&1
  echo "rc=$? $tag" >> "$LOG"
}

synth_one keep  "--keep-hierarchy" ""
synth_one mixed "--keep-hierarchy" " -flatten" "$KEEPMODS"
grep "^rc=" "$LOG"
for t in keep mixed; do
  echo "--- $t"; grep -E "Number of cells|Number of wires|Chip area" "$W/syn/stat_$t.txt" | tail -3
done
