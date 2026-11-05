#!/usr/bin/env bash
# Q142(k6), step 8: E171's checks on the box (E171's README, box steps 5-7), no device opened: pool 8's SHA256SUMS (89 OK), the harness
# with the binaries (HARNESS OK: 101 files), the device-command preflight (GO) and the items' check (0 problems).
#
#   bash tools/claims-v3/q141k-runbook/k6/s08_a3_preflight_k6.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s08_a3_preflight
rb_probe aifoundry3
f=$(rb_file e171)
{ rb_prelude aifoundry3
  cat <<'EOF'
echo "blind8 OK: $(cd tools/claims-v3/kinds/blind8 && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$')"
python3 -B tools/claims-v3/e171/check_e171.py; echo "check_e171 rc=$?"
bash tools/claims-v3/e171/preflight_e171.sh > build/e171-preflight-k6.txt 2>&1; echo "preflight_e171 rc=$? $(grep -m1 '^dmcmd_audit:' build/e171-preflight-k6.txt)"
python3 -B tools/claims-v3/e171/e171_common.py --verify | tail -n 3; echo "e171_common rc=${PIPESTATUS[0]}"
EOF
} > "$f"
rb_remote read aifoundry3 "E171's preflight (README steps 5-7)" "$f"
bad=""
rb_has '^blind8 OK: 89$' || bad="$bad blind8"
rb_has '^HARNESS OK: 101 files' || bad="$bad harness"
rb_has '^check_e171 rc=0$' || bad="$bad check_e171"
rb_has '^preflight_e171 rc=0 ' || bad="$bad preflight_e171"
rb_has '^e171_common rc=0$' || bad="$bad e171_common"
[ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's preflight failed:$bad (a binary or file differs: a dated amendment first)"
rb_say "aifoundry3: blind8 89, HARNESS OK 101, preflight_e171 GO, e171_common verified"
