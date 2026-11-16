#!/usr/bin/env bash
# E198's kit after dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): dmcmd_audit on every file the A1
# session's chain runs, at the desk and on the box. It is preflight_e198.sh (kit-e198, Q191; unchanged beside it) with A1's files in place
# of the ones A1 replaces: session_e198a1.sh for session_e198.sh, the lab's runner copy run_x04_e198a1.py for E193's run_x04.py,
# check_e198a1.py beside check_e198.py (which it imports), build_e198a1.sh for build_e198.sh, harness_e198a1.py for harness_e198.py. The
# device commands the session can send are still E191's guard's: `config` and `sample --seconds N --every-ms N`, every one a READ; the
# runner copy, the host, the kernel and the kit's own files send none of their own.
#   bash tools/claims-v3/e198/preflight_e198a1.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
E=tools/claims-v3/e198
P=tools/claims-v3/e193/proposal/src
exec python3 -B tools/claims-v3/dmcmd_audit.py "$@" \
  $E/session_e198a1.sh $E/privdev_e198.sh $E/warden_e198.py $E/holdercheck_e198.sh $E/x04host_e198.sh $E/ettelem_guard_e198.sh \
  $E/dropruntime_e198.py $E/ident_e198.py $E/ident_inner_e198.sh $E/check_e198.py $E/check_e198a1.py $E/build_e198a1.sh $E/harness_e198a1.py \
  tools/claims-v3/e191/ettelem_guard_e191.sh tools/claims-v3/e191/e191_ident.py tools/claims-v3/e193/check_e193.py \
  $E/run_x04_e198a1.py $P/host/main.cpp $P/x04_args.h $P/kernel/x04clock.c
