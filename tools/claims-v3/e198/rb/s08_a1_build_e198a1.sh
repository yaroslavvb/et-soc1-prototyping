#!/usr/bin/env bash
# E198 dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): step 6 (A1), THE BUILD. It is
# s08_a1_build_e198.sh below (kit-e198, unchanged beside it) with three changes: the job is a1-build-e198a1 and runs build_e198a1.sh (the
# listing read on the lab's runner copy through check_e198a1.py; the record names build_e198a1.sh); the job runs build_e198a1.sh under a
# PLAIN `timeout 900`, never `timeout -k` (v1's `timeout -k 15 900` would have sent a KILL to the build's process tree 15 s after its
# TERM, and that tree runs the built host for its refusal checks: A1 sends no KILL anywhere on E198's path); and the two-a-day count reads
# both names (a1-build-e198 and a1-build-e198a1), so A1 adds no start to E198.md 13's two. The wait reads the build record's
# "a1 build_e198a1.sh" line, harness_e198a1.py --box and preflight_e198a1.sh on the box. v1's header, read with these changes:
# E198 (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum; ported from E193's file of the same step, unchanged in logic but the names below), the box step "the build" (this file is s08): x04clock (kernel and host) built on aifoundry1 from proposal/src in
# E198's root, checked there, no device opened. E189's step 6's form (tools/claims-v3/e189/rb/s08_a1_build_e189.sh): the build is ONE
# DETACHED JOB, a1-build-e198 (build_e198.sh under `timeout -k 15 900`: cmake with the box's /opt/et into build/x04clock under E198's
# root; the ELF checks; the bodies check; the host read by its behaviour; the host's listing against the registration's table; the hashes
# recorded in build/x04clock-built.txt), refused beside a session of ours (ours_live) or a runbook job (jobs_live). AT MOST TWO BUILD
# STARTS A PACIFIC DAY (E183's NO-THIRD-BUILD): E198's root's build/e198-build-attempts.txt counts the starts each Pacific day; a third
# start the same day is refused with 16, and no sitting runs that day on an unbuilt host (E198.md 13: no data, never a failed check). A
# second start is allowed only when the first did not end X04-BUILT; after an X04-BUILT today a start is refused (10: run the wait).
# Each start's log is kept, build/e198-build-logs/<day>-start<k>.txt. `wait` reads the verdict (X04-BUILT rc=0 / X04-BUILD-FAILED), writes
# RB_OUT/e198-built.txt (the build's lines, which steps 8 and 9 read), then reads on the box, in one 60 s call, the build record, the
# harness and the preflight. A cut WAIT CALL is not a failed build (14, "no reading": wait again). Both sittings of one day share the
# day's build: sitting B's RB_OUT runs only `wait`, which reads the same job.
# Exit codes are k6's: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 16 a gate says stop; 17 again.
#   bash tools/claims-v3/e198/rb/s08_a1_build_e198.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198a1.sh"
rb_init s08_a1_build_A1
act=${1:-}
JOB=$E198_A1_BUILD_JOB                                 # a1-build-e198a1 (rb_e198a1.sh)
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_a1_build_e198.sh start | wait" ;; esac
e198_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry1
  f=$(rb_file count)
  { rb_prelude aifoundry1
    echo "ROOT=$E198_ROOT"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E198's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E198's build starts alone"; exit 3; fi
[ -f "$ROOT/tools/claims-v3/e198/build_e198a1.sh" ] || { echo "REFUSED: E198's root holds no build_e198a1.sh: run step 5 (A1, the sync) first"; exit 3; }
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f "$ROOT/build/e198-build-attempts.txt" ] && n=$(grep -cE "^$TODAY .* a1-build-e198(a1)? started\$" "$ROOT/build/e198-build-attempts.txt")
echo "E198-BUILDS-TODAY $n"
if job_ok_today a1-build-e198a1 && grep -q '^X04-BUILT rc=0' build/q141k/jobs/a1-build-e198a1.out 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read aifoundry1 "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E198-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "x04clock was built today (X04-BUILT): run this step's wait (a second build would remove the good one)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry1 today (Pacific): no E198 sitting today (E198.md 13: no data, never a failed check)"
  fi
  body=$(rb_file body)
  { echo "ROOT=$E198_ROOT"
    cat <<'EOF2'
mkdir -p "$ROOT/build/e198-build-logs"
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f "$ROOT/build/e198-build-attempts.txt" ] && k=$(( $(grep -cE "^$TODAY .* a1-build-e198(a1)? started\$" "$ROOT/build/e198-build-attempts.txt") + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a1-build-e198a1 started" >> "$ROOT/build/e198-build-attempts.txt"
L=$ROOT/build/e198-build-logs/$TODAY-start$k.txt
timeout 900 bash "$ROOT/tools/claims-v3/e198/build_e198a1.sh" > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a1-build-e198a1 ended rc=$rc: $(grep -E '^X04-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60 | tr '\n' ' ')" >> "$ROOT/build/e198-build-attempts.txt"
exit $rc
EOF2
  } > "$body"
  rb_job_start aifoundry1 "$JOB" "$body"
  rb_say "the build job $JOB started on aifoundry1: run this step's wait (bounded) until it ends"
  exit 0
fi
# wait
rb_probe aifoundry1
rb_job_wait aifoundry1 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e198-built.txt from the verdict lines; the build record, the harness and the preflight read on the box, one 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
grep -qE '^X04-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|ELF|BODIES|HOST|LISTING|ETDEVICES|READER|X04)' "$cap" | cut -c1-220 | sed 's/^/    /'
grep -q '^X04-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "x04clock did not build and check (the lines above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no sitting today"
grep -E '^(COMPILER|ELF|BODIES|HOST|LISTING|ETDEVICES|READER|X04)' "$cap" > "$RB_OUT/e198-built.txt"
rb_probe aifoundry1
f=$(rb_file checks)
{ rb_prelude aifoundry1
  echo "ROOT=$E198_ROOT"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
fresh "$ROOT/build/x04clock-built.txt" && sed 's/^/BUILT-RECORD /' "$ROOT/build/x04clock-built.txt" || echo "NO-BUILT-RECORD today"
python3 -I -B "$ROOT/tools/claims-v3/e198/harness_e198a1.py" --box --root "$ROOT" | tail -n 1
bash "$ROOT/tools/claims-v3/e198/preflight_e198a1.sh" 2>&1 | head -n 1
EOF2
} > "$f"
rb_remote read aifoundry1 "the build record, the harness and the preflight on the box" "$f"
rb_refused
rb_has '^BUILT-RECORD X04-BUILT ' || rb_die $RB_E_GATE "the box holds no build record written today: no sitting on these binaries"
rb_has '^BUILT-RECORD a1 build_e198a1.sh$' || rb_die $RB_E_GATE "the box's build record was not written by build_e198a1.sh (A1's build): no A1 sitting on it"
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness did not read OK on the box: no sitting"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on the box: no sitting"
rb_say "built today on aifoundry1: x04clock (X04-BUILT: the bodies check, the host's behaviour, the listing SAME x3); record, harness and preflight GO read on the box"
exit 0
