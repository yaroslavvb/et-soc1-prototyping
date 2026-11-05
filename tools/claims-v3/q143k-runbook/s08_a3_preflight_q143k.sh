#!/usr/bin/env bash
# Q143(k), step 8: E176's checks on the box (its README, box step 3), no device opened: the box list (29 OK, the three binaries included), the
# device-command preflight (GO), and the runner's --list (the four E78 tiles against kinds.json, no problem).
#
#   bash tools/claims-v3/q143k-runbook/s08_a3_preflight_q143k.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s08_a3_preflight
rb_probe aifoundry3
f=$(rb_file e176)
{ rb_prelude aifoundry3
  cat <<'EOF2'
echo "box list OK: $(sha256sum -c tools/claims-v3/e176/frozen-e176.sha256 2>&1 | grep -c ': OK$')"
mkdir -p build
bash tools/claims-v3/e176/preflight_e176.sh > build/e176-preflight-q143k.txt 2>&1; echo "preflight_e176 rc=$? $(grep -m1 '^dmcmd_audit:' build/e176-preflight-q143k.txt)"
python3 -B tools/claims-v3/e176/run_e176.py /dev/null --root "$PWD" --list > build/e176-list-q143k.txt 2>&1; r=$?
echo "run_e176 --list rc=$r tile_problems=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["tile_problems"]))' build/e176-list-q143k.txt 2>/dev/null)"
EOF2
} > "$f"
rb_remote read aifoundry3 "E176's preflight (README box step 3)" "$f"
bad=""
rb_has '^box list OK: 29$' || bad="$bad boxlist"
rb_has '^preflight_e176 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e176"
rb_has '^run_e176 --list rc=0 tile_problems=0$' || bad="$bad run_e176-list"
[ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's preflight failed:$bad (a binary or file differs: a dated amendment first)"
rb_say "aifoundry3: box list 29, preflight_e176 GO, the four E78 tiles as kinds.json lists them"
