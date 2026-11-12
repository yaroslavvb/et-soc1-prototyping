#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): THE DESK TEST OF THE TRAIN CHANGE'S CHECK
# ON REAL BUILDS, on the Intel (never a box, never a card). It makes E180's tree twice with E180's own generator (gen_acc_e180.py,
# unchanged), applies patch_host_e183.py to one (host/main.cpp at the pinned 9b8f1a08...) and leaves the other as E180's (3cad4adc...,
# the committed workloads/enercat/host/main.cpp: THE NEGATIVE CONTROL), and compiles each host four ways against E184's desk stubs
# (tools/claims-v3/e184/desk/stubs, unchanged), linked with desk/mock_runtime_e183_v2.cpp (E183's mock with a device record):
#   g++-13 -O2 (the enercat host's own CMake flag, with GCC as on the box), g++-13 -O3, clang++ -O1 (the kit's desk test's), clang++ -O2.
# On each of the eight binaries it runs:
#   OLD  build_host_e183.sh line 68 (= block_e183.sh line 48): grep -a -q -- '--operands-b' && grep -a -q 'train_kind'; and, reported,
#        line 69's grep for 'fadd.ps.acc' and block_e183.sh line 49's for 'file:';
#   NEW  train_check_e183.sh (the host's own behaviour: --list, then the three train options with an empty --kernel), with the mock's
#        device record on (E183_DEVICE_RECORD): no run of it may leave a record line;
#   CONTROL  the refusal the critic named, '--operands-b' without '--launches' (a readable kernel stand-in, images E183's): on a patched
#        host it reads 'a train needs --launches' (rc 1) only AFTER the record shows the device layer, the runtime, the kernel load and
#        the operand copy, which is why the new check does not use it; an unpatched host refuses the option before any device call (rc 2).
#        THE DESK'S GCC (Homebrew GCC 13.2 with this Mac's linker) crashes, rc 139, on any exception thrown after Session is built (an
#        unknown --pattern does the same, reported per build), so on the GCC builds the refusal's text is not printed and the record is
#        the reading; the new check's own throw (main.cpp line 603) comes before Session and reads rc 1 on every build.
# Expected and asserted: OLD fails on both GCC builds and passes on both clang builds of the patched host, and fails on all four unpatched;
# NEW passes on all four patched builds and fails on all four unpatched; every NEW run leaves the record empty; the CONTROL as above.
# Reported beside (part K): the kernel path block_e183.sh line 50 greps, on the patched host built with GCC -O2 and clang -O2 against a
# Constants.h overlay holding a box-like kernel path (E184's stub names "x").
#   bash tools/claims-v3/e183/desk/desktest_train_check_e183.sh <scratch dir>   (prints DESKTEST-TRAIN-CHECK-E183 PASS or FAIL; exit 0 or 1)
# E183_GXX and E183_CLANGXX name the compilers (default g++-13 and clang++ on PATH); `timeout` (GNU) must be on PATH. Every compile runs
# with SDKROOT unset (the Mac's /usr/bin/python3 exports the unversioned SDK, against which Homebrew's GCC 13.2 fails: a desk detail).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
D=$SRC/tools/claims-v3/e183
STUBS=$SRC/tools/claims-v3/e184/desk/stubs
MOCK=$D/desk/mock_runtime_e183_v2.cpp
PY=/usr/bin/python3
GXX=$(command -v "${E183_GXX:-g++-13}") || { echo "no ${E183_GXX:-g++-13} on PATH"; exit 2; }
CLX=$(command -v "${E183_CLANGXX:-clang++}") || { echo "no ${E183_CLANGXX:-clang++} on PATH"; exit 2; }
command -v timeout > /dev/null || { echo "no timeout on PATH"; exit 2; }
PATCHED_SHA=9b8f1a088a7a83c00af64387c80f0f92b0522dcb89ce3a330853ca8e00b0c5f1
E180_SHA=3cad4adc16534b845cc142f78a28907192b62fe21081e282d6df67342200359c
mkdir -p "$S"; S=$(cd "$S" && pwd)
main() {
rm -rf "${S:?}/src-patched" "${S:?}/src-unpatched" "${S:?}/bin" "${S:?}/rec" "${S:?}/k-overlay"
mkdir -p "$S/bin" "$S/rec" "$S/k-overlay"
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
echo "compilers: $("$GXX" --version | head -n 1); $("$CLX" --version | head -n 1)"
echo
echo "== 1. the two trees (E180's generator, unchanged; the patch on one)"
for t in patched unpatched; do
  "$PY" -I -B "$SRC/tools/claims-v3/e180/gen_acc_e180.py" --src "$SRC/workloads/enercat" --dst "$S/src-$t" > /dev/null || { echo "gen_acc_e180.py failed"; return 1; }
done
"$PY" -I -B "$D/patch_host_e183.py" "$S/src-patched/host/main.cpp"
hp=$(sha "$S/src-patched/host/main.cpp"); hu=$(sha "$S/src-unpatched/host/main.cpp")
echo "patched host/main.cpp sha256 $hp; E180's (unpatched) $hu"
[ "$hp" = "$PATCHED_SHA" ]; ok $? "the patched source is the pinned 9b8f1a08..."
[ "$hu" = "$E180_SHA" ]; ok $? "the unpatched source is E180's, the committed 3cad4adc..."
echo
echo "== 2. eight builds (each: the compiler, its flag, E184's stubs, the tree, main.cpp and the recording mock)"
CFGS="gcc13-O2 gcc13-O3 clang-O1 clang-O2"
for t in patched unpatched; do
  for c in $CFGS; do
    case "$c" in gcc13-*) cc=$GXX ;; *) cc=$CLX ;; esac
    fl=-${c##*-}
    b=$S/bin/host-$t-$c
    env -u SDKROOT "$cc" -std=c++17 "$fl" -I"$STUBS" -I"$S/src-$t" "$S/src-$t/host/main.cpp" "$MOCK" -o "$b" 2> "$S/bin/$t-$c.err"; rc=$?
    echo "$(basename "$cc") -std=c++17 $fl -I<stubs> -I<src-$t> <src-$t>/host/main.cpp <mock v2> -o host-$t-$c: rc $rc; sha256 $([ -f "$b" ] && sha "$b" || echo none); $(grep -c . "$S/bin/$t-$c.err") lines on stderr"
    [ "$rc" -eq 0 ] && [ -x "$b" ]; ok $? "host-$t-$c built"
  done
done
F=$SRC/tools/claims-v3/e183/images/e80j6.bin
SI=$SRC/tools/claims-v3/e183/images/const.bin
echo "desk stand-in kernel: the mock runtime never reads it" > "$S/kernel.elf"
echo
echo "== 3. on each binary: the OLD grep, the NEW check with the device record, and the CONTROL"
for t in patched unpatched; do
  for c in $CFGS; do
    b=$S/bin/host-$t-$c
    echo "-- host-$t-$c"
    old=fail; grep -a -q -- '--operands-b' "$b" && grep -a -q 'train_kind' "$b" && old=pass
    g69=no; grep -a -q 'fadd.ps.acc' "$b" && g69=yes
    g49=no; grep -a -q -- 'file:' "$b" && g49=yes
    echo "OLD line 68 (= block line 48): $old ('--operands-b' $(grep -a -q -- '--operands-b' "$b" && echo yes || echo no), 'train_kind' $(grep -a -q 'train_kind' "$b" && echo yes || echo no)); reported: line 69's 'fadd.ps.acc' $g69, block line 49's 'file:' $g49"
    want=fail; [ "$t" = patched ] && case "$c" in clang-*) want=pass ;; esac
    [ "$old" = "$want" ]; ok $? "OLD on host-$t-$c reads $want"
    R=$S/rec/new-$t-$c.txt; rm -f "$R"
    E183_DEVICE_RECORD="$R" bash "$D/train_check_e183.sh" "$b" > "$S/rec/new-$t-$c.out" 2>&1; nr=$?
    sed "s#$S#<scratch>#g" "$S/rec/new-$t-$c.out"
    nrec=0; [ -f "$R" ] && nrec=$(grep -c . "$R")
    echo "NEW rc $nr; device record lines after it: $nrec"
    if [ "$t" = patched ]; then
      [ "$nr" -eq 0 ] && grep -q '^TRAIN-CHANGE OK: ' "$S/rec/new-$t-$c.out"; ok $? "NEW on host-$t-$c: TRAIN-CHANGE OK"
    else
      [ "$nr" -eq 1 ] && grep -q '^TRAIN-CHANGE MISSING: .*unknown option --operands-b' "$S/rec/new-$t-$c.out"; ok $? "NEW on host-$t-$c: TRAIN-CHANGE MISSING (unknown option --operands-b)"
    fi
    [ "$nrec" -eq 0 ]; ok $? "NEW on host-$t-$c opened no device (the record is empty)"
    R2=$S/rec/ctl-$t-$c.txt; rm -f "$R2"
    E183_DEVICE_RECORD="$R2" E183_MOCK_LAUNCH_MS=1 timeout 10 "$b" --kernel "$S/kernel.elf" --pattern fadd.ps --harts 2 --operands "file:$F" \
      --operands-b "file:$SI" --abba SFFS --seconds 1 > "$S/rec/ctl-$t-$c.out" 2> "$S/rec/ctl-$t-$c.err" < /dev/null; cr=$?
    crec=0; [ -f "$R2" ] && crec=$(grep -c . "$R2")
    echo "CONTROL (--operands-b without --launches) rc $cr: $(grep -m1 -E 'FAIL|unknown option' "$S/rec/ctl-$t-$c.err" | cut -c1-100); device record: $crec lines ($([ -f "$R2" ] && sed 's/^MOCKDEV //' "$R2" | tr '\n' ',' | sed 's/,$//'))"
    if [ "$t" = patched ]; then
      # the desk's GCC builds crash (rc 139) on any exception thrown after Session is built (the toolchain note below), so there the refusal's
      # text is never printed: the record, written as each call is made, still shows how far the run went before the refusal's throw
      { [ "$cr" -eq 1 ] && grep -q 'a train needs --launches' "$S/rec/ctl-$t-$c.err"; } || { case "$c" in gcc13-*) [ "$cr" -eq 139 ] ;; *) false ;; esac; }
      [ "$?" -eq 0 ] && grep -q '^MOCKDEV createPcieDeviceLayer$' "$R2" && grep -q '^MOCKDEV loadCode$' "$R2" && grep -q '^MOCKDEV memcpyHostToDevice$' "$R2"
      ok $? "CONTROL on host-$t-$c reaches the device layer, the kernel load and the operand copy before its refusal"
      E183_MOCK_LAUNCH_MS=1 timeout 10 "$b" --kernel "$S/kernel.elf" --pattern nosuch --seconds 1 > /dev/null 2> "$S/rec/tc-$t-$c.err" < /dev/null; tr=$?
      echo "toolchain note (reported): an unknown --pattern, thrown in run() after Session is built, exits $tr: $(grep -m1 'FAIL' "$S/rec/tc-$t-$c.err" | cut -c1-60)"
    else
      [ "$cr" -eq 2 ] && grep -q 'unknown option --operands-b' "$S/rec/ctl-$t-$c.err" && [ "$crec" -eq 0 ]; ok $? "CONTROL on host-$t-$c: unknown option, no device call"
    fi
  done
done
echo
echo "== K. reported: the kernel path block_e183.sh line 50 greps, with a box-like KERNEL_ELF (E184's stub Constants.h names \"x\")"
sed 's#^\#define KERNEL_ELF .*#\#define KERNEL_ELF "/opt/desk-stand-in/aifoundry/build/enercat-e183/kernel/enercat.elf"#' "$STUBS/Constants.h" > "$S/k-overlay/Constants.h"
for c in gcc13-O2 clang-O2; do
  case "$c" in gcc13-*) cc=$GXX ;; *) cc=$CLX ;; esac
  b=$S/bin/host-k-$c
  env -u SDKROOT "$cc" -std=c++17 "-${c##*-}" -I"$S/k-overlay" -I"$STUBS" -I"$S/src-patched" "$S/src-patched/host/main.cpp" "$MOCK" -o "$b" 2> /dev/null; rc=$?
  k=$(grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$b" 2>/dev/null | head -n 1)
  echo "host-k-$c: compile rc $rc; line 50's grep reads '${k:-nothing}'"
done
echo
echo "DESKTEST-TRAIN-CHECK-E183 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
