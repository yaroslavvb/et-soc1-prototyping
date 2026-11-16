#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), the box step "the build" (this file is s08): the program built on
# aifoundry3, the kernel read by its .text, THE FILES fetched or made there and checked by sha256, the host read by its BEHAVIOUR, no device
# opened. E189's step 6 form (tools/claims-v3/e189/rb/s08_a3_build_e189.sh): the build is ONE DETACHED JOB, a3-build-e202 (build_e202.sh
# under `timeout -k 15 1500`: a build opens no device), refused beside a session of ours (ours_live) or a runbook job (jobs_live). THE
# BUILD-ATTEMPT COUNT (E183's NO-THIRD-BUILD): the box's build/e202-build-attempts.txt counts the starts each Pacific day; a third start the
# same day is refused with 16 (no session that day). A second start is allowed only when the first did not read E202-BUILT. Each start's
# log is kept, build/e202-build-logs/<day>-start<k>.txt. After the job, `wait` reads its verdict (E202-BUILT rc=0, or E202-BUILD-FAILED:
# <why>), writes RB_OUT/e202-built.txt, and reads, in one 60 s call: the harness with the built kernel (check_e202.py --box --built: the
# .text at its pin, the host and ELF at today's record), the preflight (dmcmd_audit_v2 GO) and the common module's self-check. A cut WAIT
# CALL is not a failed build (14, "no reading": wait again).
#   bash tools/claims-v3/e202/rb/s08_a3_build_e202.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e202.sh"
rb_init s08_a3_build
act=${1:-}
JOB=a3-build-e202
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_a3_build_e202.sh start | wait" ;; esac
e202_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  f=$(rb_file count)
  { rb_prelude aifoundry3
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E202's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E202's build starts alone"; exit 3; fi
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f build/e202-build-attempts.txt ] && n=$(grep -c "^$TODAY .* a3-build-e202 started\$" build/e202-build-attempts.txt)
echo "E202-BUILDS-TODAY $n"
if job_ok_today a3-build-e202 && grep -q '^E202-BUILT rc=0' build/q141k/jobs/a3-build-e202.out 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read aifoundry3 "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E202-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "E202 was built today: run this step's wait (a second build would remove the good one)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry3 today (Pacific): no E202 session today"
  fi
  body=$(rb_file body)
  cat > "$body" <<'EOF2'
mkdir -p build/e202-build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build/e202-build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* a3-build-e202 started\$" build/e202-build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e202 started" >> build/e202-build-attempts.txt
L=build/e202-build-logs/$TODAY-start$k.txt
timeout -k 15 1500 bash tools/claims-v3/e202/build_e202.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e202 ended rc=$rc: $(grep -E '^E202-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60 | tr '\n' ' ')" >> build/e202-build-attempts.txt
exit $rc
EOF2
  rb_job_start aifoundry3 "$JOB" "$body"
  rb_say "the build job $JOB started on aifoundry3: run this step's wait (bounded) until it ends"
  exit 0
fi
# wait
rb_probe aifoundry3
rb_job_wait aifoundry3 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e202-built.txt from the verdict; the harness with the built kernel, the preflight and the self-check, one 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
grep -qE '^E202-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|E202 kernel|E202 warnings|  E202-FILES|  HOST-BEHAVIOUR|E202-BUILT|E202-BUILD-FAILED)' "$cap" | cut -c1-220 | sed 's/^/    /'
grep -q '^E202-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "E202 did not build (the lines above): run start once more if this was today's first start (one re-run); after a second, NO-THIRD-BUILD: no session today"
echo "E202-BUILT" > "$RB_OUT/e202-built.txt"
rb_probe aifoundry3
f=$(rb_file checks)
{ rb_prelude aifoundry3
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
python3 -B tools/claims-v3/e202/check_e202.py --box --built | tail -n 1
bash tools/claims-v3/e202/preflight_e202.sh 2>&1 | grep -m1 '^dmcmd_audit: '
python3 -B tools/claims-v3/e202/e202_common.py | tail -n 1
EOF2
} > "$f"
rb_remote read aifoundry3 "the harness with today's kernel, the preflight, the common self-check" "$f"
rb_refused
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness with today's build did not read OK (the line above): no session on these binaries"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on the box: no session"
rb_has '^E202-COMMON SELF-CHECK PASS' || rb_die $RB_E_GATE "the common module's self-check failed on the box: no session"
rb_say "built today on aifoundry3: E202 (the kernel's .text at its pin; the files 18 of 18 at their pins; the host's behaviour); harness, preflight GO and self-check read on the box"
exit 0
