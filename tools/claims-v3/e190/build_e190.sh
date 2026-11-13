#!/usr/bin/env bash
# E190 (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): the box build, run from the box tree's root by step 6 (rb/s08_build_e190.sh)
# on each arm's box (aifoundry2 ~/claude/et-soc1-prototyping, aifoundry1 ~/nekko), or at the desk by the kit's desk test (in a sandbox).
# E136's rgm136 UNCHANGED (E190.md section 2) into build/e190rgm, a new folder of ours:
#   1. the sources: tools/claims-v3/e136/rgm136's ten files at harness-e190.json's sha256 (check_e190.py --box --only-src), else no build;
#   2. cmake against the box's /opt/et (nice 10, -j2), the compilers recorded;
#   3. THE KERNEL BY ITS BYTES: build/e190rgm/kernel/sparsity.elf at the registration's pin aace138c... (E136's build record; reproduced by
#      reg-e190 on aifoundry2 and by this kit's desk build on aifoundry1, Fri 13 Nov 2026: byte-identical), its .text's sha256 recorded;
#   4. THE HOST BY ITS BEHAVIOUR, never by its bytes (they carry its build path): four refusals main.cpp makes before it builds its device
#      Session, so no device is opened, each under `timeout 10` with stdin from /dev/null: an unknown option (rc 2, "unknown option"), a zero
#      shire mask (rc 2, "bad --shires / --per-shire"), an unreadable kernel (rc 1, "cannot read kernel"), an unknown test (rc 2, "--test
#      must be fma, tload, gemv, diverge or spin"); on aifoundry1 with ET_DEVICES=1 set all the same (card 1 only, were anything opened);
#   5. build/e190rgm/BUILD-e190.json: the box, the Pacific day, the compilers, the kernel's and .text's sha256, the host's sha256 (the session's
#      runner checks the host against it, and the kernel against the pin), each check, the verdict; the last line RGM-BUILT rc=0, or
#      RGM-BUILD-FAILED: <why>.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
B=build/e190rgm
SRC=tools/claims-v3/e136/rgm136
PIN=aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0
BOX=$(hostname | cut -d. -f1)
DAY=$(TZ=America/Los_Angeles date +%F)
PY=${E190_PY:-python3}
fail() { echo "RGM-BUILD-FAILED: $*"; "$PY" -B - "$B/BUILD-e190.json" "$BOX" "$DAY" "$*" <<'PY'
import json, sys, time
p, box, day, why = sys.argv[1:5]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILD-FAILED", "why": why}, open(p, "w"), indent=1)
PY
exit 1; }
mkdir -p "$B" || { echo "RGM-BUILD-FAILED: cannot make $B"; exit 1; }
unset V3_DEVICE ET_DEVICES
echo "== E190 build on $BOX, $(TZ=America/Los_Angeles date '+%F %T %Z'), into $B"
"$PY" -B tools/claims-v3/e190/check_e190.py --box --only-src || fail "rgm136's sources are not harness-e190.json's"
KCC=$(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)
HCC=$(c++ --version 2>/dev/null | head -n 1)
echo "COMPILER kernel: ${KCC:-none}; host: ${HCC:-none}"
nice -n 10 cmake -S "$SRC" -B "$B" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > "$B/cmake.log" 2>&1 || fail "cmake (see $B/cmake.log)"
nice -n 10 cmake --build "$B" -j2 > "$B/build.log" 2>&1 || fail "the build (see $B/build.log)"
ELFS=$(sha256sum "$B/kernel/sparsity.elf" 2>/dev/null | cut -c1-64)
HOSTS=$(sha256sum "$B/host/sparsity_host" 2>/dev/null | cut -c1-64)
TXT=""
OC=/opt/et/bin/riscv64-unknown-elf-objcopy
if [ -x "$OC" ] && "$OC" -O binary -j .text "$B/kernel/sparsity.elf" "$B/kernel/text.bin" 2>/dev/null; then TXT=$(sha256sum "$B/kernel/text.bin" | cut -c1-64); fi
echo "KERNEL $ELFS (pin $PIN); .text ${TXT:-unread}"
echo "HOST $HOSTS"
[ "$ELFS" = "$PIN" ] || fail "the kernel ELF $ELFS is not the registration's pin $PIN"
[ -n "$HOSTS" ] || fail "no host was built"
EV=(); [ "$BOX" = aifoundry1 ] && EV=(ET_DEVICES=1)
H=$B/host/sparsity_host
checks=""
chk() {  # chk <name> <want rc> <want text> <args...>: a refusal before any device opens
  local name=$1 wrc=$2 wtxt=$3; shift 3
  env ${EV[@]+"${EV[@]}"} timeout 10 "$H" "$@" < /dev/null > "$B/check-$name.out" 2> "$B/check-$name.err"
  local rc=$?
  if [ "$rc" -eq "$wrc" ] && grep -qF -- "$wtxt" "$B/check-$name.err"; then echo "HOSTCHECK $name: rc $rc, '$wtxt': ok"; checks="$checks $name:ok"
  else echo "HOSTCHECK $name: rc $rc (want $wrc), stderr '$(head -c 160 "$B/check-$name.err" | tr '\n' ' ')': FAILED"; checks="$checks $name:FAILED"; fi
}
chk unknown-option 2 "unknown option --no-such-option" --no-such-option
chk zero-shires 2 "bad --shires / --per-shire" --shires 0 --kernel "$B/kernel/sparsity.elf"
chk no-kernel 1 "cannot read kernel" --kernel "$B/kernel/no-such-kernel.elf"
chk unknown-test 2 "--test must be fma, tload, gemv, diverge or spin" --test no-such-test --kernel "$B/kernel/sparsity.elf"
case "$checks" in *FAILED*) fail "the host's behaviour:$checks" ;; esac
"$PY" -B - "$B/BUILD-e190.json" "$BOX" "$DAY" "$ELFS" "$TXT" "$HOSTS" "$KCC" "$HCC" "$checks" <<'PY' || fail "the record"
import json, sys, time
p, box, day, elf, txt, host, kcc, hcc, checks = sys.argv[1:10]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernel_sha256": elf, "kernel_text_sha256": txt or None,
           "host_sha256": host, "kernel_pin": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
           "compilers": {"kernel": kcc, "host": hcc}, "host_checks": checks.split(), "source": "tools/claims-v3/e136/rgm136 (harness-e190.json)",
           "what": "E190's build of E136's rgm136, unchanged (build_e190.sh)"}, open(p, "w"), indent=1)
PY
echo "RGM-BUILT rc=0"
