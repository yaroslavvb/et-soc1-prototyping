#!/usr/bin/env bash
# E173 (Q142(v2) fix pass, Thu 5 Nov 2026): the box steps for aifoundry2, v3, run ON THE INTEL from the top of the lab tree. box/step_e173_v2.sh
# (lab 34436d68) and box/step_e173.sh (v1, 5a2a9ba0) stay as committed. v3 changes the collection only (E173.md.dated-note-2.md; the first verifier
# of v2's fault 3): its C-log gate reads cclist_q142kg_v3.py through ../../q142kg-runbook/rb_common_v3.sh, so a session the queue's record names
# only in a session_end line, with its start line and directory lost, stops the collection (14) instead of passing it. Every other step is v2's,
# unchanged: this file hands it to step_e173_v2.sh with the same arguments (exec), so look, tree, dry start, dry wait, launch [full|subset] and
# wait keep v2's gates line for line.
#
#   export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's lock file for login checks>
#   bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>     # 0  once, from the owner's go
#   bash tools/claims-v3/e173/box/step_e173_v3.sh look | tree | dry start | dry wait | launch [full|subset] | wait     # v2's steps
#   bash tools/claims-v3/e173/box/step_e173_v3.sh collect     # v3: collect_e173_bounded.sh, the C-log gate with v3's list, the desk-path gate
#
# Exit codes are the runbook's (v2's header). RB_DRY=1 lists the exact commands and runs nothing.
# SPDX-License-Identifier: Apache-2.0
step=${1:-}
if [ "$step" != collect ]; then
  exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/step_e173_v2.sh" "$@"
fi
. "$(dirname "${BASH_SOURCE[0]}")/../../q142kg-runbook/rb_common_v3.sh"
rb_init "e173_$step"
rb_window
D=docs/reports/data/$RB_DAY-e173-blind8-aifoundry2
RAW=$RB_OUT/e173-raw
[ -n "$(ls -A "$RAW" 2>/dev/null)" ] && rb_die $RB_E_USAGE "$RAW is not empty: the bounded collector needs a new, empty scratch dir"
rb_probe aifoundry2
t_cc=$(date +%s)
rb_local desk aifoundry2 "collect_e173_bounded.sh (its own probe, every remote call under 600 s, the C-log list, the registered scorer)" \
  bash tools/claims-v3/e173/collect_e173_bounded.sh "$RAW" "$D"
if [ -z "${RB_DRY:-}" ] && [ "$RB_RC" -ne 0 ]; then
  rb_die $RB_E_FAIL "collect_e173_bounded.sh stopped (2 a dir; 3 a remote call; 4 no session; 5 no answer; 6 the code path; 7 the scrub or the scorer; 8 a required C log or its check missing): read the output above"
fi
rb_cc_gate E173 "$t_cc" "$D/aifoundry2" "$D"
rb_nopath "$D"
rb_say "E173 collected and scored: $D"
