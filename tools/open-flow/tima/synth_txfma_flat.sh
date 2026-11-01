#!/bin/bash
# Q133(a): the float unit, txfma_top, as tools/open-flow/txfma/synth.sh's `flat` netlist and nothing else: the same file list,
# slang flags, synth -flatten, dfflibmap, abc at 1250 ps, dont-use list and tie cells, so the float and int8 units come from one
# recipe. It exists so that the three formats can be counted at gate level in one bench (rtl-sim/tima_gate).
#   SCRATCH=<setup_darwin.sh's dir> bash tools/open-flow/tima/synth_txfma_flat.sh
# Writes $SCRATCH/work/syn/txfma_flat.{v,json} and stat_flat.txt, as synth.sh does.
set -u
S=${SCRATCH:?set SCRATCH}
W=$S/work
R=$S/core-et/rtl
P=$S/orfs/flow/platforms/asap7
Y=$S/oss-cad-suite/bin/yosys
PERIOD=${PERIOD:-1250}
mkdir -p "$W/syn" "$W/lib"
LOG=$W/syn/synth_flat.log
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
FL=$W/syn/files.txt
: > "$FL"
echo "$R/shire/minion/vpu/txfma_7s/txfma_top.v" >> "$FL"
for f in "$R"/shire/minion/vpu/txfma_7s/*.v; do
  [ "$f" = "$R/shire/minion/vpu/txfma_7s/txfma_top.v" ] || echo "$f" >> "$FL"
done
for d in rf_latches compressors floating_point fixed_point registers; do
  for f in "$R/libs/$d"/*.v; do [ -e "$f" ] && echo "$f" >> "$FL"; done
done
{ echo "plugin -i slang"
  printf 'read_slang --std 1800-2017 --single-unit --compat vcs --allow-use-before-declare'
  printf ' --relax-enum-conversions  --top txfma_top -I %s -I %s \\\n' "$R/inc" "$R"
  while read -r f; do printf '  %s \\\n' "$f"; done < "$FL"
  echo "  --error-limit=200"
  echo "hierarchy -check -top txfma_top"
  echo "synth -top txfma_top -flatten"
  echo "opt -purge"
  echo "dfflibmap $LIBARGS $DU"
  echo "opt"
  echo "abc $LIBARGS -D $PERIOD $DU"
  echo "setundef -zero"
  echo "opt_clean -purge"
  echo "hilomap -singleton -hicell TIEHIx1_ASAP7_75t_R H -locell TIELOx1_ASAP7_75t_R L"
  echo "tee -o $W/syn/stat_flat.txt stat $LIBARGS"
  echo "write_verilog -noattr -noexpr -nohex -nodec $W/syn/txfma_flat.v"
  echo "write_json $W/syn/txfma_flat.json"
} > "$W/syn/syn_flat.ys"
echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) flat period=${PERIOD}ps ===" >> "$LOG"
nice -n 10 "$Y" -s "$W/syn/syn_flat.ys" >> "$LOG" 2>&1
echo "rc=$? flat" >> "$LOG"
grep "^rc=" "$LOG"
grep -m1 "Chip area for module" "$W/syn/stat_flat.txt"
