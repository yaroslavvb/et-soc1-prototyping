#!/bin/bash
# Q130(i): build and run the structural register-file audit. Desk compute; no card was used.
#
#   OUT=<scratch dir> TILES_DIR=<dir holding <pattern>.hex> bash run.sh [pattern ...]
#
# Verilator only. On the Intel (macOS x86_64) the conda-forge build in ~/.local is the one
# rtl-sim/fma_toggle/README.md § "On a Mac" installs; its generated makefile names a cross
# compiler it does not ship on PATH, so CXX/LINK are overridden the way that Makefile does.
set -u
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT=${OUT:?set OUT to a writable scratch directory}
TILES_DIR=${TILES_DIR:?set TILES_DIR}
VERILATOR=${VERILATOR:-$HOME/.local/micromamba/envs/verilator/bin/verilator}
CXXOVERRIDE=${CXXOVERRIDE:-/usr/bin/clang++}
JOBS=${JOBS:-4}
mkdir -p "$OUT"

if [ ! -x "$OUT/obj_dir/Vtb" ]; then
  PATH="$(dirname "$VERILATOR"):$PATH" \
  nice -n 10 "$VERILATOR" --binary --timing -Wno-fatal -Wno-lint -Wno-style \
    --top-module tb -j "$JOBS" \
    -MAKEFLAGS CXX="$CXXOVERRIDE" -MAKEFLAGS LINK="$CXXOVERRIDE" \
    --Mdir "$OUT/obj_dir" -o Vtb \
    "$D/rf3r2w_struct.sv" "$D/tb_gate_audit.sv" > "$OUT/build.log" 2>&1
  rc=$?
  echo "build rc=$rc (log $OUT/build.log)"
  [ -x "$OUT/obj_dir/Vtb" ] || { tail -40 "$OUT/build.log"; exit 1; }
fi

: > "$OUT/counts.txt"
for p in ${@:-zeros ones randn sparse75}; do
  for am in 0 1; do
    nice -n 10 "$OUT/obj_dir/Vtb" +tiles="$TILES_DIR/$p.hex" +ops=1 +warm=1 +allmadd=$am \
      | grep -E '^CNT' | sed -e "s|^CNT ||" -e "s|\"tiles\":\"[^\"]*/|\"tiles\":\"|" >> "$OUT/counts.txt"
  done
done
wc -l < "$OUT/counts.txt"
