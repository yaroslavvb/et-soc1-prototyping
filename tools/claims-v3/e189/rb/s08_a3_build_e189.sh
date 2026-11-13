#!/usr/bin/env bash
# E189 (Q167, the kit), the box step "the build" (this file is s08): the two programs built on aifoundry3 and read by their BEHAVIOUR, no
# device opened. E188's step 6's form (tools/claims-v3/e188/rb/s08_a3_build_e188.sh): the build is ONE DETACHED JOB, a3-build-e189
# (build_e189.sh under `timeout -k 15 500`: cmake against /opt/et into build/e189ledger and build/e189spp; each kernel by its ELF's and
# its .text's sha256 against the pins; each host by hostcheck_e189.py, never a string grepped from a binary), refused beside a session of
# ours (ours_live) or a runbook job (jobs_live). THE BUILD-ATTEMPT COUNT (E183's NO-THIRD-BUILD): the box's build/e189-build-attempts.txt
# counts the starts each Pacific day; a third start the same day is refused with 16, and the programs not built that day are SKIPPED
# (E189.md section 12: no data, never a failed prediction). A second start is allowed only when the first built fewer than both programs
# (it rebuilds both). Each start's log is kept, build/e189-build-logs/<day>-start<k>.txt. After the job, `wait` reads its verdict lines
# (LEDGER-BUILT / LEDGER-BUILD-FAILED, SPP-BUILT / SPP-BUILD-FAILED), writes RB_OUT/e189-built.txt (the programs built today, which step 9
# passes to the session), and reads, each in its own 60 s call: the harness with the built kernels (check_e189.py --box --built), the
# preflight (dmcmd_audit GO) and the common module's self-check. A cut WAIT CALL is not a failed build (14, "no reading": wait again).
# Exit codes are k6's: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 16 a gate says stop; 17 again.
#   bash tools/claims-v3/e189/rb/s08_a3_build_e189.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e189.sh"
rb_init s08_a3_build
act=${1:-}
JOB=a3-build-e189
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_a3_build_e189.sh start | wait" ;; esac
e189_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  f=$(rb_file count)
  { rb_prelude aifoundry3
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E189's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E189's build starts alone"; exit 3; fi
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f build/e189-build-attempts.txt ] && n=$(grep -c "^$TODAY .* a3-build-e189 started\$" build/e189-build-attempts.txt)
echo "E189-BUILDS-TODAY $n"
if job_ok_today a3-build-e189 && grep -q '^LEDGER-BUILT rc=0' build/q141k/jobs/a3-build-e189.out 2>/dev/null && grep -q '^SPP-BUILT rc=0' build/q141k/jobs/a3-build-e189.out 2>/dev/null; then
  echo "BOTH-BUILT-TODAY"
fi
EOF2
  } > "$f"
  rb_remote read aifoundry3 "the build-attempt count today and the last build's verdicts" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E189-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BOTH-BUILT-TODAY' && rb_die $RB_E_USAGE "both programs were built today: run this step's wait (a second build would remove the good ones)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry3 today (Pacific): the programs not built today are SKIPPED (E189.md section 12: no data, never a failed prediction); go on with what step 6's wait recorded, or no session"
  fi
  body=$(rb_file body)
  cat > "$body" <<'EOF2'
mkdir -p build/e189-build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build/e189-build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* a3-build-e189 started\$" build/e189-build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e189 started" >> build/e189-build-attempts.txt
L=build/e189-build-logs/$TODAY-start$k.txt
timeout -k 15 500 bash tools/claims-v3/e189/build_e189.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e189 ended rc=$rc: $(grep -E '^(LEDGER|SPP)-(BUILT|BUILD-FAILED)' "$L" | cut -c1-40 | tr '\n' ' ')" >> build/e189-build-attempts.txt
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
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e189-built.txt from the verdict lines; the harness with the built kernels, the preflight and the self-check, each a 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
if ! grep -qE '^(LEDGER|SPP)-(BUILT|BUILD-FAILED)' "$cap"; then
  rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict lines (a cut wait is not a failed build): wait again"
fi
built=""
grep -q '^LEDGER-BUILT rc=0' "$cap" && built="ledger"
grep -q '^SPP-BUILT rc=0' "$cap" && built="${built:+$built,}spp"
grep -E '^(COMPILER|LEDGER|SPP)' "$cap" | cut -c1-200 | sed 's/^/    /'
if [ -z "$built" ]; then
  rb_die $RB_E_GATE "neither program built (the lines above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no session today"
fi
echo "$built" > "$RB_OUT/e189-built.txt"
rb_probe aifoundry3
f=$(rb_file checks)
{ rb_prelude aifoundry3
  echo "BUILT=$built"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
python3 -B tools/claims-v3/e189/check_e189.py --box --built "$BUILT" | tail -n 1
bash tools/claims-v3/e189/preflight_e189.sh 2>&1 | head -n 1
python3 -B tools/claims-v3/e189/e189_common.py | tail -n 1
EOF2
} > "$f"
rb_remote read aifoundry3 "the harness with today's kernels, the preflight, the common self-check" "$f"
rb_refused
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness with today's built kernels did not read OK (the line above): no session on these binaries"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on the box: no session"
rb_has '^E189-COMMON SELF-CHECK PASS' || rb_die $RB_E_GATE "the common module's self-check failed on the box: no session"
rb_say "built today on aifoundry3: $built (the other program, if any, is SKIPPED today); harness, preflight GO and self-check read on the box"
exit 0
