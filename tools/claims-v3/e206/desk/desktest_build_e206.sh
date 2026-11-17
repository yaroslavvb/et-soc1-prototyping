#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum): the build's desk test on this desk's REAL toolchain (GCC 15.1.0 "()" for
# the kernel, the desk's c++ and cmake, its /opt/et), E190's desk/desktest_build_e190_v2.sh form with THE KERNEL GATE's cases. Each case runs
# build_e206.sh, check_e206.py or the runner in a stand-in tree (the harness's files copied byte for byte) under bubblewrap with the box's
# hostname (a private UTS namespace). Run it ONLY inside the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): the
# built host's four refusals run it, and case B8 runs the real runner, which must stop at its box check. Cases:
#   B1 as arm A (hostname aifoundry3): BUILT; THE KERNEL GATE reads KERNEL OK on the registered ELF aace138c... (.text 61315bf6...); the host's
#      four refusals; the record (builder build_e206.sh, box aifoundry3, the gate's line, ET_DEVICES not a gate)
#   B2 as arm B (hostname aifoundry1): RGM-BUILD-FAILED "ET_DEVICES: the host has no ET_DEVICES" (this desk's stock device layer), the record
#      BUILD-FAILED
#   B3 a changed rgm136 source: refused before the build (the sources are not harness-e206.json's)
#   B4 THE KERNEL GATE on aifoundry3's form: B1's ELF with its .comment rewritten to aifoundry3's riscv gcc string "GCC: (g1b306039a) 15.1.0"
#      (a section the card never loads): its whole ELF differs from the pin, its .text and its loadable identity do not: KERNEL OK
#   B5 one byte of .rodata changed (in the PT_LOAD segment, outside .text): the .text is the registered one but the loadable identity differs:
#      KERNEL FAILED                      B6 one byte of .text changed: KERNEL FAILED (.text)
#   B7 on another box (hostname aifoundry2): refused before anything is built
#   B8 the runner (no --dry) on B1's tree as arm A: its box check passes the build record, the kernel and the host and stops at the reader's
#      pin (the stand-in tree has no reader there): "refused, no device opened"
#   bash tools/claims-v3/e206/desk/desktest_build_e206.sh <an empty scratch dir outside the repo> > logs/desktest-build-e206.txt
# The last line: DESKTEST-BUILD-E206 <n> of <m> PASS (or FAIL). SPDX-License-Identifier: Apache-2.0
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
echo "desktest_build_e206: $(date '+%F %T %Z'); riscv gcc: $(/opt/et/bin/riscv64-unknown-elf-gcc --version | head -n 1); c++: $(c++ --version | head -n 1); $(cmake --version | head -n 1); python3 $(/usr/bin/python3 --version 2>&1)"
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = "$2" ]; then n=$((n + 1)); echo "-> $3: PASS"; else echo "-> $3: FAIL (got $1, want $2)"; fi; }
tree() {  # tree <name>: a stand-in box tree with the harness's files
  local T=$S/$1 f
  mkdir -p "$T"
  for f in $(/usr/bin/python3 -I -B "$E/check_e206.py" --list) tools/claims-v3/e206/harness-e206.json; do
    mkdir -p "$T/$(dirname "$f")"; cp -p "$REPO/$f" "$T/$f"
  done
  echo "$T"
}
inbox() { local h=$1; shift; /usr/bin/bwrap --dev-bind / / --unshare-uts --hostname "$h" --die-with-parent -- "$@"; }
echo; echo "== B1 as arm A (hostname aifoundry3): the real build"
TA=$(tree a3)
inbox aifoundry3 bash "$TA/tools/claims-v3/e206/build_e206.sh" > "$S/b1.txt" 2>&1; rc=$?
grep -E '^(COMPILER|KERNEL|HOST|HOSTCHECK|ETDEVICES|RGM)' "$S/b1.txt" | cut -c1-200
r=$(/usr/bin/python3 -I -B - "$TA/build/e206rgm/BUILD-e206.json" <<'PY'
import json, sys
j = json.load(open(sys.argv[1]))
print(j.get("verdict"), j.get("builder"), j.get("box"), j.get("kernel_sha256", "")[:12], j.get("kernel_gate", "")[:9], "notagate" if "not a gate on aifoundry3" in j.get("et_devices", "") else "GATE", len([c for c in j.get("host_checks", []) if c.endswith(":ok")]))
PY
)
echo "record: $r"
ok "$rc|$r" "0|BUILT build_e206.sh aifoundry3 aace138caf80 KERNEL OK notagate 4" "B1 as arm A: BUILT, KERNEL OK on the registered ELF, the host's four refusals, the record"
echo; echo "== B2 as arm B (hostname aifoundry1): the ET_DEVICES gate on this desk's stock device layer"
TB=$(tree a1)
inbox aifoundry1 bash "$TB/tools/claims-v3/e206/build_e206.sh" > "$S/b2.txt" 2>&1; rc=$?
grep -E '^(KERNEL|ETDEVICES|RGM)' "$S/b2.txt" | cut -c1-200
v=$(/usr/bin/python3 -I -B -c "import json; print(json.load(open('$TB/build/e206rgm/BUILD-e206.json')).get('verdict'))")
ok "$rc|$(grep -c '^RGM-BUILD-FAILED: ET_DEVICES: the host has no ET_DEVICES' "$S/b2.txt")|$v" "1|1|BUILD-FAILED" "B2 as arm B: refused (ET_DEVICES), the record BUILD-FAILED"
echo; echo "== B3 a changed rgm136 source: refused before the build"
TC=$(tree src)
echo "// a desk-test change" >> "$TC/tools/claims-v3/e136/rgm136/host/main.cpp"
inbox aifoundry3 bash "$TC/tools/claims-v3/e206/build_e206.sh" > "$S/b3.txt" 2>&1; rc=$?
tail -n 2 "$S/b3.txt" | cut -c1-200
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: rgm136's sources are not harness-e206.json's" "$S/b3.txt")|$(ls "$TC/build/e206rgm/kernel" 2>/dev/null | wc -l)" "1|1|0" "B3 a changed source: refused, nothing built"
ELF=$TA/build/e206rgm/kernel/sparsity.elf
echo; echo "== B4 the kernel gate on aifoundry3's form (.comment rewritten to '(g1b306039a) 15.1.0')"
printf 'GCC: (g1b306039a) 15.1.0\0' > "$S/comment.bin"
"$OC" --update-section .comment="$S/comment.bin" "$ELF" "$S/k-a3.elf" 2>&1 | head -3
/opt/et/bin/riscv64-unknown-elf-readelf -p .comment "$S/k-a3.elf" | grep -E 'GCC' | sed 's/^/    /'
g4=$(/usr/bin/python3 -I -B "$E/check_e206.py" --kernel "$S/k-a3.elf" | tail -n 1)
echo "    ELF $(sha256sum "$S/k-a3.elf" | cut -c1-64); $g4" | cut -c1-260
ok "$(sha256sum "$S/k-a3.elf" | cut -c1-12)|$(echo "$g4" | grep -c '^KERNEL OK: .* not the registered (the difference lies in sections the card never loads); its loadable identity 649d40793e459e51... the pinned one')" \
   "$(sha256sum "$S/k-a3.elf" | cut -c1-12)|1" "B4 aifoundry3's form: its ELF not the pin, its .text and loadable identity the pinned: KERNEL OK"
[ "$(sha256sum "$S/k-a3.elf" | cut -c1-64)" != "$(sha256sum "$ELF" | cut -c1-64)" ] || echo "    (B4's ELF did not change: the case shows nothing)"
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
g5=$(/usr/bin/python3 -I -B "$E/check_e206.py" --kernel "$S/k-ro.elf" | tail -n 1); echo "    $g5" | cut -c1-240
g6=$(/usr/bin/python3 -I -B "$E/check_e206.py" --kernel "$S/k-tx.elf" | tail -n 1); echo "    $g6" | cut -c1-240
ok "$(echo "$g5" | grep -c '^KERNEL FAILED: .text the registered, but the ELF .* its loadable identity .* is not the pinned')|$(echo "$g6" | grep -c '^KERNEL FAILED: .text sha256 .* is not the registered')" "1|1" \
   "B5 a .rodata byte: refused by the identity; B6 a .text byte: refused by the .text"
echo; echo "== B7 on another box (hostname aifoundry2)"
TD=$(tree a2)
inbox aifoundry2 bash "$TD/tools/claims-v3/e206/build_e206.sh" > "$S/b7.txt" 2>&1; rc=$?
tail -n 1 "$S/b7.txt" | cut -c1-200
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: the box is 'aifoundry2'" "$S/b7.txt")|$(ls "$TD/build/e206rgm/kernel" 2>/dev/null | wc -l)" "1|1|0" "B7 another box: refused before anything is built"
echo; echo "== B8 the runner (no --dry) on B1's tree as arm A: its box check"
T0=$(date +%s)
inbox aifoundry3 /usr/bin/python3 -B "$TA/tools/claims-v3/e206/run_e206.py" session --arm A --t0 "$T0" --out "$S/b8" > "$S/b8.txt" 2>&1; rc=$?
grep -E 'refused|box and the build' "$S/b8/session.log" | cut -c1-260
w=$(grep -c "refused, no device opened: the box or the build is not the registered one (build/ettelem/ettelem: sha256 None, want 16037641" "$S/b8/session.log")
x=$(grep -cE "e206rgm/kernel/sparsity.elf: sha256|e206rgm/host/sparsity_host: sha256|build record is not" "$S/b8/session.log")
ok "$rc|$w|$x|$([ -e "$S/b8/config-start.json" ] && echo opened || echo none)" "16|1|0|none" "B8 the runner's box check: the build, the kernel and the host pass; it stops at the reader's pin, no device opened"
echo
[ "$n" -eq "$m" ] && v=PASS || v=FAIL
echo "DESKTEST-BUILD-E206 $n of $m $v"
[ "$v" = PASS ]
