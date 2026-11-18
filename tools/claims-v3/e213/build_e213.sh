#!/usr/bin/env bash
# E213 (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): the box build, E211's (tools/claims-v3/e211/build_e211.sh, landed in
# 2b7f261f, which built rgm136 and rgm211 on aifoundry3 for E211: RGM-BUILT, both KERNEL OK by the loadable identity) with E206's second box
# (tools/claims-v3/e206/build_e206.sh, landed in 906699ea, which built rgm136 on aifoundry1 for E206 arm B: KERNEL OK at the whole ELF, the
# ET_DEVICES gate passed), for E213's two kernels on each arm's box. Run from the box tree's root by step 6 (rb/s08_build_e213.sh) on aifoundry3
# (~/aifoundry, arm A) or aifoundry1 (~/nekko, arm B), or at the desk by the build's desk test (in a sandbox, under a box's hostname). No device
# is opened. Arm B needs rgm211's HOST (its gemmLnc points k37-k40 and smoke s14 run rgm136's ELF on rgm211's host, E213.md 2's contingency 2);
# rgm211's ELF is built and gated there too (the same cmake tree), never run.
#   1. the sources: the two kernels' twenty files (tools/claims-v3/e136/rgm136, unchanged; tools/claims-v3/e211/rgm211, E211's, unchanged) at
#      harness-e213.json's sha256 (check_e213.py --box --only-src), else no build;
#   2. cmake against the box's /opt/et, each tree into its own folder, build/e213rgm/rgm136 and build/e213rgm/rgm211 (nice 10, -j2), each call
#      under a plain `timeout 300` (never -k: no SIGKILL anywhere in E213's kit), the compilers recorded;
#   3. THE KERNEL GATE on each (check_e213.py --kernel rgm136|rgm211: the kit's gate ident_e213.gate): the .text always the kernel's pin (rgm136
#      61315bf6..., rgm211 82c79807...), and the whole ELF the pin or else its loadable identity the pin (aifoundry3's riscv gcc prints
#      "(g1b306039a) 15.1.0" into .comment, which the card never loads); ON aifoundry1 rgm136's WHOLE ELF (--whole: E213.md 2, E206 arm B's gate;
#      aifoundry1's gcc prints "() 15.1.0", as this desk's);
#   4. THE HOSTS BY THEIR BEHAVIOUR, each check inside a sandbox with no device node and an empty /run/lock (bubblewrap: a private /dev holding only
#      null, zero, full, random, urandom, tty and the like), under a plain `timeout 10` with stdin from /dev/null (on aifoundry1 with ET_DEVICES=1
#      set all the same), and each must end BEFORE the device stage (the runtime's "[RUNTIME]" log line never printed): rgm136's host, E206's four
#      refusals main.cpp makes before its device Session; rgm211's host, the same four plus four of its early refusals (validateArm: an arm missing
#      KB, gemm at 16 minions a shire, a missing tile file, an unknown gen), E211's twelve;
#   5. THE ET_DEVICES READING, a gate on aifoundry1 (E190's kit note 1, E206's): BOTH host binaries and /opt/et/lib/libdeviceLayer.a carry the
#      string ET_DEVICES and both builds' CMakeCache.txt took the device layer from /opt/et; else refused (a host that ignored ET_DEVICES would open
#      card 0). On aifoundry3 (one card; its stock device layer carries no ET_DEVICES) the reading is recorded, never a gate;
#   6. build/e213rgm/BUILD-e213.json: builder build_e213.sh, the box, the arm, the Pacific day, the verdict, each kernel's and each host's sha256,
#      each kernel's gate line, the compilers, the hosts' checks, the ET_DEVICES reading (run_e213.py's box check reads it; on arm B it must read
#      "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"); the last line RGM-BUILT rc=0, or RGM-BUILD-FAILED: <why>.
# Any box but aifoundry3 and aifoundry1 is refused before anything is built.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
B=build/e213rgm
BOX=$(hostname | cut -d. -f1)
DAY=$(TZ=America/Los_Angeles date +%F)
PY=${E213_PY:-python3}
DL=${E213_DEVLAYER:-/opt/et/lib/libdeviceLayer.a}
BWRAP=${E213_BWRAP:-/usr/bin/bwrap}
fail() { echo "RGM-BUILD-FAILED: $*"; mkdir -p "$B"; "$PY" -B - "$B/BUILD-e213.json" "$BOX" "$DAY" "$*" <<'PY'
import json, sys, time
p, box, day, why = sys.argv[1:5]
json.dump({"box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILD-FAILED", "why": why, "builder": "build_e213.sh"},
          open(p, "w"), indent=1)
PY
exit 1; }
case "$BOX" in
  aifoundry3) ARM=A; WHOLE=() ;;
  aifoundry1) ARM=B; WHOLE=(--whole) ;;
  *) fail "the box is '$BOX': E213 builds on aifoundry3 (arm A) and aifoundry1 (arm B) only" ;;
esac
unset V3_DEVICE ET_DEVICES
EV=(); [ "$ARM" = B ] && EV=(ET_DEVICES=1)
echo "== E213 build on $BOX (arm $ARM), $(TZ=America/Los_Angeles date '+%F %T %Z'), into $B (rgm136, rgm211)"
"$PY" -B tools/claims-v3/e213/check_e213.py --box --only-src || fail "the two kernels' sources are not harness-e213.json's"
[ -x "$BWRAP" ] || fail "no bubblewrap at $BWRAP: the hosts' checks run only in a sandbox with no device node"
rm -rf -- "./${B:?}"
mkdir -p "$B" || fail "cannot make $B"
KCC=$(/opt/et/bin/riscv64-unknown-elf-gcc --version 2>/dev/null | head -n 1)
HCC=$(c++ --version 2>/dev/null | head -n 1)
echo "COMPILER kernel: ${KCC:-none}; host: ${HCC:-none}"
declare -A ELFS HOSTS KG
for k in rgm136 rgm211; do
  case $k in rgm136) SRC=tools/claims-v3/e136/rgm136; W=(${WHOLE[@]+"${WHOLE[@]}"}) ;; rgm211) SRC=tools/claims-v3/e211/rgm211; W=() ;; esac
  timeout 300 nice -n 10 cmake -S "$SRC" -B "$B/$k" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > "$B/cmake-$k.log" 2>&1 || fail "cmake of $k (see $B/cmake-$k.log)"
  timeout 300 nice -n 10 cmake --build "$B/$k" -j2 > "$B/build-$k.log" 2>&1 || fail "the build of $k (see $B/build-$k.log)"
  [ -s "$B/$k/kernel/sparsity.elf" ] || fail "no $k kernel was built"
  [ -x "$B/$k/host/sparsity_host" ] || fail "no $k host was built"
  ELFS[$k]=$(sha256sum "$B/$k/kernel/sparsity.elf" | cut -c1-64)
  HOSTS[$k]=$(sha256sum "$B/$k/host/sparsity_host" | cut -c1-64)
  KG[$k]=$("$PY" -B tools/claims-v3/e213/check_e213.py --kernel "$k" "$B/$k/kernel/sparsity.elf" ${W[@]+"${W[@]}"} 2>&1 | tail -n 1)
  echo "KERNEL $k ${ELFS[$k]}; ${KG[$k]}"
  echo "HOST $k ${HOSTS[$k]}"
  case "${KG[$k]}" in "KERNEL OK: "*) ;; *) fail "the kernel gate of $k: ${KG[$k]#KERNEL FAILED: }" ;; esac
done
T=tools/claims-v3/kinds/tiles/fp32/randn.bin
checks=""
chk() {  # chk <host kind> <name> <want rc> <want text> <args...>: a refusal before any device opens, inside the sandbox
  local hk=$1 name=$2 wrc=$3 wtxt=$4; shift 4
  local H="$B/$hk/host/sparsity_host" o="$B/check-$hk-$name"
  env ${EV[@]+"${EV[@]}"} timeout 10 "$BWRAP" --dev-bind / / --dev /dev --tmpfs /run/lock -- "$H" "$@" < /dev/null > "$o.out" 2> "$o.err"
  local rc=$?
  if [ "$rc" -eq "$wrc" ] && grep -qF -- "$wtxt" "$o.err" && ! grep -qF -- "[RUNTIME]" "$o.out" "$o.err"; then
    echo "HOSTCHECK $hk $name: rc $rc, '$wtxt', before the device stage: ok"; checks="$checks $hk:$name:ok"
  else
    echo "HOSTCHECK $hk $name: rc $rc (want $wrc), stderr '$(head -c 160 "$o.err" | tr '\n' ' ')'$(grep -qF -- "[RUNTIME]" "$o.out" "$o.err" && echo ', THE DEVICE STAGE REACHED'): FAILED"
    checks="$checks $hk:$name:FAILED"
  fi
}
for k in rgm136 rgm211; do
  K="$B/$k/kernel/sparsity.elf"
  chk $k unknown-option 2 "unknown option --no-such-option" --no-such-option
  chk $k zero-shires 2 "bad --shires / --per-shire" --shires 0 --kernel "$K"
  chk $k no-kernel 1 "cannot read kernel" --kernel "$B/$k/kernel/no-such-kernel.elf"
  chk $k unknown-test 2 "--test must be fma, tload, gemv, diverge or spin" --test no-such-test --kernel "$K"
done
K="$B/rgm211/kernel/sparsity.elf"
A=(--test fma --type fp32 --pattern none --shires 0xffffffff --per-shire 32 --seed 1 --kernel "$K")
chk rgm211 arm-missing-kb 1 "want gemmL<MB>x<NB>x<KB>" "${A[@]}" --values "gemmLn2x2:randn:$T"
chk rgm211 per-shire-16 1 "gemm needs --per-shire 32" --test fma --type fp32 --pattern none --shires 0xffffffff --per-shire 16 --seed 1 --kernel "$K" --values "gemmLn2x2x2:randn:$T"
chk rgm211 missing-tile 1 "cannot read 2 x 1024 bytes" "${A[@]}" --values "gemmLn2x2x2:randn:tools/claims-v3/kinds/tiles/fp32/no-such-tile.bin"
chk rgm211 unknown-gen 1 "unknown gen" "${A[@]}" --values "gemmLnc2x2x2:noise:$T"
case "$checks" in *FAILED*) fail "the hosts' behaviour:$checks" ;; esac
ev_host=yes; for k in rgm136 rgm211; do grep -aq ET_DEVICES "$B/$k/host/sparsity_host" || ev_host=no; done
ev_lib=no; [ -f "$DL" ] && grep -aq ET_DEVICES "$DL" && ev_lib=yes
ev_cache=yes; for k in rgm136 rgm211; do grep -q '^deviceLayer_DIR:PATH=/opt/et/' "$B/$k/CMakeCache.txt" 2>/dev/null || ev_cache=no; done
echo "ETDEVICES both hosts $ev_host; $DL $ev_lib; both CMakeCache deviceLayer_DIR from /opt/et $ev_cache"
if [ "$ARM" = B ]; then
  [ "$ev_host" = yes ] || fail "ET_DEVICES: a host has no ET_DEVICES (built against a device layer that ignores it: it would open card 0)"
  [ "$ev_lib" = yes ] || fail "ET_DEVICES: $DL has no ET_DEVICES"
  [ "$ev_cache" = yes ] || fail "ET_DEVICES: a build did not take its device layer from /opt/et (CMakeCache.txt)"
  ETDEV="the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"
else
  ETDEV="not a gate on $BOX (one card): hosts $ev_host, libdeviceLayer.a $ev_lib, CMakeCache $ev_cache"
fi
"$PY" -B - "$B/BUILD-e213.json" "$BOX" "$ARM" "$DAY" "${ELFS[rgm136]}" "${HOSTS[rgm136]}" "${KG[rgm136]}" "${ELFS[rgm211]}" "${HOSTS[rgm211]}" \
  "${KG[rgm211]}" "$KCC" "$HCC" "$checks" "$ETDEV" <<'PY' || fail "the record"
import json, sys, time
p, box, arm, day, e136, h136, g136, e211, h211, g211, kcc, hcc, checks, etdev = sys.argv[1:15]
json.dump({"box": box, "arm": arm, "day": day, "epoch": int(time.time()), "verdict": "BUILT",
           "kernels": {"rgm136": {"kernel_sha256": e136, "host_sha256": h136, "kernel_gate": g136, "source": "tools/claims-v3/e136/rgm136",
                                  "build": "build/e213rgm/rgm136"},
                       "rgm211": {"kernel_sha256": e211, "host_sha256": h211, "kernel_gate": g211, "source": "tools/claims-v3/e211/rgm211",
                                  "build": "build/e213rgm/rgm211"}},
           "compilers": {"kernel": kcc, "host": hcc}, "host_checks": checks.split(), "builder": "build_e213.sh", "et_devices": etdev,
           "what": "E213's build of rgm136 (E136's, unchanged) and rgm211 (E211's, unchanged) (build_e213.sh: the kernel gates, the hosts' "
                   "behaviour in a sandbox with no device node, the ET_DEVICES reading, a gate on aifoundry1)"},
          open(p, "w"), indent=1)
PY
echo "RGM-BUILT rc=0"
