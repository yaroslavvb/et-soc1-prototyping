#!/usr/bin/env bash
# E193 (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): THE BUILD ON THE BOX, run by step 6 (rb/s08_a3_build_e193.sh) as
# k6's detached job under `timeout -k 15 900`, from E193's root on aifoundry3 (<tree>/build/claims-v3/aifoundry3/e193, the synced files
# at their repository paths). It never opens a device, takes no card lock and sends no device command:
#   1. the harness: every synced file at its pin (harness_e193.py --box), the registration's 29 among them;
#   2. the toolchain's versions (cmake, the RISC-V gcc, the host's c++), then the proposal's own build, as its README and E193.md 16.3
#      give it: `cmake -S proposal/src -B build/x04clock -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev`, `cmake --build build/x04clock -j4`, nice
#      10, into E193's root only (a new start removes build/x04clock first; nothing is written into proposal/src);
#   3. THE ELF CHECKS: the kernel ELF's and its .text's sha256 beside the desk build's (E193.md 16.5: 01a37767..., fd720727...) and
#      request.md's (bd5770ba...): reported SAME or DIFFERENT, never a gate (E193.md 14: "compare watts only within one build");
#      path strings in the kernel ELF counted; THE BODIES CHECK (desk/bodies_e193.py with the box's own objdump: 30 of 30 bodies slot for
#      slot, the sleds, the divide chain, the aligned counter reads): BODIES CHECK PASS, else no sitting (E193.md 11);
#   4. THE HOST READ BY ITS BEHAVIOUR, each call refused BEFORE the device layer by two barriers or more (an unreadable --kernel, and
#      ET_DEVICES=99 so that checkOneCard would refuse even if the parse let it through): --budget 9.6 (exit 1, "--budget must be in
#      (0, 9.5] seconds"), an unknown option (exit 2, "unknown option"), and the unreadable kernel alone (exit 1, "cannot read kernel");
#   5. THE HOST'S LISTING AGAINST THE REGISTRATION'S TABLE: the runner's --dry with this host's path (it opens nothing) for the smoke
#      (--smoke --blocks S,D,W,T,C), session A (--blocks S,D,W,T) and session B (--blocks C), each equal, byte for byte with the host's
#      path written as the registration's, to desk/dry-e193-smoke-all.txt, -A.txt and -B.txt, the listings E193.md 16.6 checked cell by
#      cell against the arm table (check_e193.py drycmp: LISTING SAME); else no sitting;
#   6. the sampler the session uses, <tree>/build/ettelem/ettelem (the box's own build, every aifoundry3 kit's, through E128's guard):
#      present and executable, its sha256 recorded (never run here);
#   7. on every gate passed: build/x04clock-built.txt (X04-BUILT, the kernel's, .text's, host's and sampler's sha256), which the session
#      checks its binaries against; a start that fails removes the last record first, so no session runs on a failed start's binaries.
# Prints COMPILER / ELF / BODIES / HOST-BEHAVIOUR / LISTING lines, then X04-BUILT rc=0, or X04-BUILD-FAILED <why> (exit 1).
#   bash <R>/tools/claims-v3/e193/build_e193.sh
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
KIT=$RR/tools/claims-v3/e193
SRC=$KIT/proposal/src
B=$RR/build/x04clock
BUILT=$RR/build/x04clock-built.txt
X=/opt/et/bin
H=$B/host/x04clock_host
K=$B/kernel/x04clock.elf
DESK_ELF=01a3776755f5c684f5a71a38f13a550ea8c4aae5658c46cb003f846aea71b531
DESK_TEXT=fd7207275661c23f33a99dd2a1c16b54e92e09b75cdb828258b09849ee9d643e
REQ_ELF=bd5770bab12f2b39379960b434af2dfe5cf46f2e75278a26580d5694c03be2ec
fail() { echo "X04-BUILD-FAILED $*"; exit 1; }
echo "E193 build on $(hostname), $(TZ=America/Los_Angeles date '+%F %T %Z'), root $RR"
mkdir -p "$RR/build" || fail "cannot make $RR/build"
rm -f "$BUILT"
python3 -I -B "$KIT/harness_e193.py" --box --root "$RR" | tail -n 1
python3 -I -B "$KIT/harness_e193.py" --box --root "$RR" > /dev/null || fail "the harness: a synced file is not at its pin"
echo "COMPILER cmake: $(cmake --version 2>&1 | head -n 1)"
echo "COMPILER riscv gcc: $("$X/riscv64-unknown-elf-gcc" --version 2>&1 | head -n 1)"
echo "COMPILER host c++: $(c++ --version 2>&1 | head -n 1)"
echo "COMPILER $(python3 --version 2>&1)"
[ -d "$B" ] && rm -rf "${R:?}/build/x04clock"
nice -n 10 cmake -S "$SRC" -B "$B" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > "$RR/build/cmake-configure.txt" 2>&1 || fail "cmake configure (build/cmake-configure.txt)"
nice -n 10 cmake --build "$B" -j4 > "$RR/build/cmake-build.txt" 2>&1 || fail "cmake build (build/cmake-build.txt)"
echo "COMPILER warnings in the build's output: $(grep -c 'warning:' "$RR/build/cmake-build.txt")"
[ -f "$K" ] || fail "no kernel ELF at $K"
[ -x "$H" ] || fail "no host at $H"
kh=$(sha256sum "$K" | cut -d' ' -f1)
T=$RR/build/x04clock-text.bin
"$X/riscv64-unknown-elf-objcopy" -O binary --only-section=.text "$K" "$T" || fail "objcopy of .text"
th=$(sha256sum "$T" | cut -d' ' -f1)
echo "ELF kernel sha256 $kh: $([ "$kh" = "$DESK_ELF" ] && echo SAME AS || echo DIFFERENT FROM) the desk build's (E193.md 16.5), $([ "$kh" = "$REQ_ELF" ] && echo SAME AS || echo DIFFERENT FROM) request.md's (reported, never a gate)"
echo "ELF .text sha256 $th ($(stat -c %s "$T") B): $([ "$th" = "$DESK_TEXT" ] && echo SAME AS || echo DIFFERENT FROM) the desk build's .text (reported, never a gate)"
echo "ELF path strings in the kernel: $(strings -a "$K" | grep -c -E '/home/|/tmp/|/Users/')"
python3 -I -B "$KIT/desk/bodies_e193.py" "$X/riscv64-unknown-elf-objdump" "$K" "$SRC/gen_blocks.py" > "$RR/build/bodies-check.txt" 2>&1
grep -E '^BODIES CHECK' "$RR/build/bodies-check.txt"
grep -q '^BODIES CHECK PASS' "$RR/build/bodies-check.txt" || fail "the bodies check (build/bodies-check.txt): no sitting (E193.md 11)"
hr() {  # hr <want rc> <want stderr text> <args after --kernel>: a refusal before the device layer
  local want=$1 text=$2 out rc; shift 2
  out=$(env ET_DEVICES=99 LD_LIBRARY_PATH=/opt/et/lib timeout -k 1 10 "$H" --kernel /nonexistent-e193/x04clock.elf "$@" 2>&1 > /dev/null)
  rc=$?
  local what="--kernel <unreadable> ${*:-(alone)}"
  if [ "$rc" -eq "$want" ] && printf '%s\n' "$out" | grep -qF -- "$text"; then echo "HOST-REFUSAL ok: $what -> exit $rc, '$text'"; return 0; fi
  echo "HOST-REFUSAL FAILED: $what -> exit $rc (want $want), stderr: $(printf '%s' "$out" | tr '\n' ' ' | cut -c1-200)"; return 1
}
hb=0
hr 1 "FAIL: --budget must be in (0, 9.5] seconds" --budget 9.6 || hb=1
hr 2 "unknown option --no-such-option" --no-such-option || hb=1
hr 1 "FAIL: cannot read kernel /nonexistent-e193/x04clock.elf" || hb=1
[ "$hb" -eq 0 ] || fail "the host's behaviour: a refusal did not read as built (the lines above)"
echo "HOST-BEHAVIOUR OK: three refusals before the device layer, as main.cpp writes them"
LD=$RR/build/listing-$(date +%s)
mkdir -p "$LD" || fail "cannot make $LD"
lb=0
for spec in "smoke|--smoke --blocks S,D,W,T,C|dry-e193-smoke-all.txt" "A|--blocks S,D,W,T|dry-e193-A.txt" "B|--blocks C|dry-e193-B.txt"; do
  IFS='|' read -r name opts reg <<EOF
$spec
EOF
  # shellcheck disable=SC2086
  python3 -I -B "$SRC/run_x04.py" "$LD/$name" --host "$H" --dry $opts --device 0 > "$LD/$name.txt" 2>&1
  python3 -I -B "$KIT/check_e193.py" drycmp "$LD/$name.txt" "$KIT/desk/$reg" --host "$H" || lb=1
done
[ "$lb" -eq 0 ] || fail "the host's listing differs from the registration's (the lines above): no sitting (E193.md 11)"
[ -x build/ettelem/ettelem ] || fail "the box's sampler build/ettelem/ettelem is missing or not executable"
sh=$(sha256sum build/ettelem/ettelem | cut -d' ' -f1)
hh=$(sha256sum "$H" | cut -d' ' -f1)
echo "SAMPLER the box's build/ettelem/ettelem, sha256 $sh (not run here)"
echo "HOST x04clock_host sha256 $hh"
{ echo "X04-BUILT $(TZ=America/Los_Angeles date '+%F %T %Z')"; echo "kernel $kh"; echo "text $th"; echo "host $hh"; echo "sampler $sh"; } > "$BUILT"
echo "X04-BUILT rc=0"
