#!/usr/bin/env bash
# E174 (Q142(kg)): the box steps, run ON THE INTEL from the top of the lab tree, each remote call through the q142kg runbook (v3.1's rb_common.sh
# and rb_run.py, sourced unchanged by tools/claims-v3/q142kg-runbook/rb_common.sh): a 15 s hard-killed probe first; then the call under its bound
# (read 60 s, copy 600 s, wait 600 s, launch 60 s, which detaches on the box and returns at once); a login link kills the call, appends
# "<HH:MM:SS> aifoundry1 needs a check" to $RB_LOCK and exits 11; nothing prompts; every command is logged with its exit status in $RB_OUT/runbook.log.
# It is E170's box/step_e170.sh, ported: E174's scripts, the day's window passed to the launch, and a collect step that ends with the C-log gate and
# the desk-path gate (v3.1's step 22, with the Q142 critic's list of the sessions that must carry a C log).
#
#   export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's lock file for login checks>
#   bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>     # 0  once, from the owner's go
#   bash tools/claims-v3/e174/box/step_e174.sh look            # 1  read only: boot vs E84's read, et-who, E172's end, binaries
#   bash tools/claims-v3/e174/box/step_e174.sh sync            # 2  E174's one rsync into aifoundry1:nekko/ (only after E172 has ended)
#   bash tools/claims-v3/e174/box/step_e174.sh check           # 3  harness, binaries, preflight GO, tiles, blind8 89, the box dry pass
#                                                              # 4  the day's one post (the card lanes, under the post's lock)
#   bash tools/claims-v3/e174/box/step_e174.sh launch [subset] # 5  the queue, detached, inside the day's window
#   bash tools/claims-v3/e174/box/step_e174.sh wait            # 6  one bounded wait; exit 17 = still running, call again
#   bash tools/claims-v3/e174/box/step_e174.sh pull            # 7  a bounded copy of build/e174/ into build/e174-raw/
#   bash tools/claims-v3/e174/box/step_e174.sh collect         # 8  at the desk: collect_e174.sh, the C-log gate, the desk-path gate
#
# Exit codes are the runbook's: 0 done; 10 refused; 11 a login link; 12 the probe got no answer; 13 past its bound; 14 non-zero (a check of C
# that did not finish, a required C log missing); 16 a gate says stop; 17 not yet. RB_DRY=1 lists the exact commands and runs nothing.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q142kg-runbook/rb_common.sh"
step=${1:-}
rb_init "e174_$step"
K="$RB_REPO/tools/claims-v3/e174/box"
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
    rb_probe aifoundry1
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
    rb_probe aifoundry1
    rb_remote wait aifoundry1 "E174 box step 3: box/check_box_e174.sh" "$K/check_box_e174.sh"
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "check_box_e174.sh exited $RB_RC"
    rb_has '^HARNESS OK [0-9]+ \+ 3 binaries' || rb_die $RB_E_GATE "check_e174.py is not HARNESS OK with the binaries: read above (a rebuilt binary needs a dated amendment first)"
    rb_has 'dmcmd_audit: GO' || rb_die $RB_E_GATE "the device-command preflight is not GO"
    rb_has '^== pool 8.s SHA256SUMS: 89 OK' || rb_die $RB_E_GATE "pool 8's SHA256SUMS is not 89 OK"
    { rb_has 'stoptest-die dry rc=4' && rb_has 'smoke dry rc=0' && rb_has '\(126 BURST runs listed'; } || rb_die $RB_E_GATE "the box dry pass did not end as registered"
    rb_say "the box check reads clean" ;;
  launch)
    plan=${2:-}
    case "$plan" in ""|subset) ;; *) rb_die $RB_E_USAGE "the only option is subset (the registered subset, chosen before the launch)" ;; esac
    rb_window
    rb_need_start
    if [ "$plan" = subset ]; then rb_need_end 1800; else rb_need_end 2700; fi
    if [ -z "${RB_DRY:-}" ] && [ -z "${RB_E174_DEADLINE:-}" ]; then rb_die $RB_E_USAGE "the window file has no E174 deadline: run s02_window_q142kg.sh"; fi
    dl=${RB_E174_DEADLINE:-<the last end less 5 min>}
    rcmd="bash -s -- '$dl' '${RB_LAST_START:-<last start>}' '${RB_LAST_END:-<last end>}'${plan:+ $plan}"
    rb_probe aifoundry1
    rb_remote launch aifoundry1 "E174 box step 5: box/launch_e174.sh, deadline $dl${plan:+, $plan}" "$K/launch_e174.sh" "$rcmd"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_identity_stop
    rb_has '^LAUNCHED e174 ' && { rb_say "E174 launched on aifoundry1 card 0; wait with step_e174.sh wait and read its state gate, stop tests and smoke"; exit 0; }
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
    rb_say "copied build/e174/ to build/e174-raw/; collect with step_e174.sh collect" ;;
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
  *) rb_die $RB_E_USAGE "usage: step_e174.sh look|sync|check|launch [subset]|wait|pull|collect" ;;
esac
