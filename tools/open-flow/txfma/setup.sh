#!/bin/bash
# Q126(e): fetch the open EDA flow into $SCRATCH. Nothing is installed system-wide.
#   SCRATCH=$HOME/scratch-open-flow bash tools/open-flow/txfma/setup.sh
# About 4 GB on disk and 15 minutes on a cold machine, most of it the oss-cad-suite download.
set -u
S=${SCRATCH:?set SCRATCH to a directory outside any synced folder}
mkdir -p "$S/bin"
LOG=$S/setup.log
echo "=== $(date -Is) setup ===" >> "$LOG"

# Everything is PINNED to what the published run used (docs/reports/data/2026-10-26-open-netlist/
# versions.txt), because the numbers in that directory depend on all of it: Verilator's version
# alone moves a toggle count 3x (Q126(b)). Override any of these to re-measure on a newer tool,
# and say in the report which pin you moved.
OSS_REL=${OSS_REL:-2026-10-26}                  # oss-cad-suite release tag
OPENROAD_PKG=${OPENROAD_PKG:-openroad=2.0_3175_gf12e2f474=20220317_162926}
ORFS_SHA=${ORFS_SHA:-64939f3717ad7c694199ba04cb98924b98022868}
ASAP7_SHA=${ASAP7_SHA:-e5bd25da72cd297b8c0ec6f77600e0cbaa1124d0}
COREET_SHA=${COREET_SHA:-b38a1a31da67efe00c61e983e64b892c58080115}   # branch erbium

# 1. Yosys (with the slang SystemVerilog frontend), Verilator 5, Icarus 14
if [ ! -x "$S/oss-cad-suite/bin/yosys" ]; then
  REL=https://github.com/YosysHQ/oss-cad-suite-build/releases/download/$OSS_REL/oss-cad-suite-linux-x64-$(echo "$OSS_REL" | tr -d -).tgz
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
  nice -n 19 "$S/bin/micromamba" create -y -p "$S/eda" -c litex-hub -c conda-forge "$OPENROAD_PKG" >> "$LOG" 2>&1
fi

# A pinned sha cannot be fetched out of a --depth 1 clone of a moving branch, so each clone
# below fetches that one commit by name. Blob-filtered and sparse, so it is still a few MB.
clone_at() {   # clone_at <url> <dir> <sha> [sparse paths...]
  local url=$1 dir=$2 sha=$3; shift 3
  rm -rf "$dir"; mkdir -p "$dir"
  ( cd "$dir" && git init -q . \
      && git remote add origin "$url" \
      && git config extensions.partialClone origin \
      && git fetch -q --depth 1 --filter=blob:none origin "$sha" \
      && if [ $# -gt 0 ]; then git sparse-checkout set --skip-checks "$@"; fi \
      && git checkout -q FETCH_HEAD ) >> "$LOG" 2>&1
}

# 3. The ORFS asap7 platform: LEF, liberty, RC, rcx rules, tracks. Already at 1x (see README).
if [ ! -d "$S/orfs/flow/platforms/asap7/lib" ]; then
  clone_at https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts "$S/orfs" "$ORFS_SHA" \
      flow/platforms/asap7 flow/util flow/scripts
fi

# 4. ASAP7's transistor-level CDL, for the transistor and fin census
if [ ! -d "$S/asap7cells/CDL" ]; then
  clone_at https://github.com/The-OpenROAD-Project/asap7sc7p5t_28 "$S/asap7cells" "$ASAP7_SHA" \
      CDL LICENSE
fi

# 5. The RTL
if [ ! -d "$S/core-et/.git" ]; then
  clone_at https://github.com/openhwfoundation/core-et.git "$S/core-et" "$COREET_SHA"
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
