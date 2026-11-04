#!/usr/bin/env bash
# Q141(k), go checklist step 13 (Q141(f)'s F7): E164 on aifoundry1 card 1, launched ONLY with box/launch_e164_a1.sh and its new usage
# line (E164 README.md.dated-note.md § 1), never box/launch_e164.sh (README step 5 still names it; it would run 0 passes):
#
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e164/box/launch_e164_a1.sh
#   (the registered subset: "E164_DROP_P2=1 bash -s -- '<...>'")
#
# The deadline is the round's last end less 10 minutes (s02_window.sh's RB_E164_DEADLINE). Run it only after the day's post names
# aifoundry1 card 1 and steps 5 and 12 read clean. The launcher detaches session_e164.sh and returns in about 10 s. Its refusals open
# nothing: exit 2 (no deadline, or not a date), 3 (card 1 held, or anything of ours on either card), 4 (less than 1,930 s left),
# 9 (check_e164.py not HARNESS OK); this step then exits 14 with the launcher's code in the log.
#
#   bash tools/claims-v3/q141k-runbook/s13_a1_launch.sh [--drop-p2]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s13_a1_launch
opt=${1:-}
case "$opt" in ""|--drop-p2) ;; *) rb_die $RB_E_USAGE "the only option is --drop-p2 (the registered subset, chosen before the launch)" ;; esac
rb_window
rb_need_start
rb_need_end 1930
L=tools/claims-v3/e164/box/launch_e164_a1.sh
[ -f "$RB_REPO/$L" ] || rb_die $RB_E_USAGE "$L is missing"
pre=""; [ "$opt" = --drop-p2 ] && pre="E164_DROP_P2=1 "
rcmd="${pre}bash -s -- '$RB_E164_DEADLINE'"
rb_probe aifoundry1
rb_remote launch aifoundry1 "box/launch_e164_a1.sh, deadline $RB_E164_DEADLINE" "$RB_REPO/$L" "$rcmd"
[ -n "${RB_DRY:-}" ] && exit 0
if [ "$RB_RC" -ne 0 ]; then
  why=$(grep -m1 -E '^REFUSED|^usage|^not a date' "$RB_CAP")
  rb_die $RB_E_FAIL "launch_e164_a1.sh refused or failed (rc in the log): ${why:-read the output above}"
fi
rb_has '^launched T0=' || rb_die $RB_E_FAIL "launch_e164_a1.sh did not print its launch line: read the output above"
rb_say "E164 launched on aifoundry1 card 1 (deadline $RB_E164_DEADLINE); wait with s20_wait.sh e164 and read its smoke gate"
