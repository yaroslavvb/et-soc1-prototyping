#!/usr/bin/env bash
# E183 (Q155, the kit): the desk test of the host-only change, on the Intel (never a box, never a card). It builds E180's tree with E180's
# own generator (gen_acc_e180.py, unchanged) in a scratch directory, applies patch_host_e183.py to that tree's host/main.cpp, compiles the
# patched host twice with clang++ against E184's desk stubs (tools/claims-v3/e184/desk/stubs, unchanged): -fsyntax-only -Wall, and linked
# with desk/mock_runtime_e183.cpp into a desk binary whose "device" is host memory; then it runs that binary:
#   H1 a train SFFS of 13 launches (F e80j6, S const): 13 ENERCAT lines, train_kind S, then S F F S three times, launch 0..12, each
#      launch's source word (the mock's MOCK launch line) its kind's own word, train_operands its kind's image, every launch ok;
#   H2 the same train FSSF: F, then F S S F three times;
#   H3 no --launches: exit 1 before any launch;  H4 --abba SFSF: exit 1;  H5 --operands random with --operands-b: exit 1;
#   H6 an S image of the wrong size: exit 1 before any launch (the host's own "needs exactly 256 bytes");
#   H7 no --operands-b: the catalogue's own loop, unchanged (no train field; every launch runs the --operands image);
#   H8 the budget (0.05 s) with 30 ms mock launches: the train is cut short, exit 3, fewer than 13 records, its stderr line.
#   bash tools/claims-v3/e183/desk/desktest_host_e183.sh <scratch dir>     (prints "DESKTEST-HOST-E183 PASS" or FAIL; exit 0 or 1)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
D=$SRC/tools/claims-v3/e183
STUBS=$SRC/tools/claims-v3/e184/desk/stubs
PY=/usr/bin/python3
mkdir -p "$S"
T=$S/enercat-e183-src
rm -rf "$T"
fail=0
ok() { if [ "$1" -eq 0 ]; then echo "-> PASS"; else echo "-> FAIL"; fail=1; fi; }
$PY -B "$SRC/tools/claims-v3/e180/gen_acc_e180.py" --src "$SRC/workloads/enercat" --dst "$T" > /dev/null || { echo "gen_acc_e180.py failed"; exit 1; }
$PY -B "$D/patch_host_e183.py" "$T/host/main.cpp" | sed "s#$SRC#<repo>#g; s#$S#<scratch>#g"
echo "== H0 the patched host compiles against E184's stubs (-fsyntax-only -Wall) and links with the mock runtime"
clang++ -std=c++17 -fsyntax-only -Wall -Wno-unused-function -I"$STUBS" -I"$T" "$T/host/main.cpp" 2> "$S/syntax.err"; a=$?
clang++ -std=c++17 -O1 -I"$STUBS" -I"$T" "$T/host/main.cpp" "$D/desk/mock_runtime_e183.cpp" -o "$S/enercat_host_desk" 2> "$S/link.err"; b=$?
echo "syntax rc $a ($(wc -l < "$S/syntax.err" | tr -d ' ') warning lines), link rc $b"
[ "$a" -eq 0 ] && [ "$b" -eq 0 ] && [ ! -s "$S/syntax.err" ]; ok $?
H=$S/enercat_host_desk
F=$SRC/tools/claims-v3/e183/images/e80j6.bin
SI=$SRC/tools/claims-v3/e183/images/const.bin
head -c 200 "$SI" > "$S/short.bin"
echo "desk stand-in kernel: the mock runtime never reads it" > "$S/kernel.elf"
base=(--kernel "$S/kernel.elf" --pattern fadd.ps --harts 2 --shires 0xffffffff --window 240000000 --budget 9.5)
check_train() {  # check_train <out> <err> <rc> <orientation> <F word> <S word>
  $PY - "$@" <<'PYEOF'
import json, sys
out, err, rc, ori, fw, sw = sys.argv[1:7]
lines = [json.loads(l[8:]) for l in open(out) if l.startswith("ENERCAT {")]
words = [l.split()[-1] for l in open(err) if l.startswith("MOCK launch sources word0")]
want = [ori[0] if k < 1 else ori[(k - 1) % 4] for k in range(13)]
kinds = [x.get("train_kind") for x in lines]
okw = all(w == (fw if k == "F" else sw) for w, k in zip(words, want)) and len(words) == 13
oko = all(x.get("train_operands", "").endswith("e80j6.bin" if k == "F" else "const.bin") for x, k in zip(lines, want))
okl = [x.get("launch") for x in lines] == list(range(13)) and all(x.get("abba") == ori for x in lines)
good = rc == "0" and len(lines) == 13 and kinds == want and okw and oko and okl and all(x["ok"] for x in lines)
print("rc %s, %d lines, kinds %s, source words by kind %s, operands by kind %s, launch numbers %s, every launch ok %s" % (
    rc, len(lines), "".join(k or "-" for k in kinds), "right" if okw else words, "right" if oko else "WRONG", "right" if okl else "WRONG",
    all(x["ok"] for x in lines)))
sys.exit(0 if good else 1)
PYEOF
}
echo "== H1 a train, SFFS, 13 launches"
E183_MOCK_LAUNCH_MS=5 "$H" "${base[@]}" --operands "file:$F" --operands-b "file:$SI" --abba SFFS --launches 13 --seconds 30 > "$S/h1.out" 2> "$S/h1.err"; rc=$?
check_train "$S/h1.out" "$S/h1.err" "$rc" SFFS 407e0000 3f800000; ok $?
echo "== H2 the same train, FSSF"
E183_MOCK_LAUNCH_MS=5 "$H" "${base[@]}" --operands "file:$F" --operands-b "file:$SI" --abba FSSF --launches 13 --seconds 30 > "$S/h2.out" 2> "$S/h2.err"; rc=$?
check_train "$S/h2.out" "$S/h2.err" "$rc" FSSF 407e0000 3f800000; ok $?
refusal() {  # refusal <case> <want rc> <stderr text> <args...>
  local c=$1 want=$2 txt=$3; shift 3
  E183_MOCK_LAUNCH_MS=5 "$H" "${base[@]}" "$@" > "$S/$c.out" 2> "$S/$c.err"; local rc=$?
  local n; n=$(grep -c '^ENERCAT' "$S/$c.out")
  echo "rc $rc, $n launches, $(grep -m1 -E 'FAIL|E183' "$S/$c.err" | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g")"
  [ "$rc" -eq "$want" ] && [ "$n" -eq 0 ] && grep -q -- "$txt" "$S/$c.err"
}
echo "== H3 no --launches"
refusal h3 1 'a train needs --launches' --operands "file:$F" --operands-b "file:$SI" --abba SFFS --seconds 30; ok $?
echo "== H4 a bad orientation"
refusal h4 1 'is SFFS or FSSF' --operands "file:$F" --operands-b "file:$SI" --abba SFSF --launches 13 --seconds 30; ok $?
echo "== H5 a built-in fill with --operands-b"
refusal h5 1 'takes --operands file: and --operands-b file:' --operands random --operands-b "file:$SI" --abba SFFS --launches 13 --seconds 30; ok $?
echo "== H6 an S image of the wrong size"
refusal h6 1 'needs exactly 256 bytes' --operands "file:$F" --operands-b "file:$S/short.bin" --abba SFFS --launches 13 --seconds 30; ok $?
echo "== H7 no --operands-b: the catalogue's own loop"
E183_MOCK_LAUNCH_MS=5 "$H" "${base[@]}" --operands "file:$F" --seconds 0.05 > "$S/h7.out" 2> "$S/h7.err"; rc=$?
n=$(grep -c '^ENERCAT' "$S/h7.out"); t=$(grep -c 'train_kind' "$S/h7.out"); w=$(grep -c 'MOCK launch sources word0 407e0000' "$S/h7.err")
echo "rc $rc, $n launches, with a train field $t, running the --operands image $w"
[ "$rc" -eq 0 ] && [ "$n" -ge 1 ] && [ "$t" -eq 0 ] && [ "$w" -eq "$n" ]; ok $?
echo "== H8 the budget cuts a train short"
E183_MOCK_LAUNCH_MS=30 "$H" "${base[@]}" --budget 0.05 --operands "file:$F" --operands-b "file:$SI" --abba SFFS --launches 13 --seconds 30 > "$S/h8.out" 2> "$S/h8.err"; rc=$?
n=$(grep -c '^ENERCAT' "$S/h8.out"); echo "rc $rc, $n launches of 13, $(grep -m1 'E183: the train ended' "$S/h8.err")"
[ "$rc" -eq 3 ] && [ "$n" -lt 13 ] && grep -q 'E183: the train ended after' "$S/h8.err"; ok $?
echo "DESKTEST-HOST-E183 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
