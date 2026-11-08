#!/usr/bin/env bash
# E184 (Q154), kit note 2 (KIT.md.dated-note-2.md section 5): the device-command audit of the desk files dated amendment A3 and kit note 2 add
# that never run on a box, in audit_desk_e184_v2.sh's form (v2, which stays as committed): Q136(w)'s dmcmd_audit, no WRITE allowed, no
# exception: A3's power file, the v3 reducer and scorer, the v2 collector, the scorer's self-test v3, the interpreter check v3 and this file.
# The runbook's own audit is audit_rb_e184_v2.sh.
#   bash tools/claims-v3/e184/audit_desk_e184_v3.sh        # exit 0 = GO
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=tools/claims-v3/e184
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  $D/power_e184_a3.py $D/reduce_e184_v3.py $D/score_e184_v3.py $D/collect_e184_v2.sh $D/selftest_score_e184_v3.py $D/interp_check_e184_v3.sh \
  $D/audit_desk_e184_v3.sh
