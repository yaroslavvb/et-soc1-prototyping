#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): THE ET_DEVICES READING of one built
# host, E190's kit note 1's (build_e190_v2.sh, bff31df2; the lab's own gates read it the same way: workloads/pciebench/run_pcie.sh,
# tools/lab/dashboard/remote.sh): aifoundry1's device layer, the one that honours ET_DEVICES, carries the variable's name, the stock
# library has none, and a host built against the stock library opens card 0 as device 0 whatever ET_DEVICES says. It prints one line:
#   yes: the host and <the device layer> carry ET_DEVICES; the device layer came from /opt/et
#   no: <what is missing>
# and exits 0 either way (build_e191.sh refuses a "no" on aifoundry1; build_e194.sh only RECORDS it on aifoundry2, one card, as E190 arm A's build did). It reads three files, never runs one: the host binary
# (grep -a ET_DEVICES), the device layer library (default /opt/et/lib/libdeviceLayer.a) and the build's CMakeCache.txt
# (deviceLayer_DIR:PATH=/opt/et/...). Desk test only: RB_DESKTEST=1 with E194_DEVICELAYER names a stand-in library.
#   bash tools/claims-v3/e194/etdevices_e194.sh <host binary> <CMakeCache.txt>
# SPDX-License-Identifier: Apache-2.0
set -u
H=${1:?the host binary}; CC=${2:?the CMakeCache.txt of the build}
DL=/opt/et/lib/libdeviceLayer.a
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E194_DEVICELAYER:-}" ] && DL=$E194_DEVICELAYER
miss=()
[ -f "$H" ] && grep -aq ET_DEVICES "$H" || miss+=("the host has no ET_DEVICES")
[ -f "$DL" ] && grep -aq ET_DEVICES "$DL" || miss+=("$DL has no ET_DEVICES")
grep -q '^deviceLayer_DIR:PATH=/opt/et/' "$CC" 2>/dev/null || miss+=("the build did not take its device layer from /opt/et (CMakeCache.txt)")
if [ "${#miss[@]}" -eq 0 ]; then
  echo "yes: the host and $DL carry ET_DEVICES; the device layer came from /opt/et"
else
  out=""
  for x in "${miss[@]}"; do out="${out:+$out; }$x"; done
  echo "no: $out"
fi
exit 0
