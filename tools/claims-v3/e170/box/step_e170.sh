#!/usr/bin/env bash
# E170 (Q141(w)): the box steps, run ON THE INTEL from the top of the lab tree, each remote call through Q141(k)'s bounded runner
# (tools/claims-v3/q141k-runbook/rb_common.sh and rb_run.py, e962227a): a 15 s hard-killed probe first; then the call under its bound (read 60 s,
# copy 600 s, wait 600 s, launch 60 s, which detaches on the box and returns at once); a login link kills the call, appends
# "<HH:MM:SS> aifoundry1 needs a check" to $RB_LOCK and exits 11; nothing prompts; every command is logged with its exit status in $RB_OUT/runbook.log.
#
#   export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's tailscale-needed file>
#   bash tools/claims-v3/e170/box/step_e170.sh look                         # 1  read only: boot vs E84's read, et-who, E164's end, binaries
#   bash tools/claims-v3/e170/box/step_e170.sh sync                         # 2  E170's one rsync into aifoundry1:nekko/ (only after E164 ended)
#   bash tools/claims-v3/e170/box/step_e170.sh check                        # 3  harness, binaries, preflight GO, tiles, blind7 91, the box dry pass
#                                                                           # 4  the day's one post (the main session, under the Discord lock)
#   bash tools/claims-v3/e170/box/step_e170.sh launch '<YYYY-MM-DD HH:MM PST>' [subset]   # 5  the queue, detached
#   bash tools/claims-v3/e170/box/step_e170.sh wait                         # 6  one bounded wait; exit 17 = still running, call again
#   bash tools/claims-v3/e170/box/step_e170.sh pull                         # 7  a bounded copy of build/e170/ into build/e170-raw/
# then, at the desk: bash tools/claims-v3/e170/collect_e170.sh build/e170-raw   (README.md, box step 8)
#
# Exit codes are the runbook's: 0 done; 10 refused; 11 a login link; 12 the probe got no answer; 13 past its bound; 14 non-zero; 16 a gate says stop;
# 17 not yet. RB_DRY=1 lists the exact commands and runs nothing.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/rb_common.sh"
step=${1:-}
rb_init "e170_$step"
K="$RB_REPO/tools/claims-v3/e170/box"
case "$step" in
  look)
    rb_probe aifoundry1
    rb_remote read aifoundry1 "E170 box step 1: box/look_e170.sh" "$K/look_e170.sh"
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "look_e170.sh exited $RB_RC"
    rb_has 'host boot: .*AFTER' && rb_die $RB_E_GATE "the host booted after E84's identity read: E170 cannot run (NO-GO on the day)"
    rb_say "read the et-who lines above: card 0's must be empty and nothing of ours on card 1" ;;
  sync)
    rb_local read local "tools/claims-v3 clean before the sync" git -C "$RB_REPO" status --short tools/claims-v3/
    [ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "tools/claims-v3 has uncommitted changes: sync only the pushed commit"
    rb_probe aifoundry1
    rb_local copy aifoundry1 "E170's one rsync: tools/claims-v3/e170/, pool 7 and the chain E170 imports" \
      rsync -a -c -R --exclude __pycache__ -e "$RB_RSH" \
      tools/claims-v3/e170/ tools/claims-v3/kinds/blind7/ tools/claims-v3/kinds/kinds.json tools/claims-v3/kinds/e78_common.py \
      tools/claims-v3/kinds/e101_common.py tools/claims-v3/kspeed/run_kspeed.py tools/claims-v3/kspeed/predictions.json \
      tools/claims-v3/kspeed/e84/run_e84.py tools/claims-v3/kspeed/e101/run_e101s.py tools/claims-v3/kspeed/e105/run_e105.py \
      tools/claims-v3/e119/run_e119.py tools/claims-v3/e119/predictions-e119.json tools/claims-v3/e111/idle_logins_e111.py \
      tools/claims-v3/hpl/run_hpl.py tools/claims-v3/e165/e165_common.py tools/claims-v3/ccheck/ tools/claims-v3/dmcmd_audit.py \
      tools/claims-v3/dmcmd_table.json workloads/sparsity/host/main.cpp workloads/sparsity/kernel/sparsity.c \
      docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json docs/reports/data/2026-11-04-q140l-a2-session-terms/predict_m9_a2.py \
      aifoundry1:nekko/
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
    rb_say "synced E170's files to aifoundry1:nekko/" ;;
  check)
    rb_probe aifoundry1
    rb_remote wait aifoundry1 "E170 box step 3: box/check_box_e170.sh" "$K/check_box_e170.sh"
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "check_box_e170.sh exited $RB_RC"
    rb_has '^HARNESS OK [0-9]+ \+ 3 binaries' || rb_die $RB_E_GATE "check_e170.py is not HARNESS OK with the binaries: read above (a rebuilt binary needs a dated amendment first)"
    rb_has 'dmcmd_audit: GO' || rb_die $RB_E_GATE "the device-command preflight is not GO"
    rb_has 'OK \(want 91\)' && rb_has '^== pool 7.s SHA256SUMS: 91 OK' || rb_die $RB_E_GATE "pool 7's SHA256SUMS is not 91 OK"
    rb_has 'stoptest-die dry rc=4' && rb_has 'smoke dry rc=0' || rb_die $RB_E_GATE "the box dry pass did not end as registered"
    rb_say "the box check reads clean" ;;
  launch)
    shift
    [ $# -ge 1 ] || rb_die $RB_E_USAGE "usage: step_e170.sh launch '<YYYY-MM-DD HH:MM PST>' [subset]"
    dl=$1; plan=${2:-}
    case "$plan" in ""|subset) ;; *) rb_die $RB_E_USAGE "the only option is subset (the registered subset, chosen before the launch)" ;; esac
    rcmd="bash -s -- '$dl'${plan:+ $plan}"
    rb_probe aifoundry1
    rb_remote launch aifoundry1 "E170 box step 5: box/launch_e170.sh, deadline $dl${plan:+, $plan}" "$K/launch_e170.sh" "$rcmd"
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "launch_e170.sh refused or failed (rc in the log): $(grep -m1 -E '^REFUSED|^usage|^not a date' "$RB_CAP")"
    rb_has '^launched T0=' || rb_die $RB_E_FAIL "launch_e170.sh did not print its launch line: read the output above"
    rb_say "E170 launched on aifoundry1 card 0; wait with step_e170.sh wait and read its state gate, stop tests and smoke" ;;
  wait)
    rb_probe aifoundry1
    rb_remote wait aifoundry1 "E170 box step 6: box/wait_e170.sh" "$K/wait_e170.sh"
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "wait_e170.sh exited $RB_RC"
    rb_has '"state": "halted"' && rb_die $RB_E_GATE "E170's queue halted (state gate, stop test, smoke or alarm): read QUEUE-HALT above"
    rb_has '"state": "ended"' && { rb_say "E170's queue has ended"; exit 0; }
    rb_say "E170 still runs: call again"; exit $RB_E_AGAIN ;;
  pull)
    [ -n "${RB_DRY:-}" ] || mkdir -p "$RB_REPO/build/e170-raw"
    rb_probe aifoundry1
    rb_local copy aifoundry1 "E170's raw runs and logs" rsync -a -e "$RB_RSH" aifoundry1:nekko/build/e170/ "$RB_REPO/build/e170-raw/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited non-zero"
    rb_local copy aifoundry1 "E170's box preflight" rsync -a -e "$RB_RSH" aifoundry1:nekko/build/e170-preflight.txt "$RB_REPO/build/e170-raw/"
    rb_say "copied build/e170/ to build/e170-raw/; collect with collect_e170.sh build/e170-raw" ;;
  *) rb_die $RB_E_USAGE "usage: step_e170.sh look|sync|check|launch '<deadline>' [subset]|wait|pull" ;;
esac
