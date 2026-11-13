#!/usr/bin/env bash
# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): THE DESK TEST OF THE HOST CHECK ON REAL BUILDS, on the Intel (never a box,
# never a card). E183's kit note 4's and E188's form (desk/desktest_train_check_e188.sh) carried to E189's two hosts. Sources:
#   LEDGER      workloads/ledger/host/main.cpp as committed (sha256 5383150f..., 46a16bd0), with ledger_args.h;
#   SPP         workloads/sparseparity/host/main.cpp as committed (faf4a30c..., unchanged since a768f840, the 29 Sep card runs');
# and FOUR NEGATIVE CONTROLS, each one line changed in a scratch copy (the kind of change a stale or wrong build would carry):
#   L-BUDGET    the ledger host's budget refusal at 9.9 s instead of 9.5 s (a host whose processes could pass 10 s);
#   L-MODEL     the ledger guard's DRAM figure at 25 GB/s instead of 20 GB/s (another host's launch model: other K arithmetic);
#   L-EXPECT    the ledger host never reads --expect (SHA-256's digests unchecked);
#   S-MARGIN    sparse parity's est_s margin x1.35 instead of x1.3 (the band's slow end moves);
# each compiled four ways against desk/include (the check of C's mock headers widened) and desk/mock_rt_e189.cpp (a device record):
#   g++-13 -O2 (GCC as on the box, at the hosts' own CMake flag), g++-13 -O3, clang++ -O1, clang++ -O2.
# On each binary: hostcheck_e189.py (ledger or spp, as the source is) with the device record on. Asserted: LEDGER and SPP read
# HOST-BEHAVIOUR OK on all four builds; every negative control reads FAIL on all four; each good host read as the other program reads
# FAIL; spp_selftest (CPU only, g++-13 -O2) reads SELFTEST PASS; NO run leaves a device-record line. Reported beside, never used: energy.sh's
# own binary grep ('launch_epoch_ms' in the sparse-parity host) on each build. E189's kit greps no binary anywhere.
#   bash tools/claims-v3/e189/desk/desktest_hosts_e189.sh <scratch dir>   (prints DESKTEST-HOSTS-E189 <n> of <m> PASS or FAIL; exit 0 or 1)
# E189_GXX and E189_CLANGXX name the compilers (default g++-13 and clang++ on PATH). Every compile runs with SDKROOT unset (the Mac's
# /usr/bin/python3 exports the unversioned SDK, against which Homebrew's GCC 13.2 fails: a desk detail) and TMPDIR in the scratch.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
D=$SRC/tools/claims-v3/e189
INC=$D/desk/include
MOCK=$D/desk/mock_rt_e189.cpp
PY=/usr/bin/python3
GXX=$(command -v "${E189_GXX:-g++-13}") || { echo "no ${E189_GXX:-g++-13} on PATH"; exit 2; }
CLX=$(command -v "${E189_CLANGXX:-clang++}") || { echo "no ${E189_CLANGXX:-clang++} on PATH"; exit 2; }
LEDGER_SHA=5383150f70d16fa5377f58aa9476e059abde541669515cd41a1126a4c2bbbfd9
SPP_SHA=faf4a30c7b9790c171ea1f9b3b4aadf63ef84f3b54484a2ba4fab29adea4af41
mkdir -p "$S"; S=$(cd "$S" && pwd)
main() {
rm -rf "${S:?}/src" "${S:?}/bin" "${S:?}/rec" "${S:?}/tmp"
mkdir -p "$S/src" "$S/bin" "$S/rec" "$S/tmp"
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
echo "compilers: $("$GXX" --version | head -n 1); $("$CLX" --version | head -n 1)"
echo "== 1. the sources and the four negative controls"
[ "$(sha "$SRC/workloads/ledger/host/main.cpp")" = "$LEDGER_SHA" ]; ok $? "the ledger host's source is the pinned 5383150f... (46a16bd0)"
[ "$(sha "$SRC/workloads/sparseparity/host/main.cpp")" = "$SPP_SHA" ]; ok $? "sparse parity's host source is the pinned faf4a30c..."
for t in ledger l-budget l-model l-expect; do mkdir -p "$S/src/$t"; cp "$SRC/workloads/ledger/host/main.cpp" "$S/src/$t/main.cpp"; done
for t in spp s-margin; do mkdir -p "$S/src/$t"; cp "$SRC/workloads/sparseparity/host/main.cpp" "$S/src/$t/main.cpp"; done
"$PY" -I -B - "$S/src" <<'PYEOF'
import sys
s = sys.argv[1]
def sub(t, a, b):
    p = f"{s}/{t}/main.cpp"
    x = open(p).read()
    assert x.count(a) == 1, (t, a)
    open(p, "w").write(x.replace(a, b))
sub("l-budget", 'if (o.budget > 9.5) usage(argv[0], "--budget at most 9.5 s");', 'if (o.budget > 9.9) usage(argv[0], "--budget at most 9.5 s");')
sub("l-model", "return double(o.bytes) * double(o.passes) * 2.0 / 20e9;", "return double(o.bytes) * double(o.passes) * 2.0 / 25e9;")
sub("l-expect", "if (!o.expect.empty()) {", "if (false) {")
sub("s-margin", "estS = modelS * (m1Kernel ? 1.15 : 1.3);", "estS = modelS * (m1Kernel ? 1.15 : 1.35);")
print("negative controls written: l-budget, l-model, l-expect, s-margin (one line each)")
PYEOF
echo
echo "== 2. four builds of each source"
nb=0; nbok=0
for t in ledger l-budget l-model l-expect spp s-margin; do
  case "$t" in ledger|l-*) I2=$SRC/workloads/ledger; X="" ;; *) I2=$SRC/workloads/sparseparity; X="-mpopcnt -pthread -I $SRC/workloads/sparseparity/host" ;; esac
  for cv in g13O2 g13O3 clangO1 clangO2; do
    case "$cv" in g13O2) CX=$GXX; O=-O2 ;; g13O3) CX=$GXX; O=-O3 ;; clangO1) CX=$CLX; O=-O1 ;; clangO2) CX=$CLX; O=-O2 ;; esac
    nb=$((nb + 1))
    if env -u SDKROOT TMPDIR="$S/tmp" nice -n 10 "$CX" -std=c++17 $O $X -w -I "$INC" -I "$I2" "$S/src/$t/main.cpp" "$MOCK" -o "$S/bin/$t-$cv" 2> "$S/bin/$t-$cv.log"; then
      nbok=$((nbok + 1))
    else echo "build failed: $t $cv"; tail -n 5 "$S/bin/$t-$cv.log"; fi
  done
done
env -u SDKROOT TMPDIR="$S/tmp" nice -n 10 "$GXX" -std=c++17 -O2 -mpopcnt -w -I "$SRC/workloads/sparseparity" "$SRC/workloads/sparseparity/host/spp_selftest.cpp" -o "$S/bin/spp_selftest" 2> "$S/bin/spp_selftest.log"
[ "$nbok" -eq "$nb" ] && [ -x "$S/bin/spp_selftest" ]; ok $? "$nbok of $nb builds and spp_selftest built"
echo
echo "== 3. the host check on every build (the device record on)"
for cv in g13O2 g13O3 clangO1 clangO2; do
  for t in ledger l-budget l-model l-expect spp s-margin; do
    case "$t" in ledger|l-*) kind=ledger ;; *) kind=spp ;; esac
    rec=$S/rec/$t-$cv.txt; : > "$rec"
    st=(); [ "$kind" = spp ] && st=(--selftest-bin "$S/bin/spp_selftest")
    out=$(cd "$SRC" && E189_DEVICE_RECORD="$rec" "$PY" -I -B "$D/hostcheck_e189.py" "$kind" "$S/bin/$t-$cv" ${st[@]+"${st[@]}"} 2>&1 | sed "s#$S#<scratch>#g")
    echo "   $t $cv: $out"
    case "$t" in
      ledger|spp) case "$out" in "HOST-BEHAVIOUR OK $kind"*) r=0 ;; *) r=1 ;; esac; ok $r "$t ($cv) reads OK" ;;
      *) case "$out" in "HOST-BEHAVIOUR FAIL $kind"*) r=0 ;; *) r=1 ;; esac; ok $r "negative control $t ($cv) reads FAIL" ;;
    esac
    [ ! -s "$rec" ]; ok $? "$t ($cv): no device call recorded"
  done
  for pair in "ledger spp" "spp ledger"; do
    set -- $pair
    rec=$S/rec/cross-$1-$cv.txt; : > "$rec"
    out=$(cd "$SRC" && E189_DEVICE_RECORD="$rec" "$PY" -I -B "$D/hostcheck_e189.py" "$2" "$S/bin/$1-$cv" 2>&1 | head -c 120)
    case "$out" in "HOST-BEHAVIOUR FAIL $2"*) r=0 ;; *) r=1 ;; esac; ok $r "the $1 host ($cv) read as the $2 program reads FAIL"
    [ ! -s "$rec" ]; ok $? "cross $1 ($cv): no device call recorded"
  done
  if [ ! -f "$S/bin/spp-$cv" ]; then g="(no binary)"; elif grep -a -q 'launch_epoch_ms' "$S/bin/spp-$cv"; then g=found; else g="NOT found"; fi
  echo "   reported only (energy.sh's binary grep, never used by this kit): 'launch_epoch_ms' $g in spp-$cv"
done
echo
echo "binaries (sha256, reported):"
for f in "$S"/bin/*; do case "$f" in *.log) ;; *) echo "  $(sha "$f")  $(basename "$f")" ;; esac; done
echo
if [ "$fail" = 0 ]; then echo "DESKTEST-HOSTS-E189 $npass of $ncase PASS"; else echo "DESKTEST-HOSTS-E189 $npass of $ncase FAIL"; fi
[ "$fail" = 0 ]
}
main
