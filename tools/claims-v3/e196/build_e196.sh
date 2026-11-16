#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE TWO BUILDS ON THE BOX, step 6's job body
# (rb/s08_a3_build_e196.sh runs it from E196's root R on aifoundry3, under `timeout -k 15 900`). No device is opened: each host runs only
# to a refusal of its option parser (exit 2 before anything), with ET_DEVICES=99 and stdin from /dev/null.
#   1. the sources at their sha256 (E196.md section 3): the lab's unchanged host workloads/sparsity/host/main.cpp 0f53a7d5..., the
#      request's proposal/src/host/main.cpp b91a2c76...; every synced build file at its pin is the session's own check (the lists);
#   2. cmake with the box's /opt/et, nice 10, -j4, each into a folder of E196's own (never build/sparsity, which other kits use):
#      R/build/sparsity-lab from R/workloads/sparsity (the lab's unchanged sparsity workload, 9 files synced from GitHub main) and
#      R/build/x14 from R/tools/claims-v3/e196/proposal/src (the request's x14_host and the same kernel); an earlier build of either is
#      moved aside first, never removed;
#   3. THE KERNELS' .text (objcopy -O binary --only-section=.text), A GATE: both must read 8798e43c... (E196.md sections 11 and 16: a
#      .text that differs is no session); the ELFs' sha256 reported beside the desk's 990807f4... and request.md's abbdbe40... (another
#      toolchain's version string makes another file: reported, never judged);
#   4. THE HOSTS BY BEHAVIOUR, A GATE: the lab's host given the registered heater command and each registered pass command
#      (desk/commands-e196.txt) with an unknown option after it stops at that option alone (exit 2, "unknown option"), so every
#      registered option is one it knows; given --label (the request's option) it exits 2 (E196.md section 16 item 10); the request's
#      host given each registered train command and premise run with an unknown option after it exits 2 at that option; given
#      --abba XXXX, --launches 17 or --budget 10, exit 2. Nothing is grepped from either binary;
#   5. the arm table: make_x14.py --out R/build/gen-check, then --check ({"problems": []}) and cmp with proposal/src/arms.json;
#   6. the record R/build/BUILD-E196.txt (the hashes; the session checks both hosts against it and its date), then
#      E196-BUILT rc=0 ... or E196-BUILD-FAILED rc=<n>: <why> (exit 0 or 16).
#   bash tools/claims-v3/e196/build_e196.sh           (from E196's root on the box, or the stand-in box of the runbook desk test)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
K=tools/claims-v3/e196
SRC=$K/proposal/src
LABSRC=workloads/sparsity
OBJ=${E196_OBJCOPY:-/opt/et/bin/riscv64-unknown-elf-objcopy}
TEXT=8798e43c4869a124690bc652d574d5ab78d686faa70293cbcff658d24c30a399
DESK_ELF=990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24
REQ_ELF=abbdbe40976f7413e9c246e0992dcf52a56885ab69e1746351f9903cb8f7de46
LAB_SRC_SHA=0f53a7d505155156c933e2d9a64d38803ca4e0cea3e20242e0aaafbf35e82284
X14_SRC_SHA=b91a2c767e39cdad1172d4a33048c79e42dc9ae9dc9fa20479e8426ee1b494cb
fail() { echo "E196-BUILD-FAILED rc=$1: $2"; exit 16; }
echo "COMPILER $(g++ --version 2>/dev/null | head -n 1); $(cmake --version 2>/dev/null | head -n 1); $(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)"
echo "PYTHON $(command -v python3) $(python3 -V 2>&1)"
[ "$(sha256sum "$LABSRC/host/main.cpp" 2>/dev/null | cut -d' ' -f1)" = "$LAB_SRC_SHA" ] || fail 2 "the lab's host source is not at 0f53a7d5..."
[ "$(sha256sum "$SRC/host/main.cpp" 2>/dev/null | cut -d' ' -f1)" = "$X14_SRC_SHA" ] || fail 2 "the request's host source is not at b91a2c76..."
mkdir -p build || fail 2 "could not make build/ in E196's root"
build_one() {  # build_one <name> <source dir> <build dir>
  local n=$1 s=$2 b=$3 rc
  if [ -e "$b" ]; then mv "$b" "$b.before-$(date +%Y%m%dT%H%M%S)" || fail 2 "could not move the earlier $n build aside"; fi
  nice -n 10 cmake -S "$s" -B "$b" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > "$b.cmake.log" 2>&1; rc=$?
  tail -n 2 "$b.cmake.log" | sed "s/^/  [$n configure] /"
  [ "$rc" -eq 0 ] || fail "$rc" "$n: cmake configure (the last lines above)"
  mv "$b.cmake.log" "$b/cmake-configure.log"
  nice -n 10 cmake --build "$b" -j4 > "$b/cmake-build.log" 2>&1; rc=$?
  tail -n 2 "$b/cmake-build.log" | sed "s/^/  [$n build] /"
  [ "$rc" -eq 0 ] || fail "$rc" "$n: cmake --build (the last lines above)"
  echo "  [$n] compiler warnings in the build log: $(grep -c 'warning:' "$b/cmake-build.log")"
}
build_one lab "$LABSRC" build/sparsity-lab
build_one x14 "$SRC" build/x14
LH=build/sparsity-lab/host/sparsity_host; XH=build/x14/host/x14_host
for f in build/sparsity-lab/kernel/sparsity.elf build/x14/kernel/sparsity.elf; do [ -s "$f" ] || fail 3 "no kernel ELF $f"; done
[ -x "$LH" ] && [ -x "$XH" ] || fail 3 "no host after the builds"
for n in lab x14; do
  d=build/sparsity-lab; [ "$n" = x14 ] && d=build/x14
  "$OBJ" -O binary --only-section=.text "$d/kernel/sparsity.elf" "$d/sparsity.text.bin" || fail 4 "objcopy of the $n kernel's .text"
done
kel=$(sha256sum build/sparsity-lab/kernel/sparsity.elf | cut -d' ' -f1); kex=$(sha256sum build/x14/kernel/sparsity.elf | cut -d' ' -f1)
ktl=$(sha256sum build/sparsity-lab/sparsity.text.bin | cut -d' ' -f1); ktx=$(sha256sum build/x14/sparsity.text.bin | cut -d' ' -f1)
[ "$ktl" = "$TEXT" ] && [ "$ktx" = "$TEXT" ] || fail 5 "a kernel's .text is not 8798e43c... (lab ${ktl:0:12}, x14 ${ktx:0:12}): E196.md section 11, no session"
# the hosts by behaviour: every registered command parses; nothing opens (each stops at the unknown option, exit 2, before anything)
beh=0; nbeh=0
probe() {  # probe <binary> <want text> <args...>: exit 2 with the text, before anything
  local b=$1 want=$2 o r; shift 2
  o=$(ET_DEVICES=99 timeout 10 "$b" "$@" 2>&1 < /dev/null); r=$?
  nbeh=$((nbeh + 1))
  if [ "$r" -eq 2 ] && printf '%s' "$o" | grep -q -- "$want"; then beh=$((beh + 1)); else echo "  behaviour: $(basename "$b") $* -> exit $r '$(printf '%s' "$o" | head -n 1 | cut -c1-100)'"; fi
}
GEN=build/gen-check
while IFS= read -r ln; do
  case "$ln" in '#'*|'') continue ;; esac
  set -- $ln
  case "$2" in
    sparsity_host) shift 2; a=("$@"); probe "$LH" "unknown option --no-such-option-e196" "${a[@]//GEN\//$GEN/}" --no-such-option-e196 ;;
    x14_host) shift 2; a=("$@"); probe "$XH" "unknown option --no-such-option-e196" "${a[@]//GEN\//$GEN/}" --no-such-option-e196 ;;
    *) if [ "$3" = x14_host ]; then shift 3; a=("$@"); probe "$XH" "unknown option --no-such-option-e196" "${a[@]//GEN\//$GEN/}" --no-such-option-e196; fi ;;
  esac
done < "$K/desk/commands-e196.txt"
probe "$LH" "unknown option --label" --test fma --type fp32 --pattern none --values randn --label heater --seconds 2
probe "$XH" "abba" --values randn --label x --abba XXXX --launches 13
probe "$XH" "launches" --values file:x --label x --values-b file:x --abba SFFS --launches 17
probe "$XH" "budget" --values randn --label x --seconds 2 --budget 10
[ "$beh" -eq "$nbeh" ] && [ "$nbeh" -eq 42 ] || fail 6 "the hosts' behaviour: $beh of $nbeh refusals as expected (want 42 of 42; the lines above)"
python3 -I -B "$SRC/make_x14.py" --lab-tiles tools/claims-v3/kinds/tiles/fp32 --out "$GEN" > /dev/null 2>&1 || fail 7 "make_x14.py --out"
python3 -I -B "$SRC/make_x14.py" --lab-tiles tools/claims-v3/kinds/tiles/fp32 --out "$GEN" --check > build/gen-check.json 2>&1 || fail 7 "make_x14.py --check"
grep -q '"problems": \[\]' build/gen-check.json && cmp -s "$GEN/arms.json" "$SRC/arms.json" || fail 7 "make_x14.py --check found problems, or arms.json differs"
lh=$(sha256sum "$LH" | cut -d' ' -f1); xh=$(sha256sum "$XH" | cut -d' ' -f1)
{
  echo "built $(TZ=America/Los_Angeles date '+%F %T %Z') on $(hostname)"
  echo "lab_source_sha256 $LAB_SRC_SHA"
  echo "x14_source_sha256 $X14_SRC_SHA"
  echo "lab_host_sha256 $lh"
  echo "x14_host_sha256 $xh"
  echo "kernel_elf_sha256_lab $kel"
  echo "kernel_elf_sha256_x14 $kex"
  echo "kernel_text_sha256_lab $ktl"
  echo "kernel_text_sha256_x14 $ktx"
  echo "kernel_elf_same_as_desk_build (990807f4..., E196.md section 16) lab $([ "$kel" = "$DESK_ELF" ] && echo yes || echo no) x14 $([ "$kex" = "$DESK_ELF" ] && echo yes || echo no); as request.md's (abbdbe40...) $([ "$kel" = "$REQ_ELF" ] && echo yes || echo no) (reported, never judged)"
  echo "hosts_behaviour $beh of $nbeh refusals before anything (every registered command parses; --label refused by the lab's host)"
  echo "arm_table make_x14.py --check no problems; arms.json byte-equal to proposal/src/arms.json"
  echo "E196-BUILT rc=0 lab ${lh:0:12} x14 ${xh:0:12} text ${ktl:0:12}"
} > build/BUILD-E196.txt
cat build/BUILD-E196.txt
