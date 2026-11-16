#!/usr/bin/env bash
# E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): THE BUILD ON THE BOX, step 6's job body
# (rb/s08_a3_build_e195.sh runs it from E195's root R = <tree>/build/claims-v3/aifoundry3/e195 on aifoundry3, under `timeout -k 15 900`).
# NO DEVICE IS OPENED: the host runs only with --list and --dump-image (both before any device code: host/main.cpp), the heater only its
# option parser, which stops at an unknown option before anything (E192's box check on this box's heater, Sat 14 Nov 2026).
#   1. cmake with the box's /opt/et from the registered source (tools/claims-v3/e195/proposal/src) into R/build/x09mem (an earlier build
#      is moved aside first, never removed), nice 10, -j4 (BUILD.md's lines);
#   2. the proposal's check_elf.py on the kernel: "CHECK OK: five timed loops as designed" (a gate);
#   3. the registration's desk/loops_e195.py: the five loops' heads mod 32 and the store / no-store pair (reported: E195.md 15, E61's trap;
#      C2 reads it in the data);
#   4. the kernel ELF, its .text and its disassembly (lib_x09.sh's form) by sha256, beside the registration's desk build (7c5faea8...,
#      007a355d..., b59a6caf...): SAME or DIFFERENT, reported, never a gate (E195.md 15: the box's compiler differs; E195's kernel is the
#      one built here);
#   5. the host's --list --json and --list byte for byte the registration's desk/arm-table-e195.json and .txt (a gate: E195.md 17 item 6
#      checked them cell by cell against request.md's table);
#   6. make_x09.py --check --no-ms from THIS host's bytes, with the tree's numpy (<tree>/.venv, lib.sh's), into R/build/x09-gen-check:
#      "CHECK OK: 31 arms" and its manifest.json and counts.json byte for byte the kit's gen-e195-noms/ (a gate; the session runs from
#      gen-e195-noms/); without numpy on the box it is NOT RUN (reported) and step 5 stands alone;
#   7. THE BOX'S TWO TOOLS in E195's root, as the block library needs them there (lib.sh: build/ettelem/ettelem behind E128's guard;
#      build/sparsity/host/sparsity_host, the anchor and the heater): symlinks to the box tree's own builds, which every aifoundry3 kit
#      uses (E132, E139, E188, E192, E193), made if absent, else they must point there; each read by sha256 and the heater's option parser
#      by behaviour (the registered heater arguments and --stop-file, then an unknown option: exit 2 at it);
#   8. the record R/build/x09mem-built.txt (X09MEM-BUILT, host, kernel, ettelem, sparsity_host lines: the session checks every one).
# Prints X09MEM-BUILT rc=0 ... or X09MEM-BUILD-FAILED rc=<n>: <why> (exit 0 or 16).
#   bash tools/claims-v3/e195/build_e195.sh           (from E195's root on the box, or the stand-in box of the runbook desk test)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
R=$(pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
SRC=tools/claims-v3/e195/proposal/src
D=tools/claims-v3/e195/desk
B=build/x09mem
REC=build/x09mem-built.txt
OBJ=/opt/et/bin/riscv64-unknown-elf-objcopy
OD=/opt/et/riscv64-unknown-elf/bin/objdump; [ -x "$OD" ] || OD=/opt/et/bin/riscv64-unknown-elf-objdump
export LD_LIBRARY_PATH=/opt/et/lib
fail() { echo "X09MEM-BUILD-FAILED rc=$1: $2"; exit 16; }
echo "COMPILER $(g++ --version 2>/dev/null | head -n 1); $(cmake --version 2>/dev/null | head -n 1); $(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)"
echo "PYTHON $(command -v python3) $(python3 -V 2>&1)"
mkdir -p build || fail 2 "could not make build/ in E195's root"
[ -e "$REC.new" ] && mv "$REC.new" "$REC.new.before-$(date +%Y%m%dT%H%M%S)"
if [ -e "$B" ]; then mv "$B" "$B.before-$(date +%Y%m%dT%H%M%S)" || fail 2 "could not move the earlier build aside"; fi
if [ -e "$REC" ]; then mv "$REC" "$REC.before-$(date +%Y%m%dT%H%M%S)" || fail 2 "could not move the earlier record aside"; fi
nice -n 10 cmake -S "$SRC" -B "$B" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/x09mem.cmake.log 2>&1; rc=$?
tail -n 3 build/x09mem.cmake.log
[ "$rc" -eq 0 ] || fail "$rc" "cmake configure (the last lines above)"
mv build/x09mem.cmake.log "$B/cmake-configure.log"
nice -n 10 cmake --build "$B" -j4 > "$B/cmake-build.log" 2>&1; rc=$?
tail -n 3 "$B/cmake-build.log"
[ "$rc" -eq 0 ] || fail "$rc" "cmake --build (the last lines above)"
H=$B/host/x09mem_host; K=$B/kernel/x09mem.elf
[ -s "$K" ] && [ -x "$H" ] || fail 3 "no kernel ELF or no host after the build"
python3 -I -B "$SRC/check_elf.py" "$K" > "$B/check_elf.txt" 2>&1; rc=$?
tail -n 1 "$B/check_elf.txt"
[ "$rc" -eq 0 ] && grep -q '^CHECK OK: five timed loops as designed' "$B/check_elf.txt" || fail 4 "check_elf.py: $(tail -n 1 "$B/check_elf.txt")"
python3 -I -B "$D/loops_e195.py" "$OD" "$K" > "$B/loops.txt" 2>&1; lrc=$?
echo "loops_e195.py rc $lrc (reported): $(tr '\n' ' ' < "$B/loops.txt" | cut -c1-400)"
"$H" --list --json > "$B/arm-table.json" 2> "$B/list.err" < /dev/null || fail 5 "the host's --list --json exited non-zero"
"$H" --list > "$B/arm-table.txt" 2>> "$B/list.err" < /dev/null || fail 5 "the host's --list exited non-zero"
cmp -s "$B/arm-table.json" "$D/arm-table-e195.json" || fail 6 "the host's --list --json differs from the registration's arm table"
cmp -s "$B/arm-table.txt" "$D/arm-table-e195.txt" || fail 6 "the host's --list differs from the registration's arm table"
"$OBJ" -O binary --only-section=.text "$K" "$B/x09mem.text.bin" || fail 7 "objcopy of the kernel's .text"
ke=$(sha256sum "$K" | cut -d' ' -f1); kt=$(sha256sum "$B/x09mem.text.bin" | cut -d' ' -f1)
kd=$("$OD" -d "$K" 2>/dev/null | tail -n +3 | sha256sum | cut -d' ' -f1)
hh=$(sha256sum "$H" | cut -d' ' -f1)
PYN=$TREE/.venv/bin/python3
gen="NOT RUN (no numpy in the tree's .venv on this box: step 5's listing stands alone)"
if [ -x "$PYN" ] && "$PYN" -I -c 'import numpy' > /dev/null 2>&1; then
  if [ -e build/x09-gen-check ]; then mv build/x09-gen-check "build/x09-gen-check.before-$(date +%Y%m%dT%H%M%S)" || fail 8 "could not move the earlier generator check aside"; fi
  "$PYN" -I -B "$SRC/make_x09.py" build/x09-gen-check --host "$H" --check --no-ms > "$B/make-check.txt" 2>&1; mrc=$?
  tail -n 1 "$B/make-check.txt"
  [ "$mrc" -eq 0 ] && grep -q '^CHECK OK: 31 arms' "$B/make-check.txt" || fail 8 "make_x09.py --check --no-ms: $(tail -n 1 "$B/make-check.txt")"
  cmp -s build/x09-gen-check/manifest.json tools/claims-v3/e195/gen-e195-noms/manifest.json &&
    cmp -s build/x09-gen-check/counts.json tools/claims-v3/e195/gen-e195-noms/counts.json ||
    fail 8 "the generator's output from this host's bytes differs from the kit's gen-e195-noms/"
  gen="CHECK OK: 31 arms from this host's bytes (numpy $("$PYN" -I -c 'import numpy; print(numpy.__version__)')); manifest.json and counts.json byte-equal to gen-e195-noms/"
fi
echo "generator: $gen"
for t in ettelem/ettelem sparsity/host/sparsity_host; do
  src=$TREE/build/$t
  [ -x "$src" ] || fail 9 "the box's tool $src is not an executable file"
  if [ -L "build/$t" ]; then
    [ "$(readlink "build/$t")" = "$src" ] || fail 9 "build/$t points to $(readlink "build/$t"), not $src"
  elif [ -e "build/$t" ]; then
    fail 9 "build/$t exists and is not the symlink to $src"
  else
    mkdir -p "$(dirname "build/$t")" && ln -s "$src" "build/$t" || fail 9 "could not link build/$t to $src"
  fi
done
eh=$(sha256sum build/ettelem/ettelem | cut -d' ' -f1); ph=$(sha256sum build/sparsity/host/sparsity_host | cut -d' ' -f1)
o=$(build/sparsity/host/sparsity_host --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 \
      --seed 1 --stop-file /nonexistent/e195-stop --no-such-option-e195 2>&1 < /dev/null); hrc=$?
echo "heater: ${ph:0:16}...; its parser with the registered arguments and an unknown option: exit $hrc, '$(printf '%s' "$o" | head -n 1 | cut -c1-80)'"
[ "$hrc" -eq 2 ] && printf '%s' "$o" | grep -q 'unknown option --no-such-option-e195' || fail 10 "the heater's parser did not stop at the unknown option alone (exit $hrc)"
grep -a -q -- '--stop-file' build/sparsity/host/sparsity_host || fail 10 "the heater has no --stop-file (block_x09.sh's own preflight reads it)"
{
  echo "X09MEM-BUILT $(TZ=America/Los_Angeles date '+%F %T %Z') on $(hostname)"
  echo "host $hh"
  echo "kernel $ke"
  echo "kernel_text $kt"
  echo "kernel_disassembly $kd"
  echo "ettelem $eh $TREE/build/ettelem/ettelem"
  echo "sparsity_host $ph $TREE/build/sparsity/host/sparsity_host"
  echo "registration_desk_build (aifoundry2, E195.md section 17 item 5) kernel_elf 7c5faea8db181f8761754fe8af222f751624187f3a12bbe30254d84be6226fa6 text 007a355d2da5b420648a80f8a0d8304e172ecba3fdc94903fb6ca4ae67a12f2e disassembly b59a6caf9abec79ba8feb3adc4fa190831fc018428d782febafdfe868ebe25ce"
  echo "same_as_registration_desk_build elf $([ "$ke" = 7c5faea8db181f8761754fe8af222f751624187f3a12bbe30254d84be6226fa6 ] && echo yes || echo no) text $([ "$kt" = 007a355d2da5b420648a80f8a0d8304e172ecba3fdc94903fb6ca4ae67a12f2e ] && echo yes || echo no) disassembly $([ "$kd" = b59a6caf9abec79ba8feb3adc4fa190831fc018428d782febafdfe868ebe25ce ] && echo yes || echo no) (reported, never judged)"
  echo "check_elf $(tail -n 1 "$B/check_elf.txt")"
  echo "arm_table byte-equal to desk/arm-table-e195.json and .txt"
  echo "generator $gen"
} > "$REC.new"
mv "$REC.new" "$REC"
cat "$REC"
echo "X09MEM-BUILT rc=0 kernel ${ke:0:12} text ${kt:0:12} host ${hh:0:12}"
