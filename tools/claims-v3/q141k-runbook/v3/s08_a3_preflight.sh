#!/usr/bin/env bash
# Q141(k), go checklist step 8: aifoundry3's preflight, on the box, no device opened. Two reads (60 s each), after the probe:
#   E163 (README steps 5-7): blind7 sha256sum -c (91 OK); check_e163.py HARNESS OK (142 files, with the binaries 99ed75fb / d521e432
#   / 20e760c2 / 16037641); preflight_e163.sh GO; e163_common.py --verify (0 problems);
#   E166 (README box step 3): sha256sum -c frozen-e166.sha256 (30, the three binaries included); preflight_e166.sh GO.
# If any binary or file differs, that run stops here: a dated amendment comes first (16).
#
#   bash tools/claims-v3/q141k-runbook/s08_a3_preflight.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s08_a3_preflight
rb_probe aifoundry3
f=$(rb_file e163)
{ rb_prelude aifoundry3
  cat <<'EOF'
echo "blind7 OK: $(cd tools/claims-v3/kinds/blind7 && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$')"
python3 tools/claims-v3/e163/check_e163.py; echo "check_e163 rc=$?"
bash tools/claims-v3/e163/preflight_e163.sh > build/e163-preflight-q141k.txt 2>&1; echo "preflight_e163 rc=$? $(grep -m1 '^dmcmd_audit:' build/e163-preflight-q141k.txt)"
python3 tools/claims-v3/e163/e163_common.py --verify | tail -n 3; echo "e163_common rc=${PIPESTATUS[0]}"
EOF
} > "$f"
rb_remote read aifoundry3 "E163's preflight (README steps 5-7)" "$f"
bad=""
rb_has '^blind7 OK: 91$' || bad="$bad blind7"
rb_has '^HARNESS OK: 142 files' || bad="$bad harness"
rb_has '^check_e163 rc=0$' || bad="$bad check_e163"
rb_has '^preflight_e163 rc=0 ' || bad="$bad preflight_e163"
rb_has '^e163_common rc=0$' || bad="$bad e163_common"
f=$(rb_file e166)
{ rb_prelude aifoundry3
  cat <<'EOF'
sha256sum -c tools/claims-v3/e166/frozen-e166.sha256 > build/e166-frozen-q141k.txt 2>&1; echo "frozen-e166 rc=$? OK $(grep -c ': OK$' build/e166-frozen-q141k.txt)"
grep -v ': OK$' build/e166-frozen-q141k.txt | head -n 5
bash tools/claims-v3/e166/preflight_e166.sh > build/e166-preflight-q141k.txt 2>&1; echo "preflight_e166 rc=$? $(grep -m1 '^dmcmd_audit:' build/e166-preflight-q141k.txt)"
EOF
} > "$f"
rb_remote read aifoundry3 "E166's preflight (README box step 3)" "$f"
rb_has '^frozen-e166 rc=0 OK 30$' || bad="$bad frozen-e166"
rb_has '^preflight_e166 rc=0 ' || bad="$bad preflight_e166"
[ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's preflight failed:$bad (a binary or file differs: that run needs a dated amendment first)"
rb_say "aifoundry3: blind7 91, HARNESS OK 142, preflight_e163 GO, e163_common verified, frozen-e166 30 OK, preflight_e166 GO"
