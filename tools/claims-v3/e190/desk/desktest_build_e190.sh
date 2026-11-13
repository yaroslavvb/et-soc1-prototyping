#!/usr/bin/env bash
# E190 (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): the desk test of the box build (build_e190.sh) on this desk's REAL toolchain
# (/opt/et, the box's cmake and C++ compiler), in scratch trees that hold the files the build reads (tools/claims-v3/e190, the rgm136
# sources, the tiles, the device-command checker). On a box with a card run it ONLY inside a sandbox with no /dev/et* and an empty
# /run/lock: the build runs the built host four times (its refusals, before any device).
#   B1  the build as committed: RGM-BUILT rc=0; the kernel ELF at the registration's pin aace138c...; the host's four refusals each ok
#       (an unknown option rc 2, a zero shire mask rc 2, an unreadable kernel rc 1, an unknown test rc 2); BUILD-e190.json BUILT, today
#       (Pacific), this box, the host's sha256 the file's; no /dev/et* existed, so none could be opened
#   B2  NEGATIVE: one rgm136 source changed, the harness as committed: RGM-BUILD-FAILED (the sources are not harness-e190.json's), no build
#   B3  NEGATIVE: the kernel's source changed AND the harness re-made to match it: the build runs, and the kernel ELF is not the pin:
#       RGM-BUILD-FAILED naming the pin
#   B4  the built host as the session's runner would read it: run_e190.py's box check, in the B1 tree with a stand-in reader file, reads
#       the kernel at the pin and the host at the record's sha256 and stops only at the reader's pin (as it must, no reader being real)
#   bash tools/claims-v3/e190/desk/desktest_build_e190.sh <scratch dir> > desktest-build-e190.txt
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
E=tools/claims-v3/e190
npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fi; }
tree() {  # tree <dir>: a scratch tree with what the build reads, copied from the lab clone this test runs from
  local d=$1 f
  mkdir -p "$d"
  for f in $E tools/claims-v3/e136/rgm136 tools/claims-v3/kinds/tiles/fp32/randn.bin tools/claims-v3/kinds/tiles/fp16/randn.bin \
           tools/claims-v3/kinds/tiles/int8/full.bin tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json; do
    mkdir -p "$d/$(dirname "$f")"; cp -rp "$SRC/$f" "$d/$f"
  done
}
echo "desktest_build_e190 on $(hostname), $(TZ=America/Los_Angeles date '+%F %T %Z'); /dev/et*: $(ls /dev/et* 2>&1 | head -n 1); /run/lock entries: $(ls /run/lock 2>/dev/null | wc -l)"
echo "toolchain: $(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1); $(c++ --version | head -n 1); $(cmake --version | head -n 1)"
echo; echo "== B1: the build as committed"
T1=$S/b1; tree "$T1"
( cd "$T1" && bash $E/build_e190.sh ) > "$S/b1.txt" 2>&1; r=$?
cat "$S/b1.txt" | grep -E '^(COMPILER|KERNEL|HOST|HOSTCHECK|RGM)'
rec=$(/usr/bin/python3 -I -B - "$T1/build/e190rgm/BUILD-e190.json" "$T1/build/e190rgm/host/sparsity_host" "$(hostname | cut -d. -f1)" "$(TZ=America/Los_Angeles date +%F)" <<'PY'
import hashlib, json, sys
r = json.load(open(sys.argv[1]))
h = hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest()
print("rec-ok" if (r["verdict"] == "BUILT" and r["box"] == sys.argv[3] and r["day"] == sys.argv[4] and r["host_sha256"] == h
                   and r["kernel_sha256"] == "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"
                   and len(r["host_checks"]) == 4 and all(c.endswith(":ok") for c in r["host_checks"])) else f"rec-bad {r}")
PY
)
ok "$r $(grep -c '^HOSTCHECK .*: ok$' "$S/b1.txt") $(grep -c '^RGM-BUILT rc=0$' "$S/b1.txt") $rec" "0 4 1 rec-ok" "$(grep '^KERNEL' "$S/b1.txt" | cut -c1-90)"
echo; echo "== B2: one rgm136 source changed, the harness as committed"
T2=$S/b2; tree "$T2"; echo "// changed" >> "$T2/tools/claims-v3/e136/rgm136/host/main.cpp"
( cd "$T2" && bash $E/build_e190.sh ) > "$S/b2.txt" 2>&1; r=$?
ok "$r $(grep -c "^RGM-BUILD-FAILED: rgm136's sources are not harness-e190.json's" "$S/b2.txt") $( [ -e "$T2/build/e190rgm/host/sparsity_host" ] && echo built || echo none)" "1 1 none" "$(grep '^RGM' "$S/b2.txt" | cut -c1-120)"
echo; echo "== B3: the kernel's source changed and the harness re-made to it"
T3=$S/b3; tree "$T3"
# one instruction more at the kernel's entry (an unused function would be dropped by the link: the ELF would not change)
/usr/bin/python3 -I -B - "$T3/tools/claims-v3/e136/rgm136/kernel/sparsity.c" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
old = "    const uint64_t t_entry = cycles();\n"
assert s.count(old) == 1
open(p, "w").write(s.replace(old, old + '    __asm__ volatile("nop");   /* E190 desk test B3 */\n'))
PY
( cd "$T3" && /usr/bin/python3 -I -B $E/check_e190.py --make > /dev/null && bash $E/build_e190.sh ) > "$S/b3.txt" 2>&1; r=$?
grep -E '^(KERNEL|RGM)' "$S/b3.txt" | cut -c1-160
ok "$r $(grep -c '^RGM-BUILD-FAILED: the kernel ELF .* is not the registration.s pin' "$S/b3.txt")" "1 1" "$(grep '^RGM' "$S/b3.txt" | cut -c1-140)"
echo; echo "== B4: the runner's box check on the B1 build (a stand-in reader file: it must stop there, and only there)"
mkdir -p "$T1/build/ettelem-hpl"; printf 'stand-in\n' > "$T1/build/ettelem-hpl/ettelem"
( cd "$T1" && /usr/bin/python3 -B - <<'PY'
import os, sys
sys.path.insert(0, "tools/claims-v3/e190")
import run_e190 as R
class A: pass
a = A(); a.arm = "A"; a.dry = False; a.out = os.path.abspath("build/e190/desk-boxcheck"); a.t0 = 0
s = R.Session(a)
why = s.box_check()
print("BOXCHECK " + why)
PY
) > "$S/b4.txt" 2>&1
cat "$S/b4.txt" | cut -c1-300
host=$(hostname | cut -d. -f1)
if [ "$host" = aifoundry2 ]; then
  ok "$(grep -c 'build/ettelem-hpl/ettelem: sha256 [0-9a-f]*, want 77a46171' "$S/b4.txt") $(grep -c 'sparsity.elf\|sparsity_host' "$S/b4.txt")" "1 0" "the box check stops at the reader's pin only"
else
  ok "$(grep -c "not arm A's 'aifoundry2'" "$S/b4.txt")" "1" "on $host the box check stops at the host name"
fi
echo
echo "DESKTEST-BUILD-E190 $npass of $ncase $([ "$npass" = "$ncase" ] && echo PASS || echo FAIL)"
[ "$npass" = "$ncase" ]
