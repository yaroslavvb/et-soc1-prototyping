#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): THE BUILD ON THE BOX, step 6's job body (rb/s08_a3_build_e192.sh
# runs it from E192's root R on aifoundry3, under `timeout -k 15 900`). No device is opened: the host runs only with --list.
#   1. cmake with the box's /opt/et into R/build/intbits (a former build of another day is moved aside first, never removed), nice 10,
#      -j4 (BUILD.md's lines);
#   2. the proposal's check_elf.py on the kernel: "loops 16, bad 0" (16 timed loops, 259 instructions, 4-byte encodings, 64-byte heads);
#   3. the host's `--list --json` and `--list` byte for byte the registration's desk/arm-table-e192.jsonl and .txt (E192.md section 16
#      item 6: 224 of 224 cells against request.md's table);
#   4. the hashes recorded: the kernel ELF, its .text (objcopy -O binary --only-section=.text), the host, beside E192.md section 16's
#      (a987904b..., aafdba4b..., built on aifoundry2: a different file is reported, never judged: E192's kernel is the box's).
# Writes R/build/intbits/BUILD-E192.txt and prints INTBITS-BUILT rc=0 ... or INTBITS-BUILD-FAILED rc=<n>: <why> (exit 0 or 16).
#   bash tools/claims-v3/e192/build_e192.sh           (from E192's root on the box, or the stand-in box of the runbook desk test)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
SRC=tools/claims-v3/e192/proposal/src
D=tools/claims-v3/e192/desk
B=build/intbits
OBJ=/opt/et/bin/riscv64-unknown-elf-objcopy
fail() { echo "INTBITS-BUILD-FAILED rc=$1: $2"; exit 16; }
echo "COMPILER $(g++ --version 2>/dev/null | head -n 1); $(cmake --version 2>/dev/null | head -n 1); $(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)"
echo "PYTHON $(command -v python3) $(python3 -V 2>&1)"
mkdir -p build || fail 2 "could not make build/ in E192's root"
if [ -e "$B" ]; then mv "$B" "$B.before-$(date +%Y%m%dT%H%M%S)" || fail 2 "could not move the earlier build aside"; fi
nice -n 10 cmake -S "$SRC" -B "$B" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > "$B.cmake.log" 2>&1; rc=$?
tail -n 3 "$B.cmake.log"
[ "$rc" -eq 0 ] || fail "$rc" "cmake configure (the last lines above)"
mv "$B.cmake.log" "$B/cmake-configure.log"
nice -n 10 cmake --build "$B" -j4 > "$B/cmake-build.log" 2>&1; rc=$?
tail -n 3 "$B/cmake-build.log"
[ "$rc" -eq 0 ] || fail "$rc" "cmake --build (the last lines above)"
[ -s "$B/kernel/intbits.elf" ] && [ -x "$B/host/intbits_host" ] || fail 3 "no kernel ELF or no host after the build"
python3 -I -B "$SRC/check_elf.py" "$B/kernel/intbits.elf" > "$B/check_elf.txt" 2>&1; rc=$?
tail -n 1 "$B/check_elf.txt"
[ "$rc" -eq 0 ] && grep -qx 'loops 16, bad 0' "$B/check_elf.txt" || fail 4 "check_elf.py: $(tail -n 1 "$B/check_elf.txt")"
"$B/host/intbits_host" --list --json > "$B/arm-table.jsonl" 2> "$B/list.err" < /dev/null || fail 5 "the host's --list --json exited non-zero"
"$B/host/intbits_host" --list > "$B/arm-table.txt" 2>> "$B/list.err" < /dev/null || fail 5 "the host's --list exited non-zero"
cmp -s "$B/arm-table.jsonl" "$D/arm-table-e192.jsonl" || fail 6 "the host's --list --json differs from the registration's arm table"
cmp -s "$B/arm-table.txt" "$D/arm-table-e192.txt" || fail 6 "the host's --list differs from the registration's arm table"
"$OBJ" -O binary --only-section=.text "$B/kernel/intbits.elf" "$B/intbits.text.bin" || fail 7 "objcopy of the kernel's .text"
ke=$(sha256sum "$B/kernel/intbits.elf" | cut -d' ' -f1); kt=$(sha256sum "$B/intbits.text.bin" | cut -d' ' -f1)
hh=$(sha256sum "$B/host/intbits_host" | cut -d' ' -f1)
{
  echo "built $(TZ=America/Los_Angeles date '+%F %T %Z') on $(hostname)"
  echo "kernel_elf_sha256 $ke"
  echo "kernel_text_sha256 $kt"
  echo "host_sha256 $hh"
  echo "registration_desk_build (aifoundry2, E192.md section 16 item 5) kernel_elf a987904b6cd322bff51e5913e3fe2af709f24e1d2dabf82c4138b552c0b4d6ea text aafdba4b7bce846c7ef18c41f3dbf2c776581179c20f39634bc168c23ca1e42f"
  echo "same_as_registration_desk_build elf $([ "$ke" = a987904b6cd322bff51e5913e3fe2af709f24e1d2dabf82c4138b552c0b4d6ea ] && echo yes || echo no) text $([ "$kt" = aafdba4b7bce846c7ef18c41f3dbf2c776581179c20f39634bc168c23ca1e42f ] && echo yes || echo no) (reported, never judged)"
  echo "check_elf $(tail -n 1 "$B/check_elf.txt")"
  echo "arm_table byte-equal to desk/arm-table-e192.jsonl and .txt"
} > "$B/BUILD-E192.txt"
cat "$B/BUILD-E192.txt"
echo "INTBITS-BUILT rc=0 kernel ${ke:0:12} text ${kt:0:12} host ${hh:0:12}"
