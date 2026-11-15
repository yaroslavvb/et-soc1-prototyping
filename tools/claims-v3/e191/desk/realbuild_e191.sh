#!/usr/bin/env bash
# E191 (Q178, the kit's fix after its verifier, lane fix-e191k, Sat 14 Nov 2026, before any E191 datum): THE KERNEL GATE's desk test on
# the REAL build (the verifier's finding 1: E189's whole-ELF kernel pins came from aifoundry3's riscv gcc "(g1b306039a) 15.1.0" and refuse
# the "() 15.1.0" toolchain aifoundry1 has, so step 6 there would have built neither program; the kit's other build tests use stand-in
# kernels and pins and could not see it). build_e191.sh as committed, with NO stand-in (no RB_DESKTEST: the desk's real /opt/et, cmake
# and riscv objcopy, E191's real pins), in a stand-in tree (every harness file copied) under the hostname aifoundry2 (a private UTS
# namespace: there the ET_DEVICES reading is recorded, never a gate, so the build can reach BUILT; on aifoundry1 it is a gate, tested
# by desk/etdevices_test_e191.sh). The desk's riscv gcc reads "() 15.1.0" as aifoundry1's does (E190's build log there of Fri 13 Nov
# 2026; E136's kernel built here is byte-identical to E190's aifoundry1 build, verify-e191k's finding). Builds and reads only: the
# hosts are run by E189's host check alone (their self-tests, --dry lines and refusals, before any device can open). Cases (verdicts
# stated first):
#   K1  the real build: LEDGER-BUILT and SPP-BUILT, each kernel "KERNEL OK" with its ELF the '() 15.1.0' toolchain's pin (built at
#       another path: the pins hold whatever the tree's path), E191-BUILD rc=0, each record BUILT with the kernel gate's line;
#   K2  check_e191.py --box --built ledger,spp in that tree: HARNESS OK: 46 files (42 and two checks a kernel);
#   K3  each kernel with aifoundry3's .comment written in ("GCC: (g1b306039a) 15.1.0", objcopy --update-section): its ELF none of the
#       pinned, KERNEL OK by its loadable identity (the card loads the same bytes);
#   K4  one byte of the ledger's .debug_str changed (a section the card never loads): KERNEL OK by the loadable identity;
#   K5  one byte of the ledger's .rodata changed: KERNEL FAILED, the loadable identity not the pinned (the .text still the registered);
#   K6  one byte of sparse parity's .text changed: KERNEL FAILED, the .text not the registered;
#   K7  sparse parity's entry point moved by 2 in its ELF header: KERNEL FAILED, the loadable identity not the pinned;
#   K8  the pinned identity against E189's committed records of the kernel E189 ran (docs/reports/data/2026-11-12-q166-counter-
#       sparseparity/kernel/: sparseparity.hdr's sections, sparseparity.phdr's program headers, sparseparity.nm's symbols): sparse parity's
#       built sections (name, size, address), EVERY program header (LOAD and GNU_STACK: offset, addresses, sizes, flags, alignment; fix-e191k2:
#       the identity's second form reads them all) and symbols (address, type, name) equal them;
#   K9  the gate's pins: check_e191.py's registered .text is hostcheck-e189.json's (and named in E189.md 4), its ELF_ALSO are K1's ELFs and
#       its LOAD_SHA256 are K1's loadable identities (the second form);
#   K10 (fix-e191k2, verify-e191k2's nit 4 and its observations O1-O4) what the identity's first form left out now refuses, each on sparse
#       parity's built ELF with its .text the registered one: the GNU_STACK header's flags (RW to RWX), its type set to PT_TLS, the OS/ABI
#       byte (e_ident[7]) set to Linux's, e_version set to 2, and .sdata's entry size (8 to 16): each KERNEL FAILED by the loadable
#       identity (never by the .text).
# Run ONLY inside the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): the host check runs the built hosts.
#   bash tools/claims-v3/e191/desk/realbuild_e191.sh <an empty scratch dir outside the repo> > realbuild-e191.txt
# The last line: REALBUILD-E191 <n> of <m> PASS (or FAIL). A desk check of code: nothing here is measured.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?an empty scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
for v in RB_DESKTEST E191_PREFIX E191_CMAKE E191_OBJCOPY E191_KERNEL_PINS; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs the real build with no stand-in"; exit 2; }
done
for c in bwrap cmake sha256sum /opt/et/bin/riscv64-unknown-elf-gcc /opt/et/bin/riscv64-unknown-elf-objcopy /opt/et/bin/riscv64-unknown-elf-readelf \
         /opt/et/bin/riscv64-unknown-elf-nm; do command -v "$c" > /dev/null || { echo "no $c"; exit 2; }; done
mkdir -p "$S"; S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "$S is not empty"; exit 2; }
E=tools/claims-v3/e191
OC=/opt/et/bin/riscv64-unknown-elf-objcopy; RE=/opt/et/bin/riscv64-unknown-elf-readelf; NM=/opt/et/bin/riscv64-unknown-elf-nm
PY=/usr/bin/python3
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = "$2" ]; then n=$((n + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fi; }
echo "realbuild_e191: $(date '+%F %T %Z') on $(hostname), $($PY --version 2>&1) at $PY; riscv $(/opt/et/bin/riscv64-unknown-elf-gcc --version | head -n 1); $(cmake --version | head -n 1)"
T=$S/tree
( cd "$SRC" && $PY -I -B $E/check_e191.py --list; echo $E/harness-e191.json ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
gate() { ( cd "$T" && $PY -I -B $E/check_e191.py --kernel "$1" "$2" 2>&1 | tail -n 1 ); }
rec() { $PY -I -B - "$T/$1/BUILD-e191.json" <<'PY'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    r = {}
print(f"{r.get('builder')}|{r.get('verdict')}|{(r.get('kernel_gate') or '')[:9]}")
PY
}
# ---- K1: the real build under the hostname aifoundry2
/usr/bin/bwrap --dev-bind / / --unshare-uts --hostname aifoundry2 --die-with-parent -- env -C "$T" -u RB_DESKTEST bash "$T/$E/build_e191.sh" > "$S/build.txt" 2>&1
b=$?
grep -E '^(COMPILER|LEDGER|SPP|E191-BUILD|HARNESS)' "$S/build.txt" | cut -c1-230 | sed 's/^/   K1: /'
LE=$T/build/e191ledger/kernel/ledger.elf; SE=$T/build/e191spp/kernel/sparseparity.elf
ok "$b.$(grep -c "^LEDGER KERNEL OK ledger: .* the '() 15.1.0' toolchain's pin" "$S/build.txt").$(grep -c "^SPP KERNEL OK spp: .* the '() 15.1.0' toolchain's pin" "$S/build.txt").$(grep -c '^LEDGER-BUILT rc=0' "$S/build.txt").$(grep -c '^SPP-BUILT rc=0' "$S/build.txt").$(rec build/e191ledger).$(rec build/e191spp)" \
  "0.1.1.1.1.build_e191.sh|BUILT|KERNEL OK.build_e191.sh|BUILT|KERNEL OK" \
  "K1 the real build (no stand-in): both kernels through the gate by the '() 15.1.0' pin, both BUILT, E191-BUILD rc=0, the records carry the gate's line"
# ---- K2: the harness with the built kernels
k2=$( cd "$T" && $PY -I -B $E/check_e191.py --box --built ledger,spp 2>&1 | tail -n 1 ); echo "   K2: $k2"
ok "$k2" "HARNESS OK: 46 files" "K2 check_e191.py --box --built ledger,spp on the built tree (step 6's own read)"
# ---- K3, K4: bytes the card never loads
printf 'GCC: (g1b306039a) 15.1.0\0' > "$S/comment-a3.bin"
"$OC" --update-section .comment="$S/comment-a3.bin" "$LE" "$S/ledger-c3.elf"; "$OC" --update-section .comment="$S/comment-a3.bin" "$SE" "$S/spp-c3.elf"
g3l=$(gate ledger "$S/ledger-c3.elf"); g3s=$(gate spp "$S/spp-c3.elf"); echo "   K3: $g3l"; echo "   K3: $g3s"
ok "$(case "$g3l" in "KERNEL OK ledger: "*"none of the pinned"*"the pinned one") echo 1 ;; *) echo 0 ;; esac).$(case "$g3s" in "KERNEL OK spp: "*"none of the pinned"*"the pinned one") echo 1 ;; *) echo 0 ;; esac)" \
  "1.1" "K3 aifoundry3's .comment written in: each ELF none of the pinned, each KERNEL OK by its loadable identity"
flip() {  # flip <elf in> <elf out> <section name | @entry> : one byte of that section's contents (or the entry point + 2), the rest unchanged
  $PY -I -B - "$1" "$2" "$3" <<'PY'
import struct, sys
src, dst, what = sys.argv[1:4]
b = bytearray(open(src, "rb").read())
if what == "@entry":
    e = struct.unpack_from("<Q", b, 24)[0]
    struct.pack_into("<Q", b, 24, e + 2)
else:
    shoff, = struct.unpack_from("<Q", b, 40); shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 58)
    sh = [struct.unpack_from("<IIQQQQIIQQ", b, shoff + i * shentsize) for i in range(shnum)]
    st = sh[shstrndx]
    name = lambda s: bytes(b[st[4] + s[0]:st[4] + st[5]]).split(b"\0", 1)[0].decode()
    s = [x for x in sh if name(x) == what][0]
    b[s[4] + s[5] // 2] ^= 0x01
open(dst, "wb").write(bytes(b))
print(f"changed {what}")
PY
}
flip "$LE" "$S/ledger-dbg.elf" .debug_str > /dev/null; g4=$(gate ledger "$S/ledger-dbg.elf"); echo "   K4: $g4"
ok "$(case "$g4" in "KERNEL OK ledger: "*"the pinned one") echo 1 ;; *) echo 0 ;; esac)" 1 "K4 a .debug_str byte changed: KERNEL OK (the card never loads it)"
flip "$LE" "$S/ledger-ro.elf" .rodata > /dev/null; g5=$(gate ledger "$S/ledger-ro.elf"); echo "   K5: $g5"
ok "$(case "$g5" in "KERNEL FAILED ledger: .text the registered, but"*"loadable identity"*"is not the pinned"*) echo 1 ;; *) echo 0 ;; esac)" 1 \
  "K5 a .rodata byte changed: KERNEL FAILED by the loadable identity (the .text still the registered)"
flip "$SE" "$S/spp-tx.elf" .text > /dev/null; g6=$(gate spp "$S/spp-tx.elf"); echo "   K6: $g6"
ok "$(case "$g6" in "KERNEL FAILED spp: .text sha256 "*"is not the registered"*) echo 1 ;; *) echo 0 ;; esac)" 1 "K6 a .text byte changed: KERNEL FAILED, the .text not the registered"
flip "$SE" "$S/spp-en.elf" @entry > /dev/null; g7=$(gate spp "$S/spp-en.elf"); echo "   K7: $g7"
ok "$(case "$g7" in "KERNEL FAILED spp: "*"loadable identity"*"is not the pinned"*) echo 1 ;; *) echo 0 ;; esac)" 1 "K7 the entry point moved: KERNEL FAILED by the loadable identity"
# ---- K8: sparse parity's pinned identity against E189's committed records of the kernel E189 ran
K=$SRC/docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel
secs() { grep ALLOC | awk '$2 ~ /^\./ && NF >= 7 {print $2, $3, $4}' | sed 's/ 0*\([0-9a-f]\)/ \1/g'; }   # name, size, address
/opt/et/bin/riscv64-unknown-elf-objdump -h -w "$SE" | secs > "$S/built-secs.txt"     # -w: each section on one line, as the record holds it
secs < "$K/sparseparity.hdr" > "$S/e189-secs.txt"
phl() { sed -n '/^  Type /,/^$/p' | grep -v -e '^  Type ' -e '^$'; }     # every program header line, as readelf -l -W prints the table
"$RE" -l -W "$SE" | phl > "$S/built-load.txt"; phl < "$K/sparseparity.phdr" > "$S/e189-load.txt"
"$NM" -n "$SE" > "$S/built-nm.txt"
d1=$(diff "$S/built-secs.txt" "$S/e189-secs.txt" > /dev/null && echo same || echo DIFFER)
d2=$(diff -w "$S/built-load.txt" "$S/e189-load.txt" > /dev/null && echo same || echo DIFFER)
d3=$(diff "$S/built-nm.txt" "$K/sparseparity.nm" > /dev/null && echo same || echo DIFFER)
echo "   K8: the ALLOC sections ($(tr '\n' ';' < "$S/built-secs.txt")) against sparseparity.hdr: $d1; the program headers ($(awk '{print $1}' "$S/built-load.txt" | tr '\n' ' ')) against sparseparity.phdr: $d2; the symbols ($(grep -c . "$S/built-nm.txt")) against sparseparity.nm: $d3"
ok "$d1.$d2.$d3.$(grep -c . "$S/built-secs.txt").$(grep -c . "$S/built-load.txt")" "same.same.same.4.2" \
  "K8 sparse parity's sections, every program header (LOAD, GNU_STACK) and symbols equal E189's committed records of the kernel E189 ran"
# ---- K9: the gate's pins
k9=$(cd "$SRC" && $PY -I -B - "$LE" "$SE" <<'PY'
import hashlib, json, sys
sys.path.insert(0, "tools/claims-v3/e191")
import check_e191 as H
hc = json.load(open("tools/claims-v3/e189/hostcheck-e189.json"))["kernels"]
md = open("tools/claims-v3/e189/E189.md").read()
out = []
for prog, elf in (("ledger", sys.argv[1]), ("spp", sys.argv[2])):
    t, elfs, load = H.kernel_pins(prog)
    ident, _ = H.elf_identity(elf)
    out.append(t == hc[prog]["text_sha256"] and ("`.text` " + t[:8]) in md and elfs[0][0] == hc[prog]["elf_sha256"]
               and H.ELF_ALSO[prog] == hashlib.sha256(open(elf, "rb").read()).hexdigest() and load == H.identity_sha(ident))
print("K9 " + ".".join("ok" if x else "NOT" for x in out))
PY
); echo "   $k9"
ok "$k9" "K9 ok.ok" "K9 the registered .text (hostcheck-e189.json, E189.md 4), E189's ELF pins, ELF_ALSO and LOAD_SHA256 as built in K1"
# ---- K10 (fix-e191k2, verify-e191k2's nit 4): what the identity's first form left out now refuses
mut() {  # mut <elf in> <elf out> <stack-flags | stack-tls | osabi | version | sdata-entsize>: one header field changed, every byte else kept
  $PY -I -B - "$1" "$2" "$3" <<'PY'
import struct, sys
src, dst, what = sys.argv[1:4]
b = bytearray(open(src, "rb").read())
phoff, = struct.unpack_from("<Q", b, 32); phentsize, phnum = struct.unpack_from("<HH", b, 54)
shoff, = struct.unpack_from("<Q", b, 40); shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 58)
stack = [phoff + i * phentsize for i in range(phnum) if struct.unpack_from("<I", b, phoff + i * phentsize)[0] == 0x6474e551][0]
if what == "stack-flags":
    struct.pack_into("<I", b, stack + 4, 7)            # p_flags RW -> RWX
elif what == "stack-tls":
    struct.pack_into("<I", b, stack, 7)                # p_type PT_GNU_STACK -> PT_TLS
elif what == "osabi":
    b[7] = 3                                           # e_ident[EI_OSABI] NONE -> LINUX
elif what == "version":
    struct.pack_into("<I", b, 20, 2)                   # e_version 1 -> 2
elif what == "sdata-entsize":
    sh = [struct.unpack_from("<IIQQQQIIQQ", b, shoff + i * shentsize) for i in range(shnum)]
    st = sh[shstrndx]
    name = lambda s: bytes(b[st[4] + s[0]:st[4] + st[5]]).split(b"\0", 1)[0].decode()
    i = [k for k, s in enumerate(sh) if name(s) == ".sdata"][0]
    struct.pack_into("<Q", b, shoff + i * shentsize + 56, 16)   # sh_entsize 8 -> 16
open(dst, "wb").write(bytes(b))
print(f"changed {what}")
PY
}
k10=""
for w in stack-flags stack-tls osabi version sdata-entsize; do
  mut "$SE" "$S/spp-$w.elf" "$w" > /dev/null; g=$(gate spp "$S/spp-$w.elf"); echo "   K10 $w: $g" | cut -c1-230
  k10="$k10$(case "$g" in "KERNEL FAILED spp: .text the registered, but"*"loadable identity"*"is not the pinned"*) echo 1 ;; *) echo 0 ;; esac)"
done
ok "$k10" "11111" "K10 the GNU_STACK header's flags, its type (PT_TLS), the OS/ABI byte, e_version and an allocated section's entry size: each refused by the loadable identity's second form"
echo "REALBUILD-E191 $n of $m $([ "$n" -eq "$m" ] && echo PASS || echo FAIL)"
[ "$n" -eq "$m" ]
