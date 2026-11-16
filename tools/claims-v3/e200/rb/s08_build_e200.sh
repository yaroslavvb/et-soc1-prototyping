#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum), the box step "the build" (this file is s08): regfile (kernel and host)
# built on aifoundry2 from E197's proposal/src in E200's root, checked there, and E200's runner made there from E197's lab runner and W1,
# no device opened. E197's step 6 (tools/claims-v3/e197/rb/s08_a3_build_e197.sh, unchanged beside it) on this box: the build is ONE
# DETACHED JOB, a2-build-e200 (build_e200.sh under `timeout 900`, no -k: cmake with the box's /opt/et into build/regfile under E200's root;
# make_images.py --check and check_elf.py (gates); the ELF report; the host's table byte for byte E197's (a gate); the host read by its
# behaviour; its signal handling re-read on this build (reported); E200's runner made by W1 at its sha256 (a gate); the session's dry
# listings with this host and E200's runner (LISTING SAME x3: E197's but W1, a gate); the reader at its pin (a gate); the hashes recorded in
# build/regfile-built.txt), refused beside a session of ours (ours_live) or a runbook job (jobs_live), and only with THE QUIET DESK FLAG
# raised (the build runs the host to its refusals on this box). AT MOST TWO BUILD STARTS A PACIFIC DAY (E183's NO-THIRD-BUILD; E200.md
# 19.1): E200's root's build/e200-build-attempts.txt counts the starts each Pacific day; a third start the same day is refused with 16, and
# no sitting runs that day on an unbuilt host (E200.md 13: no data, never a failed check). A second start is allowed only when the first did
# not end REGFILE-BUILT; after a REGFILE-BUILT today a start is refused (10: run the wait). Each start's log is kept,
# build/e200-build-logs/<day>-start<k>.txt. `wait` reads the verdict (REGFILE-BUILT rc=0 / REGFILE-BUILD-FAILED), writes
# RB_OUT/e200-built.txt (the build's lines, which steps 7, 8 and 9 read), then reads on the box, in one 60 s call, the build record, the
# harness and the preflight. A cut WAIT CALL is not a failed build (14, "no reading": wait again). Both sittings of one day share the day's
# build: sitting 2's RB_OUT runs only `wait`, which reads the same job.
# Exit codes are k6's: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 16 a gate says stop; 17 again.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e200/rb/s08_build_e200.sh start      then      ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e200.sh"
rb_init s08_build
act=${1:-}
JOB=a2-build-e200
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_build_e200.sh start | wait" ;; esac
e200_window
e200_quiet
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry2
  f=$(rb_file count)
  { rb_prelude aifoundry2
    echo "ROOT=$E200_ROOT"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E200's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E200's build starts alone"; exit 3; fi
[ -f "$ROOT/tools/claims-v3/e200/build_e200.sh" ] || { echo "REFUSED: E200's root holds no build_e200.sh: run step 5 (the sync) first"; exit 3; }
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f "$ROOT/build/e200-build-attempts.txt" ] && n=$(grep -c "^$TODAY .* a2-build-e200 started\$" "$ROOT/build/e200-build-attempts.txt")
echo "E200-BUILDS-TODAY $n"
if job_ok_today a2-build-e200 && grep -q '^REGFILE-BUILT rc=0' build/q141k/jobs/a2-build-e200.out 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read aifoundry2 "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E200-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "regfile was built today (REGFILE-BUILT): run this step's wait (a second build would remove the good one)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry2 today (Pacific): no E200 sitting today (E200.md 13: no data, never a failed check)"
  fi
  body=$(rb_file body)
  { echo "ROOT=$E200_ROOT"
    cat <<'EOF2'
mkdir -p "$ROOT/build/e200-build-logs"
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f "$ROOT/build/e200-build-attempts.txt" ] && k=$(( $(grep -c "^$TODAY .* a2-build-e200 started\$" "$ROOT/build/e200-build-attempts.txt") + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a2-build-e200 started" >> "$ROOT/build/e200-build-attempts.txt"
L=$ROOT/build/e200-build-logs/$TODAY-start$k.txt
timeout 900 bash "$ROOT/tools/claims-v3/e200/build_e200.sh" > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a2-build-e200 ended rc=$rc: $(grep -E '^REGFILE-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60 | tr '\n' ' ')" >> "$ROOT/build/e200-build-attempts.txt"
exit $rc
EOF2
  } > "$body"
  rb_job_start aifoundry2 "$JOB" "$body"
  rb_say "the build job $JOB started on aifoundry2: run this step's wait (bounded) until it ends"
  exit 0
fi
# wait
rb_probe aifoundry2
rb_job_wait aifoundry2 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e200-built.txt from the verdict lines; the build record, the harness and the preflight read on the box, one 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
grep -qE '^REGFILE-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|ELF|CHECK|HOST|SIGNAL|RUNNER|LISTING|SAMPLER|REGFILE)' "$cap" | cut -c1-220 | sed 's/^/    /'
grep -q '^REGFILE-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "regfile did not build and check (the lines above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no sitting today"
grep -E '^(COMPILER|ELF|CHECK|HOST|SIGNAL|RUNNER|LISTING|SAMPLER|REGFILE)' "$cap" > "$RB_OUT/e200-built.txt"
rb_probe aifoundry2
f=$(rb_file checks)
{ rb_prelude aifoundry2
  echo "ROOT=$E200_ROOT"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
fresh "$ROOT/build/regfile-built.txt" && sed 's/^/BUILT-RECORD /' "$ROOT/build/regfile-built.txt" || echo "NO-BUILT-RECORD today"
python3 -I -B "$ROOT/tools/claims-v3/e200/harness_e200.py" --box --root "$ROOT" | tail -n 1
bash "$ROOT/tools/claims-v3/e200/preflight_e200.sh" 2>&1 | head -n 1
EOF2
} > "$f"
rb_remote read aifoundry2 "the build record, the harness and the preflight on the box" "$f"
rb_refused
rb_has '^BUILT-RECORD REGFILE-BUILT ' || rb_die $RB_E_GATE "the box holds no build record written today: no sitting on these binaries"
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness did not read OK on the box: no sitting"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on the box: no sitting"
rb_say "built today on aifoundry2: regfile (REGFILE-BUILT: make_images and check_elf, the host's table SAME, its behaviour, E200's runner at its sha256, the listing SAME x3 but W1, the reader at its pin); record, harness and preflight GO read on the box"
exit 0
