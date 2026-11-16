#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): THE KERNEL GATE's desk test on the
# REAL build of THIS BOX's toolchain, the box E194's kernels are built on (the task's lesson: "the kernel gate on what loads (this box's
# toolchain)"). E191's test (tools/claims-v3/e191/desk/realbuild_e191.sh, unchanged beside it; fix-e191k and fix-e191k2) on E194's build:
# build_e194.sh as written, with NO stand-in (no RB_DESKTEST: this box's real /opt/et, cmake and riscv objcopy, the gate's real pins), in a
# stand-in tree (every harness file copied) under the hostname aifoundry2 (a private UTS namespace; this box's own name). Builds and reads
# only: the hosts are run by E189's host check alone (their self-tests, --dry lines and refusals, before any device can open), inside the
# sandbox. Cases (verdicts stated first):
#   K1  the real build: LEDGER-BUILT and SPP-BUILT, each kernel "KERNEL OK" with its ELF the '() 15.1.0' toolchain's pin, E194-BUILD rc=0,
#       each record BUILT by build_e194.sh on aifoundry2 with the kernel gate's line, and its ET_DEVICES reading recorded "not a gate";
#   K2  check_e194.py --box --built ledger,spp in that tree: HARNESS OK: 46 files (42 and two checks a kernel);
#   K3-K7, K10  E191's cases on these ELFs, unchanged: aifoundry3's .comment written in (OK by the loadable identity); a .debug_str byte
#       (OK); a .rodata byte, a .text byte, the entry point (each refused); the GNU_STACK flags and type, the OS/ABI byte, e_version and an
#       entry size (each refused by the identity's second form);
#   K8  sparse parity's built sections, every program header and symbols equal E189's committed records of the kernel E189 ran;
#   K9  the gate's pins: the registered .text (hostcheck-e189.json, E189.md 4), E189's ELF pins, ELF_ALSO and LOAD_SHA256 equal K1's.
# Run ONLY inside the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): the host check runs the built hosts.
#   bash tools/claims-v3/e194/desk/realbuild_e194.sh <an empty scratch dir outside the repo> > realbuild-e194.txt
# The last line: REALBUILD-E194 <n> of <m> PASS (or FAIL). A desk check of code: nothing here is measured.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?an empty scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
for v in RB_DESKTEST E194_PREFIX E194_CMAKE E194_OBJCOPY E194_KERNEL_PINS; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs the real build with no stand-in"; exit 2; }
done
for c in bwrap cmake sha256sum /opt/et/bin/riscv64-unknown-elf-gcc /opt/et/bin/riscv64-unknown-elf-objcopy /opt/et/bin/riscv64-unknown-elf-readelf \
         /opt/et/bin/riscv64-unknown-elf-nm; do command -v "$c" > /dev/null || { echo "no $c"; exit 2; }; done
mkdir -p "$S"; S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "$S is not empty"; exit 2; }
E=tools/claims-v3/e194
OC=/opt/et/bin/riscv64-unknown-elf-objcopy; RE=/opt/et/bin/riscv64-unknown-elf-readelf; NM=/opt/et/bin/riscv64-unknown-elf-nm
PY=/usr/bin/python3
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = "$2" ]; then n=$((n + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fi; }
echo "realbuild_e194: $(date '+%F %T %Z') on $(hostname), $($PY --version 2>&1) at $PY; riscv $(/opt/et/bin/riscv64-unknown-elf-gcc --version | head -n 1); $(cmake --version | head -n 1)"
T=$S/tree
( cd "$SRC" && $PY -I -B $E/check_e194.py --list; echo $E/harness-e194.json ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
gate() { ( cd "$T" && $PY -I -B $E/check_e194.py --kernel "$1" "$2" 2>&1 | tail -n 1 ); }
rec() { $PY -I -B - "$T/$1/BUILD-e194.json" <<'PY'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    r = {}
print(f"{r.get('builder')}|{r.get('verdict')}|{(r.get('kernel_gate') or '')[:9]}|{r.get('box')}|{(r.get('et_devices') or '')[:10]}")
PY
}
# ---- K1: the real build under the hostname aifoundry2
/usr/bin/bwrap --dev-bind / / --unshare-uts --hostname aifoundry2 --die-with-parent -- env -C "$T" -u RB_DESKTEST -u ET_DEVICES -u V3_DEVICE bash "$T/$E/build_e194.sh" > "$S/build.txt" 2>&1
b=$?
grep -E '^(COMPILER|LEDGER|SPP|E194-BUILD|HARNESS)' "$S/build.txt" | cut -c1-230 | sed 's/^/   K1: /'
LE=$T/build/e194ledger/kernel/ledger.elf; SE=$T/build/e194spp/kernel/sparseparity.elf
ok "$b.$(grep -c "^LEDGER KERNEL OK ledger: .* the '() 15.1.0' toolchain's pin" "$S/build.txt").$(grep -c "^SPP KERNEL OK spp: .* the '() 15.1.0' toolchain's pin" "$S/build.txt").$(grep -c '^LEDGER-BUILT rc=0' "$S/build.txt").$(grep -c '^SPP-BUILT rc=0' "$S/build.txt").$(rec build/e194ledger).$(rec build/e194spp)" \
  "0.1.1.1.1.build_e194.sh|BUILT|KERNEL OK|aifoundry2|not a gate.build_e194.sh|BUILT|KERNEL OK|aifoundry2|not a gate" \
  "K1 the real build on this box's toolchain (no stand-in): both kernels through the gate by the '() 15.1.0' pin, both BUILT, E194-BUILD rc=0, the records carry the gate's line, the box and the ET_DEVICES reading (not a gate)"
# ---- K2: the harness with the built kernels
k2=$( cd "$T" && $PY -I -B $E/check_e194.py --box --built ledger,spp 2>&1 | tail -n 1 ); echo "   K2: $k2"
ok "$k2" "HARNESS OK: 46 files" "K2 check_e194.py --box --built ledger,spp on the built tree (step 6's own read)"
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
sys.path.insert(0, "tools/claims-v3/e194")
import check_e194 as H
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
echo "REALBUILD-E194 $n of $m $([ "$n" -eq "$m" ] && echo PASS || echo FAIL)"
[ "$n" -eq "$m" ]
