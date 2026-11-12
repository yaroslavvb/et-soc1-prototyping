#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): KIT.md box step 6 v2, the train host's
# build. It is rb/s08_a3_build_e183.sh (cc597bf2, which stays as committed) with these changes only, each marked "note 4":
#   - its start refuses (10), before any call, unless step 5a (rb/s06_a3_records_e183.sh) has copied Thu 12 Nov 2026's build records into
#     this RB_OUT (RECORDS-COPIED): this build rewrites the cmake log, the inputs and tree checks and the job's files on the box;
#   - the job runs build_host_e183_v2.sh, whose train change's check is the host's own behaviour (train_check_e183.sh), not v1's grep of
#     'train_kind', which a correctly patched host built by GCC at -O2 fails;
#   - its wait's harness read is harness_e183_v2.py --binaries (v1's check of the 80 files, the binaries and the build tree, then note 4's box
#     files) and its preflight read is preflight_e183_v2.sh (v1's audit with note 4's box files);
#   - its name in the runbook's log is s08_a3_build_v2_e183.
# The job's name (a3-build-e183), the box's count file, the build logs, the re-run rule, the fallback (SKIP) and every reading are v1's, so
# step 9 v2's "today's good build" and step 11 v2's copy of the build's records read it unchanged.
#   bash tools/claims-v3/e183/rb/s08_a3_build_e183_v2.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# v1's words follow:
# E183 (Q155, the kit), KIT.md box step 6: the train host's build and E183's checks on aifoundry3, no device opened. E182's step 6 v4
# (rb/s08_a3_preflight_e182_v4.sh, its kit note 3) ported to the train host of the vector add:
#   start  1. one bounded read: REFUSED (10) if a card session of ours runs on the box (k6's ours_live) or a runbook job still runs (k6's
#             jobs_live), or if the train host was built here today (the job ended rc 0 today with TRAIN-HOST-BUILT, its record present:
#             a second build would remove it); the day's builds (the box's own count file, less the jobs that built nothing); the build
#             inputs at their pins (check_inputs_e183.py): if they differ, nothing is built or counted and the step stops (16): run step 5
#             once more, then this step's start; if they differ again, the fallback;
#          2. the build as ONE DETACHED JOB (k6's rb_job_start; it refuses beside a session of ours too) under its own bound,
#             `timeout -k 15 500`, reading TRAIN-HOST-BUILT, TRAIN-HOST-BUILD-FAILED, TRAIN-HOST-BUILD-OVERRAN (rc 124 or 137), or
#             TRAIN-HOST-INPUTS-DIFFER (not a build); each build's own log kept on the box (build/e183-build-logs/<day>/), one "ended"
#             line a build in build/e183-build-attempts.txt;
#   wait   one bounded wait on the job (k6's rb_job_wait; 17 while it runs: call wait again); when it has ended rc 0, the checks, each in its
#          own bounded read, each refused beside a session of ours: check_inputs_e183.py (BUILD INPUTS OK: 40 files), check_e183.py harness
#          --binaries (HARNESS OK), preflight_e183.sh (dmcmd_audit GO) and e183_common.py --verify (E183 VERIFY OK).
# E182's dated note 4 (step 6 v5, `6b2d2ae6`: what its verifier verify-q154k found in v4, and fix-q154k's case of the same kind) is
# ported too: (1) a failed or cut WAIT CALL is not a failed build: a build's failure is read only from the box's own end of the job, a
# whole `JOB-DONE a3-build-e183 rc=<n>` line or `JOB-LOST a3-build-e183`; any other 14 (k6's "no reading": ssh's 255 on a dropped link,
# or a line cut short) stops with 14, "no reading: run this step's wait again", and nothing is counted or named; (2) the registered
# fallback is never named beside a good train host (start is refused after a good build, before the count is read, so no later wait
# reads a failed build that day); (3) each check's read after the build that exits non-zero with no result line of its own (its
# "... rc=" line) is a failed call, not a failed check: 14, "no reading of <check>: run this step's wait again"; a box that answers
# without its tree (NO-TREE) still reads as a failed check (16).
# THE RE-RUN RULE (E182's, as its dated note 2 states it): a build that failed, overran its bound or was lost gets AT MOST ONE RE-RUN
# (start again, then wait). The box counts the builds started there today, less the jobs that read TRAIN-HOST-INPUTS-DIFFER, so a cut call
# cannot hide one: after the second failed build the step names the registered fallback, and a third start is refused (16) with the same
# words. THE FALLBACK (E183.md section 7): SKIP, no E183 session that day.
# Exit codes are k6's: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 16 a gate says stop;
# 17 call again. After 11-14 on start, run wait before any second start.
# E183_BUILD_S overrides the build's 500 s bound for the desk test only, read only with RB_DESKTEST=1 (else 10).
#
#   bash tools/claims-v3/e183/rb/s08_a3_build_e183.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s08_a3_build_v2
act=${1:-}
JOB=a3-build-e183
BUILD_S=500
if [ -n "${E183_BUILD_S:-}" ]; then
  [ "${RB_DESKTEST:-}" = 1 ] || rb_die $RB_E_USAGE "E183_BUILD_S is a desk-test bound, read only with RB_DESKTEST=1: unset it (the card day builds under 500 s)"
  case "$E183_BUILD_S" in *[!0-9]*|'') rb_die $RB_E_USAGE "E183_BUILD_S must be whole seconds" ;; esac
  BUILD_S=$E183_BUILD_S
fi
FALLBACK="E183 does not run today: E183.md section 7's registered fallback, SKIP (no device opens, no card time is spent, every rule reads NOT RUN; drop E183's clause from the day's post, and the card time goes to the day's next run)"
RESYNC="run step 5 (rb/s07_a3_sync_e183.sh) once more, then this step's start; if they differ again, $FALLBACK"

ours_refusal() {
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E183's step 6 never builds or checks beside one (one session of ours at a time)"; exit 3; fi
EOF2
}
jobs_refusal() {
  cat <<'EOF2'
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E183's step 6 starts alone (read them with their own step first)"; exit 3; fi
EOF2
}
built_refusal() {
  cat <<'EOF2'
if job_ok_today a3-build-e183 && grep -q '^TRAIN-HOST-BUILT rc=0' build/q141k/jobs/a3-build-e183.out 2>/dev/null && [ -s build/enercat-e183/BUILD-E183.json ]; then
  echo "REFUSED: the train host was built on $BOX today (job a3-build-e183 ended rc 0 with TRAIN-HOST-BUILT, its build record present): run this step's wait, which reads its checks; a second build would remove it"; exit 3
fi
EOF2
}
builds_today() {
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0
if [ -f build/e183-build-attempts.txt ]; then
  ns=$(grep -c "^$TODAY .* a3-build-e183 started\$" build/e183-build-attempts.txt)
  nd=$(grep -c "^$TODAY .* a3-build-e183 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" build/e183-build-attempts.txt)
  n=$((ns - nd))
fi
echo "E183-BUILDS-TODAY $n"
EOF2
}
bad=""; noread=""
check_read() {  # check_read <tag> <what> <file> <its result line>: one bounded read; a refusal stops the step (10); a failed reading is
  #             collected in $bad; a call that exited non-zero with no result line of its own (and no NO-TREE) in $noread (E182 v5's fix 3)
  rb_remote read aifoundry3 "$2" "$3"
  [ -n "${RB_DRY:-}" ] && return 0
  rb_refused
  if [ "$RB_RC" -ne 0 ] && ! rb_has "$4" && ! rb_has '^NO-TREE'; then noread="$noread $1 (rc $RB_RC)"; fi
  return 0
}
noread_stop() {  # no reading of a check is a failed call, never a failed check: stop with 14, the same sub-command again
  [ -z "$noread" ] && return 0
  rb_die $RB_E_FAIL "no reading of$noread on aifoundry3 (each call exited non-zero with no result line of its own: it failed or was cut, which is not a failed check): run this step's $1 again"
}

case "$act" in
  start)
    if [ -z "${RB_DRY:-}" ] && [ ! -f "$RB_OUT/box-records-e183/RECORDS-COPIED" ]; then    # note 4: the records first
      rb_die $RB_E_USAGE "no copy of aifoundry3's E183 build records in RB_OUT: run step 5a (rb/s06_a3_records_e183.sh) first; this build rewrites the cmake log, the inputs and tree checks and the job's files on the box"
    fi
    rb_probe aifoundry3
    f=$(rb_file e183-pre)
    { rb_prelude aifoundry3
      ours_refusal
      jobs_refusal
      built_refusal
      builds_today
      cat <<'EOF2'
if [ "$n" -ge 2 ]; then echo "NO-THIRD-BUILD: $n train-host builds were started here today (the first and its one re-run)"; exit 0; fi
mkdir -p build
python3 -B tools/claims-v3/e183/check_inputs_e183.py > build/e183-inputs.txt 2>&1; ci=$?
head -n 12 build/e183-inputs.txt | cut -c1-240; echo "check_inputs_e183 rc=$ci"
if [ "$ci" -ne 0 ]; then
  rm -rf build/enercat-e183 build/enercat-e183-src build/e183-enercat-stage     # no train host of an earlier build outlives a refused one
  echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e183 not started: TRAIN-HOST-INPUTS-DIFFER at the read before the build" >> build/e183-build-attempts.txt
  echo "TRAIN-HOST-INPUTS-DIFFER rc=$ci"
fi
EOF2
    } > "$f"
    rb_remote read aifoundry3 "before the build: no session or job of ours, no good build today, today's builds, the build inputs at their pins" "$f"
    if [ -z "${RB_DRY:-}" ]; then
      rb_refused
      [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "no reading of the read before the build on aifoundry3 (it exited $RB_RC: it failed or was cut): nothing was started or counted; run this step's start again"
      rb_has '^NO-THIRD-BUILD' && rb_die $RB_E_GATE "two train-host builds were started on aifoundry3 today (the first and its one re-run): no third. $FALLBACK"
      rb_has '^TRAIN-HOST-INPUTS-DIFFER' && rb_die $RB_E_GATE "the train host's build inputs on aifoundry3 are not the pinned ones (the lines above), so nothing was built and no build is counted: $RESYNC"
      rb_has '^check_inputs_e183 rc=0$' || rb_die $RB_E_FAIL "the build inputs' check on aifoundry3 printed no reading (the lines above)"
    fi
    body=$(rb_file body)
    { echo "BUILD_S=$BUILD_S"
      cat <<'EOF2'
mkdir -p build
TODAY=$(TZ=America/Los_Angeles date +%F)
echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e183 started" >> build/e183-build-attempts.txt
k=$(grep -c "^$TODAY .* a3-build-e183 started\$" build/e183-build-attempts.txt)
nd=$(grep -c "^$TODAY .* a3-build-e183 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" build/e183-build-attempts.txt)
echo "E183-BUILD-ATTEMPT $((k - nd)) today (the day's start $k)"
L=build/e183-build-logs/$TODAY; mkdir -p "$L"; LOG=$L/e183-build-host-start$k.txt
t0=$(date +%s)
timeout -k 15 "$BUILD_S" bash tools/claims-v3/e183/build_host_e183_v2.sh > "$LOG" 2>&1; b=$?     # note 4
cp -p "$LOG" build/e183-build-host.txt
echo "build_host_e183_v2 rc=$b after $(( $(date +%s) - t0 )) s (its own bound $BUILD_S s); its log on the box: $LOG"
tail -n 6 "$LOG" | cut -c1-240
if [ "$b" -eq 0 ] && grep -q '^BUILD OK' "$LOG"; then
  res="TRAIN-HOST-BUILT rc=0"; code=0
else
  rm -rf build/enercat-e183 build/enercat-e183-src build/e183-enercat-stage     # no train host of a failed build outlives it
  if grep -q '^TRAIN-HOST-INPUTS-DIFFER' "$LOG"; then
    res="TRAIN-HOST-INPUTS-DIFFER rc=$b: build_host_e183.sh found a build input or its tree off its pin and built nothing (not a build)"
  else
    case "$b" in
      124|137) res="TRAIN-HOST-BUILD-OVERRAN rc=$b: past the build's own $BUILD_S s bound" ;;
      *) res="TRAIN-HOST-BUILD-FAILED rc=$b" ;;
    esac
  fi
  code=1
fi
echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e183 ended rc=$b: $res" >> build/e183-build-attempts.txt
echo "$res"
exit "$code"
EOF2
    } > "$body"
    rb_job_start aifoundry3 "$JOB" "$body" 1
    rb_say "the train host's build runs on aifoundry3 as the detached job $JOB (its own bound $BUILD_S s): run this step's wait, again while it says 17"
    ;;

  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 "$JOB"; rc=$?
    if [ -z "${RB_DRY:-}" ]; then
      case "$rc" in
        0) rb_has '^TRAIN-HOST-BUILT rc=0' || rb_die $RB_E_FAIL "the build job ended rc 0 without its TRAIN-HOST-BUILT line: read build/q141k/jobs/$JOB.out and build/e183-build-host.txt on aifoundry3" ;;
        "$RB_E_AGAIN") exit "$RB_E_AGAIN" ;;
        "$RB_E_FAIL")
          # E182 v5's fix 1: a build's failure is read only from the box's own end of the job, a whole JOB-DONE line with a non-zero
          # status or JOB-LOST; any other 14 is a failed or cut wait call: nothing is counted, nothing named but the wait again
          if ! rb_has "^JOB-DONE $JOB rc=[0-9]+\$" && ! rb_has "^JOB-LOST $JOB"; then
            rb_die $RB_E_FAIL "no reading of the build job: the wait call did not read the build job (it exited $RB_RC before the box printed a whole JOB-DONE, JOB-LOST or JOB-RUNNING line: a failed or cut call, not a failed build): nothing is counted; run this step's wait again before any start"
          fi
          for k in 'E183-BUILD-ATTEMPT ' 'build_host_e183_v2 rc=' 'TRAIN-CHANGE ' 'TRAIN-HOST-BUILD-' 'TRAIN-HOST-INPUTS-DIFFER' 'JOB-LOST' 'JOB-DONE'; do grep -m1 "^$k" "$RB_CAP" | cut -c1-240; done
          rb_has "^JOB-DONE $JOB rc=[0-9]+\$" && rb_has '^TRAIN-HOST-INPUTS-DIFFER' &&
            rb_die $RB_E_GATE "the train host's build inputs or tree on aifoundry3 were not the pinned ones when the build job read them (the lines above), so nothing was built and no build is counted: $RESYNC"
          why="build failed"
          rb_has '^TRAIN-HOST-BUILD-OVERRAN' && why="build ran past its own bound"
          rb_has "^JOB-LOST $JOB" && why="build job was lost (no process and no exit status)"
          f=$(rb_file e183-count)
          { rb_prelude aifoundry3; builds_today; } > "$f"
          rb_remote read aifoundry3 "how many train-host builds were started on the box today" "$f"
          n=$(rb_val '^E183-BUILDS-TODAY ([0-9]+)$')
          [ -n "$n" ] || rb_die $RB_E_FAIL "the count of today's train-host builds on aifoundry3 did not read (rc $RB_RC): run this step's wait again"
          [ "$n" -ge 2 ] && rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above), and it was the day's build $n (the first and its one re-run are spent): $FALLBACK"
          [ "$n" -lt 1 ] && rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above) before the job recorded its start (no build recorded today): run this step's start once more, then its wait"
          rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above; build $n of at most 2 today): run this step's start once more (the one re-run), then its wait; if that build does not read TRAIN-HOST-BUILT either, $FALLBACK" ;;
        *) exit "$rc" ;;
      esac
    fi
    f=$(rb_file e183-inputs)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e183/check_inputs_e183.py | head -n 12 | cut -c1-240; echo "check_inputs_e183 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read inputs "after the build: the build inputs at their pins (check_inputs_e183.py)" "$f" '^check_inputs_e183 rc='
    rb_has '^BUILD INPUTS OK: 40 files' || bad="$bad inputs"
    rb_has '^check_inputs_e183 rc=0$' || bad="$bad check_inputs_e183"
    f=$(rb_file e183-harness)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e183/harness_e183_v2.py --binaries | head -n 20 | cut -c1-240; echo "harness_e183_v2 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read harness "after the build: the harness with the train host and its build tree, and note 4's box files (harness_e183_v2.py --binaries)" "$f" '^harness_e183_v2 rc='
    rb_has '^HARNESS OK: ' || bad="$bad harness"
    rb_has '^harness_e183_v2 rc=0$' || bad="$bad harness_e183_v2"
    f=$(rb_file e183-preflight)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
bash tools/claims-v3/e183/preflight_e183_v2.sh > build/e183-preflight-rb.txt 2>&1; echo "preflight_e183_v2 rc=$? $(grep -m1 '^dmcmd_audit:' build/e183-preflight-rb.txt)"
EOF2
    } > "$f"
    check_read preflight "after the build: the device-command preflight (preflight_e183_v2.sh)" "$f" '^preflight_e183_v2 rc='
    rb_has '^preflight_e183_v2 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e183_v2"
    f=$(rb_file e183-verify)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e183/e183_common.py --verify | tail -n 3; echo "e183_common rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read verify "after the build: the registration's files, images, plan and schedule (e183_common.py --verify)" "$f" '^e183_common rc='
    rb_has '^e183_common rc=0$' || bad="$bad e183_common"
    [ -n "${RB_DRY:-}" ] || noread_stop wait
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's checks after the build failed:$bad (a binary or file differs: a dated amendment first)"
    rb_say "aifoundry3: the train host built by the detached job $JOB (build v2: TRAIN-CHANGE OK, read from the host's behaviour); BUILD INPUTS OK 40, HARNESS OK with the binaries, the build tree and note 4's box files, preflight_e183_v2 GO, the registration verified, each in its own bounded read"
    ;;

  *) rb_die $RB_E_USAGE "usage: s08_a3_build_e183_v2.sh start | wait" ;;
esac
