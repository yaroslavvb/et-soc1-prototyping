#!/usr/bin/env bash
# E182 (Q154, the kit's dated note 3), KIT.md box step 6 v4 (this file is s08 v4): the train host's build and E182's checks on aifoundry3,
# no device opened. It replaces step 6 v3 (rb/s08_a3_preflight_e182_v3.sh, which stays as committed) on the card day. v3 is note 2's: the
# build as ONE DETACHED JOB of the runbook (E180's form), each check after it in its own 60 s read, refused beside a session of ours, and at
# most one re-run before the registered fallback. v4 keeps all of that and fixes what note 2's verifier (verify-e182n) found, each marked v4:
#   1. (its minor 1) the read before the build checks ALL NINE build inputs, main.cpp with them: v3 ran check_inputs_e182.py's tree mode
#      (the 8 inputs beside main.cpp and note 1's 2 box files) only, so a main.cpp off its pin was caught inside the job, read as a failed
#      build and spent the one re-run, and note 1's re-sync words were never said. v4 also runs check_inputs_e182.py --src on a scratch copy
#      of the 9 (the check build_host_e182_v2.sh makes of its own copy), so a differing main.cpp reads TRAIN-HOST-INPUTS-DIFFER before any
#      job, with note 1's words (step 5 v2 once more, then this step; if they differ again, the fallback), and no build is started or
#      counted. If the inputs change after that read and the job's own check finds it, the job reads TRAIN-HOST-INPUTS-DIFFER, records it
#      on the box as not a build, and wait says note 1's words: such a job is never counted among the day's builds;
#   2. (its minor 2) start is REFUSED (10) when the train host was built on the box today (the job ended rc 0 today with TRAIN-HOST-BUILT,
#      and the build record is there): v3 started a second build, which removes the good host first (build_host_e182_v2.sh), spends the
#      one re-run, and if it fails names the fallback, so a repeated start could lose the trains. After a good build run wait (its checks);
#   3. (its nit 5) every build's own log is kept on the box, build/e182-build-logs/<day>/e182-build-host-start<k>.txt (k: the day's k-th
#      start), and the box's count file build/e182-build-attempts.txt gets one "ended" line a build with its result: step 11 v3
#      (rb/s22_collect_e182_v3.sh) copies both into the data's logs/, so the data shows the day's builds, each with its log, even after a
#      re-run has replaced build/e182-build-host.txt;
#   4. its cosmetic words: "the train host's build ran past its own N s bound", "the train host's build job was lost", and a job lost before
#      it recorded its start reads "no build recorded" (v3 read "build 0 of at most 2").
# Everything else is v3's, line for line:
#   start        1. one bounded read: REFUSED if a card session of ours runs on the box (k6's ours_live) or a runbook job still runs (k6's
#                   jobs_live), or (v4) if the train host was built here today; the day's builds (the box's own count); the nine build
#                   inputs and note 1's two box files at their pins (v4: tree and copy); if they differ, nothing is built, an earlier
#                   build's host, copy and record are removed, and the step stops (16) with note 1's words;
#                2. the build as ONE DETACHED JOB (k6's rb_job_start; it refuses beside a session of ours too) under its own bound,
#                   `timeout -k 15 500`, reading TRAIN-HOST-BUILT, or TRAIN-HOST-BUILD-FAILED / -OVERRAN (rc 124 or 137), or (v4)
#                   TRAIN-HOST-INPUTS-DIFFER (not a build), after removing the failed build's host, copy and record (v2's rule);
#   wait         one bounded wait on the job (k6's rb_job_wait; 17 while it runs: call wait again); when it has ended rc 0, the checks, each in
#                its own bounded read, each refused beside a session of ours: check_inputs_e182.py (NOTE1 FILES OK 10), check_e182.py
#                (HARNESS OK: 73 files), preflight_e182.sh (dmcmd_audit GO) and e182_common.py --verify (rc 0);
#   --no-trains  the registered fallback (E182.md section 7, PASSES): no input check and no build; check_e182.py --no-trains (HARNESS OK:
#                70 files), the preflight and the verify, each in its own bounded read, refused beside a session or job of ours.
# THE RE-RUN RULE (note 2; how it departs from the letter of E182.md section 7 is E182.md.dated-note-2.md): a build that failed, overran its
# bound or was lost gets AT MOST ONE RE-RUN (start again, then wait). The box counts the builds started there today, less the jobs that read
# TRAIN-HOST-INPUTS-DIFFER (v4: not builds), so a cut call cannot hide one: after the second failed build the step names the fallback, and a
# third start is refused (16) with the same words. Exit codes are k6's (rb_common.sh): 0 done; 10 refused; 11 a login link; 12 no answer;
# 13 past a bound; 14 a call failed; 16 a gate says stop (read the message); 17 call again. After 11-14 on start, run wait before any second
# start (CARD-LANE-BRIEF.md.dated-note-1.md).
# E182_BUILD_S overrides the build's 500 s bound for the desk test only, read only with RB_DESKTEST=1 (else 10): the card day never sets it.
# Step 6 v3 is not run on a day v4 runs: v3 counts every line of the day in the count file, v4's "ended" lines with them.
#
#   bash tools/claims-v3/e182/rb/s08_a3_preflight_e182_v4.sh start      then      ... wait   (repeat while it says 17)
#   bash tools/claims-v3/e182/rb/s08_a3_preflight_e182_v4.sh --no-trains       (the fallback)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s08_a3_preflight_v4
act=${1:-}
JOB=a3-build-e182
BUILD_S=500
if [ -n "${E182_BUILD_S:-}" ]; then
  [ "${RB_DESKTEST:-}" = 1 ] || rb_die $RB_E_USAGE "E182_BUILD_S is a desk-test bound, read only with RB_DESKTEST=1: unset it (the card day builds under 500 s)"
  case "$E182_BUILD_S" in *[!0-9]*|'') rb_die $RB_E_USAGE "E182_BUILD_S must be whole seconds" ;; esac
  BUILD_S=$E182_BUILD_S
fi
FALLBACK="no train runs today: run step 6 v4 with --no-trains (rb/s08_a3_preflight_e182_v4.sh --no-trains), then step 8 v2 with --no-trains (rb/s10_a3_dry_e182_v2.sh start --no-trains, then wait --no-trains), then step 9 v2 PASSES no (rb/s11_a3_session_e182_v2.sh PASSES no): E182.md section 7's registered fallback, PASSES (cap 40 card-minutes, the post 'for 1 h'); every train rule reads NOT SCORED"
RESYNC="run step 5 v2 (rb/s07_a3_sync_e182_v2.sh) once more, then this step's start; if they differ again, $FALLBACK"

ours_refusal() {  # the remote lines every v4 call that works on the box starts with, after the prelude: never beside a session of ours
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E182's step 6 never builds or checks beside one (one session of ours at a time)"; exit 3; fi
EOF2
}
jobs_refusal() {  # and, before a build or the fallback's checks: no runbook job of any day still running
  cat <<'EOF2'
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E182's step 6 starts alone (read them with their own step first)"; exit 3; fi
EOF2
}
built_refusal() {  # v4 (minor 2): never a second build after a good one today: it would remove the good host first
  cat <<'EOF2'
if job_ok_today a3-build-e182 && grep -q '^TRAIN-HOST-BUILT rc=0' build/q141k/jobs/a3-build-e182.out 2>/dev/null && [ -s build/e182host/SHA256 ]; then
  echo "REFUSED: the train host was built on $BOX today (job a3-build-e182 ended rc 0 with TRAIN-HOST-BUILT, its build record present): run this step's wait, which reads its checks; a second build would remove it"; exit 3
fi
EOF2
}
builds_today() {  # the remote lines that count the train-host builds started on the box today (Pacific calendar); v4: less the jobs that
  #               read TRAIN-HOST-INPUTS-DIFFER, which built nothing
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0
if [ -f build/e182-build-attempts.txt ]; then
  ns=$(grep -c "^$TODAY .* a3-build-e182 started\$" build/e182-build-attempts.txt)
  nd=$(grep -c "^$TODAY .* a3-build-e182 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" build/e182-build-attempts.txt)
  n=$((ns - nd))
fi
echo "E182-BUILDS-TODAY $n"
EOF2
}
bad=""
check_read() {  # check_read <tag> <what> <file>: one bounded read; a refusal stops the step (10); a failed reading is collected in $bad
  rb_remote read aifoundry3 "$2" "$3"
  [ -n "${RB_DRY:-}" ] && return 0
  rb_refused
  return 0
}

case "$act" in
  start)
    rb_probe aifoundry3
    f=$(rb_file e182-pre)
    { rb_prelude aifoundry3
      ours_refusal
      jobs_refusal
      built_refusal
      builds_today
      cat <<'EOF2'
if [ "$n" -ge 2 ]; then echo "NO-THIRD-BUILD: $n train-host builds were started here today (the first and its one re-run)"; exit 0; fi
mkdir -p build
python3 -B tools/claims-v3/e182/check_inputs_e182.py > build/e182-inputs.txt 2>&1; ci=$?
head -n 12 build/e182-inputs.txt | cut -c1-240; echo "check_inputs_e182 rc=$ci"
# v4 (minor 1): the nine build inputs, main.cpp with them, in a scratch copy, checked as build_host_e182_v2.sh checks its own copy
rm -rf build/e182-inputs-copy; mkdir -p build/e182-inputs-copy
for rel in $(python3 -B tools/claims-v3/e182/check_inputs_e182.py --list); do
  mkdir -p "build/e182-inputs-copy/$(dirname "$rel")"; cp -p "workloads/sparsity/$rel" "build/e182-inputs-copy/$rel" 2>/dev/null
done
python3 -B tools/claims-v3/e182/check_inputs_e182.py --src build/e182-inputs-copy > build/e182-inputs-src.txt 2>&1; cs=$?
rm -rf build/e182-inputs-copy
head -n 12 build/e182-inputs-src.txt | cut -c1-240; echo "check_inputs_e182 --src rc=$cs"
if [ "$ci" -ne 0 ] || [ "$cs" -ne 0 ]; then
  rm -rf build/e182host/b build/e182host/src build/e182host/SHA256     # no train host of an earlier build outlives a refused one (v2's rule)
  echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e182 not started: TRAIN-HOST-INPUTS-DIFFER at the read before the build" >> build/e182-build-attempts.txt
  echo "TRAIN-HOST-INPUTS-DIFFER rc=$ci/$cs"
fi
EOF2
    } > "$f"
    rb_remote read aifoundry3 "before the build (v4): no session or job of ours, no good build today, today's builds, the nine build inputs at their pins" "$f"
    if [ -z "${RB_DRY:-}" ]; then
      rb_refused
      [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the build on aifoundry3 exited $RB_RC (the lines above)"
      rb_has '^NO-THIRD-BUILD' && rb_die $RB_E_GATE "two train-host builds were started on aifoundry3 today (the first and its one re-run): no third. $FALLBACK"
      rb_has '^TRAIN-HOST-INPUTS-DIFFER' && rb_die $RB_E_GATE "the train host's build inputs on aifoundry3 are not the pinned ones (the lines above), so nothing was built and no build is counted: $RESYNC"
      rb_has '^check_inputs_e182 rc=0$' || rb_die $RB_E_FAIL "the build inputs' check on aifoundry3 printed no reading (the lines above)"
      rb_has '^check_inputs_e182 --src rc=0$' || rb_die $RB_E_FAIL "the build inputs' copy check on aifoundry3 printed no reading (the lines above)"
    fi
    body=$(rb_file body)
    { echo "BUILD_S=$BUILD_S"
      cat <<'EOF2'
mkdir -p build
TODAY=$(TZ=America/Los_Angeles date +%F)
echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e182 started" >> build/e182-build-attempts.txt
k=$(grep -c "^$TODAY .* a3-build-e182 started\$" build/e182-build-attempts.txt)
nd=$(grep -c "^$TODAY .* a3-build-e182 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" build/e182-build-attempts.txt)
echo "E182-BUILD-ATTEMPT $((k - nd)) today (the day's start $k)"
L=build/e182-build-logs/$TODAY; mkdir -p "$L"; LOG=$L/e182-build-host-start$k.txt      # v4 (nit 5): every build's own log kept
t0=$(date +%s)
timeout -k 15 "$BUILD_S" bash tools/claims-v3/e182/build_host_e182_v2.sh > "$LOG" 2>&1; b=$?
cp -p "$LOG" build/e182-build-host.txt
echo "build_host_e182_v2 rc=$b after $(( $(date +%s) - t0 )) s (its own bound $BUILD_S s); its log on the box: $LOG"
tail -n 6 "$LOG" | cut -c1-240
if [ "$b" -eq 0 ] && grep -q '^BUILD OK' "$LOG"; then
  res="TRAIN-HOST-BUILT rc=0"; code=0
else
  rm -rf build/e182host/b build/e182host/src build/e182host/SHA256     # no train host of a failed build outlives it (v2's rule)
  if grep -q '^TRAIN-HOST-INPUTS-DIFFER' "$LOG"; then
    res="TRAIN-HOST-INPUTS-DIFFER rc=$b: build_host_e182_v2.sh found a build input off its pin and built nothing (not a build)"
  else
    case "$b" in
      124|137) res="TRAIN-HOST-BUILD-OVERRAN rc=$b: past the build's own $BUILD_S s bound" ;;
      *) res="TRAIN-HOST-BUILD-FAILED rc=$b" ;;
    esac
  fi
  code=1
fi
echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e182 ended rc=$b: $res" >> build/e182-build-attempts.txt
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
        0) rb_has '^TRAIN-HOST-BUILT rc=0' || rb_die $RB_E_FAIL "the build job ended rc 0 without its TRAIN-HOST-BUILT line: read build/q141k/jobs/$JOB.out and build/e182-build-host.txt on aifoundry3" ;;
        "$RB_E_AGAIN") exit "$RB_E_AGAIN" ;;
        "$RB_E_FAIL")
          for k in 'E182-BUILD-ATTEMPT ' 'build_host_e182_v2 rc=' 'TRAIN-HOST-BUILD-' 'TRAIN-HOST-INPUTS-DIFFER' 'JOB-LOST' 'JOB-DONE'; do grep -m1 "^$k" "$RB_CAP" | cut -c1-240; done
          # v4 (minor 1): a job whose own input check failed built nothing: note 1's words, and no build counted
          rb_has '^JOB-DONE ' && rb_has '^TRAIN-HOST-INPUTS-DIFFER' &&
            rb_die $RB_E_GATE "the train host's build inputs on aifoundry3 were not the pinned ones when the build job copied them (the lines above), so nothing was built and no build is counted: $RESYNC"
          why="build failed"
          rb_has '^TRAIN-HOST-BUILD-OVERRAN' && why="build ran past its own $(rb_val '^TRAIN-HOST-BUILD-OVERRAN rc=[0-9]+: past the build.s own ([0-9]+) s bound.*$') s bound"
          rb_has '^JOB-LOST' && why="build job was lost (no process and no exit status)"
          f=$(rb_file e182-count)
          { rb_prelude aifoundry3; builds_today; } > "$f"
          rb_remote read aifoundry3 "how many train-host builds were started on the box today" "$f"
          n=$(rb_val '^E182-BUILDS-TODAY ([0-9]+)$')
          [ -n "$n" ] || rb_die $RB_E_FAIL "the count of today's train-host builds on aifoundry3 did not read (rc $RB_RC): run this step's wait again"
          [ "$n" -ge 2 ] && rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above), and it was the day's build $n (the first and its one re-run are spent): $FALLBACK"
          [ "$n" -lt 1 ] && rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above) before the job recorded its start (no build recorded today): run this step's start once more, then its wait"
          rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above; build $n of at most 2 today): run this step's start once more (the one re-run), then its wait; if that build does not read TRAIN-HOST-BUILT either, $FALLBACK" ;;
        *) exit "$rc" ;;
      esac
    fi
    f=$(rb_file e182-inputs)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e182/check_inputs_e182.py | head -n 12 | cut -c1-240; echo "check_inputs_e182 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read inputs "after the build: the build inputs and note 1's box files at their pins (check_inputs_e182.py)" "$f"
    rb_has '^NOTE1 FILES OK: 10 files' || bad="$bad inputs"
    rb_has '^check_inputs_e182 rc=0$' || bad="$bad check_inputs_e182"
    f=$(rb_file e182-harness)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e182/check_e182.py | head -n 20 | cut -c1-240; echo "check_e182 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read harness "after the build: the harness with the four binaries and the train host (check_e182.py)" "$f"
    rb_has '^HARNESS OK: 73 files' || bad="$bad harness"
    rb_has '^check_e182 rc=0$' || bad="$bad check_e182"
    f=$(rb_file e182-preflight)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
bash tools/claims-v3/e182/preflight_e182.sh > build/e182-preflight-rb.txt 2>&1; echo "preflight_e182 rc=$? $(grep -m1 '^dmcmd_audit:' build/e182-preflight-rb.txt)"
EOF2
    } > "$f"
    check_read preflight "after the build: the device-command preflight with the train host's patched source (preflight_e182.sh)" "$f"
    rb_has '^preflight_e182 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e182"
    f=$(rb_file e182-verify)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e182/e182_common.py --verify | tail -n 3; echo "e182_common rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read verify "after the build: the items, the registered orders and the trains (e182_common.py --verify)" "$f"
    rb_has '^e182_common rc=0$' || bad="$bad e182_common"
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's checks after the build failed:$bad (a binary or file differs: a dated amendment first)"
    rb_say "aifoundry3: the train host built by the detached job $JOB; NOTE1 FILES OK 10, HARNESS OK 73, preflight_e182 GO, e182_common verified, each in its own bounded read"
    ;;

  --no-trains)
    rb_probe aifoundry3
    f=$(rb_file e182-harness-nt)
    { rb_prelude aifoundry3; ours_refusal; jobs_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e182/check_e182.py --no-trains | head -n 20 | cut -c1-240; echo "check_e182 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read harness "the fallback (the trains off): the harness with the four binaries, no train host (check_e182.py --no-trains)" "$f"
    rb_has '^HARNESS OK: 70 files' || bad="$bad harness"
    rb_has '^check_e182 rc=0$' || bad="$bad check_e182"
    f=$(rb_file e182-preflight-nt)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
bash tools/claims-v3/e182/preflight_e182.sh > build/e182-preflight-rb.txt 2>&1; echo "preflight_e182 rc=$? $(grep -m1 '^dmcmd_audit:' build/e182-preflight-rb.txt)"
EOF2
    } > "$f"
    check_read preflight "the fallback: the device-command preflight (preflight_e182.sh)" "$f"
    rb_has '^preflight_e182 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e182"
    f=$(rb_file e182-verify-nt)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e182/e182_common.py --verify | tail -n 3; echo "e182_common rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read verify "the fallback: the items and the registered orders (e182_common.py --verify)" "$f"
    rb_has '^e182_common rc=0$' || bad="$bad e182_common"
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's checks for the fallback failed:$bad (a binary or file differs: a dated amendment first)"
    rb_say "aifoundry3: the trains off (the fallback, PASSES): HARNESS OK 70, preflight_e182 GO, e182_common verified, each in its own bounded read; next step 7 (k6's reads), then step 8 v2 start --no-trains"
    ;;

  *) rb_die $RB_E_USAGE "usage: s08_a3_preflight_e182_v4.sh start | wait | --no-trains" ;;
esac
