#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the desk test of THE ET_DEVICES
# READING (etdevices_e191.sh) and of build_e191.sh's refusal of a host without ET_DEVICES on aifoundry1 (E190's kit note 1's gate, both
# ways). No device, no box. Cases (verdicts stated first):
#   E1 a host and a device layer that carry ET_DEVICES and a CMakeCache.txt from /opt/et: "yes: ...";
#   E2 the host without it: "no: the host has no ET_DEVICES";  E3 the device layer without it: "no: ... has no ET_DEVICES";
#   E4 the device layer taken from elsewhere (CMakeCache.txt): "no: the build did not take its device layer from /opt/et";
#   E5 a stand-in library named without RB_DESKTEST=1: ignored (the default /opt/et/lib/libdeviceLayer.a is read: absent here, "no");
#   B1 build_e191.sh in a stand-in tree under the hostname aifoundry1 (a private UTS namespace), the REAL hosts built by g++-13 -O2 against
#      E189's desk mock (no ET_DEVICES, as the stock device layer): LEDGER-BUILD-FAILED and SPP-BUILD-FAILED "ET_DEVICES: no: ...", E191-BUILD
#      rc=1, each record BUILD-FAILED;
#   B2 the same build with the stand-in device layer (rb/fake_cmake_e191.sh: the hosts carry ET_DEVICES, CMakeCache.txt from /opt/et, a
#      stand-in library): LEDGER-BUILT and SPP-BUILT, each record BUILT with et_devices "yes" (the runner's box check reads it);
#   B3 that build under the hostname aifoundry2: BUILT, its reading recorded as "not a gate on aifoundry2" (the runner's box check refuses
#      such a record: realpath case RP6).
# Run ONLY inside the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2).
#   bash tools/claims-v3/e191/desk/etdevices_test_e191.sh <an empty scratch dir outside the repo> > etdevices-e191.txt
# The last line: ETDEVICES-E191 <n> of <m> PASS (or FAIL).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?an empty scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
for c in g++-13 bwrap sha256sum; do command -v "$c" > /dev/null || { echo "no $c"; exit 2; }; done
mkdir -p "$S"; S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "$S is not empty"; exit 2; }
E=tools/claims-v3/e191
EV=$SRC/$E/etdevices_e191.sh
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = "$2" ]; then n=$((n + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fi; }
echo "etdevices_test_e191: $(date '+%F %T %Z') on $(hostname), $(g++-13 --version | head -n 1)"
printf 'ELF stand-in\nET_DEVICES\n' > "$S/host-yes"; printf 'ELF stand-in\n' > "$S/host-no"
printf 'lib stand-in ET_DEVICES\n' > "$S/lib-yes.a"; printf 'lib stand-in\n' > "$S/lib-no.a"
printf 'deviceLayer_DIR:PATH=/opt/et/lib/cmake/deviceLayer\n' > "$S/cache-yes"; printf 'deviceLayer_DIR:PATH=/usr/lib/cmake/deviceLayer\n' > "$S/cache-no"
r1=$(RB_DESKTEST=1 E191_DEVICELAYER="$S/lib-yes.a" bash "$EV" "$S/host-yes" "$S/cache-yes"); echo "   E1: $r1"
r2=$(RB_DESKTEST=1 E191_DEVICELAYER="$S/lib-yes.a" bash "$EV" "$S/host-no" "$S/cache-yes"); echo "   E2: $r2"
r3=$(RB_DESKTEST=1 E191_DEVICELAYER="$S/lib-no.a" bash "$EV" "$S/host-yes" "$S/cache-yes"); echo "   E3: $r3"
r4=$(RB_DESKTEST=1 E191_DEVICELAYER="$S/lib-yes.a" bash "$EV" "$S/host-yes" "$S/cache-no"); echo "   E4: $r4"
r5=$(E191_DEVICELAYER="$S/lib-yes.a" bash "$EV" "$S/host-yes" "$S/cache-yes"); echo "   E5: $r5"
ok "$(case "$r1" in "yes: "*) echo 1 ;; *) echo 0 ;; esac)" 1 "E1 the host, the device layer and the cache: yes"
ok "$(case "$r2" in "no: the host has no ET_DEVICES") echo 1 ;; *) echo 0 ;; esac)" 1 "E2 a host without ET_DEVICES: no"
ok "$(case "$r3" in "no: $S/lib-no.a has no ET_DEVICES") echo 1 ;; *) echo 0 ;; esac)" 1 "E3 a device layer without ET_DEVICES: no"
ok "$(case "$r4" in "no: the build did not take its device layer from /opt/et (CMakeCache.txt)") echo 1 ;; *) echo 0 ;; esac)" 1 "E4 the device layer from elsewhere: no"
ok "$(case "$r5" in "no: /opt/et/lib/libdeviceLayer.a has no ET_DEVICES") echo 1 ;; *) echo 0 ;; esac)" 1 "E5 a stand-in library without RB_DESKTEST=1 is ignored"
# ---- the build, in a stand-in tree (every harness file copied), under the box's hostname
T=$S/tree
( cd "$SRC" && /usr/bin/python3 -I -B $E/check_e191.py --list; echo $E/harness-e191.json; echo tools/claims-v3/e189/rb/fake_cmake_e189.sh;
  find tools/claims-v3/e189/desk -type f ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
mkdir -p "$S/bin"
printf '#!/bin/sh\n[ "$1" = "-O" ] && [ "$6" = /dev/stdout ] && exec cat "$5"\nexit 2\n' > "$S/bin/objcopy"; chmod +x "$S/bin/objcopy"
lp=$(printf 'E189 desk-test stand-in kernel: ledger\n' | sha256sum | cut -c1-64); sp=$(printf 'E189 desk-test stand-in kernel: sparse parity\n' | sha256sum | cut -c1-64)
printf '{"kernels": {"ledger": {"elf_sha256": "%s", "text_sha256": "%s"}, "spp": {"elf_sha256": "%s", "text_sha256": "%s"}}}\n' "$lp" "$lp" "$sp" "$sp" > "$S/standin-pins.json"
printf '#!/bin/sh\nFAKE_CMAKE_ETDEV=no exec bash "%s" "$@"\n' "$SRC/$E/rb/fake_cmake_e191.sh" > "$S/bin/cmake-stock"
printf '#!/bin/sh\nexec bash "%s" "$@"\n' "$SRC/$E/rb/fake_cmake_e191.sh" > "$S/bin/cmake-etdev"
chmod +x "$S/bin/cmake-stock" "$S/bin/cmake-etdev"
build() {  # build <hostname> <cmake stand-in> <log>
  /usr/bin/bwrap --dev-bind / / --unshare-uts --hostname "$1" --die-with-parent -- env -C "$T" RB_DESKTEST=1 FAKE_CMAKE_REPO="$T" \
    E191_CMAKE="$S/bin/$2" E191_KERNEL_PINS="$S/standin-pins.json" E191_OBJCOPY="$S/bin/objcopy" E191_DEVICELAYER="$S/lib-yes.a" \
    PATH="$S/bin:$PATH" bash "$T/$E/build_e191.sh" > "$3" 2>&1
}
rec() { /usr/bin/python3 -I -B - "$T/$1/BUILD-e191.json" <<'PY'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    r = {}
print(f"{r.get('builder')}|{r.get('verdict')}|{r.get('et_devices')}")
PY
}
build aifoundry1 cmake-stock "$S/b1.txt"; b1=$?
grep -E '^(LEDGER|SPP|E191-BUILD)' "$S/b1.txt" | cut -c1-200 | sed 's/^/   B1: /'
ok "$b1.$(grep -c '^LEDGER-BUILD-FAILED: ET_DEVICES: no: the host has no ET_DEVICES' "$S/b1.txt").$(grep -c '^SPP-BUILD-FAILED: ET_DEVICES: no: the host has no ET_DEVICES' "$S/b1.txt").$(rec build/e191ledger | cut -d'|' -f1,2).$(rec build/e191spp | cut -d'|' -f2)" \
  "1.1.1.build_e191.sh|BUILD-FAILED.BUILD-FAILED" "B1 aifoundry1, the stock device layer: both hosts refused by the ET_DEVICES reading, E191-BUILD rc=1, the records BUILD-FAILED"
build aifoundry1 cmake-etdev "$S/b2.txt"; b2=$?
grep -E '^(LEDGER|SPP|E191-BUILD)' "$S/b2.txt" | cut -c1-200 | sed 's/^/   B2: /'
ok "$b2.$(grep -c '^LEDGER-BUILT rc=0' "$S/b2.txt").$(grep -c '^SPP-BUILT rc=0' "$S/b2.txt").$(rec build/e191ledger).$(rec build/e191spp | cut -d'|' -f3)" \
  "0.1.1.build_e191.sh|BUILT|yes.yes" "B2 aifoundry1, the stand-in device layer that carries ET_DEVICES: both BUILT, their behaviour read OK, records et_devices yes"
build aifoundry2 cmake-etdev "$S/b3.txt"; b3=$?
ok "$b3.$(rec build/e191ledger | cut -d'|' -f2).$(rec build/e191ledger | cut -d'|' -f3 | cut -c1-30)" "0.BUILT.not a gate on aifoundry2 (E191" \
  "B3 aifoundry2: BUILT, the reading recorded as not a gate (the runner refuses such a record on aifoundry1: RP6)"
echo "ETDEVICES-E191 $n of $m $([ "$n" -eq "$m" ] && echo PASS || echo FAIL)"
[ "$n" -eq "$m" ]
