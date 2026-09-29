#!/usr/bin/env bash
# PCIE2: the freeze before validation (the owner's method). In the checkout, after development and before any
# validation pass: runs the reduction's self-test; builds the two kernels (touch.elf, empty.elf) from this tree into
# build/pcie2-freeze-kernel (a directory no block uses; nice -n 19, -j2; or takes them from --elf-dir) and writes the
# sha256 of their .text to TEXT.sha256 (the three hosts' toolchains give identical code: AGENT.md section 6); then
# writes LOCK.sha256 over this experiment's code, the probe's sources, the schedules and TEXT.sha256, and
# PREREG.sha256; prints PREREG.md's sha256 for README.md. block.sh then refuses validation passes (1-99) unless
# LOCK.sha256 verifies, the probe was built from the locked sources (the hash compiled into it) and the kernels
# compiled into it have the frozen .text; and refuses any pass if LOCK.sha256 exists and does not verify.
# tools/claims-v3/lib.sh and queue.sh are not in the lock (the DV2 lock pins them in this checkout; the lab trees keep
# their own copies): every pass records their sha256 in code.sha256, and deploy.sh reports whether a host's differ.
#   bash tools/claims-v3/pcie2/freeze.sh [--elf-dir <dir with touch.elf and empty.elf>]
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=tools/claims-v3/pcie2
ELF_DIR=
case "${1:-}" in
  --elf-dir) ELF_DIR=${2:?--elf-dir needs a directory} ;;
  '') ;;
  *) echo "freeze.sh: usage: freeze.sh [--elf-dir <dir>]" >&2; exit 2 ;;
esac
[ -e "$D/LOCK.sha256" ] && { echo "freeze.sh: $D/LOCK.sha256 exists already (an amendment replaces it deliberately)" >&2; exit 2; }
[ -f "$D/PREREG.md" ] || { echo "freeze.sh: no $D/PREREG.md" >&2; exit 2; }
python3 "$D/reduce.py" --self-test > /dev/null || { echo "freeze.sh: reduce.py --self-test fails: not freezing" >&2; exit 1; }
OC=/opt/et/bin/riscv64-unknown-elf-objcopy
[ -x "$OC" ] || { echo "freeze.sh: no $OC: cannot hash the kernels' .text" >&2; exit 2; }
if [ -z "$ELF_DIR" ]; then
  ELF_DIR=build/pcie2-freeze-kernel
  rm -rf "$ELF_DIR"
  nice -n 19 cmake -S workloads/pciebench/kernel -B "$ELF_DIR" -Wno-dev \
    -DCMAKE_TOOLCHAIN_FILE=/opt/et/lib/cmake/riscv64-ec-toolchain.cmake -DCMAKE_PREFIX_PATH=/opt/et \
    -DCMAKE_MODULE_PATH=/opt/et/lib/cmake/cmake-modules -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib \
    > "$ELF_DIR.log" 2>&1 && nice -n 19 cmake --build "$ELF_DIR" -j2 >> "$ELF_DIR.log" 2>&1 ||
    { tail -20 "$ELF_DIR.log" >&2; echo "freeze.sh: the kernel build failed: not freezing" >&2; exit 1; }
fi
: > "$D/TEXT.sha256.tmp"
for k in touch empty; do
  [ -f "$ELF_DIR/$k.elf" ] || { echo "freeze.sh: no $ELF_DIR/$k.elf" >&2; rm -f "$D/TEXT.sha256.tmp"; exit 1; }
  echo "$("$OC" -O binary -j .text "$ELF_DIR/$k.elf" /dev/stdout | sha256sum | cut -c1-64)  $k.elf" >> "$D/TEXT.sha256.tmp"
done
mv "$D/TEXT.sha256.tmp" "$D/TEXT.sha256"
FILES=("$D/block.sh" "$D/pcie2lib.py" "$D/reduce.py" "$D/run_passes.sh" "$D/PREREG.md" "$D/TEXT.sha256"
       "$D"/schedule-*.txt
       workloads/pciebench/CMakeLists.txt workloads/pciebench/host/CMakeLists.txt workloads/pciebench/host/Constants.h.in
       workloads/pciebench/host/main.cpp workloads/pciebench/kernel/CMakeLists.txt workloads/pciebench/kernel/touch.c
       workloads/pciebench/kernel/empty.c workloads/pciebench/kernel/crt.S workloads/pciebench/kernel/sections.ld
       workloads/pciebench/touch_args.h)
sha256sum "${FILES[@]}" > "$D/LOCK.sha256"
sha256sum "$D/PREREG.md" > "$D/PREREG.sha256"
echo "frozen $(date +%FT%T%z): $(wc -l < "$D/LOCK.sha256") files; PREREG.md sha256 $(cut -c1-64 "$D/PREREG.sha256")"
echo "kernels' .text (TEXT.sha256, from $ELF_DIR):"; cat "$D/TEXT.sha256"
