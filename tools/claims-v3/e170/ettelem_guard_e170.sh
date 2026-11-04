#!/usr/bin/env bash
# E170 (Q141(w)): the only way E170 calls the telemetry reader on aifoundry1 card 0. An allow-list in front of build/ettelem-e84/ettelem (E84's
# build of tools/claims-v3/dv2/ettelem-dv2 on aifoundry1), in E128's guard's form, so that the device-management commands the run sends are exactly
# the classified ones (E170.md, "Device commands sent"; the owner's rule of Mon 2 Nov 2026, "take more care for writing commands"):
#   ettelem config                                -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                    GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>   -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                    GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
#   ettelem sptrace <file>                        -> TRACE_EXTRACT (no DM command: two driver ioctls copy the trace region; READ)
#   ettelem uptime                                -> GET_MODULE_UPTIME (service-processor RAM; READ): card 0's identity by continuity
# Anything else - `sample --reset-ms` (the statistics reset), `residency` (run_hpl.py's query, which E119 rewrites to states 1-3: never sent here),
# `threshold`, `loglevel`, any other word - is refused with exit 97 before the device is opened. It refuses to run unless ET_DEVICES=0 (card 0
# only). It execs the reader, so the process keeps this PID and its name becomes `ettelem` (run_hpl.py's DEV_COMM and its SIGTERM see it as before).
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REAL="$HERE/../../../build/ettelem-e84/ettelem"
refuse() { echo "ettelem_guard_e170: refused ($*): not in E170's classified command list" >&2; exit 97; }
[ "${ET_DEVICES:-}" = 0 ] || refuse "ET_DEVICES is '${ET_DEVICES:-unset}', not 0: E170 opens card 0 only"
case "${1:-}" in
  config)
    [ $# -eq 1 ] || refuse "$@"
    exec "$REAL" config ;;
  uptime)
    [ $# -eq 1 ] || refuse "$@"
    exec "$REAL" uptime ;;
  sptrace)
    [ $# -eq 2 ] || refuse "$@"
    case "$2" in -*|'') refuse "$@" ;; esac
    exec "$REAL" sptrace "$2" ;;
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
    exec "$REAL" sample ${args[@]+"${args[@]}"} ;;
  *) refuse "$@" ;;
esac
