#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 6: E184's build and checks on an arm's box, as one detached job of the
# runbook (k6's rb_job_start / rb_job_wait), no device opened: build_e184.sh (the patched host's first compile against the real runtime; a
# recorded build is never rebuilt without --rebuild), then check_e184_v2.py harness --binaries and preflight_e184_v2.sh <arm>. If the build
# fails, that arm does not run that day; the fix is a dated amendment. ../../e180/rb/s08_a3_build_e180_v2.sh's form, for either box. The job is
# named <a3|a1c1>-build-e184, which step 9 (s11_session_e184.sh) needs ended rc 0 today.
#
#   bash tools/claims-v3/e184/rb/s08_build_e184.sh S|B start       then        ... S|B wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s08_build
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s08_build_e184.sh S|B start|wait"
JOB=$E184_J-build-e184
case "${2:-}" in
  start)
    body=$(rb_file body)
    { echo "ARM=$E184_ARM"
      cat <<'EOF2'
bash tools/claims-v3/e184/build_e184.sh > build/e184-build-rb.txt 2>&1; b=$?; echo "build_e184 rc=$b $(tail -n 1 build/e184-build-rb.txt)"
python3 -B tools/claims-v3/e184/check_e184_v2.py harness --binaries; c=$?; echo "check_e184_v2 rc=$c"
bash tools/claims-v3/e184/preflight_e184_v2.sh "$ARM" > build/e184-preflight-rb-$ARM.txt 2>&1; p=$?
echo "preflight_e184_v2 rc=$p $(grep -m1 '^dmcmd_audit:' build/e184-preflight-rb-$ARM.txt)"
[ "$b" -eq 0 ] && [ "$c" -eq 0 ] && [ "$p" -eq 0 ]
EOF2
    } > "$body"
    rb_probe "$E184_BOX"
    rb_job_start "$E184_BOX" "$JOB" "$body" 1
    ;;
  wait)
    rb_probe "$E184_BOX"
    rb_job_wait "$E184_BOX" "$JOB"; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'build_e184 rc=' 'HARNESS ' 'check_e184_v2 rc=' 'preflight_e184_v2 rc='; do grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"; done
    fi
    [ "$rc" -eq 0 ] || exit "$rc"
    bad=""
    rb_has '^build_e184 rc=0 ' || bad="$bad build"
    rb_has '^HARNESS OK: ' || bad="$bad harness"
    rb_has '^preflight_e184_v2 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e184_v2"
    [ -z "$bad" ] || rb_die $RB_E_GATE "$E184_BOX's build or preflight failed:$bad (a file or binary differs: a dated amendment first)"
    rb_say "$E184_BOX: build_e184 OK, HARNESS OK with the binaries, preflight_e184_v2 $E184_ARM GO"
    ;;
  *) rb_die $RB_E_USAGE "usage: s08_build_e184.sh S|B start|wait" ;;
esac
