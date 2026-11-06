#!/usr/bin/env bash
# E178 (Q146, the kit), step 8: E178's checks on the box, no device opened: the harness with the binaries (HARNESS OK: 84 files), the
# device-command preflight (GO) and the items' check against the registered order (0 problems). A port of
# ../../q141k-runbook/k6/s08_a3_preflight_k6.sh.
#
#   bash tools/claims-v3/e178/rb/s08_a3_preflight_e178.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e178.sh"
rb_init s08_a3_preflight
rb_probe aifoundry3
f=$(rb_file e178)
{ rb_prelude aifoundry3
  cat <<'EOF2'
python3 -B tools/claims-v3/e178/check_e178.py; echo "check_e178 rc=$?"
bash tools/claims-v3/e178/preflight_e178.sh > build/e178-preflight-rb.txt 2>&1; echo "preflight_e178 rc=$? $(grep -m1 '^dmcmd_audit:' build/e178-preflight-rb.txt)"
python3 -B tools/claims-v3/e178/e178_common.py --verify | tail -n 3; echo "e178_common rc=${PIPESTATUS[0]}"
EOF2
} > "$f"
rb_remote read aifoundry3 "E178's preflight on the box" "$f"
bad=""
rb_has '^HARNESS OK: 84 files' || bad="$bad harness"
rb_has '^check_e178 rc=0$' || bad="$bad check_e178"
rb_has '^preflight_e178 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e178"
rb_has '^e178_common rc=0$' || bad="$bad e178_common"
[ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's preflight failed:$bad (a binary or file differs: a dated amendment first)"
rb_say "aifoundry3: HARNESS OK 84, preflight_e178 GO, e178_common verified (the registered order of every planned pass)"
