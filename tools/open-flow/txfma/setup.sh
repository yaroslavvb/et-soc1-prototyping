#!/bin/bash
# Q126(e): fetch the open EDA flow into $SCRATCH. Nothing is installed system-wide.
#   SCRATCH=$HOME/scratch-open-flow bash tools/open-flow/txfma/setup.sh
# About 4 GB on disk and 15 minutes on a cold machine, most of it the oss-cad-suite download.
set -u
S=${SCRATCH:?set SCRATCH to a directory outside any synced folder}
mkdir -p "$S/bin"
LOG=$S/setup.log
echo "=== $(date -Is) setup ===" >> "$LOG"

# 1. Yosys (with the slang SystemVerilog frontend), Verilator 5, Icarus 14
if [ ! -x "$S/oss-cad-suite/bin/yosys" ]; then
  REL=$(curl -sS -m 60 https://api.github.com/repos/YosysHQ/oss-cad-suite-build/releases/latest \
        | grep -o '"browser_download_url": *"[^"]*linux-x64[^"]*\.tgz"' | head -1 | cut -d'"' -f4)
  echo "oss-cad-suite: $REL" >> "$LOG"
  nice -n 19 curl -L -m 1800 -o "$S/oss.tgz" "$REL" >> "$LOG" 2>&1
  nice -n 19 tar -xzf "$S/oss.tgz" -C "$S" >> "$LOG" 2>&1 && rm -f "$S/oss.tgz"
fi

# 2. OpenROAD (OpenRCX + OpenSTA come with it) from the litex-hub conda channel.
#    'openroad' alone: adding 'tcl' makes the solver pick a build line whose libboost is gone.
if [ ! -x "$S/bin/micromamba" ]; then
  curl -Ls -m 300 https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C "$S" bin/micromamba
fi
export MAMBA_ROOT_PREFIX=$S/mamba
if [ ! -x "$S/eda/bin/openroad" ]; then
  nice -n 19 "$S/bin/micromamba" create -y -p "$S/eda" -c litex-hub -c conda-forge openroad >> "$LOG" 2>&1
fi

# 3. The ORFS asap7 platform: LEF, liberty, RC, rcx rules, tracks. Already at 1x (see README).
if [ ! -d "$S/orfs/flow/platforms/asap7/lib" ]; then
  rm -rf "$S/orfs"
  nice -n 19 git clone --depth 1 --filter=blob:none --sparse \
      https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts "$S/orfs" >> "$LOG" 2>&1
  ( cd "$S/orfs" && git sparse-checkout set flow/platforms/asap7 flow/util flow/scripts ) >> "$LOG" 2>&1
fi

# 4. ASAP7's transistor-level CDL, for the transistor and fin census
if [ ! -d "$S/asap7cells/CDL" ]; then
  rm -rf "$S/asap7cells"
  nice -n 19 git clone --depth 1 --filter=blob:none --sparse \
      https://github.com/The-OpenROAD-Project/asap7sc7p5t_28 "$S/asap7cells" >> "$LOG" 2>&1
  ( cd "$S/asap7cells" && git sparse-checkout set --skip-checks CDL LICENSE ) >> "$LOG" 2>&1
fi

# 5. The RTL
if [ ! -d "$S/core-et/.git" ]; then
  rm -rf "$S/core-et"
  nice -n 19 git clone --depth 1 --branch erbium \
      https://github.com/openhwfoundation/core-et.git "$S/core-et" >> "$LOG" 2>&1
fi

{ echo "--- versions ---"
  "$S/oss-cad-suite/bin/yosys" -V
  "$S/oss-cad-suite/bin/verilator" --version
  "$S/oss-cad-suite/bin/iverilog" -V 2>&1 | head -1
  echo "openroad $("$S/eda/bin/openroad" -version)"
  echo "orfs $(git -C "$S/orfs" rev-parse HEAD)"
  echo "asap7sc7p5t_28 $(git -C "$S/asap7cells" rev-parse HEAD)"
  echo "core-et $(git -C "$S/core-et" rev-parse HEAD)"
} | tee -a "$LOG"
