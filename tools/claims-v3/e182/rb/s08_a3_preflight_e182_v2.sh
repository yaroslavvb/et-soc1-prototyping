#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1), step 8 v2: E182's checks on the box, no device opened. It is v1 (rb/s08_a3_preflight_e182.sh, which
# stays as committed) with the train host built by build_host_e182_v2.sh from exactly its pinned inputs, and with the inputs checked first:
#   1. (trains) check_inputs_e182.py on the box: the 8 build inputs step 7 v2 sent and note 1's two box files at harness-e182-note1.json's
#      sha256 (NOTE1 FILES OK: 10 files). If they differ, nothing is built and an earlier build's host, copy and record are removed:
#      TRAIN-HOST-INPUTS-DIFFER, exit 16, and the message says to run step 7 v2 once more and then this step; if they differ again, the
#      trains do not run that day (the fallback below);
#   2. (trains) the train host's first compile on the box, build_host_e182_v2.sh (BUILD OK), as v1's build but from the pinned copy;
#      a failed build reads TRAIN-HOST-BUILD-FAILED, exit 16, and the message names the registered fallback's three v2 steps;
#   3. as v1: check_e182.py (HARNESS OK: 73 files with the trains, 70 with --no-trains), the device-command preflight (GO) and the items'
#      check (0 problems).
# THE FALLBACK (E182.md section 7, PASSES; the verifier's MAJOR 1): this step again with --no-trains (no input check and no build: the
# kinds passes read none of them), then step 10 v2 with --no-trains, then step 11 v2 PASSES no.
#
#   bash tools/claims-v3/e182/rb/s08_a3_preflight_e182_v2.sh [--no-trains]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s08_a3_preflight_v2
NT=; [ "${1:-}" = --no-trains ] && NT=--no-trains
FALLBACK="no train runs today: run step 8 v2 with --no-trains, then step 10 v2 with --no-trains (start, then wait), then step 11 v2 PASSES no (E182.md section 7's registered fallback; every train rule reads NOT SCORED)"
rb_probe aifoundry3
f=$(rb_file e182)
{ rb_prelude aifoundry3
  echo "NT=$NT"
  cat <<'EOF2'
if [ -z "$NT" ]; then
  python3 -B tools/claims-v3/e182/check_inputs_e182.py > build/e182-inputs.txt 2>&1; ci=$?
  head -n 12 build/e182-inputs.txt | cut -c1-240; echo "check_inputs_e182 rc=$ci"
  if [ "$ci" -ne 0 ]; then
    rm -rf build/e182host/b build/e182host/src build/e182host/SHA256     # no train host of an earlier build outlives a refused one
    echo "TRAIN-HOST-INPUTS-DIFFER rc=$ci"
  else
    timeout 500 bash tools/claims-v3/e182/build_host_e182_v2.sh > build/e182-build-host.txt 2>&1; b=$?
    tail -n 6 build/e182-build-host.txt | cut -c1-240
    if [ "$b" -ne 0 ] || ! grep -q '^BUILD OK' build/e182-build-host.txt; then echo "TRAIN-HOST-BUILD-FAILED rc=$b"; fi
  fi
fi
python3 -B tools/claims-v3/e182/check_e182.py $NT; echo "check_e182 rc=$?"
bash tools/claims-v3/e182/preflight_e182.sh > build/e182-preflight-rb.txt 2>&1; echo "preflight_e182 rc=$? $(grep -m1 '^dmcmd_audit:' build/e182-preflight-rb.txt)"
python3 -B tools/claims-v3/e182/e182_common.py --verify | tail -n 3; echo "e182_common rc=${PIPESTATUS[0]}"
EOF2
} > "$f"
rb_remote read aifoundry3 "E182's preflight on the box (v2: the build inputs checked, then the train host built from them)" "$f"
if [ -z "${RB_DRY:-}" ]; then
  rb_has '^TRAIN-HOST-INPUTS-DIFFER' && rb_die $RB_E_GATE "the train host's build inputs on aifoundry3 are not the pinned ones (the lines above), so nothing was built: run step 7 v2 once more, then this step; if they differ again, $FALLBACK"
  rb_has '^TRAIN-HOST-BUILD-FAILED' && rb_die $RB_E_GATE "the train host did not build on aifoundry3 (the lines above): $FALLBACK"
fi
bad=""
want=73; [ -n "$NT" ] && want=70
rb_has "^HARNESS OK: $want files" || bad="$bad harness"
[ -n "$NT" ] || rb_has '^check_inputs_e182 rc=0$' || bad="$bad check_inputs_e182"
rb_has '^check_e182 rc=0$' || bad="$bad check_e182"
rb_has '^preflight_e182 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e182"
rb_has '^e182_common rc=0$' || bad="$bad e182_common"
[ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's preflight failed:$bad (a binary or file differs: a dated amendment first)"
rb_say "aifoundry3: $([ -n "$NT" ] && echo 'the trains off (the fallback), ' || echo 'the build inputs at their pins, the train host built, ')HARNESS OK $want, preflight_e182 GO, e182_common verified"
