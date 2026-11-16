#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): THE BOX BUILD, the body of step 6's detached job a3-build-e202 on
# aifoundry3 (run from the tree's root, ~/aifoundry; no device opened). E189's build_e189.sh form:
#   1. the synced files at harness-e202.json's sha256 (check_e202.py --box), else nothing is built;
#   2. workloads/mnistmlp built against the installed ET tree into E202's own directory, build/e202mnist (the program's README recipe:
#      cmake -S workloads/mnistmlp -B build/e202mnist -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev; cmake --build -j4 at nice 10), each phase
#      bounded (`timeout -k 15`: a build opens no device);
#   3. THE KERNEL BY ITS .text (E202.md 2: "record a kernel by its .text"; the kit builds on aifoundry3 and refuses any other .text):
#      `objcopy -O binary -j .text` sha256 must be ace7bcb0...; the ELF's sha256 is reported beside E202.md's aifoundry3 build
#      (0f74ff0d...), never judged (the boxes' RISC-V GCC builds carry different version strings);
#   4. THE FILES (files_e202.sh): MNIST fetched on the box and checked by sha256, the trained weights from the registration's .gz, the
#      random weights and the expected outputs regenerated, all 18 at their pins;
#   5. THE HOST BY ITS BEHAVIOUR (hostcheck_e202.py, never a string grepped from a binary): its CPU self-test, its refusals at parse
#      (each carrying a missing pins file as a second refusal before any device), its --dry plans of every registered launch, its
#      reference of the kernel's arithmetic against the expected files (--ref), and a negative control;
#   6. the record build/e202mnist/BUILD-E202.json (the host's, the ELF's and the .text's sha256, the compilers, the files' line), which
#      the session checks before it opens anything.
# Verdict lines: E202-BUILT rc=0, or E202-BUILD-FAILED: <why> (then no session that day without a second start; E202.md 12's build
# count is step 6's). No desk-test knob: the runbook's desk test runs this file as it is, with the desk's own /opt/et.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
PREFIX=/opt/et; OBJCOPY=/opt/et/bin/riscv64-unknown-elf-objcopy
[ -x "$OBJCOPY" ] || OBJCOPY=$(command -v objcopy || echo objcopy)
B=build/e202mnist
ELF=$B/kernel/mnistmlp.elf; HOST=$B/host/mnistmlp_host
TEXT_PIN=ace7bcb04536329f1d75135446049c442b9f4b65f726083f7623b959b279d82d
fail() { echo "E202-BUILD-FAILED: $*"; exit 1; }
echo "COMPILER host: $(c++ --version 2>/dev/null | head -n 1)"
echo "COMPILER riscv: $("$PREFIX"/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)"
echo "COMPILER cmake: $(cmake --version 2>/dev/null | head -n 1)"
python3 -B tools/claims-v3/e202/check_e202.py --box || fail "the synced files differ from harness-e202.json"
case "$B" in build/e202mnist) ;; *) fail "not E202's build directory: $B" ;; esac
rm -rf "./${B:?}"
mkdir -p "$B"
timeout -k 15 300 cmake -S workloads/mnistmlp -B "$B" -DCMAKE_PREFIX_PATH="$PREFIX" -Wno-dev > "$B/configure.log" 2>&1 ||
  fail "cmake configure (its log: $B/configure.log): $(tail -n 3 "$B/configure.log" | tr '\n' ' ' | cut -c1-200)"
timeout -k 15 500 nice -n 10 cmake --build "$B" -j4 > "$B/build.log" 2>&1 ||
  fail "cmake build (its log: $B/build.log): $(grep -m3 -iE 'error' "$B/build.log" | tr '\n' ' ' | cut -c1-200)"
[ -s "$ELF" ] && [ -x "$HOST" ] || fail "no kernel or no host after the build"
e=$(sha256sum "$ELF" | cut -c1-64)
t=$("$OBJCOPY" -O binary -j .text "$ELF" /dev/stdout 2>/dev/null | sha256sum | cut -c1-64)
echo "E202 kernel: ELF sha256 $e (E202.md's aifoundry3 build 0f74ff0d...: reported, not gated), .text sha256 $t"
[ "$t" = "$TEXT_PIN" ] || fail "the kernel's .text sha256 $t is not E202.md's $TEXT_PIN"
echo "E202 warnings: $(grep -ciE 'warning:' "$B/build.log") compiler warning line(s) in the build log"
fl=$(bash tools/claims-v3/e202/files_e202.sh build/e202files 2>&1)
echo "$fl" | sed 's/^/  /' | tail -n 12
echo "$fl" | grep -q '^E202-FILES OK' || fail "the files: $(echo "$fl" | grep -m1 '^E202-FILES-FAILED' | cut -c1-200)"
hc=$(LD_LIBRARY_PATH=/opt/et/lib python3 -B tools/claims-v3/e202/hostcheck_e202.py "$HOST" build/e202files 2>&1)
echo "$hc" | sed 's/^/  /' | tail -n 30
case "$(echo "$hc" | tail -n 1)" in "HOST-BEHAVIOUR OK"*) ;; *) fail "the host's behaviour: $(echo "$hc" | tail -n 1 | cut -c1-200)" ;; esac
python3 -B - "$B/BUILD-E202.json" "$(sha256sum "$HOST" | cut -c1-64)" "$e" "$t" "$(echo "$fl" | grep -m1 '^E202-FILES OK')" \
  "$(echo "$hc" | tail -n 1)" "$(c++ --version 2>/dev/null | head -n 1)" "$("$PREFIX"/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)" <<'PY'
import json, sys, time
p, h, e, t, fl, hc, cxx, rv = sys.argv[1:9]
json.dump({"built": True, "written": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "host": "build/e202mnist/host/mnistmlp_host",
           "host_sha256": h, "elf": "build/e202mnist/kernel/mnistmlp.elf", "elf_sha256": e, "text_sha256": t,
           "files": fl, "host_behaviour": hc, "compiler_host": cxx, "compiler_riscv": rv}, open(p, "w"), indent=1)
PY
[ -s "$B/BUILD-E202.json" ] || fail "the build record was not written"
echo "E202-BUILT rc=0"
exit 0
