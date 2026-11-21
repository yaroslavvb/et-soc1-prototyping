#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): E224's second build on aifoundry2, RIGHT AFTER E208's src/build_mms.sh
# (unchanged: rgm136 and the reader into build/rgm and build/ettelem, its record build/BUILD-mms.json): rgm211's HOST for family G, from E211's
# rgm211 sources in src/rgm211 (each at kernel-e224.json's pin), into build/e224brgm211 (a folder of E224's own), in E208's build form:
#  1. THE SOURCES: the ten files of src/rgm211 at kernel-e224.json > kernels > rgm211 > sources_sha256 (E211's committed bytes); else no build;
#  2. cmake against /opt/et (Unix Makefiles, nice 10, 2 jobs, each step under a plain `timeout 900`), the compilers recorded;
#  3. THE HOST BY ITS BEHAVIOUR, each run INSIDE a bubblewrap with no /dev/et* node and an empty /run/lock (W/nodev.sh's form: the card is on
#     this box): E208's four refusals main.cpp makes before it opens a device, and rgm211's four early refusals (validateArm, before the
#     device Session: an arm missing its KB, --per-shire 16, a missing tile, an unknown gen), each with rgm136's ELF as --kernel and a
#     gemmLnc arm where an arm is given; none may reach the device stage (no "[RUNTIME]" line);
#  4. THE ELF FAMILY G RUNS: rgm136's build/rgm/kernel/sparsity.elf (E208's build) passes src/ident_e224b.py's gate for 'rgm136 gemmLnc'
#     and 'rgm136 gemmL' (the .text and the whole ELF at the pins), and src/ident_e224b.py --check reads CHECK PASS; rgm211's own ELF
#     (built beside its host, never run in E224) is recorded with whether it is E211's whole-ELF pin, and must FAIL both gates;
#  5. build/BUILD-e224b.json (src/run_e224b.py's box check refuses any other record, or one not written today on this box); the last line
#     E224-BUILT rc=0, or E224-BUILD-FAILED: <why>.
# Refused at once (E224-BUILD-REFUSED, exit 3, the record untouched) while run/box.lock is held (a session, a dry pass or a build of the kit)
# or while any card of this box is held or measured or a CI job runs (E208's rule: no host compute beside a card run), or without E208's
# build of today (build/BUILD-mms.json BUILT today). It holds run/box.lock from its first check to its end.
#   bash <root>/src/build_e224b.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
BOX=$(hostname | cut -d. -f1)
DAY=$(TZ=America/Los_Angeles date +%F)
B=build/e224brgm211
BWRAP=/usr/bin/bwrap
quiet_box() {
  local chk=9 devn cin
  if command -v et-who > /dev/null 2>&1; then timeout 20 et-who --check > /dev/null 2>&1; chk=$?; fi
  devn=$(ps -eo comm= | grep -Ec '(_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$)')
  cin=$(ps -eo comm= | grep -c '^Runner\.Worker$')
  if [ "$chk" -ne 0 ] || [ "$devn" -ne 0 ] || [ "$cin" -ne 0 ]; then
    echo "a card of this box is held or measured, or a CI job runs (et-who --check rc $chk: 0 free, 1 held, 2 failed, 9 no et-who; device processes $devn; CI jobs $cin)"
    return 1
  fi
  return 0
}
mkdir -p build run
exec 9>>run/box.lock
if ! flock -n 9; then echo "E224-BUILD-REFUSED: run/box.lock is held (a session, a dry pass or a build of this kit runs on this box)"; exit 3; fi
WHY=$(quiet_box) || { echo "E224-BUILD-REFUSED: $WHY: no build now"; exit 3; }
[ "$BOX" = aifoundry2 ] || { echo "E224-BUILD-REFUSED: this is $BOX, E224's card is on aifoundry2"; exit 3; }
fail() { echo "E224-BUILD-FAILED: $*"; /usr/bin/python3 -I -B - build/BUILD-e224b.json "$BOX" "$DAY" "$*" <<'PY'
import json, sys, time
p, box, day, why = sys.argv[1:5]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILD-FAILED", "why": why}, open(p, "w"), indent=1)
PY
exit 1; }
unset V3_DEVICE ET_DEVICES
echo "== E224's build of rgm211's host on $BOX, $(TZ=America/Los_Angeles date '+%F %T %Z')"
M=$(/usr/bin/python3 -I -B - "$DAY" <<'PY'
import json, sys
r = json.load(open("build/BUILD-mms.json"))
print("ok" if r.get("verdict") == "BUILT" and r.get("day") == sys.argv[1] else f"E208's build record reads {r.get('verdict')} of {r.get('day')}")
PY
)
[ "$M" = ok ] || fail "no E208 build of today before it (src/build_mms.sh first): $M"
SRCOK=$(/usr/bin/python3 -I -B - <<'PY'
import hashlib, json, os
k = json.load(open("src/kernel-e224.json"))["kernels"]["rgm211_host"]["sources_sha256"]
bad = []
for rel, want in sorted(k.items()):
    p = "src/rgm211/" + rel.split("tools/claims-v3/e211/rgm211/", 1)[1]
    got = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else "missing"
    if got != want:
        bad.append(f"{p} {got[:16]} (want {want[:16]})")
print("SOURCES OK: 10 of 10 at kernel-e224.json's pins" if not bad and len(k) == 10 else "SOURCES DIFFER: " + "; ".join(bad))
PY
)
echo "$SRCOK"
case "$SRCOK" in "SOURCES OK"*) ;; *) fail "the rgm211 sources: $SRCOK" ;; esac
KCC=$(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)
HCC=$(c++ --version 2>/dev/null | head -n 1)
echo "COMPILER kernel: ${KCC:-none}; host: ${HCC:-none}"
rm -rf -- "${B:?}"
timeout 900 nice -n 10 cmake -G "Unix Makefiles" -S src/rgm211 -B "$B" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/e224brgm211-cmake.log 2>&1 || fail "cmake rgm211 (build/e224brgm211-cmake.log)"
timeout 900 nice -n 10 cmake --build "$B" -j2 > build/e224brgm211-build.log 2>&1 || fail "the rgm211 build (build/e224brgm211-build.log)"
H=$B/host/sparsity_host
K=build/rgm/kernel/sparsity.elf
K211=$B/kernel/sparsity.elf
[ -x "$H" ] || fail "no rgm211 host was built"
HOSTS=$(sha256sum "$H" | cut -c1-64)
E211S=$(sha256sum "$K211" 2>/dev/null | cut -c1-64)
echo "HOST rgm211 $HOSTS"
echo "rgm211's own ELF (never run in E224) ${E211S:-none}"
T=src/tiles/fp32/randn.bin
checks=""
chk() {  # chk <name> <want rc> <want text> <args...>: a refusal before any device opens, inside the sandbox
  local name=$1 wrc=$2 wtxt=$3; shift 3
  local o="build/e224b-check-$name"
  timeout 10 "$BWRAP" --dev-bind / / --dev /dev --tmpfs /run/lock --die-with-parent -- "$H" "$@" < /dev/null > "$o.out" 2> "$o.err"
  local rc=$?
  if [ "$rc" -eq "$wrc" ] && grep -qF -- "$wtxt" "$o.err" && ! grep -qF -- "[RUNTIME]" "$o.out" "$o.err"; then
    echo "HOSTCHECK rgm211 $name: rc $rc, '$wtxt', before the device stage: ok"; checks="$checks $name:ok"
  else
    echo "HOSTCHECK rgm211 $name: rc $rc (want $wrc), stderr '$(head -c 160 "$o.err" | tr '\n' ' ')': FAILED"; checks="$checks $name:FAILED"
  fi
}
A=(--test fma --type fp32 --pattern none --shires 0xffffffff --per-shire 32 --seed 1 --kernel "$K")
chk unknown-option 2 "unknown option --no-such-option" --no-such-option
chk zero-shires 2 "bad --shires / --per-shire" --shires 0 --kernel "$K"
chk no-kernel 1 "cannot read kernel" --kernel build/rgm/kernel/no-such-kernel.elf
chk unknown-test 2 "--test must be fma, tload, gemv, diverge or spin" --test no-such-test --kernel "$K"
chk arm-missing-kb 1 "want gemmL<MB>x<NB>x<KB>" "${A[@]}" --values "gemmLnc2x2:randn:$T"
chk per-shire-16 1 "gemm needs --per-shire 32" --test fma --type fp32 --pattern none --shires 0xffffffff --per-shire 16 --seed 1 --kernel "$K" --values "gemmLnc2x2x2:randn:$T"
chk missing-tile 1 "cannot read 2 x 1024 bytes" "${A[@]}" --values "gemmLnc2x2x2:randn:src/tiles/fp32/no-such-tile.bin"
chk unknown-gen 1 "unknown gen" "${A[@]}" --values "gemmLnc2x2x2:noise:$T"
case "$checks" in *FAILED*) fail "the host's behaviour:$checks" ;; esac
G1=$(/usr/bin/python3 -I -B src/ident_e224b.py --gate "rgm136 gemmLnc" "$K" 2>&1 | tail -n 1)
G2=$(/usr/bin/python3 -I -B src/ident_e224b.py --gate "rgm136 gemmL" "$K" 2>&1 | tail -n 1)
G3=$(/usr/bin/python3 -I -B src/ident_e224b.py --gate "rgm136 gemmLnc" "$K211" 2>&1 | tail -n 1)
G4=$(/usr/bin/python3 -I -B src/ident_e224b.py --gate "rgm136 gemmL" "$K211" 2>&1 | tail -n 1)
IC=$(/usr/bin/python3 -I -B src/ident_e224b.py --check 2>&1 | tail -n 1)
echo "GATE rgm136's ELF for 'rgm136 gemmLnc': $G1"
echo "GATE rgm136's ELF for 'rgm136 gemmL': $G2"
echo "GATE rgm211's own ELF for 'rgm136 gemmLnc' (must fail): $G3"
echo "GATE rgm211's own ELF for 'rgm136 gemmL' (must fail): $G4"
echo "IDENT CHECK: $IC"
case "$G1" in "GATE OK: "*) ;; *) fail "rgm136's ELF does not pass for family G: $G1" ;; esac
case "$G2" in "GATE OK: "*) ;; *) fail "rgm136's ELF does not pass for 'rgm136 gemmL': $G2" ;; esac
case "$G3" in "GATE FAILED: "*) ;; *) fail "rgm211's ELF passed for family G: $G3" ;; esac
case "$G4" in "GATE FAILED: "*) ;; *) fail "rgm211's ELF passed for 'rgm136 gemmL': $G4" ;; esac
[ "$IC" = "CHECK PASS" ] || fail "the identity gate's check: $IC"
/usr/bin/python3 -I -B - build/BUILD-e224b.json "$BOX" "$DAY" "$HOSTS" "${E211S:-}" "$KCC" "$HCC" "$checks" "$G1" <<'PY' || fail "the record"
import json, sys, time
p, box, day, host, e211, kcc, hcc, checks, g1 = sys.argv[1:10]
k = json.load(open("src/kernel-e224.json"))["kernels"]["rgm211_host"]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILT", "host_sha256": host,
           "host": "build/e224brgm211/host/sparsity_host", "host_checks": checks.split(),
           "rgm211_elf_sha256": e211 or None, "rgm211_elf_is_e211_whole_pin": e211 == k["elf_sha256"],
           "rgm211_elf_never_run": "E224 runs rgm136's ELF on rgm211's host (family G); rgm211's ELF is built beside its host and refused by the gate",
           "family_g_elf": "build/rgm/kernel/sparsity.elf", "family_g_gate": g1,
           "sources": "src/rgm211 at kernel-e224.json > kernels > rgm211_host > sources_sha256 (10 of 10)",
           "compilers": {"kernel": kcc, "host": hcc}, "builder": "src/build_e224b.sh",
           "what": "E224: E211's rgm211 host for family G, after E208's build_mms.sh"}, open(p, "w"), indent=1)
PY
echo "E224-BUILT rc=0"
