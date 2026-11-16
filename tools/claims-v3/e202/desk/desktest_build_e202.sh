#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): THE BUILD'S DESK TEST on this desk's real toolchain (aifoundry2's
# /opt/et: cmake 3.28.3, riscv64-unknown-elf-gcc 15.1.0, g++ 13.3.0), E190's desktest_build form: build_e202.sh run AS IT IS in a
# stand-in box tree that holds harness-e202.json's files at their paths (what step 5's sync puts on the box), into an EMPTY
# build/e202files (so files_e202.sh FETCHES the four MNIST files from the program's mirrors and checks each by sha256, decompresses the
# trained weights from the registration's .gz, regenerates the random weights and the expected outputs, all 18 at their pins), then the
# host read by its behaviour (hostcheck_e202.py, every case opening no device). Then the negative controls:
#   B2 a synced source changed (one byte added to the kernel): refused at the harness, before anything is removed or built;
#   B3 the same change with the harness re-made in the stand-in: built, and refused at THE .text GATE;
#   B4 a second start with the files present: the files kept (no fetch), built again;
#   B5 the program's pins file with one wrong hash (harness re-made): the files step refuses, nothing recorded as built.
# Run it inside W/nodev.sh (the host's checks run the real binary; nodev hides /dev/et*), from a CPU slot.
#   bash tools/claims-v3/e202/desk/desktest_build_e202.sh <scratch dir outside the repo>
# Prints DESKTEST-BUILD-E202 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for d in /dev/et*; do
  [ -e "$d" ] || continue
  if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi
done
mkdir -p "$S" && S=$(cd "$S" && pwd -P)
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = 0 ]; then n=$((n + 1)); echo "PASS $2"; else echo "FAIL $2"; fi; }
mkbox() {  # mkbox <dir>: a stand-in box tree with the harness's files at their paths
  mkdir -p "$1"
  ( cd "$SRC" && /usr/bin/python3 -B tools/claims-v3/e202/check_e202.py --list; echo tools/claims-v3/e202/harness-e202.json ) |
    while read -r p; do mkdir -p "$1/$(dirname "$p")"; cp -p "$SRC/$p" "$1/$p"; done
}
echo "desktest_build_e202: $(date '+%F %T %Z'); $(c++ --version | head -n 1); $(/opt/et/bin/riscv64-unknown-elf-gcc --version | head -n 1); $(cmake --version | head -n 1)"
B=$S/box1; mkbox "$B"
t=$(date +%s); (cd "$B" && bash tools/claims-v3/e202/build_e202.sh) > "$S/b1.txt" 2>&1; rc=$?
sed -e "s|$S|<S>|g" -e "s|$HOME|~|g" "$S/b1.txt" | sed 's/^/    /'
grep -q '^E202-BUILT rc=0$' "$S/b1.txt" && [ "$rc" = 0 ]; ok $? "B1 the real build, AS IT IS: E202-BUILT rc=0 ($(( $(date +%s) - t )) s)"
grep -q "^E202 kernel: .*\.text sha256 ace7bcb04536329f1d75135446049c442b9f4b65f726083f7623b959b279d82d$" "$S/b1.txt"; ok $? "B1 the kernel's .text at E202.md's pin ace7bcb0... on this desk's toolchain"
grep -q 'fetch_mnist: t10k-labels-idx1-ubyte.gz and t10k-labels-idx1-ubyte OK' "$S/b1.txt" && grep -q 'E202-FILES OK: 18 of 18' "$S/b1.txt"; ok $? "B1 the files: MNIST FETCHED into an empty folder and checked by sha256; 18 of 18 at their pins"
grep -q 'HOST-BEHAVIOUR OK: 20 of 20' "$S/b1.txt"; ok $? "B1 the host by its behaviour: 20 of 20 (self-test, six refusals at parse, seven --dry plans, four --ref, the negative control, a wrong pin)"
/usr/bin/python3 -B - "$B" <<'PY'
import json, sys, hashlib, os
b = sys.argv[1]
r = json.load(open(os.path.join(b, "build/e202mnist/BUILD-E202.json")))
h = lambda p: hashlib.sha256(open(os.path.join(b, p), "rb").read()).hexdigest()
ok = r["built"] and r["host_sha256"] == h("build/e202mnist/host/mnistmlp_host") and r["elf_sha256"] == h("build/e202mnist/kernel/mnistmlp.elf")
print("record:", r["elf_sha256"][:16], r["text_sha256"][:16], r["host_sha256"][:16])
sys.exit(0 if ok else 1)
PY
ok $? "B1 the build record: the host's and the ELF's sha256 as built"
(cd "$B" && /usr/bin/python3 -B tools/claims-v3/e202/check_e202.py --box --built) > "$S/b1h.txt" 2>&1
grep -q '^HARNESS OK: 33 files$' "$S/b1h.txt"; ok $? "B1 the harness with the built kernel (step 6's box read): $(cat "$S/b1h.txt")"
# B2: a synced source changed, the harness not re-made
B2=$S/box2; mkbox "$B2"; printf '\n' >> "$B2/workloads/mnistmlp/kernel/mnistmlp.c"
(cd "$B2" && bash tools/claims-v3/e202/build_e202.sh) > "$S/b2.txt" 2>&1; rc=$?
[ "$rc" != 0 ] && grep -q '^E202-BUILD-FAILED: the synced files differ' "$S/b2.txt" && [ ! -d "$B2/build/e202mnist" ]; ok $? "B2 a changed source: refused at the harness, nothing built"
# B3: a different kernel with the harness re-made: the .text gate
B3=$S/box3; mkbox "$B3"
/usr/bin/python3 - "$B3/workloads/mnistmlp/kernel/mnistmlp.c" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
j = s.index("{", s.index("int64_t entry_point(const struct MlpArgs* args)", s.index("int64_t entry_point(const struct MlpArgs* args)") + 10))
s = s[:j + 1] + "\n  __asm__ volatile(\"nop\");   /* the desk test's negative control: one more instruction */" + s[j + 1:]
open(p, "w").write(s)
PY
(cd "$B3" && /usr/bin/python3 -B tools/claims-v3/e202/check_e202.py --make > /dev/null && bash tools/claims-v3/e202/build_e202.sh) > "$S/b3.txt" 2>&1; rc=$?
[ "$rc" != 0 ] && grep -q "^E202-BUILD-FAILED: the kernel's .text sha256" "$S/b3.txt" && [ ! -e "$B3/build/e202mnist/BUILD-E202.json" ]; ok $? "B3 a different kernel: built, refused at the .text gate, no record ($(grep -m1 '^E202-BUILD-FAILED' "$S/b3.txt" | cut -c1-90))"
# B4: a second start with the files present
(cd "$B" && bash tools/claims-v3/e202/build_e202.sh) > "$S/b4.txt" 2>&1; rc=$?
[ "$rc" = 0 ] && grep -q '^E202-BUILT rc=0$' "$S/b4.txt" && ! grep -q 'from .* failed' "$S/b4.txt"; ok $? "B4 a second start: the files kept at their pins, built again"
# B5: a wrong pin in the program's pins file (harness re-made)
B5=$S/box5; mkbox "$B5"
mkdir -p "$B5/build"; cp -a "$B/build/e202files" "$B5/build/"
sed -i 's/^82d3f71f/00000000/' "$B5/workloads/mnistmlp/model/PINS-SHA256SUMS"
(cd "$B5" && /usr/bin/python3 -B tools/claims-v3/e202/check_e202.py --make > /dev/null && bash tools/claims-v3/e202/build_e202.sh) > "$S/b5.txt" 2>&1; rc=$?
[ "$rc" != 0 ] && grep -q '^E202-BUILD-FAILED: the files: E202-FILES-FAILED' "$S/b5.txt" && [ ! -e "$B5/build/e202mnist/BUILD-E202.json" ]; ok $? "B5 a wrong pin: the files step refuses, no record ($(grep -m1 'E202-FILES-FAILED' "$S/b5.txt" | cut -c1-100))"
echo "DESKTEST-BUILD-E202 $n of $m $([ "$n" = "$m" ] && echo PASS || echo FAIL)"
[ "$n" = "$m" ]
