#!/usr/bin/env bash
# E180 (Q146(f), the kit), step 8: E180's build and checks on aifoundry3, as one detached job of the runbook (k6's rb_job_start /
# rb_job_wait: a cmake build outlasts a bounded read), no device opened: build_e180.sh (the catalogue with E180's two accumulating modes,
# from the committed workloads/enercat into build/enercat-e180 at nice with 4 jobs, its binaries recorded in BUILD-E180.json), then the
# harness with the binaries (HARNESS OK) and the device-command preflight (GO). It refuses during a card session of ours (rb_job_start). A
# recorded build is never rebuilt without --rebuild, so a session only ever runs the binary recorded before it. tools/claims-v3/e178/rb/
# s08_a3_preflight_e178.sh's checks, s10_a3_dry_e178.sh's job form.
#
#   bash tools/claims-v3/e180/rb/s08_a3_build_e180.sh start       then        ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s08_a3_build
act=${1:-}
case "$act" in
  start)
    body=$(rb_file body)
    cat > "$body" <<'EOF2'
bash tools/claims-v3/e180/build_e180.sh > build/e180-build-rb.txt 2>&1; b=$?; echo "build_e180 rc=$b $(tail -n 1 build/e180-build-rb.txt)"
python3 -B tools/claims-v3/e180/check_e180.py harness --binaries; c=$?; echo "check_e180 rc=$c"
bash tools/claims-v3/e180/preflight_e180.sh > build/e180-preflight-rb.txt 2>&1; p=$?; echo "preflight_e180 rc=$p $(grep -m1 '^dmcmd_audit:' build/e180-preflight-rb.txt)"
[ "$b" -eq 0 ] && [ "$c" -eq 0 ] && [ "$p" -eq 0 ]
EOF2
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-build-e180 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-build-e180; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'build_e180 rc=' 'HARNESS ' 'check_e180 rc=' 'preflight_e180 rc='; do grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"; done
    fi
    [ "$rc" -eq 0 ] || exit "$rc"
    bad=""
    rb_has '^build_e180 rc=0 ' || bad="$bad build"
    rb_has '^HARNESS OK: ' || bad="$bad harness"
    rb_has '^preflight_e180 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e180"
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's build or preflight failed:$bad (a file or binary differs: a dated amendment first)"
    rb_say "aifoundry3: build_e180 OK, HARNESS OK with the binaries, preflight_e180 GO"
    ;;
  *) rb_die $RB_E_USAGE "usage: s08_a3_build_e180.sh start|wait" ;;
esac
