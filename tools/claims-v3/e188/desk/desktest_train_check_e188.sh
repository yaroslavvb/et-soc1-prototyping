#!/usr/bin/env bash
# E188 (Q165, the kit, Thu 12 Nov 2026, before any E188 datum): THE DESK TEST OF THE TRAIN CHANGE'S CHECK ON REAL BUILDS, on the Intel
# (never a box, never a card). E183's kit note 4's desk test (tools/claims-v3/e183/desk/desktest_train_check_e183.sh) carried to E188's
# train host. It makes three sources from the committed workloads/sparsity/host/main.cpp (its pinned 0f53a7d5...):
#   PATCHED     E182's patch_host_e182.py applied (Q139(k)'s C-log patch, then E182's three flags): the pinned 37ca98ad..., the source
#               E182 registered and E182 and E186 ran, which build_host_e188.sh builds on the box;
#   CCHECK      Q139(k)'s C-log patch alone (patch_host_ccheck.patch_text): the C-logging host's source (the box's build/ccheck host), THE
#               FIRST NEGATIVE CONTROL: it accepts --c-log and --c-poison but not E182's flags;
#   E78         the committed source unchanged (E78's host, the box's build/sparsity host and heater), THE SECOND NEGATIVE CONTROL;
# and compiles each four ways against the check of C's mock headers (tools/claims-v3/ccheck/mockrt/include, unchanged), linked with
# desk/mock_rt_e188.cpp (the check of C's mock with a device record, E188_DEVICE_RECORD):
#   g++-13 -O2 (GCC as on the box, at the host's own CMake flag), g++-13 -O3, clang++ -O1 (E186's desk test's), clang++ -O2.
# On each of the twelve binaries it runs:
#   OLD  E186's binary greps, reported (build_host_e186.sh's loop: '--c-log' '--c-poison' '--values-b' '--abba' '--launches' '--stop-file'
#        'file:' int8 fp16, and block_e186.sh's train-host loop): E188's kit greps none of them;
#   NEW  train_check_e188.sh (the host's own behaviour) with the mock's device record on: PATCHED must read TRAIN-CHANGE OK on all four
#        builds, CCHECK and E78 TRAIN-CHANGE MISSING (unknown option --values-b) on all four; no run of it may leave a record line;
#   CONTROL  the refusal a check must NOT use, a train without --launches (E188's B05 tiles, a readable kernel stand-in): on PATCHED it
#        reaches the device layer, the runtime, a stream and the kernel load (Session's constructor) before its refusal "a train needs
#        --launches" (E182's patch refuses there, before its tile copies); on the controls the option is refused before any device call
#        (rc 2). E183's kit note 4 found the desk's GCC 13.2 crashing (rc 139) on an exception thrown after Session is built; either way
#        the record, written as each call is made, is the reading.
# Expected and asserted: as above, and every NEW run leaves the record empty. Reported beside: each binary's sha256 and OLD's reading.
#   bash tools/claims-v3/e188/desk/desktest_train_check_e188.sh <scratch dir>   (prints DESKTEST-TRAIN-CHECK-E188 PASS or FAIL; exit 0 or 1)
# E188_GXX and E188_CLANGXX name the compilers (default g++-13 and clang++ on PATH); `timeout` (GNU) must be on PATH. Every compile runs
# with SDKROOT unset (the Mac's /usr/bin/python3 exports the unversioned SDK, against which Homebrew's GCC 13.2 fails: a desk detail).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
D=$SRC/tools/claims-v3/e188
INC=$SRC/tools/claims-v3/ccheck/mockrt/include
MOCK=$D/desk/mock_rt_e188.cpp
PY=/usr/bin/python3
GXX=$(command -v "${E188_GXX:-g++-13}") || { echo "no ${E188_GXX:-g++-13} on PATH"; exit 2; }
CLX=$(command -v "${E188_CLANGXX:-clang++}") || { echo "no ${E188_CLANGXX:-clang++} on PATH"; exit 2; }
command -v timeout > /dev/null || { echo "no timeout on PATH"; exit 2; }
COMMITTED_SHA=0f53a7d505155156c933e2d9a64d38803ca4e0cea3e20242e0aaafbf35e82284
PATCHED_SHA=37ca98adf1e677d7b8087b28e932dcbb05f5a0dd37c42be2215a7c503c72e5b8
mkdir -p "$S"; S=$(cd "$S" && pwd)
main() {
rm -rf "${S:?}/src" "${S:?}/bin" "${S:?}/rec"
mkdir -p "$S/src/patched/host" "$S/src/ccheck/host" "$S/src/e78/host" "$S/bin" "$S/rec"
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
echo "compilers: $("$GXX" --version | head -n 1); $("$CLX" --version | head -n 1)"
echo
echo "== 1. the three sources"
for t in patched ccheck e78; do cp "$SRC/workloads/sparsity/host/main.cpp" "$S/src/$t/host/main.cpp"; cp "$SRC/workloads/sparsity/sparsity_args.h" "$S/src/$t/"; done
[ "$(sha "$S/src/e78/host/main.cpp")" = "$COMMITTED_SHA" ]; ok $? "the committed host source is the pinned 0f53a7d5..."
"$PY" -I -B "$SRC/tools/claims-v3/e182/patch_host_e182.py" "$S/src/patched/host/main.cpp" > /dev/null
"$PY" -I -B - "$SRC/tools/claims-v3/ccheck" "$S/src/ccheck/host/main.cpp" <<'PYEOF'
import sys
sys.path.insert(0, sys.argv[1])
import patch_host_ccheck as PC
p = sys.argv[2]
text = PC.patch_text(open(p).read())
open(p, "w").write(text)
PYEOF
echo "patched $(sha "$S/src/patched/host/main.cpp"); ccheck $(sha "$S/src/ccheck/host/main.cpp"); e78 $(sha "$S/src/e78/host/main.cpp")"
[ "$(sha "$S/src/patched/host/main.cpp")" = "$PATCHED_SHA" ]; ok $? "the patched source is the pinned 37ca98ad... (harness-e186.json's and harness-e182.json's)"
echo
echo "== 2. twelve builds (each: the compiler, its flag, the mock headers, the source and the recording mock)"
CFGS="gcc13-O2 gcc13-O3 clang-O1 clang-O2"
for t in patched ccheck e78; do
  for c in $CFGS; do
    case "$c" in gcc13-*) cc=$GXX ;; *) cc=$CLX ;; esac
    fl=-${c##*-}
    b=$S/bin/host-$t-$c
    env -u SDKROOT "$cc" -std=c++17 "$fl" -I"$INC" -I"$S/src/$t" "$S/src/$t/host/main.cpp" "$MOCK" -o "$b" 2> "$S/bin/$t-$c.err"; rc=$?
    echo "$(basename "$cc") -std=c++17 $fl -I<mock headers> -I<src-$t> <src-$t>/host/main.cpp <mock_rt_e188> -o host-$t-$c: rc $rc; sha256 $([ -f "$b" ] && sha "$b" || echo none); $(grep -c . "$S/bin/$t-$c.err") lines on stderr"
    [ "$rc" -eq 0 ] && [ -x "$b" ]; ok $? "host-$t-$c built"
  done
done
F=$SRC/tools/claims-v3/e188/tiles/fp32/e188_a1_b3f800020.bin
SI=$SRC/tools/claims-v3/kinds/tiles/fp32/ones.bin
echo "desk stand-in kernel: the mock runtime never reads it" > "$S/kernel.elf"
echo
echo "== 3. on each binary: OLD (reported), NEW with the device record, and the CONTROL"
for t in patched ccheck e78; do
  for c in $CFGS; do
    b=$S/bin/host-$t-$c
    echo "-- host-$t-$c"
    miss=""
    for s in '--c-log' '--c-poison' '--values-b' '--abba' '--launches' '--stop-file' 'file:' int8 fp16; do
      grep -a -q -- "$s" "$b" || miss="$miss $s"
    done
    echo "OLD (E186's greps, reported): $([ -z "$miss" ] && echo 'every string found' || echo "not found:$miss")"
    R=$S/rec/new-$t-$c.txt; rm -f "$R"
    E188_DEVICE_RECORD="$R" bash "$D/train_check_e188.sh" "$b" > "$S/rec/new-$t-$c.out" 2>&1; nr=$?
    sed "s#$S#<scratch>#g" "$S/rec/new-$t-$c.out"
    nrec=0; [ -f "$R" ] && nrec=$(grep -c . "$R")
    echo "NEW rc $nr; device record lines after it: $nrec"
    if [ "$t" = patched ]; then
      [ "$nr" -eq 0 ] && grep -q '^TRAIN-CHANGE OK: ' "$S/rec/new-$t-$c.out"; ok $? "NEW on host-$t-$c: TRAIN-CHANGE OK"
    else
      [ "$nr" -eq 1 ] && grep -q '^TRAIN-CHANGE MISSING: .*unknown option --values-b' "$S/rec/new-$t-$c.out" &&
        grep -q -- '--values-b alone: unknown option' "$S/rec/new-$t-$c.out"
      ok $? "NEW on host-$t-$c: TRAIN-CHANGE MISSING (unknown option --values-b)"
    fi
    [ "$nrec" -eq 0 ]; ok $? "NEW on host-$t-$c opened no device (the record is empty)"
    R2=$S/rec/ctl-$t-$c.txt; rm -f "$R2"
    E188_DEVICE_RECORD="$R2" MOCK_SLEEP_MS=1 timeout 10 "$b" --test fma --type fp32 --pattern none --values "file:$F" --values-b "file:$SI" \
      --abba SFFS --seconds 1 --shires 0x3 --per-shire 8 --kernel "$S/kernel.elf" > "$S/rec/ctl-$t-$c.out" 2> "$S/rec/ctl-$t-$c.err" < /dev/null; cr=$?
    crec=0; [ -f "$R2" ] && crec=$(grep -c . "$R2")
    echo "CONTROL (a train without --launches) rc $cr: $(grep -m1 -E 'FAIL|unknown option' "$S/rec/ctl-$t-$c.err" | cut -c1-90); device record: $crec lines ($([ -f "$R2" ] && sed 's/^MOCKDEV //' "$R2" | tr '\n' ',' | sed 's/,$//'))"
    if [ "$t" = patched ]; then
      { [ "$cr" -eq 1 ] && grep -q 'a train needs --launches' "$S/rec/ctl-$t-$c.err"; } || { case "$c" in gcc13-*) [ "$cr" -eq 139 ] ;; *) false ;; esac; }
      [ "$?" -eq 0 ] && grep -q '^MOCKDEV createPcieDeviceLayer$' "$R2" && grep -q '^MOCKDEV IRuntime::create$' "$R2" && grep -q '^MOCKDEV loadCode$' "$R2"
      ok $? "CONTROL on host-$t-$c reaches the device layer, the runtime and the kernel load before its refusal"
    else
      [ "$cr" -eq 2 ] && grep -q 'unknown option --values-b' "$S/rec/ctl-$t-$c.err" && [ "$crec" -eq 0 ]; ok $? "CONTROL on host-$t-$c: unknown option, no device call"
    fi
  done
done
echo
echo "DESKTEST-TRAIN-CHECK-E188 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
