#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the box build, the body of step 6's
# detached job a1-build-e191 on aifoundry1 (run from the tree's root, ~/nekko; no device opened). E189's build (tools/claims-v3/e189/
# build_e189.sh, unchanged beside it) into E191's own directories, with E190's kit note 1's ET_DEVICES reading (build_e190_v2.sh):
#   workloads/ledger       -> build/e191ledger  (cmake -S workloads/ledger -B build/e191ledger -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev)
#   workloads/sparseparity -> build/e191spp     (the same recipe: its host, spp_selftest and the kernel)
# and then reads each, as E189's build does:
#   - the kernel through THE KERNEL GATE (check_e191.py --kernel; fix-e191k, the verifier's finding 1: E189's whole-ELF pins came from
#     aifoundry3's toolchain and refuse aifoundry1's, whose riscv gcc reads "() 15.1.0"): its .text sha256 always the registered one
#     (E189.md 4, hostcheck-e189.json's text_sha256, unchanged), and its whole ELF one of the pinned (E189's, or the "() 15.1.0"
#     toolchain's) or else its loadable identity the pinned one (what the card's loader reads: no loadable byte may differ);
#   - the host by its BEHAVIOUR (E189's hostcheck_e189.py, unchanged, by path: the ledger's self-test, its --dry lines for the five
#     ledger configurations with their K, which E191's plan holds the same as E189's, and its refusals; sparse parity's --dry line, its
#     refusal and its CPU self-test), every run before any device can open, here with ET_DEVICES=1 and V3_DEVICE=1 set all the same;
#   - THE ET_DEVICES READING (etdevices_e191.sh), a REFUSAL on aifoundry1 only (E190 arm B's build gate, which passed there for E136's
#     host on Fri 13 Nov 2026): the host binary and /opt/et/lib/libdeviceLayer.a carry the string ET_DEVICES and the build's
#     CMakeCache.txt took the device layer from /opt/et; else that program is not built (a host that ignored ET_DEVICES would open card 0,
#     whose PMIC alarm trips at 75 W). It is the one place this kit reads a string out of a binary, and it can only refuse: the host's
#     behaviour is still read by hostcheck_e189.py, and its card at run time by the identity gate and the watch (e191_ident.py).
# Each program's verdict line: LEDGER-BUILT rc=0 or LEDGER-BUILD-FAILED: <why>; SPP-BUILT rc=0 or SPP-BUILD-FAILED: <why> (a program that
# fails is SKIPPED that day: no data, never a failed prediction, E191.md 12), and its record <build dir>/BUILD-e191.json (builder
# build_e191.sh, verdict, the Pacific day, the host's and the kernel's sha256, the kernel gate's line, the ET_DEVICES reading: the
# runner's box check reads it).
# It ends with E191-BUILD rc=0 when at least one program built, else rc=1. Each cmake configure and build is bounded (`timeout -k 15 220`).
# Desk test only: RB_DESKTEST=1 lets E191_PREFIX, E191_CMAKE, E191_OBJCOPY and E191_KERNEL_PINS stand in; the card day never sets them.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
PREFIX=/opt/et; CMAKE=cmake; OBJCOPY=/opt/et/bin/riscv64-unknown-elf-objcopy
if [ "${RB_DESKTEST:-}" = 1 ]; then
  PREFIX=${E191_PREFIX:-$PREFIX}; CMAKE=${E191_CMAKE:-$CMAKE}; OBJCOPY=${E191_OBJCOPY:-$OBJCOPY}
elif [ -n "${E191_PREFIX:-}${E191_CMAKE:-}${E191_OBJCOPY:-}${E191_KERNEL_PINS:-}" ]; then
  echo "REFUSED: E191_PREFIX, E191_CMAKE, E191_OBJCOPY and E191_KERNEL_PINS are desk-test stand-ins, read only with RB_DESKTEST=1"; exit 3
fi
[ -x "$OBJCOPY" ] || OBJCOPY=$(command -v objcopy || echo objcopy)
BOX=$(hostname 2>/dev/null | cut -d. -f1)
DAY=$(TZ=America/Los_Angeles date +%F)
echo "== E191 build on $BOX, $(TZ=America/Los_Angeles date '+%F %T %Z'), into build/e191ledger and build/e191spp"
echo "COMPILER host: $(c++ --version 2>/dev/null | head -n 1)"
echo "COMPILER riscv: $("$PREFIX"/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)"
echo "COMPILER cmake: $("$CMAKE" --version 2>/dev/null | head -n 1)"
python3 -B tools/claims-v3/e191/check_e191.py --box || { echo "LEDGER-BUILD-FAILED: the synced files differ from harness-e191.json"; echo "SPP-BUILD-FAILED: the synced files differ from harness-e191.json"; echo "E191-BUILD rc=1"; exit 1; }
nbuilt=0
record() {  # record <build dir> <verdict> <why> <host> <elf> <et_devices> <the kernel gate's line>
  python3 -B - "$1/BUILD-e191.json" "$BOX" "$DAY" "$2" "$3" "$4" "$5" "$6" "$7" <<'PY'
import hashlib, json, os, sys, time
p, box, day, verdict, why, host, elf, etd, kg = sys.argv[1:10]
def sha(f):
    return hashlib.sha256(open(f, "rb").read()).hexdigest() if os.path.isfile(f) else None
json.dump({"builder": "build_e191.sh", "box": box, "day": day, "epoch": int(time.time()), "verdict": verdict, "why": why,
           "host": host, "host_sha256": sha(host), "kernel": elf, "kernel_sha256": sha(elf), "kernel_gate": kg, "et_devices": etd,
           "what": "E191's build record (build_e191.sh): the runner's box check reads it"}, open(p, "w"), indent=1)
PY
}
build_one() {  # build_one <tag LEDGER|SPP> <source dir> <build dir> <kernel elf> <host> <pin key> [<selftest bin>]
  local tag=$1 src=$2 b=$3 elf=$4 host=$5 key=$6 st=${7:-} why="" etd="not read" kg="not read"
  case "$b" in build/e191ledger|build/e191spp) ;; *) echo "$tag-BUILD-FAILED: not E191's build directory: $b"; return 1 ;; esac
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
    kg=$(python3 -B tools/claims-v3/e191/check_e191.py --kernel "$key" "$elf" 2>&1 | tail -n 1)     # THE KERNEL GATE (finding 1)
    echo "$tag $kg"
    case "$kg" in "KERNEL OK $key: "*) ;; *) why="the kernel gate: ${kg#KERNEL FAILED $key: }" ;; esac
    if [ -z "$why" ]; then
      local k; [ "$tag" = LEDGER ] && k=ledger || k=spp
      local args=("$k" "$host"); [ -n "$st" ] && args+=(--selftest-bin "$st")
      out=$(ET_DEVICES=1 V3_DEVICE=1 python3 -B tools/claims-v3/e189/hostcheck_e189.py "${args[@]}" 2>&1)
      echo "$tag host: $out"
      case "$out" in "HOST-BEHAVIOUR OK"*) ;; *) why="the host's behaviour: $out" ;; esac
    fi
    if [ -z "$why" ]; then
      r=$(bash tools/claims-v3/e191/etdevices_e191.sh "$host" "$b/CMakeCache.txt")
      echo "$tag ETDEVICES: $r"
      if [ "$BOX" = aifoundry1 ]; then
        case "$r" in "yes:"*) etd=yes ;; *) why="ET_DEVICES: $r (a host that ignored ET_DEVICES would open card 0)" ;; esac
      else
        etd="not a gate on $BOX (E191 runs on aifoundry1): $r"
      fi
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
build_one LEDGER workloads/ledger build/e191ledger build/e191ledger/kernel/ledger.elf build/e191ledger/host/ledger_host ledger
build_one SPP workloads/sparseparity build/e191spp build/e191spp/kernel/sparseparity.elf build/e191spp/host/sparseparity_host spp \
  build/e191spp/host/spp_selftest
if [ "$nbuilt" -gt 0 ]; then echo "E191-BUILD rc=0 ($nbuilt of 2 programs built)"; exit 0; fi
echo "E191-BUILD rc=1 (no program built)"; exit 1
