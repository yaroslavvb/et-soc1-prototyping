#!/usr/bin/env bash
# E198's kit after dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): THE BUILD ON aifoundry1, in E198's root,
# against the box's own /opt/et. It is build_e198.sh (kit-e198, Q191; unchanged beside it, not run for E198 after A1) with three changes
# and no other: the harness read is harness-e198-a1.json (harness_e198a1.py); THE LISTING (item 6) is the lab's runner copy's own --dry
# (run_x04_e198a1.py, given E193's arms.tsv by --arms as the session gives it) against E193's registered listings by check_e198a1.py drycmp
# (check_e198.py's five exact mappings and A1's sixth, `timeout 10` for `timeout -k 1 10`; the listing must name no `timeout -k`); and the
# build record gains the line "a1 build_e198a1.sh", which session_e198a1.sh requires. Step 6 (rb/s08_a1_build_e198a1.sh) runs it as a
# detached job under a plain `timeout 900` (never `timeout -k`), at most two starts a Pacific day. From E198's root:
#   1. the harness at its pins; the compilers named (cmake, the riscv gcc: aifoundry1's reads "() 15.1.0", the host c++, python);
#   2. cmake -S <E193's proposal/src> -B build/x04clock with CMAKE_PREFIX_PATH=/opt/et, then the build (-j4, nice 10);
#   3. THE KERNEL GATE (E198.md 13): the kernel's .text (objcopy) must be E193's registered one, fd7207275661... (68,358 B), else no sitting;
#   4. the bodies check (E193's desk/bodies_e193.py, 30 of 30), a gate;
#   5. the host's behaviour: three refusals before the device layer (ET_DEVICES=99, an unreadable kernel; plain `timeout 10`), a gate;
#   6. THE LISTING (A1's): smoke, A and B, a gate;
#   7. E191's ET_DEVICES reading of the host, REPORTED;
#   8. the box's tree files at the pins harness-e198-a1.json names (a gate), and the record build/x04clock-built.txt: X04-BUILT, the hashes,
#      "a1 build_e198a1.sh".
# Prints COMPILER/ELF/BODIES/HOST/LISTING/ETDEVICES/READER lines and X04-BUILT rc=0, or X04-BUILD-FAILED <why> (exit 1).
#   bash <tree>/build/claims-v3/aifoundry1/e198/tools/claims-v3/e198/build_e198a1.sh
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
KIT=$RR/tools/claims-v3/e198
E193K=$RR/tools/claims-v3/e193
SRC=$E193K/proposal/src
B=$RR/build/x04clock
BUILT=$RR/build/x04clock-built.txt
X=/opt/et/bin
H=$B/host/x04clock_host
K=$B/kernel/x04clock.elf
WRAP=$KIT/x04host_e198.sh
HC=$KIT/holdercheck_e198.sh
DESK_ELF=01a3776755f5c684f5a71a38f13a550ea8c4aae5658c46cb003f846aea71b531
REG_TEXT=fd7207275661c23f33a99dd2a1c16b54e92e09b75cdb828258b09849ee9d643e
REG_TEXT_B=68358
REQ_ELF=bd5770bab12f2b39379960b434af2dfe5cf46f2e75278a26580d5694c03be2ec
fail() { echo "X04-BUILD-FAILED $*"; exit 1; }
echo "E198 build (A1, the lab's runner copy) on $(hostname), $(TZ=America/Los_Angeles date '+%F %T %Z'), root $RR"
mkdir -p "$RR/build" || fail "cannot make $RR/build"
rm -f "$BUILT"
python3 -I -B "$KIT/harness_e198a1.py" --box --root "$RR" | tail -n 1
python3 -I -B "$KIT/harness_e198a1.py" --box --root "$RR" > /dev/null || fail "the harness: a synced file is not at its pin"
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
th=$(sha256sum "$T" | cut -d' ' -f1); tb=$(stat -c %s "$T")
echo "ELF kernel sha256 $kh: $([ "$kh" = "$DESK_ELF" ] && echo SAME AS || echo DIFFERENT FROM) E193's desk build's, $([ "$kh" = "$REQ_ELF" ] && echo SAME AS || echo DIFFERENT FROM) request.md's (reported, never a gate)"
echo "ELF .text sha256 $th ($tb B): $([ "$th" = "$REG_TEXT" ] && echo SAME AS || echo DIFFERENT FROM) E193's registered .text (${REG_TEXT:0:12}..., $REG_TEXT_B B): the kernel gate"
[ "$th" = "$REG_TEXT" ] && [ "$tb" = "$REG_TEXT_B" ] || fail "THE KERNEL GATE: the kernel's .text is not E193's registered one: no sitting (E198.md 13)"
echo "ELF path strings in the kernel: $(strings -a "$K" | grep -c -E '/home/|/tmp/|/Users/')"
python3 -I -B "$E193K/desk/bodies_e193.py" "$X/riscv64-unknown-elf-objdump" "$K" "$SRC/gen_blocks.py" > "$RR/build/bodies-check.txt" 2>&1
grep -E '^BODIES CHECK' "$RR/build/bodies-check.txt"
grep -q '^BODIES CHECK PASS' "$RR/build/bodies-check.txt" || fail "the bodies check (build/bodies-check.txt): no sitting (E198.md 13)"
hr() {  # hr <want rc> <want stderr text> <args after --kernel>: a refusal before the device layer
  local want=$1 text=$2 out rc; shift 2
  out=$(env ET_DEVICES=99 LD_LIBRARY_PATH=/opt/et/lib timeout 10 "$H" --kernel /nonexistent-e198/x04clock.elf "$@" 2>&1 > /dev/null)
  rc=$?
  local what="--kernel <unreadable> ${*:-(alone)}"
  if [ "$rc" -eq "$want" ] && printf '%s\n' "$out" | grep -qF -- "$text"; then echo "HOST-REFUSAL ok: $what -> exit $rc, '$text'"; return 0; fi
  echo "HOST-REFUSAL FAILED: $what -> exit $rc (want $want), stderr: $(printf '%s' "$out" | tr '\n' ' ' | cut -c1-200)"; return 1
}
hb=0
hr 1 "FAIL: --budget must be in (0, 9.5] seconds" --budget 9.6 || hb=1
hr 2 "unknown option --no-such-option" --no-such-option || hb=1
hr 1 "FAIL: cannot read kernel /nonexistent-e198/x04clock.elf" || hb=1
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
  python3 -I -B "$KIT/run_x04_e198a1.py" "$LD/$name" --arms "$SRC/arms.tsv" --host "$WRAP" --holder-check "$HC" --dry $opts --device 1 > "$LD/$name.txt" 2>&1
  python3 -I -B "$KIT/check_e198a1.py" drycmp "$LD/$name.txt" "$E193K/desk/$reg" --host "$WRAP" --holder-check "$HC" || lb=1
done
[ "$lb" -eq 0 ] || fail "the listing differs from E193's registered one (the lines above): no sitting (E198.md 13)"
echo "ETDEVICES $(bash "$RR/tools/claims-v3/e191/etdevices_e191.sh" "$H" "$B/CMakeCache.txt") (reported)"
[ -x build/ettelem/ettelem ] || fail "the box's reader build/ettelem/ettelem is missing or not executable"
python3 -I -B "$KIT/harness_e198a1.py" --tree --root "$RR" > "$RR/build/tree-check.txt" 2>&1
grep -q '^TREE OK: ' "$RR/build/tree-check.txt" || fail "the box's tree files are not at their pins (the reader, E191's guard): $(tail -n 1 "$RR/build/tree-check.txt" | cut -c1-160)"
sh=$(sha256sum build/ettelem/ettelem | cut -d' ' -f1)
hh=$(sha256sum "$H" | cut -d' ' -f1)
echo "READER build/ettelem/ettelem sha256 $sh, at its pin in harness-e198-a1.json's tree (not run here); $(cut -c1-160 "$RR/build/tree-check.txt")"
echo "HOST x04clock_host sha256 $hh"
{ echo "X04-BUILT $(TZ=America/Los_Angeles date '+%F %T %Z')"; echo "kernel $kh"; echo "text $th"; echo "host $hh"; echo "reader $sh"; echo "a1 build_e198a1.sh"; } > "$BUILT"
echo "X04-BUILT rc=0"
