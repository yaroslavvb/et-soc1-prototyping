#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the only way E194's session calls the
# telemetry reader. E128's guard (tools/claims-v3/e128/ettelem_guard.sh) in E190's form (ettelem_guard_e190.sh, arm A's half, unchanged
# beside it): an allow-list in front of aifoundry2's reader, so that the device-management commands the session sends are exactly the
# classified ones (KIT.md, "Device commands"):
#   ettelem config                                 -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                     GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>    -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                     GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
# Anything else - `sample --reset-ms` (the statistics reset), `residency`, `threshold`, `loglevel`, `sptrace`, `uptime`, any other word -
# is refused with exit 97 before the device is opened. E194's one card is aifoundry2's card 0 (E194.md 2): the box must be aifoundry2 and
# ET_DEVICES and V3_DEVICE must be UNSET (E190 arm A's form on this card: its device layer carries no ET_DEVICES; a setting of either is
# refused before the device opens). The reader is build/ettelem-hpl/ettelem of the box tree (~/claude/et-soc1-prototyping), E136's,
# E146's, E169's and E190 arm A's sampler on this card; the runner checks its sha256 against its pin (e194_common.READER_SHA256) before the
# first device command. It execs the reader, so the process keeps this PID (the sampler's /proc fds are the reader's) and its name becomes
# `ettelem`.
# SPDX-License-Identifier: Apache-2.0
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
refuse() { echo "ettelem_guard_e194: refused ($*): not in E194's classified command list" >&2; exit 97; }
BOX=$(hostname 2>/dev/null | cut -d. -f1)
[ "$BOX" = aifoundry2 ] || refuse "box '$BOX': E194 runs on aifoundry2 card 0 only"
[ -z "${ET_DEVICES+set}" ] || refuse "ET_DEVICES is set ('${ET_DEVICES}'): aifoundry2's one card is opened with ET_DEVICES unset"
[ -z "${V3_DEVICE+set}" ] || refuse "V3_DEVICE is set ('${V3_DEVICE}'): aifoundry2's one card is opened with V3_DEVICE unset"
case "${1:-}" in
  config)
    [ $# -eq 1 ] || refuse "$@"
    exec "$ROOT/build/ettelem-hpl/ettelem" config ;;
  sample)
    shift
    args=()
    while [ $# -gt 0 ]; do
      case "$1" in
        --seconds|--every-ms)
          [ $# -ge 2 ] || refuse "$1 without a value"
          case "$2" in ''|*[!0-9.]*) refuse "$1 $2" ;; esac
          args+=("$1" "$2"); shift 2 ;;
        *) refuse "sample $*" ;;
      esac
    done
    exec "$ROOT/build/ettelem-hpl/ettelem" sample ${args[@]+"${args[@]}"} ;;
  *) refuse "$@" ;;
esac
