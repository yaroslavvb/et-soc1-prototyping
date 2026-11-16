#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE REAL-BUILD DESK TEST of build_e199.sh, run for real at the desk
# (aifoundry2, whose riscv toolchain is aifoundry1's "() 15.1.0": E191's kit, verify-e191k) on a stand-in E199 root holding
# boxfiles-e199.txt's files: cmake with this desk's /opt/et, nice 10, -j4, check_elf.py, E192's loop_order_e192.py on the disassembly, the
# built host's --list (no device: main.cpp returns before any device code), the hashes. Run ONLY inside W/slot.sh and W/nodev.sh (it runs a
# built host). Cases:
#   RB1 as on the card day (no override): every gate before the selection passes (check_elf "loops 16, bad 0"; loop_order 16 of 16; the
#       host's --list --json and --list byte for byte E192's arm table), then THE SELECTION fails as it must on THIS desk (aifoundry2's
#       /opt/et carries no ET_DEVICES, E191's real-build log): INTBITS-BUILD-FAILED rc=8 naming the host and the device layer;
#   RB2 with the desk-only override (RB_DESKTEST=1 E199_SELECTION_REPORT_ONLY=1): INTBITS-BUILT, BUILD-E199.txt with the hashes beside
#       E192's (reported), the selection line "NOT JUDGED", RB1's build moved aside, never removed;
#   RB3 E192's registered arm table one byte off in the stand-in root: INTBITS-BUILD-FAILED rc=6 (the --list differs);
#   RB4 the override WITHOUT RB_DESKTEST=1: the selection judged (rc=8) - the override is the desk's alone;
#   RB5 the box check (boxcheck_e199.sh) on the RB2 build reads its host's selection NOT JUDGED only under the override, and fails
#       without it (on this desk; on aifoundry1 the host carries ET_DEVICES).
#   bash W/slot.sh bash W/nodev.sh bash tools/claims-v3/e199/desk/realbuild_e199.sh <an empty scratch dir outside the repo>
# Prints REALBUILD-E199 <n> of <m> PASS (exit 0) or FAIL. SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for d in /dev/et*; do [ -e "$d" ] || continue; if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi; done
mkdir -p "$S" && S=$(cd "$S" && pwd -P); [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
E=tools/claims-v3/e199
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
mkroot() {  # mkroot <dir>: a stand-in E199 root holding the sync list's files at their repository paths
  local p
  while IFS= read -r p; do case "$p" in ''|'#'*) continue ;; esac; [ -f "$SRC/$p" ] || continue; mkdir -p "$1/$(dirname "$p")"; cp -p "$SRC/$p" "$1/$p"; done < "$SRC/$E/boxfiles-e199.txt"
}
echo "E199 real-build desk test (kit-e199), $(TZ=America/Los_Angeles date '+%F %T %Z'); $(g++ --version | head -n 1); $(cmake --version | head -n 1); $(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1); /usr/bin/python3 $(/usr/bin/python3 -V 2>&1 | cut -d' ' -f2); /dev/et*: $(ls /dev/et* 2>/dev/null | wc -l)"
R1=$S/root; mkroot "$R1"
echo; echo "== RB1 as on the card day"
( unset RB_DESKTEST E199_SELECTION_REPORT_ONLY; bash "$R1/$E/build_e199.sh" ) > "$S/rb1.txt" 2>&1; r1=$?
grep -E '^(COMPILER|loops|INTBITS|SELECTION)' "$S/rb1.txt" | cut -c1-220
B=$R1/build/intbits
ok "$r1.$(has 'INTBITS-BUILD-FAILED rc=8: the selection: the host carries no ET_DEVICES' "$S/rb1.txt").$(grep -cx 'loops 16, bad 0' "$B/check_elf.txt").$(tail -n 1 "$B/loop_order.txt" | grep -c '^loops 16; forms x ops found 16 of 16; missing none; duplicated none; unexpected none; bad 0$').$(cmp -s "$B/arm-table.jsonl" "$SRC/tools/claims-v3/e192/desk/arm-table-e192.jsonl" && cmp -s "$B/arm-table.txt" "$SRC/tools/claims-v3/e192/desk/arm-table-e192.txt" && echo 1)" \
  "16.1.1.1.1" "RB1 every gate before the selection passes on the real build (check_elf, loop_order 16 of 16, E192's arm table byte for byte); the selection fails on this desk (rc=8)"
echo; echo "== RB2 the desk-only override"
( export RB_DESKTEST=1 E199_SELECTION_REPORT_ONLY=1; bash "$R1/$E/build_e199.sh" ) > "$S/rb2.txt" 2>&1; r2=$?
grep -E '^(kernel_|host_|same_as|loop_order|selection|INTBITS)' "$S/rb2.txt" | cut -c1-200
ok "$r2.$(has 'INTBITS-BUILT rc=0' "$S/rb2.txt").$(has '^selection NOT JUDGED' "$S/rb2.txt").$(ls -d "$R1"/build/intbits.before-* 2>/dev/null | wc -l | tr -d ' ').$(has '^kernel_text_sha256 ' "$R1/build/intbits/BUILD-E199.txt")" \
  "0.1.1.1.1" "RB2 INTBITS-BUILT with the hashes recorded beside E192's, the selection NOT JUDGED, RB1's build moved aside (never removed)"
echo "   reported, never judged: $(grep -E '^same_as' "$R1/build/intbits/BUILD-E199.txt" | tr '\n' ' ')"
echo; echo "== RB3 E192's arm table one byte off"
R3=$S/root3; mkroot "$R3"; printf ' ' >> "$R3/tools/claims-v3/e192/desk/arm-table-e192.txt"
( export RB_DESKTEST=1 E199_SELECTION_REPORT_ONLY=1; bash "$R3/$E/build_e199.sh" ) > "$S/rb3.txt" 2>&1; r3=$?
ok "$r3.$(has "INTBITS-BUILD-FAILED rc=6: the host's --list differs from E192's registered arm table" "$S/rb3.txt")" "16.1" "RB3 the --list against a changed table: rc=6"
echo; echo "== RB4 the override without RB_DESKTEST=1"
( unset RB_DESKTEST; export E199_SELECTION_REPORT_ONLY=1; bash "$R1/$E/build_e199.sh" ) > "$S/rb4.txt" 2>&1; r4=$?
ok "$r4.$(has 'INTBITS-BUILD-FAILED rc=8: the selection' "$S/rb4.txt")" "16.1" "RB4 E199_SELECTION_REPORT_ONLY alone does nothing: the selection judged, rc=8"
echo; echo "== RB5 the box check's selection line on the desk build"
( export RB_DESKTEST=1 E199_SELECTION_REPORT_ONLY=1; cd "$R1" && bash "$E/boxcheck_e199.sh" ) > "$S/rb5a.txt" 2>&1
( unset RB_DESKTEST E199_SELECTION_REPORT_ONLY; cd "$R1" && bash "$E/boxcheck_e199.sh" ) > "$S/rb5b.txt" 2>&1
grep -E '^selection:' "$S/rb5a.txt" "$S/rb5b.txt" | cut -c1-200
ok "$(has 'no(NOT JUDGED' "$S/rb5a.txt").$(has 'intbits_host carries no ET_DEVICES' "$S/rb5b.txt")" "1.1" "RB5 the box check: the desk's built host NOT JUDGED only under the override; judged (a failure) without it"
echo; echo "REALBUILD-E199 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
