#!/usr/bin/env bash
# E190 (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py
# (unchanged) on every file E190's session runs or builds, with NO --allow (no WRITE of any kind: not even the statistics reset) and NO
# exception: the runner and its common module, the session's wrapper, the build, the harness check, E190's guard (the only way the runner
# calls a telemetry reader: `config`, and `sample` with --seconds and --every-ms only, refusing --reset-ms and every other word before the
# device opens; build/ettelem-hpl/ettelem on aifoundry2, build/ettelem/ettelem on aifoundry1), and the host's source (it opens the ops node
# only). The runner runs it on the box before its first device access and opens nothing unless it reads GO (E190.md section 8).
# Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e190/preflight_e190.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  tools/claims-v3/e190/run_e190.py tools/claims-v3/e190/e190_common.py tools/claims-v3/e190/session_e190.sh \
  tools/claims-v3/e190/build_e190.sh tools/claims-v3/e190/check_e190.py tools/claims-v3/e190/ettelem_guard_e190.sh \
  tools/claims-v3/e136/rgm136/host/main.cpp
