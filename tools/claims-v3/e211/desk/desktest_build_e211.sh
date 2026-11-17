#!/usr/bin/env bash
# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum): the build's desk test on this desk's REAL toolchain (GCC 15.1.0 "()" for
# the kernel, the desk's c++ and cmake, its /opt/et), E206's desk/desktest_build_e206.sh form with THE KERNEL GATE's cases, as E207's kit
# ported it (Q199), for E211's one box and its two kernels.
# Each case runs build_e211.sh, check_e211.py, the guard or the runner in a stand-in tree (the harness's files copied byte for byte) under
# bubblewrap with a box's hostname (a private UTS namespace). Run it ONLY inside the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh
# on aifoundry2): the built hosts' refusals run there (in the build's own sandbox), and case B8 runs the real runner, which must stop at its
# box check. Cases:
#   B1 on aifoundry3 (hostname aifoundry3): BUILT; THE KERNEL GATE (the registration's ident_e211.gate) reads KERNEL OK on both desk ELFs,
#      rgm136's aace138c... (.text 61315bf6...) and rgm211's 00402801... (.text 82c79807...); the hosts' twelve refusals, each before the
#      device stage, in a sandbox with no device node; the record (builder build_e211.sh, box aifoundry3, both gates' lines, ET_DEVICES not
#      a gate)
#   B2 on aifoundry1 (hostname aifoundry1): refused before anything is built (E211 builds on aifoundry3 only), the record BUILD-FAILED
#   B3 a changed rgm136 source, and B3b a changed rgm211 source: each refused before the build (the sources are not harness-e211.json's)
#   B4 THE KERNEL GATE on aifoundry3's form: each of B1's ELFs with its .comment rewritten to aifoundry3's riscv gcc string "GCC: (g1b306039a)
#      15.1.0" (a section the card never loads; this lane's real build there, Tue 17 Nov 2026 00:25 PST, logs/a3-build-e211.txt, read the
#      same): its whole ELF differs from the desk build's, its .text and its loadable identity do not: KERNEL OK (rgm136 649d4079...,
#      rgm211 1351a569...)
#   B5 one byte of rgm211's .rodata changed (in the PT_LOAD segment, outside .text): the .text is the pinned one but the loadable identity
#      differs: KERNEL FAILED                B6 one byte of rgm211's .text changed: KERNEL FAILED (.text)
#   B6b THE WRONG KERNEL: rgm136's ELF given as rgm211's, and rgm211's as rgm136's: KERNEL FAILED (".text is rgm136's" / "rgm211's")
#   B7 on another box (hostname aifoundry2): refused before anything is built
#   B8 the runner (no --dry) on B1's tree under aifoundry3: its box check passes the build record, both kernels and both hosts and stops at
#      the reader's pin (the stand-in tree has no reader there): "refused, no device opened"
#   B9 the guard: under aifoundry1 and aifoundry2 refused (97) before the reader opens; on aifoundry3 with ET_DEVICES set, refused; `sample
#      --reset-ms` (the statistics reset) refused
#   bash tools/claims-v3/e211/desk/desktest_build_e211.sh <an empty scratch dir outside the repo> > logs/desktest-build-e211.txt
# The last line: DESKTEST-BUILD-E211 <n> of <m> PASS (or FAIL). SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E=$(cd "$D/.." && pwd)
REPO=$(cd "$E/../../.." && pwd)
S=${1:?an empty scratch directory outside the repository}
case "$S" in "$REPO"|"$REPO"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "$S is not empty"; exit 2; }
OC=/opt/et/bin/riscv64-unknown-elf-objcopy
echo "desktest_build_e211: $(date '+%F %T %Z'); riscv gcc: $(/opt/et/bin/riscv64-unknown-elf-gcc --version | head -n 1); c++: $(c++ --version | head -n 1); $(cmake --version | head -n 1); python3 $(/usr/bin/python3 --version 2>&1)"
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = "$2" ]; then n=$((n + 1)); echo "-> $3: PASS"; else echo "-> $3: FAIL (got $1, want $2)"; fi; }
tree() {  # tree <name>: a stand-in box tree with the harness's files
  local T=$S/$1 f
  mkdir -p "$T"
  for f in $(/usr/bin/python3 -I -B "$E/check_e211.py" --list) tools/claims-v3/e211/harness-e211.json; do
    mkdir -p "$T/$(dirname "$f")"; cp -p "$REPO/$f" "$T/$f"
  done
  echo "$T"
}
inbox() { local h=$1; shift; /usr/bin/bwrap --dev-bind / / --unshare-uts --hostname "$h" --die-with-parent -- "$@"; }
echo; echo "== B1 on aifoundry3 (its hostname): the real build"
TA=$(tree a3)
inbox aifoundry3 bash "$TA/tools/claims-v3/e211/build_e211.sh" > "$S/b1.txt" 2>&1; rc=$?
grep -E '^(COMPILER|KERNEL|HOST|HOSTCHECK|ETDEVICES|RGM)' "$S/b1.txt" | cut -c1-200
r=$(/usr/bin/python3 -I -B - "$TA/build/e211rgm/BUILD-e211.json" <<'PY'
import json, sys
j = json.load(open(sys.argv[1]))
k = j.get("kernels") or {}
print(j.get("verdict"), j.get("builder"), j.get("box"), (k.get("rgm136") or {}).get("kernel_sha256", "")[:12], (k.get("rgm211") or {}).get("kernel_sha256", "")[:12], (k.get("rgm136") or {}).get("kernel_gate", "")[:9], (k.get("rgm211") or {}).get("kernel_gate", "")[:9], "notagate" if "not a gate on aifoundry3" in j.get("et_devices", "") else "GATE", len([c for c in j.get("host_checks", []) if c.endswith(":ok")]))
PY
)
echo "record: $r"
ok "$rc|$r" "0|BUILT build_e211.sh aifoundry3 aace138caf80 00402801a1a5 KERNEL OK KERNEL OK notagate 12" "B1 on aifoundry3: BUILT, KERNEL OK on both desk ELFs, the hosts' twelve refusals before the device stage, the record"
echo; echo "== B2 on aifoundry1 (its hostname): refused before anything is built (E211 builds on aifoundry3 only)"
TB=$(tree a1)
inbox aifoundry1 bash "$TB/tools/claims-v3/e211/build_e211.sh" > "$S/b2.txt" 2>&1; rc=$?
tail -n 1 "$S/b2.txt" | cut -c1-200
v=$(/usr/bin/python3 -I -B -c "import json; print(json.load(open('$TB/build/e211rgm/BUILD-e211.json')).get('verdict'))")
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: the box is 'aifoundry1'" "$S/b2.txt")|$v|$(ls -d "$TB"/build/e211rgm/rgm*/kernel 2>/dev/null | wc -l)" "1|1|BUILD-FAILED|0" "B2 aifoundry1: refused, the record BUILD-FAILED, nothing built"
echo; echo "== B3 a changed rgm136 source: refused before the build"
TC=$(tree src)
echo "// a desk-test change" >> "$TC/tools/claims-v3/e136/rgm136/host/main.cpp"
inbox aifoundry3 bash "$TC/tools/claims-v3/e211/build_e211.sh" > "$S/b3.txt" 2>&1; rc=$?
tail -n 2 "$S/b3.txt" | cut -c1-200
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: the two kernels' sources are not harness-e211.json's" "$S/b3.txt")|$(ls -d "$TC"/build/e211rgm/rgm*/kernel 2>/dev/null | wc -l)" "1|1|0" "B3 a changed rgm136 source: refused, nothing built"
TC2=$(tree src2)
echo "// a desk-test change" >> "$TC2/tools/claims-v3/e211/rgm211/kernel/sparsity.c"
inbox aifoundry3 bash "$TC2/tools/claims-v3/e211/build_e211.sh" > "$S/b3b.txt" 2>&1; rc=$?
tail -n 2 "$S/b3b.txt" | cut -c1-200
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: the two kernels' sources are not harness-e211.json's" "$S/b3b.txt")|$(ls -d "$TC2"/build/e211rgm/rgm*/kernel 2>/dev/null | wc -l)" "1|1|0" "B3b a changed rgm211 source: refused, nothing built"
ELF=$TA/build/e211rgm/rgm211/kernel/sparsity.elf
ELF136=$TA/build/e211rgm/rgm136/kernel/sparsity.elf
echo; echo "== B4 the kernel gate on aifoundry3's form (.comment rewritten to '(g1b306039a) 15.1.0'), both kernels"
printf 'GCC: (g1b306039a) 15.1.0\0' > "$S/comment.bin"
"$OC" --update-section .comment="$S/comment.bin" "$ELF136" "$S/k136-a3.elf" 2>&1 | head -3
"$OC" --update-section .comment="$S/comment.bin" "$ELF" "$S/k211-a3.elf" 2>&1 | head -3
/opt/et/bin/riscv64-unknown-elf-readelf -p .comment "$S/k211-a3.elf" | grep -E 'GCC' | sed 's/^/    /'
g4a=$(/usr/bin/python3 -I -B "$E/check_e211.py" --kernel rgm136 "$S/k136-a3.elf" | tail -n 1)
g4b=$(/usr/bin/python3 -I -B "$E/check_e211.py" --kernel rgm211 "$S/k211-a3.elf" | tail -n 1)
echo "    rgm136 ELF $(sha256sum "$S/k136-a3.elf" | cut -c1-64); $g4a" | cut -c1-280
echo "    rgm211 ELF $(sha256sum "$S/k211-a3.elf" | cut -c1-64); $g4b" | cut -c1-280
ok "$(echo "$g4a" | grep -c "^KERNEL OK: rgm136: gemmL: rgm136, .* not the desk build's (sections the card never loads differ), its loadable identity 649d40793e459e51... the pinned one")|$(echo "$g4b" | grep -c "^KERNEL OK: rgm211: gemmLn: rgm211, .* not the desk build's (sections the card never loads differ), its loadable identity 1351a569e4a200cb... the pinned one")|$([ "$(sha256sum "$S/k211-a3.elf" | cut -c1-64)" != "$(sha256sum "$ELF" | cut -c1-64)" ] && echo changed)" \
   "1|1|changed" "B4 aifoundry3's form, both kernels: the ELF not the desk build's, the .text and loadable identity the pinned: KERNEL OK"
echo; echo "== B5 one byte of .rodata changed; B6 one byte of .text changed"
/usr/bin/python3 -I -B - "$ELF" "$S/k-ro.elf" "$S/k-tx.elf" <<'PY'
import struct, sys
src, ro, tx = sys.argv[1:4]
b = bytearray(open(src, "rb").read())
e_shoff, = struct.unpack_from("<Q", b, 40); e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", b, 58)
shs = [struct.unpack_from("<IIQQQQIIQQ", b, e_shoff + i * e_shentsize) for i in range(e_shnum)]
names = shs[e_shstrndx]
def nm(s): return bytes(b[names[4] + s[0]:names[4] + names[5]]).split(b"\0", 1)[0].decode()
off = {nm(s): s[4] for s in shs}
r = bytearray(b); r[off[".rodata"] + 3] ^= 0x01; open(ro, "wb").write(r)
t = bytearray(b); t[off[".text"] + 64] ^= 0x01; open(tx, "wb").write(t)
print(f"    .rodata at {off['.rodata']:#x}, .text at {off['.text']:#x}: one byte flipped in each copy")
PY
g5=$(/usr/bin/python3 -I -B "$E/check_e211.py" --kernel rgm211 "$S/k-ro.elf" | tail -n 1); echo "    $g5" | cut -c1-240
g6=$(/usr/bin/python3 -I -B "$E/check_e211.py" --kernel rgm211 "$S/k-tx.elf" | tail -n 1); echo "    $g6" | cut -c1-240
ok "$(echo "$g5" | grep -c "^KERNEL FAILED: rgm211: gemmLn: .text rgm211's, but the ELF .* its loadable identity .* is not the pinned")|$(echo "$g6" | grep -c "^KERNEL FAILED: rgm211: gemmLn needs rgm211's .text 82c7980716a0f0ca...; this ELF's .text is ")" "1|1" \
   "B5 a .rodata byte: refused by the identity; B6 a .text byte: refused by the .text"
echo; echo "== B6b THE WRONG KERNEL: rgm136's ELF given as rgm211's, rgm211's as rgm136's"
g7=$(/usr/bin/python3 -I -B "$E/check_e211.py" --kernel rgm211 "$ELF136" | tail -n 1); echo "    $g7" | cut -c1-240
g8=$(/usr/bin/python3 -I -B "$E/check_e211.py" --kernel rgm136 "$ELF" | tail -n 1); echo "    $g8" | cut -c1-240
ok "$(echo "$g7" | grep -c "^KERNEL FAILED: rgm211: gemmLn needs rgm211's .text .*(rgm136's)$")|$(echo "$g8" | grep -c "^KERNEL FAILED: rgm136: gemmL needs rgm136's .text .*(rgm211's)$")" "1|1" \
   "B6b the wrong kernel each way: refused by its .text, named"
echo; echo "== B7 on another box (hostname aifoundry2)"
TD=$(tree a2)
inbox aifoundry2 bash "$TD/tools/claims-v3/e211/build_e211.sh" > "$S/b7.txt" 2>&1; rc=$?
tail -n 1 "$S/b7.txt" | cut -c1-200
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: the box is 'aifoundry2'" "$S/b7.txt")|$(ls -d "$TD"/build/e211rgm/rgm*/kernel 2>/dev/null | wc -l)" "1|1|0" "B7 another box: refused before anything is built"
echo; echo "== B8 the runner (no --dry) on B1's tree under aifoundry3: its box check"
T0=$(date +%s)
inbox aifoundry3 /usr/bin/python3 -B "$TA/tools/claims-v3/e211/run_e211.py" session --arm A --t0 "$T0" --out "$S/b8" > "$S/b8.txt" 2>&1; rc=$?
grep -E 'refused|box and the build' "$S/b8/session.log" | cut -c1-260
w=$(grep -c "refused, no device opened: the box or the build is not the registered one (build/ettelem/ettelem: sha256 None, want 16037641" "$S/b8/session.log")
x=$(grep -cE "e211rgm/rgm(136|211)/kernel/sparsity.elf: sha256|e211rgm/rgm(136|211)/host/sparsity_host: sha256|build record is not" "$S/b8/session.log")
ok "$rc|$w|$x|$([ -e "$S/b8/config-start.json" ] && echo opened || echo none)" "16|1|0|none" "B8 the runner's box check: the build, both kernels and both hosts pass; it stops at the reader's pin, no device opened"
echo; echo "== B9 the guard on the other boxes (hostnames aifoundry1, aifoundry2) and with ET_DEVICES set on aifoundry3: refused (97) before the reader"
g1=$(inbox aifoundry1 bash "$TA/tools/claims-v3/e211/ettelem_guard_e211.sh" config 2>&1; echo "rc $?")
g2=$(inbox aifoundry2 bash "$TA/tools/claims-v3/e211/ettelem_guard_e211.sh" sample --seconds 1 --every-ms 100 2>&1; echo "rc $?")
g3=$(ET_DEVICES=0 inbox aifoundry3 bash "$TA/tools/claims-v3/e211/ettelem_guard_e211.sh" config 2>&1; echo "rc $?")
g4=$(inbox aifoundry3 bash "$TA/tools/claims-v3/e211/ettelem_guard_e211.sh" sample --reset-ms 10 2>&1; echo "rc $?")
printf '    %s\n' "$(echo "$g1" | head -n 1 | cut -c1-150)" "$(echo "$g2" | head -n 1 | cut -c1-150)" "$(echo "$g3" | head -n 1 | cut -c1-150)" "$(echo "$g4" | head -n 1 | cut -c1-150)"
ok "$(echo "$g1" | grep -c "box 'aifoundry1': E211 runs on aifoundry3 (card 0) only")$(echo "$g2" | grep -c "box 'aifoundry2'")$(echo "$g3" | grep -c "ET_DEVICES is '0' on aifoundry3")$(echo "$g4" | grep -c 'refused (sample --reset-ms 10)')|$(echo "$g1$g2$g3$g4" | grep -c 'rc 97')" "1111|4" \
   "B9 the guard: another box refused (aifoundry1, aifoundry2), ET_DEVICES refused on aifoundry3, the statistics reset refused; each rc 97 before the reader opens"
echo
[ "$n" -eq "$m" ] && v=PASS || v=FAIL
echo "DESKTEST-BUILD-E211 $n of $m $v"
[ "$v" = PASS ]
