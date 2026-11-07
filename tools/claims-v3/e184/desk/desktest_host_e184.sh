#!/usr/bin/env bash
# E184 (Q153, the kit): the desk test of the host-only change, on the Intel (never a box, never a card). It applies host_patch_e184.py to
# the committed workloads/enercat in a scratch tree, compiles the patched host/main.cpp twice with clang++ against desk/stubs/ (the
# libetrt names the host uses): -fsyntax-only -Wall, and linked with desk/mock_runtime_e184.cpp into a desk binary whose "device" is host
# memory; then it runs that binary on the desk:
#   H1 a quad's schedule (S 2, A 4, B 4, B 4, A 4 launches): 18 ENERCAT lines, segments 0-4 labelled S A B B A in order, every launch ok,
#      and the source copies carry the images' nonzero words (0 for zeros, 384 for 3 minions on 32 shires);
#   H2 the stop file present: exit 8 before any launch;  H3 an image of the wrong size: exit 1 before any launch;
#   H4 the budget (0.05 s) with 30 ms mock launches: exit 9 before the schedule ends;
#   H5 no --schedule: the catalogue's own loop, unchanged (ENERCAT lines with "operands":"zeros" and no "seg").
#   bash tools/claims-v3/e184/desk/desktest_host_e184.sh <scratch dir>       (prints "DESKTEST-HOST-E184 PASS" or FAIL; exit 0 or 1)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
D=$SRC/tools/claims-v3/e184
mkdir -p "$S"
T=$S/enercat-e184-src
fail=0
ok() { if [ "$1" -eq 0 ]; then echo "-> PASS"; else echo "-> FAIL"; fail=1; fi; }
python3 -B "$D/host_patch_e184.py" --src "$SRC/workloads/enercat" --dst "$T" | sed "s#$SRC#<repo>#g; s#$S#<scratch>#g"
echo "== H0 the patched host compiles against the stubs (-fsyntax-only -Wall) and links with the mock runtime"
clang++ -std=c++17 -fsyntax-only -Wall -Wno-unused-function -I"$D/desk/stubs" -I"$T" "$T/host/main.cpp" 2> "$S/syntax.err"; a=$?
clang++ -std=c++17 -O1 -I"$D/desk/stubs" -I"$T" "$T/host/main.cpp" "$D/desk/mock_runtime_e184.cpp" -o "$S/enercat_host_desk" 2> "$S/link.err"; b=$?
echo "syntax rc $a ($(wc -l < "$S/syntax.err") warning lines), link rc $b"
[ "$a" -eq 0 ] && [ "$b" -eq 0 ] && [ ! -s "$S/syntax.err" ]; ok $?
H=$S/enercat_host_desk
python3 -B "$D/make_images_e184.py" --write "$S/img" 32:0 32:3 > /dev/null || { echo "images failed"; exit 1; }
head -c 1000 "$S/img/m32_n003.bin" > "$S/img/short.bin"
printf 'S 2 %s\nA 4 %s\nB 4 %s\nB 4 %s\nA 4 %s\n' "$S/img/m32_n000.bin" "$S/img/m32_n000.bin" "$S/img/m32_n003.bin" "$S/img/m32_n003.bin" "$S/img/m32_n000.bin" > "$S/quad.txt"
printf 'S 2 %s\nA 4 %s\n' "$S/img/m32_n000.bin" "$S/img/short.bin" > "$S/short.txt"
rm -f "$S/STOP"
echo "desk stand-in kernel: the mock runtime never reads it" > "$S/kernel.elf"
args=(--kernel "$S/kernel.elf" --pattern fadd.ps --harts 2 --shires 0xffffffff --window 240000000 --operands zeros --budget 9.5)
echo "== H1 a quad's schedule"
E184_MOCK_LAUNCH_MS=5 "$H" "${args[@]}" --schedule "$S/quad.txt" --stop-file "$S/STOP" > "$S/h1.out" 2> "$S/h1.err"; rc=$?
python3 - "$S/h1.out" "$S/h1.err" "$rc" <<'PYEOF'
import json, sys
lines = [json.loads(l[8:]) for l in open(sys.argv[1]) if l.startswith("ENERCAT {")]
copies = [int(l.split()[3]) for l in open(sys.argv[2]) if l.startswith("MOCK sources copied")]
segs = [(x["seg"], x["label"]) for x in lines]
want = [(0, "S")] * 2 + [(1, "A")] * 4 + [(2, "B")] * 4 + [(3, "B")] * 4 + [(4, "A")] * 4
okk = (sys.argv[3] == "0" and segs == want and all(x["ok"] for x in lines) and copies[1:] == [0, 0, 384, 384, 0]
       and all(x["participants"] == 2048 and x["shires"] == 32 for x in lines) and lines[0]["image"] == "m32_n000.bin")
print("rc %s, %d lines, segments %s, copies' nonzero words %s, every launch ok %s" % (sys.argv[3], len(lines), "as planned" if segs == want else segs, copies, all(x["ok"] for x in lines)))
sys.exit(0 if okk else 1)
PYEOF
ok $?
echo "== H2 the stop file present"
: > "$S/STOP"; E184_MOCK_LAUNCH_MS=5 "$H" "${args[@]}" --schedule "$S/quad.txt" --stop-file "$S/STOP" > "$S/h2.out" 2> "$S/h2.err"; rc=$?; rm -f "$S/STOP"
n=$(grep -c '^ENERCAT' "$S/h2.out"); echo "rc $rc, $n launches, $(grep -m1 'stop file' "$S/h2.err" | sed "s#$S#<scratch>#g")"
[ "$rc" -eq 8 ] && [ "$n" -eq 0 ]; ok $?
echo "== H3 an image of the wrong size"
E184_MOCK_LAUNCH_MS=5 "$H" "${args[@]}" --schedule "$S/short.txt" > "$S/h3.out" 2> "$S/h3.err"; rc=$?
n=$(grep -c '^ENERCAT' "$S/h3.out"); echo "rc $rc, $n launches, $(grep -m1 FAIL "$S/h3.err" | sed "s#$S#<scratch>#g")"
[ "$rc" -eq 1 ] && [ "$n" -eq 0 ] && grep -q 'is not 524288 bytes' "$S/h3.err"; ok $?
echo "== H4 the budget"
E184_MOCK_LAUNCH_MS=30 "$H" "${args[@]}" --budget 0.05 --schedule "$S/quad.txt" > "$S/h4.out" 2> "$S/h4.err"; rc=$?
n=$(grep -c '^ENERCAT' "$S/h4.out"); echo "rc $rc, $n launches of 18, $(grep -m1 budget "$S/h4.err")"
[ "$rc" -eq 9 ] && [ "$n" -lt 18 ]; ok $?
echo "== H5 no --schedule: the catalogue's loop"
E184_MOCK_LAUNCH_MS=5 "$H" "${args[@]}" --seconds 0.05 > "$S/h5.out" 2> "$S/h5.err"; rc=$?
n=$(grep -c '^ENERCAT' "$S/h5.out"); s=$(grep -c '"seg"' "$S/h5.out"); z=$(grep -c '"operands":"zeros"' "$S/h5.out")
echo "rc $rc, $n launches, with seg $s, operands zeros $z"
[ "$rc" -eq 0 ] && [ "$n" -ge 1 ] && [ "$s" -eq 0 ] && [ "$z" -eq "$n" ]; ok $?
echo "DESKTEST-HOST-E184 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
