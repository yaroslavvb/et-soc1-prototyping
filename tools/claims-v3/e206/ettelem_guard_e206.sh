#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum): the only way E206's session calls the telemetry reader, E190's guard
# (tools/claims-v3/e190/ettelem_guard_e190.sh) for E206's two boxes, in E128's guard's form (tools/claims-v3/e128/ettelem_guard.sh): an
# allow-list in front of each arm's reader, so that the device-management commands the session sends are exactly the classified ones
# (KIT.md, "Device commands"):
#   ettelem config                                 -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                     GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>    -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                     GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
# Anything else - `sample --reset-ms` (the statistics reset), `residency`, `threshold`, `loglevel`, `sptrace`, `uptime`, any other word -
# is refused with exit 97 before the device is opened. The reader is the box's build/ettelem/ettelem: on aifoundry3 (arm A, card 0, its
# only card) with ET_DEVICES unset; on aifoundry1 (arm B, card 1) with ET_DEVICES=1 (aifoundry1's device layer then opens card 1 only).
# Any other box, or ET_DEVICES not as the box needs, is refused. It execs the reader, so the process keeps this PID (the sampler's /proc
# fds are the reader's) and its name becomes `ettelem`. The runner checks each reader's sha256 against its pin (e206_common.ARMS) before
# the first device command.
# SPDX-License-Identifier: Apache-2.0
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
refuse() { echo "ettelem_guard_e206: refused ($*): not in E206's classified command list" >&2; exit 97; }
BOX=$(hostname 2>/dev/null | cut -d. -f1)
case "$BOX" in
  aifoundry3) [ -z "${ET_DEVICES:-}" ] || refuse "ET_DEVICES is '${ET_DEVICES}' on aifoundry3: its one card is opened with ET_DEVICES unset" ;;
  aifoundry1) [ "${ET_DEVICES:-}" = 1 ] || refuse "ET_DEVICES is '${ET_DEVICES:-unset}' on aifoundry1, not 1: E206 opens card 1 only there" ;;
  *) refuse "box '$BOX': E206 runs on aifoundry3 (arm A) and aifoundry1 (arm B) only" ;;
esac
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
