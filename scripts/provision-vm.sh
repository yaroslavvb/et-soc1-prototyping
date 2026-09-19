#!/usr/bin/env bash
# Provision an Ubuntu 24.04 machine (the Lima VM `et`, or any Ubuntu 24.04 box)
# for ET-SOC1 development, following the "Local Build Instructions" in
# external/et-platform/README.md:
#   1. apt build dependencies
#   2. ET RISC-V GNU toolchain (aifoundry-org/riscv-gnu-toolchain, branch `et`)
#      built from source -> /opt/et  (the prebuilt release tarball is x86_64-only)
#   3. et-platform superbuild -> /opt/et (sysemu simulator, runtime, firmware, ...)
#
# Idempotent: each stage is skipped if its output already exists.
# Usage (inside the VM):  scripts/provision-vm.sh [deps|toolchain|platform|all]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ET_PREFIX="${ET_PREFIX:-/opt/et}"
SRC_DIR="${SRC_DIR:-$HOME/src}"          # VM-local disk (ext4, case-sensitive)
BUILD_DIR="${BUILD_DIR:-$HOME/build}"    # VM-local disk
JOBS="${JOBS:-$(nproc)}"
STAGE="${1:-all}"

log() { printf '\n=== [%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

install_deps() {
  log "Installing apt dependencies"
  export DEBIAN_FRONTEND=noninteractive
  sudo -E apt-get update -q
  # Toolchain deps (docker/get_toolchain.sh) + platform deps (docker/Dockerfile)
  sudo -E apt-get install -y -q \
    autoconf automake autotools-dev curl python3 python3-pip python3-tomli \
    libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo \
    gperf libtool patchutils bc zlib1g-dev libexpat-dev dos2unix ninja-build \
    git cmake libglib2.0-dev libslirp-dev \
    pkg-config libjson-c-dev libgtest-dev libgoogle-glog-dev libgflags-dev \
    libgmock-dev lz4 liblz4-dev libboost-all-dev libcap-dev libcap2-bin \
    doxygen graphviz nlohmann-json3-dev python3-sphinx python3-sphinx-rtd-theme \
    python3-breathe python3-jsonschema libfmt-dev libfftw3-dev xxd \
    ccache gdb-multiarch vim jq
  sudo mkdir -p "$ET_PREFIX"
  sudo chown "$(id -u):$(id -g)" "$ET_PREFIX"
}

build_toolchain() {
  local done_marker="$ET_PREFIX/.et-toolchain-built"
  if [[ -f "$done_marker" ]]; then
    log "Toolchain already installed: $("$ET_PREFIX/bin/riscv64-unknown-elf-gcc" --version | head -1)"
    return
  fi
  log "Building ET RISC-V GNU toolchain (rv64imfc / lp64f) -> $ET_PREFIX"
  mkdir -p "$SRC_DIR"
  if [[ ! -d "$SRC_DIR/riscv-gnu-toolchain" ]]; then
    git clone https://github.com/aifoundry-org/riscv-gnu-toolchain "$SRC_DIR/riscv-gnu-toolchain"
  fi
  cd "$SRC_DIR/riscv-gnu-toolchain"
  if [[ ! -f Makefile ]]; then
    ./configure --prefix="$ET_PREFIX" --with-arch=rv64imfc --with-abi=lp64f \
                --with-languages=c,c++ --with-cmodel=medany
  fi
  make -j"$JOBS"   # resumable: riscv-gnu-toolchain keeps per-stage stamps
  touch "$done_marker"
  log "Toolchain done: $("$ET_PREFIX/bin/riscv64-unknown-elf-gcc" --version | head -1)"
}

# Local fixes to et-platform that are not upstream (yet); see patches/README.md.
apply_patches() {
  local src="$REPO_ROOT/external/et-platform" p
  for p in "$REPO_ROOT"/patches/et-platform-*.patch; do
    [[ -e "$p" ]] || continue
    if git -C "$src" apply --reverse --check "$p" 2>/dev/null; then
      continue  # already applied
    fi
    log "Applying $(basename "$p")"
    git -C "$src" apply "$p"
  done
}

build_platform() {
  local src="$REPO_ROOT/external/et-platform"
  local bld="$BUILD_DIR/et-platform"
  apply_patches
  log "Building et-platform from $src (build dir $bld) -> $ET_PREFIX"
  mkdir -p "$bld"
  cd "$bld"
  if [[ ! -f CMakeCache.txt ]]; then
    cmake -DTOOLCHAIN_DIR="$ET_PREFIX" -DCMAKE_INSTALL_PREFIX="$ET_PREFIX" "$src"
  fi
  make -j"$JOBS"
  log "et-platform build done"
}

case "$STAGE" in
  deps)      install_deps ;;
  toolchain) build_toolchain ;;
  platform)  build_platform ;;
  all)       install_deps; build_toolchain; build_platform ;;
  *) echo "usage: $0 [deps|toolchain|platform|all]" >&2; exit 2 ;;
esac
