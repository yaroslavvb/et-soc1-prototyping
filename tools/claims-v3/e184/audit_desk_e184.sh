#!/usr/bin/env bash
# E184 (Q153, the kit): the device-command audit of the files that never run on a box (the desk's reducer, scorer, readers, synthetic
# sessions, self-tests, the registration's scripts, the harness maker, the desk tests and the Intel dry pass): Q136(w)'s dmcmd_audit with no
# WRITE allowed. The dry pass's step 1d runs E184's telemetry guard against its own stub reader (build/ettelem/ettelem replaced, inside a
# scratch copy of the tree on the Intel, by a script that echoes its arguments), so its two guard-test lines are reviewed exceptions: no
# device and no card is reached there.
#   bash tools/claims-v3/e184/audit_desk_e184.sh        # exit 0 = GO
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=tools/claims-v3/e184
WHY="the Intel dry pass runs E184's guard against a stub reader that echoes its arguments, in a scratch tree: no device"
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "$D/dry_intel_e184.sh:70:VARIANT_UNRESOLVED=$WHY" --except "$D/dry_intel_e184.sh:70:STATS_RESET=$WHY" \
  --except "$D/dry_intel_e184.sh:71:VARIANT_UNRESOLVED=$WHY" --except "$D/dry_intel_e184.sh:71:STATS_RESET=$WHY" \
  --except "$D/dry_intel_e184.sh:71:SET_DM_TRACE_CONFIG=$WHY" \
  $D/reduce_e184.py $D/score_e184.py $D/tau_a1_e184.py $D/fake_card_e184.py $D/selftest_score_e184.py $D/power_e184.py \
  $D/inputs_e184.py $D/plan_e184.py $D/make_harness_e184.py $D/desk/desktest_host_e184.sh $D/desk/desktest_runner_e184.py \
  $D/desk/mock_runtime_e184.cpp $D/dry_intel_e184.sh $D/audit_desk_e184.sh
