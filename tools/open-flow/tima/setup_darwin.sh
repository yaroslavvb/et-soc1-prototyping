#!/bin/bash
# Q133(a): the open flow's tools on a Mac with an Intel CPU (darwin-x64), for the int8 unit.
#   SCRATCH=<dir outside any synced folder> bash tools/open-flow/tima/setup_darwin.sh
#
# tools/open-flow/txfma/setup.sh fetches the Linux builds (oss-cad-suite-linux-x64, micromamba
# linux-64, OpenROAD from litex-hub's linux-64 channel). This script keeps every pin of that file
# and changes only the platform of the one download that has a macOS build:
#   - oss-cad-suite: the SAME release tag (OSS_REL), its darwin-x64 asset. Yosys, the slang
#     frontend, Verilator and Icarus come from it.
#   - OpenROAD: Linux-only as pinned (a 2022 litex-hub linux-64 package), and not needed here:
#     a zero-delay toggle count needs no placement, routing or extraction. Not fetched.
#   - ORFS's asap7 platform, ASAP7's CDL and core-et: fetched at the same shas, as in setup.sh.
set -u
S=${SCRATCH:?set SCRATCH to a directory outside any synced folder}
mkdir -p "$S"
LOG=$S/setup.log
echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) setup_darwin ===" >> "$LOG"

# The pins, copied from tools/open-flow/txfma/setup.sh (keep them equal).
OSS_REL=${OSS_REL:-2026-10-26}
ORFS_SHA=${ORFS_SHA:-64939f3717ad7c694199ba04cb98924b98022868}
ASAP7_SHA=${ASAP7_SHA:-e5bd25da72cd297b8c0ec6f77600e0cbaa1124d0}
COREET_SHA=${COREET_SHA:-b38a1a31da67efe00c61e983e64b892c58080115}   # branch erbium

if [ ! -x "$S/oss-cad-suite/bin/yosys" ]; then
  REL=https://github.com/YosysHQ/oss-cad-suite-build/releases/download/$OSS_REL/oss-cad-suite-darwin-x64-$(echo "$OSS_REL" | tr -d -).tgz
  echo "oss-cad-suite: $REL" >> "$LOG"
  nice -n 19 curl -sS -L -m 3000 -o "$S/oss.tgz" "$REL" >> "$LOG" 2>&1
  shasum -a 256 "$S/oss.tgz" >> "$LOG"
  nice -n 19 tar -xzf "$S/oss.tgz" -C "$S" >> "$LOG" 2>&1 && rm -f "$S/oss.tgz"
fi

clone_at() {   # clone_at <url> <dir> <sha> [sparse paths...]   (as in txfma/setup.sh)
  local url=$1 dir=$2 sha=$3; shift 3
  rm -rf "$dir"; mkdir -p "$dir"
  ( cd "$dir" && git init -q . \
      && git remote add origin "$url" \
      && git config extensions.partialClone origin \
      && git fetch -q --depth 1 --filter=blob:none origin "$sha" \
      && if [ $# -gt 0 ]; then git sparse-checkout set --skip-checks "$@"; fi \
      && git checkout -q FETCH_HEAD ) >> "$LOG" 2>&1
}

if [ ! -d "$S/orfs/flow/platforms/asap7/lib" ]; then
  clone_at https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts "$S/orfs" "$ORFS_SHA" \
      flow/platforms/asap7
fi
if [ ! -d "$S/asap7cells/CDL" ]; then
  clone_at https://github.com/The-OpenROAD-Project/asap7sc7p5t_28 "$S/asap7cells" "$ASAP7_SHA" \
      CDL LICENSE
fi
if [ ! -d "$S/core-et/.git" ]; then
  clone_at https://github.com/openhwfoundation/core-et.git "$S/core-et" "$COREET_SHA"
fi

{ echo "--- versions ---"
  "$S/oss-cad-suite/bin/yosys" -V
  "$S/oss-cad-suite/bin/yosys" -p "plugin -i slang; read_slang --version" 2>&1 | grep -i "slang version" | head -1
  "$S/oss-cad-suite/bin/verilator" --version
  "$S/oss-cad-suite/bin/iverilog" -V 2>&1 | head -1
  echo "orfs $(git -C "$S/orfs" rev-parse HEAD)"
  echo "asap7sc7p5t_28 $(git -C "$S/asap7cells" rev-parse HEAD)"
  echo "core-et $(git -C "$S/core-et" rev-parse HEAD)"
  echo "oss-cad-suite $OSS_REL darwin-x64"
  echo "host $(uname -s) $(uname -r) $(uname -m) $(sysctl -n hw.ncpu) cpus"
} | tee -a "$LOG"
