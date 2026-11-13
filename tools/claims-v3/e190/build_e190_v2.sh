#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): the box build v2, build_e190.sh (the kit,
# unchanged beside it) with ONE addition, the verifier's finding 1: on aifoundry1 (arm B, card 1) the host must honour ET_DEVICES. The
# lab's own gates read it the same way (workloads/pciebench/run_pcie.sh; tools/lab/dashboard/remote.sh): aifoundry1's device layer, the one
# that honours ET_DEVICES, carries its name, the stock library has none, and a host built against the stock library opens card 0 as device
# 0 whatever ET_DEVICES says. So on aifoundry1 the build is refused unless
#   - the host binary holds the string ET_DEVICES (grep -a),
#   - /opt/et/lib/libdeviceLayer.a holds it, and
#   - the build's CMakeCache.txt took the device layer from /opt/et (deviceLayer_DIR:PATH=/opt/et/...).
# On aifoundry2 (arm A, one card) the reading is recorded, never a gate. Run from the box tree's root by step 6 v2 (rb/s08_build_e190_v2.sh)
# on each arm's box, or at the desk by the build's desk test v2 (in a sandbox). Otherwise as build_e190.sh:
#   1. the sources: tools/claims-v3/e136/rgm136's ten files at harness-e190-v2.json's sha256 (check_e190_v2.py --box --only-src), else no build;
#   2. cmake against the box's /opt/et (nice 10, -j2), the compilers recorded;
#   3. THE KERNEL BY ITS BYTES: build/e190rgm/kernel/sparsity.elf at the registration's pin aace138c..., its .text's sha256 recorded;
#   4. THE HOST BY ITS BEHAVIOUR: four refusals main.cpp makes before it builds its device Session (no device is opened), each under
#      `timeout 10` with stdin from /dev/null; on aifoundry1 with ET_DEVICES=1 set all the same;
#   5. THE ET_DEVICES READING (above);
#   6. build/e190rgm/BUILD-e190.json, now with "builder": "build_e190_v2.sh" and "et_devices" (run_e190_v2.py's box check refuses a record
#      without them, and on arm B one whose "et_devices" is not the passing reading); the last line RGM-BUILT rc=0, or RGM-BUILD-FAILED: <why>.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
B=build/e190rgm
SRC=tools/claims-v3/e136/rgm136
PIN=aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0
BOX=$(hostname | cut -d. -f1)
DAY=$(TZ=America/Los_Angeles date +%F)
PY=${E190_PY:-python3}
DL=/opt/et/lib/libdeviceLayer.a
fail() { echo "RGM-BUILD-FAILED: $*"; "$PY" -B - "$B/BUILD-e190.json" "$BOX" "$DAY" "$*" <<'PY'
import json, sys, time
p, box, day, why = sys.argv[1:5]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILD-FAILED", "why": why, "builder": "build_e190_v2.sh"},
          open(p, "w"), indent=1)
PY
exit 1; }
mkdir -p "$B" || { echo "RGM-BUILD-FAILED: cannot make $B"; exit 1; }
unset V3_DEVICE ET_DEVICES
echo "== E190 build v2 on $BOX, $(TZ=America/Los_Angeles date '+%F %T %Z'), into $B"
"$PY" -B tools/claims-v3/e190/check_e190_v2.py --box --only-src || fail "rgm136's sources are not harness-e190-v2.json's"
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
# note 1: THE ET_DEVICES READING (a gate on aifoundry1 only)
ev_host=no; grep -aq ET_DEVICES "$H" && ev_host=yes
ev_lib=no; [ -f "$DL" ] && grep -aq ET_DEVICES "$DL" && ev_lib=yes
ev_cache=no; grep -q '^deviceLayer_DIR:PATH=/opt/et/' "$B/CMakeCache.txt" 2>/dev/null && ev_cache=yes
echo "ETDEVICES host $ev_host; $DL $ev_lib; CMakeCache deviceLayer_DIR from /opt/et $ev_cache"
if [ "$BOX" = aifoundry1 ]; then
  [ "$ev_host" = yes ] || fail "ET_DEVICES: the host has no ET_DEVICES (built against a device layer that ignores it: it would open card 0)"
  [ "$ev_lib" = yes ] || fail "ET_DEVICES: $DL has no ET_DEVICES"
  [ "$ev_cache" = yes ] || fail "ET_DEVICES: the build did not take its device layer from /opt/et (CMakeCache.txt)"
  ETDEV="the host and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"
else
  ETDEV="not a gate on $BOX (one card): host $ev_host, libdeviceLayer.a $ev_lib, CMakeCache $ev_cache"
fi
"$PY" -B - "$B/BUILD-e190.json" "$BOX" "$DAY" "$ELFS" "$TXT" "$HOSTS" "$KCC" "$HCC" "$checks" "$ETDEV" <<'PY' || fail "the record"
import json, sys, time
p, box, day, elf, txt, host, kcc, hcc, checks, etdev = sys.argv[1:11]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernel_sha256": elf, "kernel_text_sha256": txt or None,
           "host_sha256": host, "kernel_pin": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
           "compilers": {"kernel": kcc, "host": hcc}, "host_checks": checks.split(), "source": "tools/claims-v3/e136/rgm136 (harness-e190-v2.json)",
           "builder": "build_e190_v2.sh", "et_devices": etdev,
           "what": "E190's build of E136's rgm136, unchanged (build_e190_v2.sh: build_e190.sh and the ET_DEVICES reading)"}, open(p, "w"), indent=1)
PY
echo "RGM-BUILT rc=0"
