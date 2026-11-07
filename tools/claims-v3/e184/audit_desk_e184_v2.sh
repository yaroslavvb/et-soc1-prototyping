#!/usr/bin/env bash
# E184 (Q153), kit v2 (KIT.md.dated-note-1.md section 6): the device-command audits of the files kit note 1 and dated amendment A2 add that
# never run as a card session's own files, in audit_desk_e184.sh's form (v1, which stays as committed): Q136(w)'s dmcmd_audit, no WRITE
# allowed: the v2 reducer and scorer, the A2 power and checks, the v2 synthetic sessions and self-test, the v2 harness maker, the runner's v2
# desk test, the v2 dry pass (its two guard-test lines, 74 and 75, run E184's guard against its own stub reader inside a scratch tree on the
# Intel: reviewed exceptions, as v1's lines 70 and 71), the interpreter check v2 and the collector. The runbook's own audit is
# audit_rb_e184.sh.
#   bash tools/claims-v3/e184/audit_desk_e184_v2.sh        # exit 0 = GO
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=tools/claims-v3/e184
WHY="the Intel dry pass runs E184's guard against a stub reader that echoes its arguments, in a scratch tree: no device"
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "$D/dry_intel_e184_v2.sh:74:VARIANT_UNRESOLVED=$WHY" --except "$D/dry_intel_e184_v2.sh:74:STATS_RESET=$WHY" \
  --except "$D/dry_intel_e184_v2.sh:75:VARIANT_UNRESOLVED=$WHY" --except "$D/dry_intel_e184_v2.sh:75:STATS_RESET=$WHY" \
  --except "$D/dry_intel_e184_v2.sh:75:SET_DM_TRACE_CONFIG=$WHY" \
  $D/reduce_e184_v2.py $D/score_e184_v2.py $D/power_e184_a2.py $D/a2_check_e184.py $D/fake_card_e184_v2.py $D/selftest_score_e184_v2.py \
  $D/make_harness_e184_v2.py $D/desk/desktest_runner_e184_v2.py $D/dry_intel_e184_v2.sh $D/interp_check_e184_v2.sh $D/collect_e184.sh \
  $D/audit_desk_e184_v2.sh
