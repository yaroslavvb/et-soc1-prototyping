#!/usr/bin/env bash
# E185, step 8: E185's checks on the box (its README, box step 3), no device opened: the box list (30 OK, the three binaries included), the
# device-command preflight (GO), and the runner's --list (the four E78 tiles against kinds.json, no problem).
# ../../q143k-runbook/s08_a3_preflight_q143k.sh (92a1b27f) ported.
#
#   bash tools/claims-v3/e185/rb/s08_a3_preflight_e185.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e185.sh"
rb_init s08_a3_preflight
rb_probe aifoundry3
f=$(rb_file e185)
{ rb_prelude aifoundry3
  cat <<'EOF2'
echo "box list OK: $(sha256sum -c tools/claims-v3/e185/frozen-e185.sha256 2>&1 | grep -c ': OK$')"
mkdir -p build
bash tools/claims-v3/e185/preflight_e185.sh > build/e185-preflight-rb.txt 2>&1; echo "preflight_e185 rc=$? $(grep -m1 '^dmcmd_audit:' build/e185-preflight-rb.txt)"
python3 -B tools/claims-v3/e185/run_e185.py /dev/null --root "$PWD" --list > build/e185-list-rb.txt 2>&1; r=$?
echo "run_e185 --list rc=$r tile_problems=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["tile_problems"]))' build/e185-list-rb.txt 2>/dev/null)"
EOF2
} > "$f"
rb_remote read aifoundry3 "E185's preflight (README box step 3)" "$f"
bad=""
rb_has '^box list OK: 30$' || bad="$bad boxlist"
rb_has '^preflight_e185 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e185"
rb_has '^run_e185 --list rc=0 tile_problems=0$' || bad="$bad run_e185-list"
[ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's preflight failed:$bad (a binary or file differs: a dated amendment first)"
rb_say "aifoundry3: box list 30, preflight_e185 GO, the four E78 tiles as kinds.json lists them"
