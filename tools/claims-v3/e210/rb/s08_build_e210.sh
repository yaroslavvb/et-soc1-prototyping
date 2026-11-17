#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c), the box step "the build" (this file is s08; step 6): E206's step 6
# (tools/claims-v3/e206/rb/s08_build_e206.sh, landed in 906699ea) running build_e210.sh (rgm136 into build/e210rgm; THE KERNEL GATE; the host's
# four refusals). ONE DETACHED JOB, a3-build-e210 (build_e210.sh under a plain `timeout 500`: never -k), refused beside a session of ours
# (ours_live) or a runbook job (jobs_live). THE BUILD-ATTEMPT COUNT (NO-THIRD-BUILD): the box's build/e210-build-attempts.txt counts the build
# job's starts each Pacific day; a third start the same day is refused with 16, and E210 has no session that day. A second start only when the
# first did not build. After the job, `wait` reads its verdict line (RGM-BUILT rc=0 / RGM-BUILD-FAILED), writes RB_OUT/e210-built-A.txt, and
# reads, in one 60 s call: the build record (build/e210rgm/BUILD-e210.json: today, BUILT, builder build_e210.sh, the box, the kernel gate's
# KERNEL OK line), the harness, the preflight (dmcmd_audit_v2 GO) and the two modules' self-checks. A cut WAIT CALL is not a failed build (14,
# "no reading": wait again).
#   bash tools/claims-v3/e210/rb/s08_build_e210.sh A start      then      ... A wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e210.sh"
rb_init s08_build
e210_arm "${1:-}"
act=${2:-}
e210_jobs "$ARM"
JOB=$JOB_BUILD
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_build_e210.sh A start | wait" ;; esac
e210_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe "$BOX"
  f=$(rb_file count)
  { rb_prelude "$BOX"
    echo "JOB=$JOB"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E210's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E210's build starts alone"; exit 3; fi
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f build/e210-build-attempts.txt ] && n=$(grep -cE "^$TODAY .* $JOB started\$" build/e210-build-attempts.txt)
echo "E210-BUILDS-TODAY $n"
if job_ok_today "$JOB" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JOB.out" 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read "$BOX" "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E210-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "rgm136 was built today on $BOX by E210's build: run this step's wait (a second build would replace the good one)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on $BOX today (Pacific): no E210 session today"
  fi
  body=$(rb_file body)
  { echo "JOB=$JOB"
    cat <<'EOF2'
mkdir -p build/e210-build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build/e210-build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* $JOB started\$" build/e210-build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $JOB started" >> build/e210-build-attempts.txt
L=build/e210-build-logs/$TODAY-start$k.txt
timeout 500 bash tools/claims-v3/e210/build_e210.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $JOB ended rc=$rc: $(grep -E '^RGM-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60)" >> build/e210-build-attempts.txt
exit $rc
EOF2
  } > "$body"
  rb_job_start "$BOX" "$JOB" "$body"
  rb_say "the build job $JOB started on $BOX: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe "$BOX"
rb_job_wait "$BOX" "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e210-built-$ARM.txt from the verdict line; the build record, the harness, the preflight and both self-checks, one 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today on $BOX: run this step's start"
cap=$RB_CAP
grep -qE '^RGM-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|KERNEL|HOST|HOSTCHECK|ETDEVICES|RGM)' "$cap" | cut -c1-220 | sed 's/^/    /'
grep -q '^RGM-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "rgm136 did not build on $BOX (the lines above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no E210 session today"
echo rgm > "$RB_OUT/e210-built-$ARM.txt"
rb_probe "$BOX"
f=$(rb_file checks)
{ rb_prelude "$BOX"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
python3 -B - <<'PY'
import json
r = json.load(open("build/e210rgm/BUILD-e210.json"))
print(f"BUILD-RECORD {r.get('verdict')} {r.get('day')} {r.get('box')} builder {r.get('builder')} host {r.get('host_sha256', '')[:12]} checks {r.get('host_checks')}")
print(f"BUILD-GATE {r.get('kernel_gate')}")
print(f"BUILD-ETDEVICES {r.get('et_devices')}")
PY
python3 -B tools/claims-v3/e210/check_e210.py --box | tail -n 1
bash tools/claims-v3/e210/preflight_e210.sh 2>&1 | head -n 1
python3 -B tools/claims-v3/e210/e210_common.py | tail -n 1
python3 -B tools/claims-v3/e210/e210_ident.py | tail -n 1
EOF2
} > "$f"
rb_remote read "$BOX" "the build record, the harness, the preflight, both self-checks" "$f"
rb_refused
rb_has "^BUILD-RECORD BUILT $(TZ=America/Los_Angeles date +%F) $BOX builder build_e210.sh " || rb_die $RB_E_GATE "the build record is not today's BUILT by build_e210.sh on $BOX (the line above): no session"
rb_has '^BUILD-GATE KERNEL OK: ' || rb_die $RB_E_GATE "the kernel gate did not read KERNEL OK on $BOX (the line above): no session"
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness did not read OK on $BOX (the line above): no session"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on $BOX: no session"
rb_has '^E210-COMMON SELF-CHECK PASS' || rb_die $RB_E_GATE "the common module's self-check failed on $BOX: no session"
rb_has '^E210-IDENT SELF-CHECK PASS' || rb_die $RB_E_GATE "the identity module's self-check failed on $BOX: no session"
rb_say "built today on $BOX: rgm136 into build/e210rgm (THE KERNEL GATE: KERNEL OK; the host read by its behaviour); harness, preflight GO and both self-checks read on the box"
exit 0
