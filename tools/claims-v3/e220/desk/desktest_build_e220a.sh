#!/usr/bin/env bash
# E220 ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): the build's desk test on this desk's REAL toolchain (GCC 15.1.0 "()"
# for the kernel, the desk's c++ and cmake, its /opt/et), E218's desk/desktest_build_e218.sh (E215's form) made ARM A'S BOX'S: aifoundry1, card 1
# (E215 arm B's RB0: on this desk's stock device layer the build is refused at its ET_DEVICES gate). Two builds: rgm136's ELF through THE KERNEL
# GATE at its WHOLE ELF (every E220 process runs it) and rgm211's tree through THE TREE GATE (its host runs rgm136's ELF for the gemmLnc branch;
# its own ELF runs no E220 point). Each case runs build_e220a.sh, check_e220a.py, the guard or the runner in a stand-in tree (the harness's files
# copied byte for byte) under bubblewrap with a box's hostname (a private UTS namespace). Run it ONLY inside the sandbox with no /dev/et* and an
# empty /run/lock (W/nodev.sh on aifoundry2): the built hosts' refusals run there (in the build's own sandbox), and case B8 runs the real runner,
# which must stop at its box check. Cases:
#   B1 on aifoundry1 (hostname aifoundry1, arm A): both trees built, THE KERNEL GATE reads KERNEL OK on rgm136's desk ELF aace138c... at its whole
#      ELF and THE TREE GATE on rgm211's desk ELF 00402801...; the hosts' twelve refusals, each before the device stage, in a sandbox with no
#      device node; then THE ET_DEVICES GATE: RGM-BUILD-FAILED "ET_DEVICES: a host has no ET_DEVICES" (this desk's device layer carries none: a
#      host built against it would open card 0 on aifoundry1), the record BUILD-FAILED (aifoundry1's own build read the reading: E215 arm B's)
#   B3 a changed rgm136 source, and B3b a changed rgm211 source: each refused before the build (the sources are not harness-e220a.json's)
#   B4 THE GATES on another box's form: each of B1's ELFs with its .comment rewritten to aifoundry3's riscv gcc string "GCC: (g1b306039a) 15.1.0"
#      (a section the card never loads): KERNEL OK by the loadable identity without --whole; WITH --whole (arm A's gate on aifoundry1) the same ELFs
#      KERNEL FAILED, the desk ELFs with --whole KERNEL OK
#   B5 one byte of rgm136's .rodata changed (in the PT_LOAD segment, outside .text): KERNEL FAILED (the identity)      B6 one byte of rgm136's
#      .text changed: KERNEL FAILED (.text); B6t the same two on rgm211's tree ELF: TREE FAILED both
#   B6b THE WRONG KERNEL: rgm211's ELF given as rgm136's: KERNEL FAILED (".text is ... (rgm211's)"), and rgm136's as rgm211's tree: refused; and the
#      gate by FAMILY on the real desk ELFs, both families both ways (ident_e220a.py --gate): each family on rgm136's ELF OK, on rgm211's FAILED
#   B7 on another box (hostname aifoundry2; and aifoundry3): refused before anything is built
#   B8 the runner (no --dry) on B1's tree under aifoundry1: its box check refuses B1's failed record ("not today's BUILT"): no device opened
#   B9 the guard: under aifoundry2 and under aifoundry3 refused (97) before the reader opens; on aifoundry1 with ET_DEVICES unset or 0, refused; on
#      aifoundry1 with ET_DEVICES=1 the guard lets `config` through to the reader (absent in the stand-in tree: not 97); `sample --reset-ms` (the
#      statistics reset) refused
#   bash tools/claims-v3/e220/desk/desktest_build_e220a.sh <an empty scratch dir outside the repo> > logs/desktest-build-e220a.txt
# The last line: DESKTEST-BUILD-E220A <n> of <m> PASS (or FAIL). SPDX-License-Identifier: Apache-2.0
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
echo "desktest_build_e220a: $(date '+%F %T %Z'); riscv gcc: $(/opt/et/bin/riscv64-unknown-elf-gcc --version | head -n 1); c++: $(c++ --version | head -n 1); $(cmake --version | head -n 1); python3 $(/usr/bin/python3 --version 2>&1); this desk's /opt/et/lib/libdeviceLayer.a carries ET_DEVICES: $(grep -aq ET_DEVICES /opt/et/lib/libdeviceLayer.a && echo yes || echo no)"
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = "$2" ]; then n=$((n + 1)); echo "-> $3: PASS"; else echo "-> $3: FAIL (got $1, want $2)"; fi; }
tree() {  # tree <name>: a stand-in box tree with the harness's files
  local T=$S/$1 f
  mkdir -p "$T"
  for f in $(/usr/bin/python3 -I -B "$E/check_e220a.py" --list) tools/claims-v3/e220/harness-e220a.json; do
    mkdir -p "$T/$(dirname "$f")"; cp -p "$REPO/$f" "$T/$f"
  done
  echo "$T"
}
inbox() { local h=$1; shift; /usr/bin/bwrap --dev-bind / / --unshare-uts --hostname "$h" --die-with-parent -- "$@"; }
rec() {  # rec <record>: verdict builder box arm rgm136-elf rgm211-elf gate136 gate211 et-devices host-checks-ok
  /usr/bin/python3 -I -B - "$1" <<'PY'
import json, sys
j = json.load(open(sys.argv[1]))
k = j.get("kernels") or {}
print(j.get("verdict"), j.get("builder"), j.get("box"), j.get("arm"), (k.get("rgm136") or {}).get("kernel_sha256", "")[:12], (k.get("rgm211") or {}).get("kernel_sha256", "")[:12],
      (k.get("rgm136") or {}).get("kernel_gate", "")[:9], (k.get("rgm211") or {}).get("kernel_gate", "")[:9],
      "notagate" if "not a gate" in str(j.get("et_devices", "")) else str(j.get("et_devices")).replace(" ", "_"), sum(1 for x in j.get("host_checks") or [] if x.endswith(":ok")))
PY
}
echo; echo "== B1 on aifoundry1 (its hostname, arm A): the real build"
TA=$(tree a1)
inbox aifoundry1 bash "$TA/tools/claims-v3/e220/build_e220a.sh" > "$S/b1.txt" 2>&1; rc=$?
grep -E '^(COMPILER|KERNEL|HOST|HOSTCHECK|ETDEVICES|RGM)' "$S/b1.txt" | cut -c1-200
r=$(rec "$TA/build/e220argm/BUILD-e220a.json"); echo "record: $r"
k136=$(grep -c "^KERNEL rgm136 aace138c.*KERNEL OK: rgm136: rgm136 gemmL: rgm136, " "$S/b1.txt")
k211=$(grep -c "^KERNEL rgm211 00402801.*KERNEL OK: rgm211: rgm211's tree: its ELF 00402801a1a53a93... the pinned one" "$S/b1.txt")
ev=$(grep -c "^RGM-BUILD-FAILED: ET_DEVICES: a host has no ET_DEVICES" "$S/b1.txt")
elves=$(ls "$TA"/build/e220argm/rgm136/kernel/sparsity.elf "$TA"/build/e220argm/rgm211/kernel/sparsity.elf 2>/dev/null | wc -l)
ok "$rc|${r%% *}|$k136|$k211|$ev|$elves" "1|BUILD-FAILED|1|1|1|2" "B1 on aifoundry1: both trees built, rgm136 KERNEL OK at its whole ELF and rgm211's tree KERNEL OK on the desk ELFs, then THE ET_DEVICES GATE refuses (this desk's device layer carries none): BUILD-FAILED"
echo; echo "== B3 a changed rgm136 source; B3b a changed rgm211 source: refused before the build"
TC=$(tree src)
echo "// a desk-test change" >> "$TC/tools/claims-v3/e136/rgm136/host/main.cpp"
inbox aifoundry1 bash "$TC/tools/claims-v3/e220/build_e220a.sh" > "$S/b3.txt" 2>&1; rc=$?
tail -n 2 "$S/b3.txt" | cut -c1-200
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: the two trees' sources are not harness-e220a.json's" "$S/b3.txt")|$(ls -d "$TC"/build/e220argm/rgm*/kernel 2>/dev/null | wc -l)" "1|1|0" "B3 a changed rgm136 source: refused, nothing built"
TC2=$(tree src2)
echo "// a desk-test change" >> "$TC2/tools/claims-v3/e211/rgm211/host/main.cpp"
inbox aifoundry1 bash "$TC2/tools/claims-v3/e220/build_e220a.sh" > "$S/b3b.txt" 2>&1; rc=$?
tail -n 2 "$S/b3b.txt" | cut -c1-200
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: the two trees' sources are not harness-e220a.json's" "$S/b3b.txt")|$(ls -d "$TC2"/build/e220argm/rgm*/kernel 2>/dev/null | wc -l)" "1|1|0" "B3b a changed rgm211 host source: refused, nothing built"
ELF=$TA/build/e220argm/rgm211/kernel/sparsity.elf
ELF136=$TA/build/e220argm/rgm136/kernel/sparsity.elf
echo; echo "== B4 the gates on another box's form (.comment rewritten to aifoundry3's '(g1b306039a) 15.1.0'), both builds; and with --whole (arm A's)"
printf 'GCC: (g1b306039a) 15.1.0\0' > "$S/comment.bin"
"$OC" --update-section .comment="$S/comment.bin" "$ELF136" "$S/k136-a3.elf" 2>&1 | head -3
"$OC" --update-section .comment="$S/comment.bin" "$ELF" "$S/k211-a3.elf" 2>&1 | head -3
g4a=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm136 "$S/k136-a3.elf" | tail -n 1)
g4b=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm211 "$S/k211-a3.elf" | tail -n 1)
g4c=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm136 "$S/k136-a3.elf" --whole | tail -n 1)
g4d=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm136 "$ELF136" --whole | tail -n 1)
g4e=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm211 "$S/k211-a3.elf" --whole | tail -n 1)
g4f=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm211 "$ELF" --whole | tail -n 1)
echo "    rgm136 ELF $(sha256sum "$S/k136-a3.elf" | cut -c1-64); $g4a" | cut -c1-280
echo "    rgm211 ELF $(sha256sum "$S/k211-a3.elf" | cut -c1-64); $g4b" | cut -c1-280
echo "    rgm136 with --whole: $g4c" | cut -c1-280
echo "    rgm136's desk ELF with --whole: $g4d" | cut -c1-200
echo "    rgm211 with --whole: $g4e" | cut -c1-240
echo "    rgm211's desk ELF with --whole: $g4f" | cut -c1-200
ok "$(echo "$g4a" | grep -c "^KERNEL OK: rgm136: rgm136 gemmL: rgm136, .* not the desk build's (sections the card never loads differ), its loadable identity 649d40793e459e51... the pinned one")|$(echo "$g4b" | grep -c "^KERNEL OK: rgm211: rgm211's tree: its ELF .* not the desk build's (sections the card never loads differ), its loadable identity 1351a569e4a200cb... the pinned one")|$(echo "$g4c" | grep -c "^KERNEL FAILED: rgm136: rgm136 gemmL: .text rgm136's, but the whole ELF")|$(echo "$g4d" | grep -c '^KERNEL OK: rgm136: .* and the whole ELF aace138caf8071cc')|$(echo "$g4e" | grep -c "^KERNEL FAILED: rgm211: rgm211's tree: .*but --whole requires the whole ELF at its pin")|$(echo "$g4f" | grep -c "^KERNEL OK: rgm211: rgm211's tree: its ELF 00402801a1a53a93")" \
   "1|1|1|1|1|1" "B4 aifoundry3's form, both builds: KERNEL OK by the loadable identity; with --whole the same ELFs refused, the desk ELFs passed"
echo; echo "== B5 one byte of .rodata changed; B6 one byte of .text changed (rgm136's ELF); B6t the same on rgm211's tree ELF"
/usr/bin/python3 -I -B - "$ELF136" "$S/k-ro.elf" "$S/k-tx.elf" "$ELF" "$S/t-ro.elf" "$S/t-tx.elf" <<'PY'
import struct, sys
for src, ro, tx in (sys.argv[1:4], sys.argv[4:7]):
    b = bytearray(open(src, "rb").read())
    e_shoff, = struct.unpack_from("<Q", b, 40); e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", b, 58)
    shs = [struct.unpack_from("<IIQQQQIIQQ", b, e_shoff + i * e_shentsize) for i in range(e_shnum)]
    names = shs[e_shstrndx]
    def nm(s): return bytes(b[names[4] + s[0]:names[4] + names[5]]).split(b"\0", 1)[0].decode()
    off = {nm(s): s[4] for s in shs}
    r = bytearray(b); r[off[".rodata"] + 3] ^= 0x01; open(ro, "wb").write(r)
    t = bytearray(b); t[off[".text"] + 64] ^= 0x01; open(tx, "wb").write(t)
    print(f"    {src.split('/')[-3]}: .rodata at {off['.rodata']:#x}, .text at {off['.text']:#x}: one byte flipped in each copy")
PY
g5=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm136 "$S/k-ro.elf" | tail -n 1); echo "    $g5" | cut -c1-240
g6=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm136 "$S/k-tx.elf" | tail -n 1); echo "    $g6" | cut -c1-240
g5t=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm211 "$S/t-ro.elf" | tail -n 1); echo "    $g5t" | cut -c1-240
g6t=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm211 "$S/t-tx.elf" | tail -n 1); echo "    $g6t" | cut -c1-240
ok "$(echo "$g5" | grep -c "^KERNEL FAILED: rgm136: rgm136 gemmL: .text rgm136's, but the ELF .* its loadable identity .* is not the pinned")|$(echo "$g6" | grep -c "^KERNEL FAILED: rgm136: rgm136 gemmL needs rgm136's .text 61315bf6a449c282...; this ELF's .text is ")|$(echo "$g5t" | grep -c "^KERNEL FAILED: rgm211: rgm211's tree: its ELF .* is not the pinned .* and its loadable identity .* is not the pinned")|$(echo "$g6t" | grep -c "^KERNEL FAILED: rgm211: rgm211's tree: its ELF .* is not the pinned")" "1|1|1|1" \
   "B5 a .rodata byte: refused by the identity; B6 a .text byte: refused by the .text; B6t both on rgm211's tree ELF: refused"
echo; echo "== B6b THE WRONG KERNEL each way, and the gate by family on the real desk ELFs (both families both ways)"
g7=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm136 "$ELF" | tail -n 1); echo "    $g7" | cut -c1-240
g8=$(/usr/bin/python3 -I -B "$E/check_e220a.py" --kernel rgm211 "$ELF136" | tail -n 1); echo "    $g8" | cut -c1-240
fams=""
for f in "rgm136 gemmL:rgm136:0" "rgm136 gemmL:rgm211:1" "rgm136 gemmLnc:rgm136:0" "rgm136 gemmLnc:rgm211:1"; do
  fam=${f%%:*}; rest=${f#*:}; k=${rest%%:*}; want=${rest##*:}
  out=$(/usr/bin/python3 -I -B "$E/ident_e220a.py" --gate "$fam" "$TA/build/e220argm/$k/kernel/sparsity.elf"); g=$?
  echo "    '$fam' on $k's ELF: rc $g: $(echo "$out" | cut -c1-120)"
  [ "$g" = "$want" ] && fams="${fams}y" || fams="${fams}n"
done
ok "$(echo "$g7" | grep -c "^KERNEL FAILED: rgm136: rgm136 gemmL needs rgm136's .text .*(rgm211's)$")|$(echo "$g8" | grep -c "^KERNEL FAILED: rgm211: rgm211's tree: its ELF aace138c")|$fams" "1|1|yyyy" \
   "B6b the wrong kernel each way refused; the gate by family: each family on rgm136's ELF OK, on rgm211's FAILED"
echo; echo "== B7 on another box (hostname aifoundry2; and aifoundry3)"
TD=$(tree a2)
inbox aifoundry2 bash "$TD/tools/claims-v3/e220/build_e220a.sh" > "$S/b7.txt" 2>&1; rc=$?
inbox aifoundry3 bash "$TD/tools/claims-v3/e220/build_e220a.sh" > "$S/b7b.txt" 2>&1; rc2=$?
tail -n 1 "$S/b7.txt" | cut -c1-200
ok "$rc|$(grep -c "^RGM-BUILD-FAILED: the box is 'aifoundry2'" "$S/b7.txt")|$rc2|$(grep -c "^RGM-BUILD-FAILED: the box is 'aifoundry3'" "$S/b7b.txt")|$(ls -d "$TD"/build/e220argm/rgm*/kernel 2>/dev/null | wc -l)" "1|1|1|1|0" "B7 another box (aifoundry2, aifoundry3): refused before anything is built"
echo; echo "== B8 the runner (no --dry) on B1's tree under aifoundry1: its box check on B1's failed record"
T0=$(date +%s)
inbox aifoundry1 /usr/bin/python3 -B "$TA/tools/claims-v3/e220/run_e220a.py" session --arm A --t0 "$T0" --out "$S/b8" > "$S/b8.txt" 2>&1; rc=$?
grep -E 'refused|box and the build' "$S/b8/session.log" | cut -c1-260
w=$(grep -c "refused, no device opened: the box or the build is not the registered one" "$S/b8/session.log")
x=$(grep -c "the build record is not today's BUILT by build_e220a.sh" "$S/b8/session.log")
ok "$rc|$w|$x|$([ -e "$S/b8/config-start.json" ] && echo opened || echo none)" "16|1|1|none" "B8 the runner's box check refuses the failed record (not today's BUILT): no device opened"
echo; echo "== B9 the guard"
g1=$(ET_DEVICES=1 inbox aifoundry2 bash "$TA/tools/claims-v3/e220/ettelem_guard_e220a.sh" config 2>&1; echo "rc $?")
g1b=$(ET_DEVICES=1 inbox aifoundry3 bash "$TA/tools/claims-v3/e220/ettelem_guard_e220a.sh" config 2>&1; echo "rc $?")
g2=$(ET_DEVICES=0 inbox aifoundry1 bash "$TA/tools/claims-v3/e220/ettelem_guard_e220a.sh" config 2>&1; echo "rc $?")
g2b=$(env -u ET_DEVICES /usr/bin/bwrap --dev-bind / / --unshare-uts --hostname aifoundry1 --die-with-parent -- bash "$TA/tools/claims-v3/e220/ettelem_guard_e220a.sh" config 2>&1; echo "rc $?")
g4=$(ET_DEVICES=1 inbox aifoundry1 bash "$TA/tools/claims-v3/e220/ettelem_guard_e220a.sh" config 2>&1; echo "rc $?")
g5=$(ET_DEVICES=1 inbox aifoundry1 bash "$TA/tools/claims-v3/e220/ettelem_guard_e220a.sh" sample --reset-ms 10 2>&1; echo "rc $?")
for g in "$g1" "$g1b" "$g2" "$g2b" "$g4" "$g5"; do echo "    $(echo "$g" | head -n 1 | cut -c1-150) [$(echo "$g" | tail -n 1)]"; done
ok "$(echo "$g1" | grep -c "box 'aifoundry2': E220 arm A runs on aifoundry1 only")$(echo "$g1b" | grep -c "box 'aifoundry3': E220 arm A runs on aifoundry1 only")$(echo "$g2" | grep -c "ET_DEVICES is '0' on aifoundry1, not 1")$(echo "$g2b" | grep -c "ET_DEVICES is 'unset' on aifoundry1, not 1")$(echo "$g5" | grep -c "refused (sample --reset-ms")|$(for g in "$g1" "$g1b" "$g2" "$g2b" "$g5"; do echo "$g" | tail -n 1; done | tr '\n' ' ')|$(echo "$g4" | grep -c "rc 97")" \
   "11111|rc 97 rc 97 rc 97 rc 97 rc 97 |0" "B9 the guard: another box refused (aifoundry2, aifoundry3), ET_DEVICES 0 or unset on aifoundry1 refused, the statistics reset refused (each rc 97 before the reader opens); ET_DEVICES=1 on aifoundry1 let through to the (absent) reader"
echo
[ "$n" -eq "$m" ] && v=PASS || v=FAIL
echo "DESKTEST-BUILD-E220A $n of $m $v"
[ "$v" = PASS ]
