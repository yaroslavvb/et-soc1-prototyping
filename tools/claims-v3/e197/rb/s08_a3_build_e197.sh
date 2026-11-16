#!/usr/bin/env bash
# E197 (Q185, the kit), the box step "the build" (this file is s08): regfile (kernel and host) built on aifoundry3 from proposal/src in
# E197's root, checked there, no device opened. E193's step 6's form (tools/claims-v3/e193/rb/s08_a3_build_e193.sh): the build is ONE
# DETACHED JOB, a3-build-e197 (build_e197.sh under `timeout 900`, no -k: cmake with the box's /opt/et into build/regfile under E197's
# root; make_images.py --check and check_elf.py (gates); the ELF report; the host's table byte for byte the registration's (a gate); the
# host read by its behaviour; its signal handling re-read on this build (reported); the session's dry listings with this host (LISTING
# SAME x3, a gate); the hashes recorded in build/regfile-built.txt), refused beside a session of ours (ours_live) or a runbook job
# (jobs_live). AT MOST TWO BUILD STARTS A PACIFIC DAY (E183's NO-THIRD-BUILD): E197's root's build/e197-build-attempts.txt counts the
# starts each Pacific day; a third start the same day is refused with 16, and no sitting runs that day on an unbuilt host (E197.md 11:
# no data, never a failed check). A second start is allowed only when the first did not end REGFILE-BUILT; after a REGFILE-BUILT today a
# start is refused (10: run the wait). Each start's log is kept, build/e197-build-logs/<day>-start<k>.txt. `wait` reads the verdict
# (REGFILE-BUILT rc=0 / REGFILE-BUILD-FAILED), writes RB_OUT/e197-built.txt (the build's lines, which steps 7, 8 and 9 read), then reads
# on the box, in one 60 s call, the build record, the harness and the preflight. A cut WAIT CALL is not a failed build (14, "no
# reading": wait again). Both sittings of one day share the day's build: sitting 2's RB_OUT runs only `wait`, which reads the same job.
# Exit codes are k6's: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 16 a gate says stop; 17 again.
#   bash tools/claims-v3/e197/rb/s08_a3_build_e197.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e197.sh"
rb_init s08_a3_build
act=${1:-}
JOB=a3-build-e197
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_a3_build_e197.sh start | wait" ;; esac
e197_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  f=$(rb_file count)
  { rb_prelude aifoundry3
    echo "ROOT=$E197_ROOT"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E197's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E197's build starts alone"; exit 3; fi
[ -f "$ROOT/tools/claims-v3/e197/build_e197.sh" ] || { echo "REFUSED: E197's root holds no build_e197.sh: run step 5 (the sync) first"; exit 3; }
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f "$ROOT/build/e197-build-attempts.txt" ] && n=$(grep -c "^$TODAY .* a3-build-e197 started\$" "$ROOT/build/e197-build-attempts.txt")
echo "E197-BUILDS-TODAY $n"
if job_ok_today a3-build-e197 && grep -q '^REGFILE-BUILT rc=0' build/q141k/jobs/a3-build-e197.out 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read aifoundry3 "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E197-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "regfile was built today (REGFILE-BUILT): run this step's wait (a second build would remove the good one)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry3 today (Pacific): no E197 sitting today (E197.md 11: no data, never a failed check)"
  fi
  body=$(rb_file body)
  { echo "ROOT=$E197_ROOT"
    cat <<'EOF2'
mkdir -p "$ROOT/build/e197-build-logs"
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f "$ROOT/build/e197-build-attempts.txt" ] && k=$(( $(grep -c "^$TODAY .* a3-build-e197 started\$" "$ROOT/build/e197-build-attempts.txt") + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e197 started" >> "$ROOT/build/e197-build-attempts.txt"
L=$ROOT/build/e197-build-logs/$TODAY-start$k.txt
timeout 900 bash "$ROOT/tools/claims-v3/e197/build_e197.sh" > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e197 ended rc=$rc: $(grep -E '^REGFILE-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60 | tr '\n' ' ')" >> "$ROOT/build/e197-build-attempts.txt"
exit $rc
EOF2
  } > "$body"
  rb_job_start aifoundry3 "$JOB" "$body"
  rb_say "the build job $JOB started on aifoundry3: run this step's wait (bounded) until it ends"
  exit 0
fi
# wait
rb_probe aifoundry3
rb_job_wait aifoundry3 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e197-built.txt from the verdict lines; the build record, the harness and the preflight read on the box, one 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
grep -qE '^REGFILE-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|ELF|CHECK|HOST|SIGNAL|LISTING|SAMPLER|REGFILE)' "$cap" | cut -c1-220 | sed 's/^/    /'
grep -q '^REGFILE-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "regfile did not build and check (the lines above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no sitting today"
grep -E '^(COMPILER|ELF|CHECK|HOST|SIGNAL|LISTING|SAMPLER|REGFILE)' "$cap" > "$RB_OUT/e197-built.txt"
rb_probe aifoundry3
f=$(rb_file checks)
{ rb_prelude aifoundry3
  echo "ROOT=$E197_ROOT"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
fresh "$ROOT/build/regfile-built.txt" && sed 's/^/BUILT-RECORD /' "$ROOT/build/regfile-built.txt" || echo "NO-BUILT-RECORD today"
python3 -I -B "$ROOT/tools/claims-v3/e197/harness_e197.py" --box --root "$ROOT" | tail -n 1
bash "$ROOT/tools/claims-v3/e197/preflight_e197.sh" 2>&1 | head -n 1
EOF2
} > "$f"
rb_remote read aifoundry3 "the build record, the harness and the preflight on the box" "$f"
rb_refused
rb_has '^BUILT-RECORD REGFILE-BUILT ' || rb_die $RB_E_GATE "the box holds no build record written today: no sitting on these binaries"
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness did not read OK on the box: no sitting"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on the box: no sitting"
rb_say "built today on aifoundry3: regfile (REGFILE-BUILT: make_images and check_elf, the host's table SAME, its behaviour, the listing SAME x3); record, harness and preflight GO read on the box"
exit 0
