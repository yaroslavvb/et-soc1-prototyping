#!/usr/bin/env bash
# E184 (Q155), kit note 3 (KIT.md.dated-note-3.md section 5): the device-command audit of the desk files dated amendment A4 and kit note 3 add
# that never run on a box, in audit_desk_e184_v3.sh's form (v3, which stays as committed): Q136(w)'s dmcmd_audit, no WRITE allowed, no
# exception: the v4 reducer, its self-test, the v3 collector, the interpreter check v4 and this file. The runbook's own audit is
# audit_rb_e184_v3.sh.
#   bash tools/claims-v3/e184/audit_desk_e184_v4.sh        # exit 0 = GO
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=tools/claims-v3/e184
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  $D/reduce_e184_v4.py $D/selftest_reduce_e184_v4.py $D/collect_e184_v3.sh $D/interp_check_e184_v4.sh $D/audit_desk_e184_v4.sh
