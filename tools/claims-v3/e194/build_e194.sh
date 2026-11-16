#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the box build, the body of step 6's
# detached job a2-build-e194 on aifoundry2 (run from the box tree's root, ~/claude/et-soc1-prototyping; no device opened). E191's build
# (tools/claims-v3/e191/build_e191.sh, eb1ac923, unchanged beside it; E189's build with THE KERNEL GATE) into E194's own directories:
#   workloads/ledger       -> build/e194ledger  (cmake -S workloads/ledger -B build/e194ledger -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev)
#   workloads/sparseparity -> build/e194spp     (the same recipe: its host, spp_selftest and the kernel)
# and then reads each, as E191's build does:
#   - the kernel through THE KERNEL GATE (check_e194.py --kernel, E191's gate and pins unchanged: its .text sha256 always the registered
#     one (E189.md 4, hostcheck-e189.json's text_sha256), and its whole ELF E189's pin or the "() 15.1.0" toolchain's (built on aifoundry2,
#     this box, Sat 14 Nov 2026) or else its loadable identity, second form, the pinned one: what the card's loader reads);
#   - the host by its BEHAVIOUR (E189's hostcheck_e189.py, unchanged, by path: the ledger's self-test, its --dry lines for the five
#     ledger configurations with their K, which E194's plan holds the same as E189's, and its refusals; sparse parity's --dry line, its
#     refusal and its CPU self-test), every run before any device can open, with ET_DEVICES and V3_DEVICE UNSET, as the session runs;
#   - THE ET_DEVICES READING (etdevices_e194.sh) is RECORDED, never a gate: aifoundry2 has one card and its device layer carries no
#     ET_DEVICES (E190 arm A's build v2 recorded the same reading here and passed it).
# Each program's verdict line: LEDGER-BUILT rc=0 or LEDGER-BUILD-FAILED: <why>; SPP-BUILT rc=0 or SPP-BUILD-FAILED: <why> (a program that
# fails is SKIPPED that day: no data, never a failed prediction, E194.md 12), and its record <build dir>/BUILD-e194.json (builder
# build_e194.sh, the box, verdict, the Pacific day, the host's and the kernel's sha256, the kernel gate's line, the ET_DEVICES reading: the
# runner's box check reads it). It ends with E194-BUILD rc=0 when at least one program built, else rc=1. Each cmake configure and build is
# bounded (`timeout -k 15 220`), nice 10, at most -j4.
# Desk test only: RB_DESKTEST=1 lets E194_PREFIX, E194_CMAKE, E194_OBJCOPY and E194_KERNEL_PINS stand in; the card day never sets them.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
unset ET_DEVICES V3_DEVICE
PREFIX=/opt/et; CMAKE=cmake; OBJCOPY=/opt/et/bin/riscv64-unknown-elf-objcopy
if [ "${RB_DESKTEST:-}" = 1 ]; then
  PREFIX=${E194_PREFIX:-$PREFIX}; CMAKE=${E194_CMAKE:-$CMAKE}; OBJCOPY=${E194_OBJCOPY:-$OBJCOPY}
elif [ -n "${E194_PREFIX:-}${E194_CMAKE:-}${E194_OBJCOPY:-}${E194_KERNEL_PINS:-}" ]; then
  echo "REFUSED: E194_PREFIX, E194_CMAKE, E194_OBJCOPY and E194_KERNEL_PINS are desk-test stand-ins, read only with RB_DESKTEST=1"; exit 3
fi
[ -x "$OBJCOPY" ] || OBJCOPY=$(command -v objcopy || echo objcopy)
BOX=$(hostname 2>/dev/null | cut -d. -f1)
DAY=$(TZ=America/Los_Angeles date +%F)
echo "== E194 build on $BOX, $(TZ=America/Los_Angeles date '+%F %T %Z'), into build/e194ledger and build/e194spp"
echo "COMPILER host: $(c++ --version 2>/dev/null | head -n 1)"
echo "COMPILER riscv: $("$PREFIX"/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)"
echo "COMPILER cmake: $("$CMAKE" --version 2>/dev/null | head -n 1)"
python3 -B tools/claims-v3/e194/check_e194.py --box || { echo "LEDGER-BUILD-FAILED: the box tree's files differ from harness-e194.json"; echo "SPP-BUILD-FAILED: the box tree's files differ from harness-e194.json"; echo "E194-BUILD rc=1"; exit 1; }
nbuilt=0
record() {  # record <build dir> <verdict> <why> <host> <elf> <et_devices> <the kernel gate's line>
  python3 -B - "$1/BUILD-e194.json" "$BOX" "$DAY" "$2" "$3" "$4" "$5" "$6" "$7" <<'PY'
import hashlib, json, os, sys, time
p, box, day, verdict, why, host, elf, etd, kg = sys.argv[1:10]
def sha(f):
    return hashlib.sha256(open(f, "rb").read()).hexdigest() if os.path.isfile(f) else None
json.dump({"builder": "build_e194.sh", "box": box, "day": day, "epoch": int(time.time()), "verdict": verdict, "why": why,
           "host": host, "host_sha256": sha(host), "kernel": elf, "kernel_sha256": sha(elf), "kernel_gate": kg, "et_devices": etd,
           "what": "E194's build record (build_e194.sh): the runner's box check reads it"}, open(p, "w"), indent=1)
PY
}
build_one() {  # build_one <tag LEDGER|SPP> <source dir> <build dir> <kernel elf> <host> <pin key> [<selftest bin>]
  local tag=$1 src=$2 b=$3 elf=$4 host=$5 key=$6 st=${7:-} why="" etd="not read" kg="not read"
  case "$b" in build/e194ledger|build/e194spp) ;; *) echo "$tag-BUILD-FAILED: not E194's build directory: $b"; return 1 ;; esac
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
    kg=$(python3 -B tools/claims-v3/e194/check_e194.py --kernel "$key" "$elf" 2>&1 | tail -n 1)     # THE KERNEL GATE (E191's)
    echo "$tag $kg"
    case "$kg" in "KERNEL OK $key: "*) ;; *) why="the kernel gate: ${kg#KERNEL FAILED $key: }" ;; esac
    if [ -z "$why" ]; then
      local k; [ "$tag" = LEDGER ] && k=ledger || k=spp
      local args=("$k" "$host"); [ -n "$st" ] && args+=(--selftest-bin "$st")
      out=$(python3 -B tools/claims-v3/e189/hostcheck_e189.py "${args[@]}" 2>&1)
      echo "$tag host: $out"
      case "$out" in "HOST-BEHAVIOUR OK"*) ;; *) why="the host's behaviour: $out" ;; esac
    fi
    if [ -z "$why" ]; then
      r=$(bash tools/claims-v3/e194/etdevices_e194.sh "$host" "$b/CMakeCache.txt")
      echo "$tag ETDEVICES: $r"
      etd="not a gate on $BOX (E194 runs on aifoundry2's one card, ET_DEVICES unset): $r"
    fi
  fi
  if [ -z "$why" ]; then
    { echo "host $(sha256sum "$host" | cut -c1-64)"; echo "kernel $(sha256sum "$elf" | cut -c1-64)"; echo "et_devices $etd"; } > "$b/SHA256"
    record "$b" BUILT "" "$host" "$elf" "$etd" "$kg"
    echo "$tag-BUILT rc=0"; nbuilt=$((nbuilt + 1)); return 0
  fi
  record "$b" BUILD-FAILED "$why" "$host" "$elf" "$etd" "$kg"
  echo "$tag-BUILD-FAILED: $why"; return 1
}
build_one LEDGER workloads/ledger build/e194ledger build/e194ledger/kernel/ledger.elf build/e194ledger/host/ledger_host ledger
build_one SPP workloads/sparseparity build/e194spp build/e194spp/kernel/sparseparity.elf build/e194spp/host/sparseparity_host spp \
  build/e194spp/host/spp_selftest
if [ "$nbuilt" -gt 0 ]; then echo "E194-BUILD rc=0 ($nbuilt of 2 programs built)"; exit 0; fi
echo "E194-BUILD rc=1 (no program built)"; exit 1
