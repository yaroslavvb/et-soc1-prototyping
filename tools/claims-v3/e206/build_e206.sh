#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum): the box build, E190's build v2 (tools/claims-v3/e190/build_e190_v2.sh,
# note 1's) for E206's two boxes, with E191's kernel gate. Run from the box tree's root by step 6 (rb/s08_build_e206.sh) on each arm's box
# (aifoundry3 ~/aifoundry, arm A; aifoundry1 ~/nekko, arm B), or at the desk by the build's desk test (in a sandbox). No device is opened.
#   1. the sources: tools/claims-v3/e136/rgm136's ten files at harness-e206.json's sha256 (check_e206.py --box --only-src), else no build;
#   2. cmake against the box's /opt/et into build/e206rgm (nice 10, -j2), each call under a plain `timeout 300` (never -k: no SIGKILL
#      anywhere in E206's kit), the compilers recorded;
#   3. THE KERNEL GATE (check_e206.py --kernel): the .text always the registered 61315bf6..., and the whole ELF the registered aace138c... or
#      else its loadable identity the pinned one (aifoundry3's riscv gcc prints "(g1b306039a) 15.1.0", the desk's and aifoundry1's "()
#      15.1.0": the string lands in .comment, which the card never loads);
#   4. THE HOST BY ITS BEHAVIOUR: four refusals main.cpp makes before it builds its device Session (no device is opened), each under a plain
#      `timeout 10` with stdin from /dev/null; on aifoundry1 with ET_DEVICES=1 set all the same;
#   5. THE ET_DEVICES READING, a gate on aifoundry1 only (E190's kit note 1): the host binary and /opt/et/lib/libdeviceLayer.a carry the
#      string ET_DEVICES and the build's CMakeCache.txt took the device layer from /opt/et; else refused (a host that ignored ET_DEVICES
#      would open card 0). On aifoundry3 (one card; its stock device layer carries no ET_DEVICES) the reading is recorded, never a gate;
#   6. build/e206rgm/BUILD-e206.json: builder build_e206.sh, the box, the Pacific day, the verdict, the kernel's and the host's sha256, the
#      kernel's .text sha256 and the gate's line, the compilers, the host's checks, the ET_DEVICES reading (run_e206.py's box check reads it;
#      on arm B it must read "the host and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"); the last line RGM-BUILT rc=0, or
#      RGM-BUILD-FAILED: <why>.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
B=build/e206rgm
SRC=tools/claims-v3/e136/rgm136
BOX=$(hostname | cut -d. -f1)
DAY=$(TZ=America/Los_Angeles date +%F)
PY=${E206_PY:-python3}
DL=/opt/et/lib/libdeviceLayer.a
fail() { echo "RGM-BUILD-FAILED: $*"; mkdir -p "$B"; "$PY" -B - "$B/BUILD-e206.json" "$BOX" "$DAY" "$*" <<'PY'
import json, sys, time
p, box, day, why = sys.argv[1:5]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILD-FAILED", "why": why, "builder": "build_e206.sh"},
          open(p, "w"), indent=1)
PY
exit 1; }
case "$BOX" in aifoundry3|aifoundry1) ;; *) fail "the box is '$BOX': E206 builds on aifoundry3 (arm A) and aifoundry1 (arm B) only" ;; esac
unset V3_DEVICE ET_DEVICES
echo "== E206 build on $BOX, $(TZ=America/Los_Angeles date '+%F %T %Z'), into $B"
"$PY" -B tools/claims-v3/e206/check_e206.py --box --only-src || fail "rgm136's sources are not harness-e206.json's"
rm -rf "./$B"
mkdir -p "$B" || fail "cannot make $B"
KCC=$(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)
HCC=$(c++ --version 2>/dev/null | head -n 1)
echo "COMPILER kernel: ${KCC:-none}; host: ${HCC:-none}"
timeout 300 nice -n 10 cmake -S "$SRC" -B "$B" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > "$B/cmake.log" 2>&1 || fail "cmake (see $B/cmake.log)"
timeout 300 nice -n 10 cmake --build "$B" -j2 > "$B/build.log" 2>&1 || fail "the build (see $B/build.log)"
[ -s "$B/kernel/sparsity.elf" ] || fail "no kernel was built"
[ -x "$B/host/sparsity_host" ] || fail "no host was built"
ELFS=$(sha256sum "$B/kernel/sparsity.elf" | cut -c1-64)
HOSTS=$(sha256sum "$B/host/sparsity_host" | cut -c1-64)
KG=$("$PY" -B tools/claims-v3/e206/check_e206.py --kernel "$B/kernel/sparsity.elf" 2>&1 | tail -n 1)
TXT=$(printf '%s\n' "$KG" | sed -nE 's/^.*\.text ([0-9a-f]{16})\.\.\. the registered.*$/\1/p')
echo "KERNEL $ELFS (the registered ELF aace138c...); $KG"
echo "HOST $HOSTS"
case "$KG" in "KERNEL OK: "*) ;; *) fail "the kernel gate: ${KG#KERNEL FAILED: }" ;; esac
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
"$PY" -B - "$B/BUILD-e206.json" "$BOX" "$DAY" "$ELFS" "$TXT" "$HOSTS" "$KCC" "$HCC" "$checks" "$ETDEV" "$KG" <<'PY' || fail "the record"
import json, sys, time
p, box, day, elf, txt, host, kcc, hcc, checks, etdev, kg = sys.argv[1:12]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernel_sha256": elf, "kernel_text_sha256_head": txt or None,
           "kernel_gate": kg, "host_sha256": host, "kernel_pin": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
           "text_pin": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
           "compilers": {"kernel": kcc, "host": hcc}, "host_checks": checks.split(), "source": "tools/claims-v3/e136/rgm136 (harness-e206.json)",
           "builder": "build_e206.sh", "et_devices": etdev,
           "what": "E206's build of E136's rgm136, unchanged (build_e206.sh: the kernel gate, the host's behaviour, the ET_DEVICES reading)"},
          open(p, "w"), indent=1)
PY
echo "RGM-BUILT rc=0"
