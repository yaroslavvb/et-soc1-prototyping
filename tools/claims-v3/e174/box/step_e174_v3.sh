#!/usr/bin/env bash
# E174 (Q142(v2) fix pass, Thu 5 Nov 2026): the box steps, v3, run ON THE INTEL from the top of the lab tree. box/step_e174_v2.sh (lab 34436d68)
# and box/step_e174.sh (v1, 5a2a9ba0) stay as committed. v3 changes the collection only (E174.md.dated-note-2.md, section 2; the first verifier
# of v2's fault 3): its C-log gate reads cclist_q142kg_v3.py through ../../q142kg-runbook/rb_common_v3.sh, so a session the queue's record names
# only in a session_end line, with its start line and directory lost, stops the collection (14) instead of passing it. Every other step is v2's,
# unchanged: this file hands it to step_e174_v2.sh with the same arguments (exec), so look, sync, check start, check wait, launch [subset], wait
# and pull keep v2's gates line for line (the box check a detached dry job that refuses beside E172 or another dry pass; the launch only after
# that day's clean check and the box's guard; the sync refused beside a session of ours).
#
# The order on aifoundry1 (E174.md.dated-note-2.md, section 1): E174 runs after E172 has ended, or if E172 never starts, and never beside it.
# E172's collection (s22_collect_k6_v3.sh e172) pulls nothing while E174 or its box check runs (exit 17), so collect E172 after E174's end.
#
#   export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's lock file for login checks>
#   bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>     # 0  once, from the owner's go
#   bash tools/claims-v3/e174/box/step_e174_v3.sh look            # 1  v2's: read only, any time
#   bash tools/claims-v3/e174/box/step_e174_v3.sh sync            # 2  v2's: refused while anything of ours runs on aifoundry1
#   bash tools/claims-v3/e174/box/step_e174_v3.sh check start     # 3a v2's: the box check as a detached dry job
#   bash tools/claims-v3/e174/box/step_e174_v3.sh check wait      # 3b v2's: one bounded wait; 17 = call again
#                                                                 # 4  the day's one post (the card lanes, under the post's lock)
#   bash tools/claims-v3/e174/box/step_e174_v3.sh launch [subset] # 5  v2's: today's clean check, the box's guard, then the queue
#   bash tools/claims-v3/e174/box/step_e174_v3.sh wait            # 6  v2's: one bounded wait; exit 17 = still running
#   bash tools/claims-v3/e174/box/step_e174_v3.sh pull            # 7  v2's: a bounded copy of build/e174/ into build/e174-raw/
#   bash tools/claims-v3/e174/box/step_e174_v3.sh collect         # 8  v3: collect_e174.sh, the C-log gate with v3's list, the desk-path gate
#
# Exit codes are the runbook's (v2's header). RB_DRY=1 lists the exact commands and runs nothing.
# SPDX-License-Identifier: Apache-2.0
step=${1:-}
if [ "$step" != collect ]; then
  exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/step_e174_v2.sh" "$@"
fi
. "$(dirname "${BASH_SOURCE[0]}")/../../q142kg-runbook/rb_common_v3.sh"
rb_init "e174_$step"
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
rb_say "E174 collected and scored: $D"
