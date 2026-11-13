#!/usr/bin/env bash
# E190 (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): the only way E190's session calls the telemetry reader, in E128's guard's
# form (tools/claims-v3/e128/ettelem_guard.sh) and E170's (one guard, one card each box): an allow-list in front of each arm's reader, so
# that the device-management commands the session sends are exactly the classified ones (KIT.md, "Device commands"):
#   ettelem config                                 -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                     GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>    -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                     GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
# Anything else - `sample --reset-ms` (the statistics reset), `residency`, `threshold`, `loglevel`, `sptrace`, `uptime`, any other word -
# is refused with exit 97 before the device is opened. The reader is the arm's: on aifoundry2 (arm A, card 0, its only card) E136's,
# E146's and E169's sampler build/ettelem-hpl/ettelem, with ET_DEVICES unset; on aifoundry1 (arm B, card 1) build/ettelem/ettelem, the
# lab's reader E137, E164 and E172 used on card 1, with ET_DEVICES=1 (aifoundry1's device layer then opens card 1 only). Any other box,
# or ET_DEVICES not as the box needs, is refused. It execs the reader, so the process keeps this PID and its name becomes `ettelem`.
# The runner checks each reader's sha256 against its pin (e190_common.ARMS) before the first device command.
# SPDX-License-Identifier: Apache-2.0
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
refuse() { echo "ettelem_guard_e190: refused ($*): not in E190's classified command list" >&2; exit 97; }
BOX=$(hostname 2>/dev/null | cut -d. -f1)
case "$BOX" in
  aifoundry2) [ -z "${ET_DEVICES:-}" ] || refuse "ET_DEVICES is '${ET_DEVICES}' on aifoundry2: its one card is opened with ET_DEVICES unset" ;;
  aifoundry1) [ "${ET_DEVICES:-}" = 1 ] || refuse "ET_DEVICES is '${ET_DEVICES:-unset}' on aifoundry1, not 1: E190 opens card 1 only there" ;;
  *) refuse "box '$BOX': E190 runs on aifoundry2 (arm A) and aifoundry1 (arm B) only" ;;
esac
case "${1:-}" in
  config)
    [ $# -eq 1 ] || refuse "$@"
    case "$BOX" in
      aifoundry2) exec "$ROOT/build/ettelem-hpl/ettelem" config ;;
      aifoundry1) exec "$ROOT/build/ettelem/ettelem" config ;;
    esac ;;
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
    case "$BOX" in
      aifoundry2) exec "$ROOT/build/ettelem-hpl/ettelem" sample ${args[@]+"${args[@]}"} ;;
      aifoundry1) exec "$ROOT/build/ettelem/ettelem" sample ${args[@]+"${args[@]}"} ;;
    esac ;;
  *) refuse "$@" ;;
esac
refuse "no reader for box $BOX"
