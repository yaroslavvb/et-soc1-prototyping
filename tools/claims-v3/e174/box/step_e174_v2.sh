#!/usr/bin/env bash
# E174 (Q142(kg) fix pass, Thu 5 Nov 2026): the box steps, v2, run ON THE INTEL from the top of the lab tree. box/step_e174.sh (v1, lab 5a2a9ba0)
# stays as committed and is superseded for the card day by this file (E174.md.dated-note-1.md; the kits' verifier's fault 1). v1's port of v3.1's
# steps dropped v3.1's two aifoundry1 gates; v2 restores them:
#   - the box check runs as one of the runbook's detached dry jobs (v3.1's s12_a1_check.sh: rb_job_start), so it refuses to start while a card
#     session of ours runs on aifoundry1 (E172's queue, session, block or runner among them: the q142kg prelude's ours_live) or while another dry
#     pass of the runbook runs there (E172's own box check among them). v1 sent check_box_e174.sh as a plain 600 s call, and its "never during a
#     session of ours" was a comment only, so its dry passes could load aifoundry1 beside E172's measured 600 MHz session on card 1;
#   - the launch needs that day's clean check twice, as v3.1's s13_a1_launch.sh did. At the desk: RB_OUT/a1c0-check-clean-e174.txt naming the
#     window's day, written only by `check wait` when every line reads clean (`check start` removes it). On the box, in one 60 s guard read before
#     the launcher is sent: v3.1's rb_guard_text (no dry pass of the runbook running, no card session of ours, the host booted before the firmware
#     read of record: E82's, 13:45:24 PDT on 31 Oct, the earlier of aifoundry1's two; launch_e174.sh then checks E84's again) and
#     job_ok_today a1c0-check-e174 (the check job ended rc 0 today: its body exits 0 only when the box's own reading is clean).
# On the same rule, the sync refuses (10) while a card session of ours or a dry pass of the runbook runs on aifoundry1 (v1's header said "only
# after E172 has ended", unenforced). The C-log gate at collect reads v2's list (rb_common_v2.sh; E174.md.dated-note-1.md, section 3). The box
# check now also reads the tiles line (e174_common.py's "64 tiles; ... OK"), which v1 printed but did not read. Everything else is v1's, line
# for line: look, wait and pull; the launch's window, start, end and deadline gates and launch_e174.sh's refusals; collect_e174.sh.
#
#   export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's lock file for login checks>
#   bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>     # 0  once, from the owner's go
#   bash tools/claims-v3/e174/box/step_e174_v2.sh look            # 1  read only, any time: boot vs E84's read, et-who, E172's end, binaries
#   bash tools/claims-v3/e174/box/step_e174_v2.sh sync            # 2  E174's one rsync into aifoundry1:nekko/: refused while anything of ours runs
#   bash tools/claims-v3/e174/box/step_e174_v2.sh check start     # 3a the box check as a detached dry job: refused while anything of ours runs
#   bash tools/claims-v3/e174/box/step_e174_v2.sh check wait      # 3b one bounded wait; 17 = call again; clean writes the day's clean file
#                                                                 # 4  the day's one post (the card lanes, under the post's lock)
#   bash tools/claims-v3/e174/box/step_e174_v2.sh launch [subset] # 5  today's clean check, the box's guard, then the queue, detached
#   bash tools/claims-v3/e174/box/step_e174_v2.sh wait            # 6  one bounded wait; exit 17 = still running, call again
#   bash tools/claims-v3/e174/box/step_e174_v2.sh pull            # 7  a bounded copy of build/e174/ into build/e174-raw/
#   bash tools/claims-v3/e174/box/step_e174_v2.sh collect         # 8  at the desk: collect_e174.sh, the C-log gate (v2's list), the desk-path gate
#
# Exit codes are the runbook's: 0 done; 10 refused (a refusal on the box, no clean check today, a check not started today, usage); 11 a login link;
# 12 the probe got no answer; 13 past its bound; 14 non-zero (a dry job that did not start, v3.1's JOB-REFUSED during a session of ours among
# them; a lost job; a check of C that did not finish, a required C log missing, the queue's record missing); 16 a gate says stop (a box check that
# read unclean, the identity stop); 17 not yet. RB_DRY=1 lists the exact commands and runs nothing.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q142kg-runbook/rb_common_v2.sh"
step=${1:-}
rb_init "e174_$step"
K="$RB_REPO/tools/claims-v3/e174/box"
JOB=a1c0-check-e174                       # the box check's dry job (build/q141k/jobs/ on aifoundry1, beside the k6 runbook's a1-check-e172)
CLEAN="$RB_OUT/a1c0-check-clean-e174.txt" # written by `check wait` only when the box check reads clean; the launch needs it, naming the window's day
quiet_guard() {  # quiet_guard <file>: the remote read before a step that writes on aifoundry1: no dry pass of the runbook, no card session of ours
  { rb_prelude aifoundry1; cat <<'EOF'
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: a dry pass of the runbook still runs on $BOX ($(jobs_live): E172's or E174's box check): nothing done"; exit 3; fi
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX ($(ours_live): E172 must have ended; nothing of E174's beside it): nothing done"; exit 3; fi
echo "QUIET-OK: no card session of ours and no dry pass of the runbook on $BOX"
EOF
  } > "$1"
}
case "$step" in
  look)
    rb_probe aifoundry1
    rb_remote read aifoundry1 "E174 box step 1: box/look_e174.sh" "$K/look_e174.sh"
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "look_e174.sh exited $RB_RC"
    rb_has 'host boot: .*AFTER' && rb_die $RB_E_GATE "the host booted after E84's identity read: E174 cannot run (NO-GO on the day)"
    rb_say "read the et-who lines above: card 0's must be empty and nothing of ours on card 1 (E172 has ended)" ;;
  sync)
    rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short tools/claims-v3/e174/ tools/claims-v3/e173/ tools/claims-v3/e170/ \
      tools/claims-v3/kinds/blind8/ tools/claims-v3/hpl/
    [ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
    g=$(rb_file quiet)
    quiet_guard "$g"
    rb_probe aifoundry1
    rb_remote read aifoundry1 "before E174's sync: no card session of ours and no dry pass of the runbook on aifoundry1" "$g"
    rb_refused
    [ -n "${RB_DRY:-}" ] || rb_has '^QUIET-OK' || rb_die $RB_E_FAIL "the read before the sync gave no reading (rc $RB_RC): nothing synced"
    rb_local copy aifoundry1 "E174's one rsync: tools/claims-v3/e174/, pool 8 and the chain E174 imports" \
      rsync -a -c -R --exclude __pycache__ --exclude logs/ -e "$RB_RSH" \
      tools/claims-v3/e174/ tools/claims-v3/e173/e173_common.py tools/claims-v3/e173/frozen-sha256-e173.json tools/claims-v3/e170/e170_common.py \
      tools/claims-v3/e170/ettelem_guard_e170.sh tools/claims-v3/kinds/blind8/ tools/claims-v3/kinds/kinds.json tools/claims-v3/kinds/e78_common.py \
      tools/claims-v3/kinds/e101_common.py tools/claims-v3/kspeed/run_kspeed.py tools/claims-v3/kspeed/predictions.json \
      tools/claims-v3/kspeed/e84/run_e84.py tools/claims-v3/kspeed/e101/run_e101s.py tools/claims-v3/kspeed/e105/run_e105.py \
      tools/claims-v3/e119/run_e119.py tools/claims-v3/e119/predictions-e119.json tools/claims-v3/e111/idle_logins_e111.py \
      tools/claims-v3/hpl/run_hpl.py tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/e165/e165_common.py tools/claims-v3/ccheck/ \
      tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json workloads/sparsity/host/main.cpp workloads/sparsity/kernel/sparsity.c \
      docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json docs/reports/data/2026-11-04-q140l-a2-session-terms/predict_m9_a2.py \
      aifoundry1:nekko/
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
    rb_say "synced E174's files to aifoundry1:nekko/" ;;
  check)
    act=${2:-}
    case "$act" in
      start)
        [ -n "${RB_DRY:-}" ] || rm -f "$CLEAN"
        body=$(rb_file body)
        cat > "$body" <<'EOF'
bash tools/claims-v3/e174/box/check_box_e174.sh > build/e174-check-box.txt 2>&1; r=$?
cat build/e174-check-box.txt
echo "check_box_e174.sh rc=$r"
bad=""
grep -qE '^HARNESS OK [0-9]+ \+ 3 binaries' build/e174-check-box.txt || bad="$bad harness"
grep -q 'dmcmd_audit: GO' build/e174-check-box.txt || bad="$bad preflight"
grep -q "^64 tiles; frozen inputs, Q139(k)'s files and tiles: OK" build/e174-check-box.txt || bad="$bad tiles"
grep -qE "^== pool 8.s SHA256SUMS: 89 OK" build/e174-check-box.txt || bad="$bad blind8"
grep -q 'stoptest-die dry rc=4' build/e174-check-box.txt || bad="$bad stoptest-die"
grep -q 'smoke dry rc=0' build/e174-check-box.txt || bad="$bad smoke"
grep -qE '\(126 BURST runs listed' build/e174-check-box.txt || bad="$bad list"
if [ -z "$bad" ]; then echo "BOX-CHECK-CLEAN"; else echo "BOX-CHECK-UNCLEAN:$bad"; fi
[ -z "$bad" ]
EOF
        rb_probe aifoundry1
        rb_job_start aifoundry1 "$JOB" "$body" 1
        rb_say "E174's box check started on aifoundry1 as the dry job $JOB; wait with step_e174_v2.sh check wait" ;;
      wait)
        rb_window
        rb_probe aifoundry1
        rb_job_wait aifoundry1 "$JOB"; rc=$?
        if [ -n "${RB_DRY:-}" ]; then
          echo "--- gate: every line of the box check reads clean, then RB_OUT/a1c0-check-clean-e174.txt is written naming the window's day"
          exit 0
        fi
        [ "$rc" -eq "$RB_E_AGAIN" ] && exit "$rc"
        [ "$rc" -eq "$RB_E_USAGE" ] && exit "$rc"            # not started today: check start first
        rb_has '^JOB-LOST' && exit "$RB_E_FAIL"              # lost: start it again (the wait said why)
        bad=""
        rb_has '^HARNESS OK [0-9]+ \+ 3 binaries' || bad="$bad harness"
        rb_has 'dmcmd_audit: GO' || bad="$bad preflight"
        rb_has "^64 tiles; frozen inputs, Q139\(k\).s files and tiles: OK" || bad="$bad tiles"
        rb_has '^== pool 8.s SHA256SUMS: 89 OK' || bad="$bad blind8"
        rb_has 'stoptest-die dry rc=4' || bad="$bad stoptest-die"
        rb_has 'smoke dry rc=0' || bad="$bad smoke"
        rb_has '\(126 BURST runs listed' || bad="$bad list"
        rb_has '^BOX-CHECK-CLEAN$' || bad="$bad box-reading"
        rb_has '^JOB-DONE .* rc=0$' || bad="$bad job-rc"
        [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry1's box check for E174 did not read clean:$bad (read the output above; a rebuilt binary needs a dated amendment first)"
        echo "$RB_DAY clean $(date '+%F %T %Z')" > "$CLEAN"     # the launch needs this (step 3 before 5)
        rb_say "aifoundry1 card 0 (E174): harness OK with the binaries, preflight GO, tiles OK, blind8 89, dry stop test rc 4, dry smoke rc 0, 126 runs listed: clean today ($RB_DAY)" ;;
      *) rb_die $RB_E_USAGE "usage: step_e174_v2.sh check start|wait" ;;
    esac ;;
  launch)
    plan=${2:-}
    case "$plan" in ""|subset) ;; *) rb_die $RB_E_USAGE "the only option is subset (the registered subset, chosen before the launch)" ;; esac
    rb_window
    rb_need_start
    if [ "$plan" = subset ]; then rb_need_end 1800; else rb_need_end 2700; fi
    if [ -z "${RB_DRY:-}" ] && [ -z "${RB_E174_DEADLINE:-}" ]; then rb_die $RB_E_USAGE "the window file has no E174 deadline: run s02_window_q142kg.sh"; fi
    if [ -z "${RB_DRY:-}" ]; then
      [ "$(cut -d' ' -f1-2 "$CLEAN" 2>/dev/null)" = "$RB_DAY clean" ] ||
        rb_die $RB_E_USAGE "check wait has not read E174's box check clean today ($RB_DAY): step_e174_v2.sh check start, then check wait, then launch"
    else
      echo "--- gate: check wait read E174's box check clean today (RB_OUT/a1c0-check-clean-e174.txt names the window's day)"
    fi
    dl=${RB_E174_DEADLINE:-<the last end less 5 min>}
    rcmd="bash -s -- '$dl' '${RB_LAST_START:-<last start>}' '${RB_LAST_END:-<last end>}'${plan:+ $plan}"
    g=$(rb_file guard)
    { rb_prelude aifoundry1
      rb_guard_text
      echo "job_ok_today $JOB || { echo \"REFUSED: E174's box check job ($JOB) has not ended rc 0 today: check start, then check wait\"; exit 3; }"
      cat <<'EOF'
echo "GUARD-OK: no dry pass of the runbook runs on $BOX, no card session of ours, and E174's box check ended rc 0 today"
EOF
    } > "$g"
    rb_probe aifoundry1
    rb_remote read aifoundry1 "the runbook's guard before E174's launch (no dry pass, no session of ours, today's box check, the identity)" "$g"
    rb_identity_stop
    rb_refused
    [ -n "${RB_DRY:-}" ] || rb_has '^GUARD-OK' || rb_die $RB_E_FAIL "the guard read gave no reading (rc $RB_RC): nothing launched"
    rb_remote launch aifoundry1 "E174 box step 5: box/launch_e174.sh, deadline $dl${plan:+, $plan}" "$K/launch_e174.sh" "$rcmd"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_identity_stop
    rb_has '^LAUNCHED e174 ' && { rb_say "E174 launched on aifoundry1 card 0; wait with step_e174_v2.sh wait and read its state gate, stop tests and smoke"; exit 0; }
    rb_has '^(REFUSED|usage|not a date)' && rb_die $RB_E_USAGE "launch_e174.sh refused: $(grep -m1 -E '^(REFUSED|usage|not a date)' "$RB_CAP")"
    rb_has '^HARNESS (BAD|DIFFERS)' && rb_die $RB_E_USAGE "launch_e174.sh refused: check_e174.py is not HARNESS OK"
    rb_die $RB_E_FAIL "launch_e174.sh did not print its launch line (rc $RB_RC): read the output above" ;;
  wait)
    rb_probe aifoundry1
    rb_remote wait aifoundry1 "E174 box step 6: box/wait_e174.sh" "$K/wait_e174.sh"
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "wait_e174.sh exited $RB_RC"
    rb_has '"state": "halted"' && rb_die $RB_E_GATE "E174's queue halted (state gate, stop test, smoke or alarm): read QUEUE-HALT above"
    rb_has '"state": "ended"' && { rb_say "E174's queue has ended"; exit 0; }
    rb_say "E174 still runs: call again"; exit $RB_E_AGAIN ;;
  pull)
    [ -n "${RB_DRY:-}" ] || mkdir -p "$RB_REPO/build/e174-raw"
    rb_probe aifoundry1
    rb_local copy aifoundry1 "E174's raw runs and logs" rsync -a -e "$RB_RSH" aifoundry1:nekko/build/e174/ "$RB_REPO/build/e174-raw/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited non-zero"
    rb_local copy aifoundry1 "E174's box preflight" rsync -a -e "$RB_RSH" aifoundry1:nekko/build/e174-preflight.txt "$RB_REPO/build/e174-raw/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy of the box preflight exited non-zero"
    rb_say "copied build/e174/ to build/e174-raw/; collect with step_e174_v2.sh collect" ;;
  collect)
    rb_window
    D=docs/reports/data/$RB_DAY-e174-blind8-card0
    t_cc=$(date +%s)
    rb_local desk local "collect_e174.sh (the C check, the C-log list, the scrub, the registered scorer)" env E174_DATE="$RB_DAY" \
      nice -n 10 bash tools/claims-v3/e174/collect_e174.sh build/e174-raw
    if [ -z "${RB_DRY:-}" ]; then
      [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "collect_e174.sh stopped (2 a dir; 3 a copy; 4 no session; 6 the harness; 7 the scrub or the scorer; 8 a required C log or its check missing): read the output above"
      rb_has '^results written' || rb_die $RB_E_FAIL "collect_e174.sh did not print 'results written': read the output above"
    fi
    rb_cc_gate E174 "$t_cc" "$D/aifoundry1-c0" "$D"
    rb_nopath "$D"
    rb_say "E174 collected and scored: $D" ;;
  *) rb_die $RB_E_USAGE "usage: step_e174_v2.sh look|sync|check start|check wait|launch [subset]|wait|pull|collect" ;;
esac
