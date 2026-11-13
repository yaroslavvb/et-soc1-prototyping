#!/usr/bin/env bash
# E190 (Q169, the kit), the box step "the build" (this file is s08), for one arm: E136's rgm136 built on the arm's box into build/e190rgm and
# read by its kernel's bytes and its host's behaviour, no device opened. E189's step 6's form: ONE DETACHED JOB, a2-build-e190 or
# a1-build-e190 (build_e190.sh under `timeout -k 15 500`), refused beside a session of ours (ours_live) or a runbook job (jobs_live).
# THE BUILD-ATTEMPT COUNT (E183's NO-THIRD-BUILD): the box's build/e190-build-attempts.txt counts the starts each Pacific day; a third start
# the same day is refused with 16, and that arm has no session that day (no data, never a failed prediction). A second start is allowed only
# when the first did not build. Each start's log is kept, build/e190-build-logs/<day>-start<k>.txt. After the job, `wait` reads its verdict
# line (RGM-BUILT rc=0 / RGM-BUILD-FAILED), writes RB_OUT/e190-built-<arm>.txt, and reads, in one 60 s call: the build record
# (build/e190rgm/BUILD-e190.json: today, BUILT, the kernel at the pin), the harness, the preflight (dmcmd_audit GO) and the common
# self-check. A cut WAIT CALL is not a failed build (14, "no reading": wait again).
#   bash tools/claims-v3/e190/rb/s08_build_e190.sh <A|B> start      then      ... <A|B> wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190.sh"
rb_init s08_build
e190_arm "${1:-}"
act=${2:-}
JOB=$([ "$ARM" = A ] && echo a2 || echo a1)-build-e190
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_build_e190.sh <A|B> start | wait" ;; esac
e190_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe "$BOX"
  f=$(rb_file count)
  { rb_prelude "$BOX"
    echo "JOB=$JOB"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E190's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E190's build starts alone"; exit 3; fi
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f build/e190-build-attempts.txt ] && n=$(grep -c "^$TODAY .* $JOB started\$" build/e190-build-attempts.txt)
echo "E190-BUILDS-TODAY $n"
if job_ok_today "$JOB" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JOB.out" 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read "$BOX" "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E190-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "rgm136 was built today on $BOX: run this step's wait (a second build would replace the good one)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on $BOX today (Pacific): no session of arm $ARM today"
  fi
  body=$(rb_file body)
  { echo "JOB=$JOB"
    cat <<'EOF2'
mkdir -p build/e190-build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build/e190-build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* $JOB started\$" build/e190-build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $JOB started" >> build/e190-build-attempts.txt
L=build/e190-build-logs/$TODAY-start$k.txt
timeout -k 15 500 bash tools/claims-v3/e190/build_e190.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $JOB ended rc=$rc: $(grep -E '^RGM-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60)" >> build/e190-build-attempts.txt
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
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e190-built-$ARM.txt from the verdict line; the build record, the harness, the preflight and the self-check, one 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today on $BOX: run this step's start"
cap=$RB_CAP
grep -qE '^RGM-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|KERNEL|HOST|HOSTCHECK|RGM)' "$cap" | cut -c1-200 | sed 's/^/    /'
grep -q '^RGM-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "rgm136 did not build on $BOX (the lines above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no session of arm $ARM today"
echo rgm > "$RB_OUT/e190-built-$ARM.txt"
rb_probe "$BOX"
f=$(rb_file checks)
{ rb_prelude "$BOX"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
python3 -B - <<'PY'
import json
r = json.load(open("build/e190rgm/BUILD-e190.json"))
print(f"BUILD-RECORD {r.get('verdict')} {r.get('day')} kernel {r.get('kernel_sha256', '')[:12]} host {r.get('host_sha256', '')[:12]} checks {r.get('host_checks')}")
PY
python3 -B tools/claims-v3/e190/check_e190.py --box | tail -n 1
bash tools/claims-v3/e190/preflight_e190.sh 2>&1 | head -n 1
python3 -B tools/claims-v3/e190/e190_common.py | tail -n 1
EOF2
} > "$f"
rb_remote read "$BOX" "the build record, the harness, the preflight, the common self-check" "$f"
rb_refused
rb_has "^BUILD-RECORD BUILT $(TZ=America/Los_Angeles date +%F) kernel aace138caf80 " || rb_die $RB_E_GATE "the build record is not today's BUILT at the kernel's pin (the line above): no session"
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness did not read OK on $BOX (the line above): no session"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on $BOX: no session"
rb_has '^E190-COMMON SELF-CHECK PASS' || rb_die $RB_E_GATE "the common module's self-check failed on $BOX: no session"
rb_say "built today on $BOX: rgm136 into build/e190rgm (the kernel at the registration's pin; the host read by its behaviour); harness, preflight GO and self-check read on the box"
exit 0
