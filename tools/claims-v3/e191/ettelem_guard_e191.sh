#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the only way E191's session calls the
# telemetry reader. E128's guard (tools/claims-v3/e128/ettelem_guard.sh, unchanged beside it) in E190's form (ettelem_guard_e190.sh, arm
# B's half): an allow-list in front of card 1's reader, so that the device-management commands the session sends are exactly the
# classified ones (KIT.md, "Device commands"):
#   ettelem config                                 -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                     GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>    -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                     GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
# Anything else - `sample --reset-ms` (the statistics reset), `residency`, `threshold`, `loglevel`, `sptrace`, `uptime`, any other word -
# is refused with exit 97 before the device is opened. E191's one card is aifoundry1's card 1 (E191.md 2; dated note 1, item 1): the box
# must be aifoundry1 and ET_DEVICES must be 1 (aifoundry1's device layer then opens card 1 only, which the reader sees as its device);
# any other box, or ET_DEVICES unset or not 1, is refused before the device opens. The reader is build/ettelem/ettelem of the box tree
# (~/nekko), the lab's reader E137, E164, E172 and E190 arm B used on card 1; the runner checks its sha256 against its pin
# (e191_common.READER_SHA256) before the first device command. It execs the reader, so the process keeps this PID (the sampler's /proc
# fds are the reader's) and its name becomes `ettelem`.
# SPDX-License-Identifier: Apache-2.0
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
refuse() { echo "ettelem_guard_e191: refused ($*): not in E191's classified command list" >&2; exit 97; }
BOX=$(hostname 2>/dev/null | cut -d. -f1)
[ "$BOX" = aifoundry1 ] || refuse "box '$BOX': E191 runs on aifoundry1 card 1 only"
[ "${ET_DEVICES:-}" = 1 ] || refuse "ET_DEVICES is '${ET_DEVICES:-unset}', not 1: E191 opens card 1 only"
case "${1:-}" in
  config)
    [ $# -eq 1 ] || refuse "$@"
    exec "$ROOT/build/ettelem/ettelem" config ;;
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
    exec "$ROOT/build/ettelem/ettelem" sample ${args[@]+"${args[@]}"} ;;
  *) refuse "$@" ;;
esac
