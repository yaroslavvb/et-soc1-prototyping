#!/usr/bin/env bash
# 1119-mmsweep5: the box build (E190's build form, tools/claims-v3/e190/build_e190_v2.sh in the public lab repo), from the kit's
# root on each box, at nice 10 with 1 job (single-threaded: the lab's host rule since aifoundry2's crash of 17 Nov keeps every
# host job single-threaded and the box's load under 6); writes nothing outside the kit's folder.
#   bash ~/claude/work/ee-1119-mmsweep5/src/build_mms.sh
#  1. the sources at src/SRC-SHA256SUMS (src/check_mms.py --box --only-src): src/rgm136 (E136's rgm136, unchanged) and
#     src/ettelem (the lab's tools/ettelem reader, unchanged); else no build;
#  2. cmake against the box's /opt/et into build/rgm and build/ettelem, the compilers recorded;
#  3. THE KERNEL BY ITS BYTES: build/rgm/kernel/sparsity.elf at E136's build record's sha256 (aace138c..., reproduced on both
#     lab boxes by E190's kit), its .text recorded;
#  4. THE HOST BY ITS BEHAVIOUR: four refusals main.cpp makes before it opens a device, each under `timeout 10`;
#  5. THE ET_DEVICES READING, a gate on aifoundry1 (two cards): the host, the reader and /opt/et/lib/libdeviceLayer.a carry the
#     string ET_DEVICES and both builds took their device layer from /opt/et (the lab's own gates read it so); else a host that
#     ignored ET_DEVICES would open card 0 whatever the session asked;
#  6. build/BUILD-mms.json (the runner refuses any other record, or one not written today on this box); the last line
#     MMS-BUILT rc=0, or MMS-BUILD-FAILED: <why>. It refuses at once (MMS-BUILD-REFUSED, exit 3, the record untouched) while
#     the kit's box lock run/box.lock is held (a session, a dry pass or another build of the kit: a build never replaces what a
#     running session uses), and while any card of this box is held or measured by anyone (the lab's rule: no host compute
#     beside a card run). It holds run/box.lock itself from its first check to its end, so no session or dry pass of the kit
#     starts beside the compile jobs. The generator is pinned (Unix Makefiles), so the kernel's sub-build shares make's 1 job.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
PIN=aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0
BOX=$(hostname | cut -d. -f1)
DAY=$(TZ=America/Los_Angeles date +%F)
DL=/opt/et/lib/libdeviceLayer.a
# No host compute beside a card run (the lab's rule): refused unless et-who --check reads every card of this box free and no
# device process (anyone's) and no CI job runs here.
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
exec 9>>run/box.lock    # held (fd 9, inherited by the build's own processes) until this script ends
if ! flock -n 9; then echo "MMS-BUILD-REFUSED: run/box.lock is held (a session, a dry pass or a build of this kit runs on this box): no build under it"; exit 3; fi
WHY=$(quiet_box) || { echo "MMS-BUILD-REFUSED: $WHY: no build now"; exit 3; }
fail() { echo "MMS-BUILD-FAILED: $*"; python3 -B - build/BUILD-mms.json "$BOX" "$DAY" "$*" <<'PY'
import json, sys, time
p, box, day, why = sys.argv[1:5]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILD-FAILED", "why": why}, open(p, "w"), indent=1)
PY
exit 1; }
unset V3_DEVICE ET_DEVICES
echo "== 1119-mmsweep5 build on $BOX, $(TZ=America/Los_Angeles date '+%F %T %Z')"
python3 -B src/check_mms.py --box --only-src || fail "the sources are not src/SRC-SHA256SUMS's"
KCC=$(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)
HCC=$(c++ --version 2>/dev/null | head -n 1)
echo "COMPILER kernel: ${KCC:-none}; host: ${HCC:-none}"
nice -n 10 cmake -G "Unix Makefiles" -S src/rgm136 -B build/rgm -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/rgm-cmake.log 2>&1 || fail "cmake rgm (build/rgm-cmake.log)"
nice -n 10 cmake --build build/rgm -j1 > build/rgm-build.log 2>&1 || fail "the rgm build (build/rgm-build.log)"
nice -n 10 cmake -G "Unix Makefiles" -S src/ettelem -B build/ettelem -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/ettelem-cmake.log 2>&1 || fail "cmake ettelem (build/ettelem-cmake.log)"
nice -n 10 cmake --build build/ettelem -j1 > build/ettelem-build.log 2>&1 || fail "the ettelem build (build/ettelem-build.log)"
ELFS=$(sha256sum build/rgm/kernel/sparsity.elf 2>/dev/null | cut -c1-64)
HOSTS=$(sha256sum build/rgm/host/sparsity_host 2>/dev/null | cut -c1-64)
sha256sum build/ettelem/ettelem 2>/dev/null | cut -c1-64 > build/reader.sha256
TXT=""
OC=/opt/et/bin/riscv64-unknown-elf-objcopy
if [ -x "$OC" ] && "$OC" -O binary -j .text build/rgm/kernel/sparsity.elf build/rgm/kernel/text.bin 2>/dev/null; then
  TXT=$(sha256sum build/rgm/kernel/text.bin | cut -c1-64)
fi
echo "KERNEL $ELFS (pin $PIN); .text ${TXT:-unread}"
echo "HOST $HOSTS"
echo "READER $(cat build/reader.sha256)"
[ "$ELFS" = "$PIN" ] || fail "the kernel ELF $ELFS is not E136's pin $PIN"
[ -n "$HOSTS" ] || fail "no host was built"
[ -s build/reader.sha256 ] || fail "no reader was built"
H=build/rgm/host/sparsity_host
EV=(); [ "$BOX" = aifoundry1 ] && EV=(ET_DEVICES=1)
checks=""
chk() {  # chk <name> <want rc> <want text> <args...>: a refusal before any device opens
  local name=$1 wrc=$2 wtxt=$3; shift 3
  env ${EV[@]+"${EV[@]}"} timeout 10 "$H" "$@" < /dev/null > "build/check-$name.out" 2> "build/check-$name.err"
  local rc=$?
  if [ "$rc" -eq "$wrc" ] && grep -qF -- "$wtxt" "build/check-$name.err"; then echo "HOSTCHECK $name: rc $rc: ok"; checks="$checks $name:ok"
  else echo "HOSTCHECK $name: rc $rc (want $wrc): FAILED"; checks="$checks $name:FAILED"; fi
}
chk unknown-option 2 "unknown option --no-such-option" --no-such-option
chk zero-shires 2 "bad --shires / --per-shire" --shires 0 --kernel build/rgm/kernel/sparsity.elf
chk no-kernel 1 "cannot read kernel" --kernel build/rgm/kernel/no-such-kernel.elf
chk unknown-test 2 "--test must be fma, tload, gemv, diverge or spin" --test no-such-test --kernel build/rgm/kernel/sparsity.elf
case "$checks" in *FAILED*) fail "the host's behaviour:$checks" ;; esac
ev_host=no; grep -aq ET_DEVICES "$H" && ev_host=yes
ev_tel=no; grep -aq ET_DEVICES build/ettelem/ettelem && ev_tel=yes
ev_lib=no; [ -f "$DL" ] && grep -aq ET_DEVICES "$DL" && ev_lib=yes
ev_cache=no
grep -q '^deviceLayer_DIR:PATH=/opt/et/' build/rgm/CMakeCache.txt 2>/dev/null && grep -q '^deviceLayer_DIR:PATH=/opt/et/' build/ettelem/CMakeCache.txt 2>/dev/null && ev_cache=yes
echo "ETDEVICES host $ev_host; reader $ev_tel; $DL $ev_lib; both CMakeCache deviceLayer_DIR from /opt/et $ev_cache"
if [ "$BOX" = aifoundry1 ]; then
  [ "$ev_host" = yes ] || fail "ET_DEVICES: the host has no ET_DEVICES (it would open card 0)"
  [ "$ev_tel" = yes ] || fail "ET_DEVICES: the reader has no ET_DEVICES (it would open card 0)"
  [ "$ev_lib" = yes ] || fail "ET_DEVICES: $DL has no ET_DEVICES"
  [ "$ev_cache" = yes ] || fail "ET_DEVICES: a build did not take its device layer from /opt/et (CMakeCache.txt)"
  ETDEV="the host, the reader and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"
else
  ETDEV="not a gate on $BOX (one card): host $ev_host, reader $ev_tel, libdeviceLayer.a $ev_lib, CMakeCache $ev_cache"
fi
python3 -B - build/BUILD-mms.json "$BOX" "$DAY" "$ELFS" "$TXT" "$HOSTS" "$KCC" "$HCC" "$checks" "$ETDEV" <<'PY' || fail "the record"
import json, sys, time
p, box, day, elf, txt, host, kcc, hcc, checks, etdev = sys.argv[1:11]
tel = open("build/reader.sha256").read().strip()
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernel_sha256": elf, "kernel_text_sha256": txt or None,
           "host_sha256": host, "ettelem_sha256": tel, "kernel_pin": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
           "compilers": {"kernel": kcc, "host": hcc}, "host_checks": checks.split(), "et_devices": etdev,
           "builder": "src/build_mms.sh", "jobs": 1, "what": "1119-mmsweep5: E136's rgm136 and the lab's ettelem, unchanged"},
          open(p, "w"), indent=1)
PY
echo "MMS-BUILT rc=0"
