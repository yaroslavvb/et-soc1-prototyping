#!/usr/bin/env bash
# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the box build, the body of step 6's detached job a3-build-e189 on aifoundry3
# (run from the tree's root, ~/aifoundry; no device opened). It builds the two programs E189 runs into E189's own directories against the
# installed ET tree, as their READMEs and Q166's BUILD-INFO do:
#   workloads/ledger      -> build/e189ledger   (cmake -S workloads/ledger -B build/e189ledger -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev)
#   workloads/sparseparity -> build/e189spp     (the same recipe: its host, spp_selftest and the kernel)
# and then reads each, never by grepping its bytes:
#   - the kernel by its file's sha256 and its .text's (`objcopy -O binary -j .text`, BUILD-INFO's recipe) against the pins in
#     hostcheck-e189.json (ledger ELF 78708041... .text 5e00e45a...; sparse parity ELF 65dd07da... .text 3e14be32..., the 29 Sep card file);
#   - the host by its BEHAVIOUR (hostcheck_e189.py: the ledger's self-test, its --dry lines for E189's five configurations and its
#     refusals; sparse parity's --dry line for E189's instance, its refusal and its CPU self-test), every run before any device can open.
# Each program's verdict line: LEDGER-BUILT rc=0 or LEDGER-BUILD-FAILED: <why>; SPP-BUILT rc=0 or SPP-BUILD-FAILED: <why> (a program that
# fails is SKIPPED that day: no data, never a failed prediction, E189.md section 12). The compilers' version lines are printed (the box's
# GCC is the box's). It ends with E189-BUILD rc=0 when at least one program built, else rc=1. Each program's cmake configure and build is
# bounded (`timeout -k 15 220` each), and the whole job by step 6's bound. Desk test only: RB_DESKTEST=1 lets E189_PREFIX, E189_CMAKE,
# E189_OBJCOPY and E189_KERNEL_PINS (stand-in kernels' pins) stand in (the runbook's desk test); the card day never sets them.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
PREFIX=/opt/et; CMAKE=cmake; OBJCOPY=/opt/et/bin/riscv64-unknown-elf-objcopy
if [ "${RB_DESKTEST:-}" = 1 ]; then
  PREFIX=${E189_PREFIX:-$PREFIX}; CMAKE=${E189_CMAKE:-$CMAKE}; OBJCOPY=${E189_OBJCOPY:-$OBJCOPY}
elif [ -n "${E189_PREFIX:-}${E189_CMAKE:-}${E189_OBJCOPY:-}${E189_KERNEL_PINS:-}" ]; then
  echo "REFUSED: E189_PREFIX, E189_CMAKE, E189_OBJCOPY and E189_KERNEL_PINS are desk-test stand-ins, read only with RB_DESKTEST=1"; exit 3
fi
[ -x "$OBJCOPY" ] || OBJCOPY=$(command -v objcopy || echo objcopy)
J=tools/claims-v3/e189/hostcheck-e189.json
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E189_KERNEL_PINS:-}" ] && J=$E189_KERNEL_PINS     # the desk test's stand-in kernels' pins only
pin() { python3 -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["kernels"][sys.argv[2]][sys.argv[3]])' "$J" "$1" "$2"; }
echo "COMPILER host: $(c++ --version 2>/dev/null | head -n 1)"
echo "COMPILER riscv: $("$PREFIX"/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)"
echo "COMPILER cmake: $("$CMAKE" --version 2>/dev/null | head -n 1)"
python3 -B tools/claims-v3/e189/check_e189.py --box || { echo "LEDGER-BUILD-FAILED: the synced files differ from harness-e189.json"; echo "SPP-BUILD-FAILED: the synced files differ from harness-e189.json"; echo "E189-BUILD rc=1"; exit 1; }
nbuilt=0
build_one() {  # build_one <tag LEDGER|SPP> <source dir> <build dir> <kernel elf> <host> <pin key> [<selftest bin>]
  local tag=$1 src=$2 b=$3 elf=$4 host=$5 key=$6 st=${7:-} why=""
  case "$b" in build/e189ledger|build/e189spp) ;; *) echo "$tag-BUILD-FAILED: not E189's build directory: $b"; return 1 ;; esac
  rm -rf "./$b"
  mkdir -p "$b"
  if ! timeout -k 15 220 "$CMAKE" -S "$src" -B "$b" -DCMAKE_PREFIX_PATH="$PREFIX" -Wno-dev > "$b/configure.log" 2>&1; then
    why="cmake configure failed (its log: $b/configure.log)"
  elif ! timeout -k 15 220 nice -n 10 "$CMAKE" --build "$b" -j4 > "$b/build.log" 2>&1; then
    why="cmake build failed (its log: $b/build.log)"
  elif [ ! -s "$elf" ] || [ ! -x "$host" ]; then
    why="no kernel or no host after the build"
  else
    local e t
    e=$(sha256sum "$elf" | cut -c1-64)
    t=$("$OBJCOPY" -O binary -j .text "$elf" /dev/stdout 2>/dev/null | sha256sum | cut -c1-64)
    echo "$tag kernel: ELF sha256 $e, .text sha256 $t"
    [ "$e" = "$(pin "$key" elf_sha256)" ] || why="the kernel's ELF sha256 $e is not the pinned $(pin "$key" elf_sha256)"
    [ -z "$why" ] && { [ "$t" = "$(pin "$key" text_sha256)" ] || why="the kernel's .text sha256 $t is not the pinned $(pin "$key" text_sha256)"; }
    if [ -z "$why" ]; then
      local k; [ "$tag" = LEDGER ] && k=ledger || k=spp
      local args=("$k" "$host"); [ -n "$st" ] && args+=(--selftest-bin "$st")
      out=$(python3 -B tools/claims-v3/e189/hostcheck_e189.py "${args[@]}" 2>&1)
      echo "$tag host: $out"
      case "$out" in "HOST-BEHAVIOUR OK"*) ;; *) why="the host's behaviour: $out" ;; esac
    fi
  fi
  if [ -z "$why" ]; then
    { echo "host $(sha256sum "$host" | cut -c1-64)"; echo "kernel $(sha256sum "$elf" | cut -c1-64)"; } > "$b/SHA256"
    echo "$tag-BUILT rc=0"; nbuilt=$((nbuilt + 1)); return 0
  fi
  echo "$tag-BUILD-FAILED: $why"; return 1
}
build_one LEDGER workloads/ledger build/e189ledger build/e189ledger/kernel/ledger.elf build/e189ledger/host/ledger_host ledger
build_one SPP workloads/sparseparity build/e189spp build/e189spp/kernel/sparseparity.elf build/e189spp/host/sparseparity_host spp \
  build/e189spp/host/spp_selftest
if [ "$nbuilt" -gt 0 ]; then echo "E189-BUILD rc=0 ($nbuilt of 2 programs built)"; exit 0; fi
echo "E189-BUILD rc=1 (no program built)"; exit 1
