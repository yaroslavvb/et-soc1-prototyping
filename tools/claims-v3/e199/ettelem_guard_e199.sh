#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): the only way E199's kit reads card 1's static config (the session's
# start and end reads, the gate (a), and step 7's read). E191's guard (tools/claims-v3/e191/ettelem_guard_e191.sh, unchanged beside it)
# narrowed to one word: an allow-list in front of card 1's reader, so the device-management commands sent are exactly the classified ones:
#   ettelem config   -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES,
#                       GET_ASIC_VOLTAGE (all READ in the audit table)
# Anything else (sample, residency, threshold, loglevel, sptrace, uptime, --reset-ms, any other word) is refused with exit 97 before the
# device is opened; the session's sampler is run_session.sh's own registered `"$ETTELEM" sample --seconds T --every-ms 100`. The box must
# be aifoundry1 and ET_DEVICES must be 1 (aifoundry1's device layer then opens card 1 only); else refused before the device opens. The
# reader is the box tree's build/ettelem/ettelem (k6's tree for aifoundry1, ~/nekko: E157's, E164's, E172's, E190 arm B's and E191's
# reader on card 1, pinned at 8008f96f... by E191's kit; session_e199.sh checks that pin before anything). It execs the reader.
#   ET_DEVICES=1 bash <E199's root>/tools/claims-v3/e199/ettelem_guard_e199.sh config
# SPDX-License-Identifier: Apache-2.0
set -u
TREE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../../.." && pwd)"
refuse() { echo "ettelem_guard_e199: refused ($*): not in E199's classified command list" >&2; exit 97; }
BOX=$(hostname 2>/dev/null | cut -d. -f1)
[ "$BOX" = aifoundry1 ] || refuse "box '$BOX': E199 runs on aifoundry1 card 1 only"
[ "${ET_DEVICES:-}" = 1 ] || refuse "ET_DEVICES is '${ET_DEVICES:-unset}', not 1: E199 opens card 1 only"
case "${1:-}" in
  config)
    [ $# -eq 1 ] || refuse "$@"
    exec "$TREE/build/ettelem/ettelem" config ;;
  *) refuse "$@" ;;
esac
