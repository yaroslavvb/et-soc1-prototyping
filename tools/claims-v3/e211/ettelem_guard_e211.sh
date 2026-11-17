#!/usr/bin/env bash
# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum): the only way E211's session calls the telemetry reader, E206's guard
# (tools/claims-v3/e206/ettelem_guard_e206.sh), as E207's kit ported it (Q199), for E211's one box, in E128's guard's form (tools/claims-v3/e128/ettelem_guard.sh): an
# allow-list in front of aifoundry3's reader, so that the device-management commands the session sends are exactly the classified ones
# (KIT.md, "Device commands"):
#   ettelem config                                 -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                     GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>    -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                     GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
# Anything else - `sample --reset-ms` (the statistics reset), `residency`, `threshold`, `loglevel`, `sptrace`, `uptime`, any other word -
# is refused with exit 97 before the device is opened. The reader is the box's build/ettelem/ettelem, on aifoundry3 (card 0, its only card)
# with ET_DEVICES unset. Any other box, or ET_DEVICES set, is refused. It execs the reader, so the process keeps this PID (the sampler's /proc
# fds are the reader's) and its name becomes `ettelem`. The runner checks the reader's sha256 against its pin (e211_common.ARMS) before the
# first device command.
# SPDX-License-Identifier: Apache-2.0
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
refuse() { echo "ettelem_guard_e211: refused ($*): not in E211's classified command list" >&2; exit 97; }
BOX=$(hostname 2>/dev/null | cut -d. -f1)
case "$BOX" in
  aifoundry3) [ -z "${ET_DEVICES:-}" ] || refuse "ET_DEVICES is '${ET_DEVICES}' on aifoundry3: its one card is opened with ET_DEVICES unset" ;;
  *) refuse "box '$BOX': E211 runs on aifoundry3 (card 0) only" ;;
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
