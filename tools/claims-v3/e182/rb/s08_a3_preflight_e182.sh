#!/usr/bin/env bash
# E182 (Q153, the kit), step 8: E182's checks on the box, no device opened. A port of E178's step 8 with one step first: THE TRAIN HOST'S
# FIRST COMPILE ON THE BOX (build_host_e182.sh: a copy of workloads/sparsity, patch_host_e182.py, cmake; nothing opens a card). Then the
# harness with the binaries and the train host (HARNESS OK: 73 files), the device-command preflight (GO) and the items' check (0 problems).
# If the compile fails, the step says TRAIN-HOST-BUILD-FAILED and exits 16: the trains do not run that day, and step 11 is then run with
# PASSES (E182.md section 7, the registered fallback; check_e182.py runs with --no-trains, HARNESS OK: 70 files).
#
#   bash tools/claims-v3/e182/rb/s08_a3_preflight_e182.sh [--no-trains]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s08_a3_preflight
NT=; [ "${1:-}" = --no-trains ] && NT=--no-trains
rb_probe aifoundry3
f=$(rb_file e182)
{ rb_prelude aifoundry3
  echo "NT=$NT"
  cat <<'EOF2'
if [ -z "$NT" ]; then
  timeout 500 bash tools/claims-v3/e182/build_host_e182.sh > build/e182-build-host.txt 2>&1; b=$?
  tail -n 4 build/e182-build-host.txt | cut -c1-240
  if [ "$b" -ne 0 ] || ! grep -q '^BUILD OK' build/e182-build-host.txt; then echo "TRAIN-HOST-BUILD-FAILED rc=$b"; fi
fi
python3 -B tools/claims-v3/e182/check_e182.py $NT; echo "check_e182 rc=$?"
bash tools/claims-v3/e182/preflight_e182.sh > build/e182-preflight-rb.txt 2>&1; echo "preflight_e182 rc=$? $(grep -m1 '^dmcmd_audit:' build/e182-preflight-rb.txt)"
python3 -B tools/claims-v3/e182/e182_common.py --verify | tail -n 3; echo "e182_common rc=${PIPESTATUS[0]}"
EOF2
} > "$f"
rb_remote read aifoundry3 "E182's preflight on the box (the train host built first)" "$f"
bad=""
[ -z "${RB_DRY:-}" ] && rb_has '^TRAIN-HOST-BUILD-FAILED' && rb_die $RB_E_GATE "the train host did not build on aifoundry3 (the lines above): no train runs today; run step 8 again with --no-trains, then step 11 with PASSES"
want=73; [ -n "$NT" ] && want=70
rb_has "^HARNESS OK: $want files" || bad="$bad harness"
rb_has '^check_e182 rc=0$' || bad="$bad check_e182"
rb_has '^preflight_e182 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e182"
rb_has '^e182_common rc=0$' || bad="$bad e182_common"
[ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's preflight failed:$bad (a binary or file differs: a dated amendment first)"
rb_say "aifoundry3: $([ -n "$NT" ] && echo 'the trains off, ' || echo 'the train host built, ')HARNESS OK $want, preflight_e182 GO, e182_common verified"
