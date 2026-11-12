#!/usr/bin/env bash
# E188 (Q165, the kit), KIT.md box step 6 (this file is s08): the train host's build and E188's checks on aifoundry3, no device opened. It is
# E186's step 6 (tools/claims-v3/e186/rb/s08_a3_build_e186.sh, which built E186's train host on 9 Nov 2026, TRAIN-HOST-BUILT; itself E182's
# step 6 v5) with E188's names, each change marked E188:
#   - the build is E188's build_host_e188.sh (E186's build into build/e188host/, its last check the host's BEHAVIOUR, train_check_e188.sh,
#     never a string grepped from its bytes: E183's kit note 4's lesson), as the detached job a3-build-e188, under its own bound
#     `timeout -k 15 500`, with the box's count file build/e188-build-attempts.txt (E188's own: E183's count file and its two builds of
#     Thu 12 Nov 2026 are not E188's) and each build's own log build/e188-build-logs/<day>/e188-build-host-start<k>.txt;
#   - the build inputs are checked with E182's check_inputs_e182.py, unchanged (the tree's 8 inputs and E182 note 1's two box files, then
#     the nine in a scratch copy build/e188-inputs-copy, as the build checks its own copy);
#   - after the build: check_inputs_e182.py (NOTE1 FILES OK 10), check_e188.py (HARNESS OK: 79 files: 72, the four binaries, the train
#     host's patched source, its record and its binary), THE TRAIN CHANGE READ FROM THE BUILT HOST'S BEHAVIOUR (train_check_e188.sh:
#     TRAIN-CHANGE OK, no device call), preflight_e188.sh (dmcmd_audit GO) and e188_common.py --verify, each in its own 60 s read; the
#     fallback's: check_e188.py --no-trains (HARNESS OK: 76 files), the preflight and the verify;
#   - THE WINDOW RULE: start and --no-trains refuse (10) unless RB_OUT's window was written today for E188, and stop (16) past the last
#     start (a build after it serves no session); wait reads a running build at any time.
# Everything else is E182 v5's, line for line, and its words follow: the build as ONE DETACHED JOB, each check after it in its own 60 s
# read, refused beside a session of ours (k6's ours_live) or a runbook job (jobs_live), at most one re-run before the registered fallback
# (two builds that did not read TRAIN-HOST-BUILT: E182.md.dated-note-2.md's reading, which E188.md section 7 takes as E182's), all nine
# build inputs checked before the job, no second build after a good one, every build's log kept; a failed or cut WAIT CALL is not a failed
# build (14, "no reading": wait again); --no-trains REFUSED after a good build; a check's read that exits non-zero with no result line of
# its own is no reading (14), never a failed check. Exit codes are k6's (rb_common.sh): 0 done; 10 refused; 11 a login link; 12 no answer;
# 13 past a bound; 14 a call failed; 16 a gate says stop (read the message); 17 call again. After 11-14 on start, run wait before any
# second start (E182's brief, note 1). E188_BUILD_S overrides the build's 500 s bound for the desk test only, read only with
# RB_DESKTEST=1 (else 10): the card day never sets it.
#
#   bash tools/claims-v3/e188/rb/s08_a3_build_e188.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
#   bash tools/claims-v3/e188/rb/s08_a3_build_e188.sh --no-trains       (the fallback, after two failed builds)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e188.sh"
rb_init s08_a3_build
act=${1:-}
JOB=a3-build-e188
BUILD_S=500
if [ -n "${E188_BUILD_S:-}" ]; then
  [ "${RB_DESKTEST:-}" = 1 ] || rb_die $RB_E_USAGE "E188_BUILD_S is a desk-test bound, read only with RB_DESKTEST=1: unset it (the card day builds under 500 s)"
  case "$E188_BUILD_S" in *[!0-9]*|'') rb_die $RB_E_USAGE "E188_BUILD_S must be whole seconds" ;; esac
  BUILD_S=$E188_BUILD_S
fi
FALLBACK="no train runs today: run step 6 with --no-trains (rb/s08_a3_build_e188.sh --no-trains), then step 8 with --no-trains (rb/s10_a3_dry_e188.sh start --no-trains, then wait --no-trains), then step 9 PASSES no (rb/s11_a3_session_e188.sh PASSES no): E188.md section 6's registered fallback, PASSES (five kinds passes of the fifteen kinds, cap 40 card-minutes, the post 'for 1 h'); every train rule reads NOT SCORED and E188-LV is the reading"
RESYNC="run step 5 (rb/s07_a3_sync_e188.sh) once more, then this step's start; if they differ again, $FALLBACK"

ours_refusal() {  # the remote lines every v4 call that works on the box starts with, after the prelude: never beside a session of ours
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E188's step 6 never builds or checks beside one (one session of ours at a time)"; exit 3; fi
EOF2
}
jobs_refusal() {  # and, before a build or the fallback's checks: no runbook job of any day still running
  cat <<'EOF2'
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E188's step 6 starts alone (read them with their own step first)"; exit 3; fi
EOF2
}
built_refusal() {  # v4 (minor 2): never a second build after a good one today: it would remove the good host first
  cat <<'EOF2'
if job_ok_today a3-build-e188 && grep -q '^TRAIN-HOST-BUILT rc=0' build/q141k/jobs/a3-build-e188.out 2>/dev/null && [ -s build/e188host/SHA256 ]; then
  echo "REFUSED: the train host was built on $BOX today (job a3-build-e188 ended rc 0 with TRAIN-HOST-BUILT, its build record present): run this step's wait, which reads its checks; a second build would remove it"; exit 3
fi
EOF2
}
nt_built_refusal() {  # v5 (verify-q154k's fault 1): the registered fallback is for a failed build, never beside a good train host
  cat <<'EOF2'
if job_ok_today a3-build-e188 && grep -q '^TRAIN-HOST-BUILT rc=0' build/q141k/jobs/a3-build-e188.out 2>/dev/null && [ -s build/e188host/SHA256 ]; then
  echo "REFUSED: the train host was built on $BOX today (job a3-build-e188 ended rc 0 with TRAIN-HOST-BUILT, its build record present): the registered fallback is for a failed build, so the trains are not given up beside a good host: run this step's wait, which reads its checks"; exit 3
fi
EOF2
}
builds_today() {  # the remote lines that count the train-host builds started on the box today (Pacific calendar); v4: less the jobs that
  #               read TRAIN-HOST-INPUTS-DIFFER, which built nothing
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0
if [ -f build/e188-build-attempts.txt ]; then
  ns=$(grep -c "^$TODAY .* a3-build-e188 started\$" build/e188-build-attempts.txt)
  nd=$(grep -c "^$TODAY .* a3-build-e188 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" build/e188-build-attempts.txt)
  n=$((ns - nd))
fi
echo "E188-BUILDS-TODAY $n"
EOF2
}
bad=""; noread=""
check_read() {  # check_read <tag> <what> <file> <its result line>: one bounded read; a refusal stops the step (10); a failed reading is
  #             collected in $bad; v5: a call that exited non-zero with no result line of its own (and no NO-TREE) is collected in $noread
  rb_remote read aifoundry3 "$2" "$3"
  [ -n "${RB_DRY:-}" ] && return 0
  rb_refused
  if [ "$RB_RC" -ne 0 ] && ! rb_has "$4" && ! rb_has '^NO-TREE'; then noread="$noread $1 (rc $RB_RC)"; fi
  return 0
}
noread_stop() {  # v5: no reading of a check is a failed call, never a failed check: stop with 14, the same sub-command again
  [ -z "$noread" ] && return 0
  rb_die $RB_E_FAIL "no reading of$noread on aifoundry3 (each call exited non-zero with no result line of its own: it failed or was cut, which is not a failed check): run this step's $1 again"
}

case "$act" in
  start)
    e188_window                                                                                          # E188: the window rule
    rb_need_start
    rb_probe aifoundry3
    f=$(rb_file e188-pre)
    { rb_prelude aifoundry3
      ours_refusal
      jobs_refusal
      built_refusal
      builds_today
      cat <<'EOF2'
if [ "$n" -ge 2 ]; then echo "NO-THIRD-BUILD: $n train-host builds were started here today (the first and its one re-run)"; exit 0; fi
mkdir -p build
python3 -B tools/claims-v3/e182/check_inputs_e182.py > build/e188-inputs.txt 2>&1; ci=$?
head -n 12 build/e188-inputs.txt | cut -c1-240; echo "check_inputs_e182 rc=$ci"
# v4 (minor 1): the nine build inputs, main.cpp with them, in a scratch copy, checked as build_host_e188.sh (E182 v2's build) checks its own copy
rm -rf build/e188-inputs-copy; mkdir -p build/e188-inputs-copy
for rel in $(python3 -B tools/claims-v3/e182/check_inputs_e182.py --list); do
  mkdir -p "build/e188-inputs-copy/$(dirname "$rel")"; cp -p "workloads/sparsity/$rel" "build/e188-inputs-copy/$rel" 2>/dev/null
done
python3 -B tools/claims-v3/e182/check_inputs_e182.py --src build/e188-inputs-copy > build/e188-inputs-src.txt 2>&1; cs=$?
rm -rf build/e188-inputs-copy
head -n 12 build/e188-inputs-src.txt | cut -c1-240; echo "check_inputs_e182 --src rc=$cs"
if [ "$ci" -ne 0 ] || [ "$cs" -ne 0 ]; then
  rm -rf build/e188host/b build/e188host/src build/e188host/SHA256     # no train host of an earlier build outlives a refused one (v2's rule)
  echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e188 not started: TRAIN-HOST-INPUTS-DIFFER at the read before the build" >> build/e188-build-attempts.txt
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
echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e188 started" >> build/e188-build-attempts.txt
k=$(grep -c "^$TODAY .* a3-build-e188 started\$" build/e188-build-attempts.txt)
nd=$(grep -c "^$TODAY .* a3-build-e188 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" build/e188-build-attempts.txt)
echo "E188-BUILD-ATTEMPT $((k - nd)) today (the day's start $k)"
L=build/e188-build-logs/$TODAY; mkdir -p "$L"; LOG=$L/e188-build-host-start$k.txt      # v4 (nit 5): every build's own log kept
t0=$(date +%s)
timeout -k 15 "$BUILD_S" bash tools/claims-v3/e188/build_host_e188.sh > "$LOG" 2>&1; b=$?
cp -p "$LOG" build/e188-build-host.txt
echo "build_host_e188 rc=$b after $(( $(date +%s) - t0 )) s (its own bound $BUILD_S s); its log on the box: $LOG"
tail -n 6 "$LOG" | cut -c1-240
if [ "$b" -eq 0 ] && grep -q '^BUILD OK' "$LOG"; then
  res="TRAIN-HOST-BUILT rc=0"; code=0
else
  rm -rf build/e188host/b build/e188host/src build/e188host/SHA256     # no train host of a failed build outlives it (v2's rule)
  if grep -q '^TRAIN-HOST-INPUTS-DIFFER' "$LOG"; then
    res="TRAIN-HOST-INPUTS-DIFFER rc=$b: build_host_e188.sh found a build input off its pin and built nothing (not a build)"
  else
    case "$b" in
      124|137) res="TRAIN-HOST-BUILD-OVERRAN rc=$b: past the build's own $BUILD_S s bound" ;;
      *) res="TRAIN-HOST-BUILD-FAILED rc=$b" ;;
    esac
  fi
  code=1
fi
echo "$TODAY $(TZ=America/Los_Angeles date '+%T %Z') a3-build-e188 ended rc=$b: $res" >> build/e188-build-attempts.txt
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
        0) rb_has '^TRAIN-HOST-BUILT rc=0' || rb_die $RB_E_FAIL "the build job ended rc 0 without its TRAIN-HOST-BUILT line: read build/q141k/jobs/$JOB.out and build/e188-build-host.txt on aifoundry3" ;;
        "$RB_E_AGAIN") exit "$RB_E_AGAIN" ;;
        "$RB_E_FAIL")
          for k in 'E188-BUILD-ATTEMPT ' 'build_host_e188 rc=' 'TRAIN-HOST-BUILD-' 'TRAIN-HOST-INPUTS-DIFFER' 'JOB-LOST' 'JOB-DONE'; do grep -m1 "^$k" "$RB_CAP" | cut -c1-240; done
          # v5 (verify-q154k's fault 1): a build's failure is read only from the box's own end of the job, a whole JOB-DONE line with a
          # non-zero status or JOB-LOST; any other 14 is a failed or cut wait call: nothing is counted, nothing named but the wait again
          if ! rb_has "^JOB-DONE $JOB rc=[0-9]+\$" && ! rb_has "^JOB-LOST $JOB"; then
            rb_die $RB_E_FAIL "no reading of the build job on aifoundry3 (the wait call exited $RB_RC before the box printed JOB-DONE, JOB-LOST or JOB-RUNNING: it failed or was cut, which is not the build's failure): nothing is counted; run this step's wait again, and no other step-6 call (start or --no-trains) until it reads"
          fi
          # v4 (minor 1): a job whose own input check failed built nothing: note 1's words, and no build counted
          rb_has '^JOB-DONE ' && rb_has '^TRAIN-HOST-INPUTS-DIFFER' &&
            rb_die $RB_E_GATE "the train host's build inputs on aifoundry3 were not the pinned ones when the build job copied them (the lines above), so nothing was built and no build is counted: $RESYNC"
          why="build failed"
          rb_has '^TRAIN-HOST-BUILD-OVERRAN' && why="build ran past its own $(rb_val '^TRAIN-HOST-BUILD-OVERRAN rc=[0-9]+: past the build.s own ([0-9]+) s bound.*$') s bound"
          rb_has '^JOB-LOST' && why="build job was lost (no process and no exit status)"
          f=$(rb_file e188-count)
          { rb_prelude aifoundry3; builds_today; } > "$f"
          rb_remote read aifoundry3 "how many train-host builds were started on the box today" "$f"
          n=$(rb_val '^E188-BUILDS-TODAY ([0-9]+)$')
          [ -n "$n" ] || rb_die $RB_E_FAIL "the count of today's train-host builds on aifoundry3 did not read (rc $RB_RC): run this step's wait again"
          [ "$n" -ge 2 ] && rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above), and it was the day's build $n (the first and its one re-run are spent): $FALLBACK"
          [ "$n" -lt 1 ] && rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above) before the job recorded its start (no build recorded today): run this step's start once more, then its wait"
          rb_die $RB_E_GATE "the train host's $why on aifoundry3 (the lines above; build $n of at most 2 today): run this step's start once more (the one re-run), then its wait; if that build does not read TRAIN-HOST-BUILT either, $FALLBACK" ;;
        *) exit "$rc" ;;
      esac
    fi
    f=$(rb_file e188-inputs)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e182/check_inputs_e182.py | head -n 12 | cut -c1-240; echo "check_inputs_e182 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read inputs "after the build: the build inputs and note 1's box files at their pins (check_inputs_e182.py)" "$f" '^check_inputs_e182 rc='
    rb_has '^NOTE1 FILES OK: 10 files' || bad="$bad inputs"
    rb_has '^check_inputs_e182 rc=0$' || bad="$bad check_inputs_e182"
    f=$(rb_file e188-harness)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e188/check_e188.py | head -n 20 | cut -c1-240; echo "check_e188 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read harness "after the build: the harness with the four binaries and the train host (check_e188.py)" "$f" '^check_e188 rc='
    rb_has '^HARNESS OK: 79 files' || bad="$bad harness"
    rb_has '^check_e188 rc=0$' || bad="$bad check_e188"
    f=$(rb_file e188-trainchk)                                                                                # E188: the behaviour
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
bash tools/claims-v3/e188/train_check_e188.sh build/e188host/b/host/sparsity_host | cut -c1-400; echo "train_check_e188 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read trainchk "after the build: the train change read from the built host's behaviour (train_check_e188.sh; no device call)" "$f" '^train_check_e188 rc='
    rb_has '^TRAIN-CHANGE OK: ' || bad="$bad train-change"
    rb_has '^train_check_e188 rc=0$' || bad="$bad train_check_e188"
    f=$(rb_file e188-preflight)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
bash tools/claims-v3/e188/preflight_e188.sh > build/e188-preflight-rb.txt 2>&1; echo "preflight_e188 rc=$? $(grep -m1 '^dmcmd_audit:' build/e188-preflight-rb.txt)"
EOF2
    } > "$f"
    check_read preflight "after the build: the device-command preflight with the train host's patched source (preflight_e188.sh)" "$f" '^preflight_e188 rc='
    rb_has '^preflight_e188 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e188"
    f=$(rb_file e188-verify)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e188/e188_common.py --verify | tail -n 3; echo "e188_common rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read verify "after the build: the items, the registered orders and the trains (e188_common.py --verify)" "$f" '^e188_common rc='
    rb_has '^e188_common rc=0$' || bad="$bad e188_common"
    [ -n "${RB_DRY:-}" ] || noread_stop wait
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's checks after the build failed:$bad (a binary or file differs: a dated amendment first)"
    rb_say "aifoundry3: the train host built by the detached job $JOB; NOTE1 FILES OK 10, HARNESS OK 79, TRAIN-CHANGE OK (its behaviour), preflight_e188 GO, e188_common verified, each in its own bounded read"
    ;;

  --no-trains)
    e188_window                                                                                          # E188: the window rule
    rb_need_start
    rb_probe aifoundry3
    f=$(rb_file e188-harness-nt)
    { rb_prelude aifoundry3; ours_refusal; jobs_refusal; nt_built_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e188/check_e188.py --no-trains | head -n 20 | cut -c1-240; echo "check_e188 rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read harness "the fallback (the trains off): the harness with the four binaries, no train host (check_e188.py --no-trains)" "$f" '^check_e188 rc='
    rb_has '^HARNESS OK: 76 files' || bad="$bad harness"
    rb_has '^check_e188 rc=0$' || bad="$bad check_e188"
    f=$(rb_file e188-preflight-nt)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
bash tools/claims-v3/e188/preflight_e188.sh > build/e188-preflight-rb.txt 2>&1; echo "preflight_e188 rc=$? $(grep -m1 '^dmcmd_audit:' build/e188-preflight-rb.txt)"
EOF2
    } > "$f"
    check_read preflight "the fallback: the device-command preflight (preflight_e188.sh)" "$f" '^preflight_e188 rc='
    rb_has '^preflight_e188 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e188"
    f=$(rb_file e188-verify-nt)
    { rb_prelude aifoundry3; ours_refusal; cat <<'EOF2'
python3 -B tools/claims-v3/e188/e188_common.py --verify | tail -n 3; echo "e188_common rc=${PIPESTATUS[0]}"
EOF2
    } > "$f"
    check_read verify "the fallback: the items and the registered orders (e188_common.py --verify)" "$f" '^e188_common rc='
    rb_has '^e188_common rc=0$' || bad="$bad e188_common"
    [ -n "${RB_DRY:-}" ] || noread_stop --no-trains
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's checks for the fallback failed:$bad (a binary or file differs: a dated amendment first)"
    rb_say "aifoundry3: the trains off (the fallback, PASSES): no good build today, HARNESS OK 76, preflight_e188 GO, e188_common verified, each in its own bounded read; next step 7 (k6's reads), then step 8 start --no-trains"
    ;;

  *) rb_die $RB_E_USAGE "usage: s08_a3_build_e188.sh start | wait | --no-trains" ;;
esac
