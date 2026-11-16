#!/usr/bin/env bash
# x09: the device-command preflight, as the lab's e183/preflight_e183_v3.sh: the public lab repo's
# tools/claims-v3/dmcmd_audit.py, unchanged, on every file this request's session runs or sources, before any device
# opens. GO (exit 0), or session_x09.sh opens nothing. One reviewed exception, the lab's own for E180 and E183:
# lib.sh's start_sampler (line 154) forwards its "$@" into `ettelem sample`, which could carry a statistics reset;
# block_x09.sh's only start_sampler call passes the file and the duration alone.
#   bash tools/claims-v3/x09/preflight_x09.sh [--json | --markdown]
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$HERE/../../.." || exit 2
X=tools/claims-v3/$(basename "$HERE")
exec python3 -B tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=x09 never forwards a --reset-ms: block_x09.sh's only start_sampler call passes the file and the duration" \
  "$X/session_x09.sh" "$X/block_x09.sh" "$X/lib_x09.sh" "$X/watch_x09.py" "$X/smoke_gate_x09.py" "$X/make_x09.py" \
  "$X/host/main.cpp" tools/claims-v3/lib.sh tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh \
  tools/claims-v3/e128/ettelem_guard.sh
