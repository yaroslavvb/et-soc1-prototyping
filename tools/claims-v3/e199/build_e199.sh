#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE BUILD ON THE BOX, step 6's job body (rb/s08_a1_build_e199.sh
# runs it from E199's root R on aifoundry1, under `timeout -k 15 900`). E192's build (tools/claims-v3/e192/build_e192.sh, unchanged beside
# it) from E192's registered source as synced into E199's root, with E199.md sections 11 and 13's two additions. No device is opened: the
# host runs only with --list, which returns before any device code (proposal/src/host/main.cpp lines 473-482: the table is printed and
# main returns before checkOneCard and the device session); ET_DEVICES=1 is exported all the same.
#   1. cmake with the box's /opt/et into R/build/intbits (a former build of another day is moved aside first, never removed), nice 10, -j4;
#   2. the proposal's check_elf.py on the kernel: "loops 16, bad 0"; and E199's addition, E192's desk/loop_order_e192.py (reg-e192's own
#      check, unchanged) on the kernel's disassembly: "loops 16; forms x ops found 16 of 16; ...; bad 0" (exit 0);
#   3. the host's `--list --json` and `--list` byte for byte E192's registered desk/arm-table-e192.jsonl and .txt;
#   4. THE SELECTION (E199's addition, E191's kit's etdevices check made here): the built host carries ET_DEVICES (its own code does not:
#      main.cpp spells the name reversed, so the string is the linked device layer's), /opt/et/lib/libdeviceLayer.a carries it, and the
#      build took its device layer from /opt/et (CMakeCache.txt deviceLayer_DIR) - else the host would open every card on aifoundry1;
#   5. the hashes recorded: the kernel ELF, its .text (objcopy -O binary --only-section=.text), the host, beside E192's registration desk
#      build (aifoundry2: ELF a987904b..., .text aafdba4b...) and E192's card-day build (aifoundry3, 14 Nov: ELF 2635bcd3..., .text
#      aafdba4b...): reported, never judged (E199.md section 13: the loop checks are the gate; card 1's kernel is the box's).
# Writes R/build/intbits/BUILD-E199.txt and prints INTBITS-BUILT rc=0 ... or INTBITS-BUILD-FAILED rc=<n>: <why> (exit 0 or 16). The desk
# alone (aifoundry2, whose /opt/et carries no ET_DEVICES: E191's real-build log) may set RB_DESKTEST=1 E199_SELECTION_REPORT_ONLY=1, which
# reports item 4 instead of failing on it (the card day never sets either; the session's own check reads the binaries again).
#   bash tools/claims-v3/e199/build_e199.sh           (from E199's root on the box, or a stand-in root at the desk)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
export ET_DEVICES=1
SRC=tools/claims-v3/e192/proposal/src
D=tools/claims-v3/e192/desk
B=build/intbits
OBJ=/opt/et/bin/riscv64-unknown-elf-objcopy
OBJD=/opt/et/bin/riscv64-unknown-elf-objdump
DL=/opt/et/lib/libdeviceLayer.a
fail() { echo "INTBITS-BUILD-FAILED rc=$1: $2"; exit 16; }
echo "COMPILER $(g++ --version 2>/dev/null | head -n 1); $(cmake --version 2>/dev/null | head -n 1); $(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)"
echo "PYTHON $(command -v python3) $(python3 -V 2>&1)"
mkdir -p build || fail 2 "could not make build/ in E199's root"
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
"$OBJD" -d "$B/kernel/intbits.elf" > "$B/intbits.dis.txt" 2> "$B/objdump.err" || fail 4 "objdump -d of the kernel"
python3 -I -B "$D/loop_order_e192.py" "$B/intbits.dis.txt" > "$B/loop_order.txt" 2>&1; rc=$?
tail -n 1 "$B/loop_order.txt"
[ "$rc" -eq 0 ] && tail -n 1 "$B/loop_order.txt" | grep -q '^loops 16; forms x ops found 16 of 16; missing none; duplicated none; unexpected none; bad 0$' ||
  fail 4 "loop_order_e192.py: $(tail -n 1 "$B/loop_order.txt")"
"$B/host/intbits_host" --list --json > "$B/arm-table.jsonl" 2> "$B/list.err" < /dev/null || fail 5 "the host's --list --json exited non-zero"
"$B/host/intbits_host" --list > "$B/arm-table.txt" 2>> "$B/list.err" < /dev/null || fail 5 "the host's --list exited non-zero"
cmp -s "$B/arm-table.jsonl" "$D/arm-table-e192.jsonl" || fail 6 "the host's --list --json differs from E192's registered arm table"
cmp -s "$B/arm-table.txt" "$D/arm-table-e192.txt" || fail 6 "the host's --list differs from E192's registered arm table"
sel=()
grep -aqw ET_DEVICES "$B/host/intbits_host" || sel+=("the host carries no ET_DEVICES")
[ -f "$DL" ] && grep -aqw ET_DEVICES "$DL" || sel+=("$DL carries no ET_DEVICES")
grep -q '^deviceLayer_DIR:PATH=/opt/et/' "$B/CMakeCache.txt" 2>/dev/null || sel+=("the build did not take its device layer from /opt/et (CMakeCache.txt)")
SELJ="ET_DEVICES in the host and in $DL; the device layer from /opt/et"
if [ "${#sel[@]}" -gt 0 ]; then
  if [ "${RB_DESKTEST:-}" = 1 ] && [ "${E199_SELECTION_REPORT_ONLY:-}" = 1 ]; then   # the desk only: aifoundry2's /opt/et has no ET_DEVICES
    SELJ="NOT JUDGED (the desk test's E199_SELECTION_REPORT_ONLY under RB_DESKTEST=1, never set on the card day): $(IFS=';'; echo "${sel[*]}")"
    echo "SELECTION NOT JUDGED (desk test): $(IFS=';'; echo "${sel[*]}")"
  else
    fail 8 "the selection: $(IFS=';'; echo "${sel[*]}")"
  fi
fi
"$OBJ" -O binary --only-section=.text "$B/kernel/intbits.elf" "$B/intbits.text.bin" || fail 7 "objcopy of the kernel's .text"
ke=$(sha256sum "$B/kernel/intbits.elf" | cut -d' ' -f1); kt=$(sha256sum "$B/intbits.text.bin" | cut -d' ' -f1)
hh=$(sha256sum "$B/host/intbits_host" | cut -d' ' -f1)
{
  echo "built $(TZ=America/Los_Angeles date '+%F %T %Z') on $(hostname)"
  echo "kernel_elf_sha256 $ke"
  echo "kernel_text_sha256 $kt"
  echo "host_sha256 $hh"
  echo "e192_registration_desk_build (aifoundry2, E192.md section 16 item 5) kernel_elf a987904b6cd322bff51e5913e3fe2af709f24e1d2dabf82c4138b552c0b4d6ea text aafdba4b7bce846c7ef18c41f3dbf2c776581179c20f39634bc168c23ca1e42f"
  echo "e192_card_day_build (aifoundry3, 14 Nov 2026, a6e17e83) kernel_elf 2635bcd3b3fe4f09a19555e974017c8cd753e881035336c2b5e7ff2c279a6568 text aafdba4b7bce846c7ef18c41f3dbf2c776581179c20f39634bc168c23ca1e42f"
  echo "same_as_e192_desk_build elf $([ "$ke" = a987904b6cd322bff51e5913e3fe2af709f24e1d2dabf82c4138b552c0b4d6ea ] && echo yes || echo no) text $([ "$kt" = aafdba4b7bce846c7ef18c41f3dbf2c776581179c20f39634bc168c23ca1e42f ] && echo yes || echo no) (reported, never judged)"
  echo "same_as_e192_card_day_build elf $([ "$ke" = 2635bcd3b3fe4f09a19555e974017c8cd753e881035336c2b5e7ff2c279a6568 ] && echo yes || echo no) text $([ "$kt" = aafdba4b7bce846c7ef18c41f3dbf2c776581179c20f39634bc168c23ca1e42f ] && echo yes || echo no) (reported, never judged)"
  echo "check_elf $(tail -n 1 "$B/check_elf.txt")"
  echo "loop_order $(tail -n 1 "$B/loop_order.txt")"
  echo "arm_table byte-equal to E192's desk/arm-table-e192.jsonl and .txt"
  echo "selection $SELJ"
} > "$B/BUILD-E199.txt"
cat "$B/BUILD-E199.txt"
echo "INTBITS-BUILT rc=0 kernel ${ke:0:12} text ${kt:0:12} host ${hh:0:12}"
