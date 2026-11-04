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
#   bash tools/claims-v3/q141k-runbook/v2/s13_a1_launch.sh [--drop-p2]
#
# v2 (Q141(k)'s verifier, fault 1): the go checklist's order, step 12 before 13, held in code, as every other launch holds it. Before
# the launcher is sent: s12's wait must have read the box check clean today (RB_OUT/a1-check-clean.txt), and one read on the box
# (60 s) must find no dry pass of the runbook still running there (s12's check job among them: V3_DRY passes 16410, 16401, 16402), no
# card session of ours (E170's queue on card 0 counts), and s12's check job ended rc 0 today. A refusal there exits 10 and sends
# nothing more. v1 sent launch_e164_a1.sh straight away, whose own refusals look only at card holders and our device processes.
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
if [ -z "${RB_DRY:-}" ]; then
  [ "$(cut -d' ' -f1-2 "$RB_OUT/a1-check-clean.txt" 2>/dev/null)" = "$RB_DAY clean" ] ||
    rb_die $RB_E_USAGE "s12_a1_check.sh wait has not read aifoundry1's box check clean today ($RB_DAY): step 12, then 13"
else
  echo "--- gate: s12_a1_check.sh wait read the box check clean today (RB_OUT/a1-check-clean.txt names the window's day)"
fi
g=$(rb_file guard)
{ rb_prelude aifoundry1
  rb_guard_text
  cat <<'EOF'
job_ok_today a1-check || { echo "REFUSED: s12's box check job has not ended rc 0 today: run s12_a1_check.sh start, then wait"; exit 3; }
echo "GUARD-OK: no dry pass of the runbook runs on $BOX, no card session of ours, and s12's check job ended rc 0 today"
EOF
} > "$g"
pre=""; [ "$opt" = --drop-p2 ] && pre="E164_DROP_P2=1 "
rcmd="${pre}bash -s -- '$RB_E164_DEADLINE'"
rb_probe aifoundry1
rb_remote read aifoundry1 "the runbook's guard before E164's launch (no dry pass, no session of ours, s12's check today)" "$g"
rb_refused
[ -n "${RB_DRY:-}" ] || rb_has '^GUARD-OK' || rb_die $RB_E_FAIL "the guard read gave no reading (rc $RB_RC): nothing launched"
rb_remote launch aifoundry1 "box/launch_e164_a1.sh, deadline $RB_E164_DEADLINE" "$RB_REPO/$L" "$rcmd"
[ -n "${RB_DRY:-}" ] && exit 0
if [ "$RB_RC" -ne 0 ]; then
  why=$(grep -m1 -E '^REFUSED|^usage|^not a date' "$RB_CAP")
  rb_die $RB_E_FAIL "launch_e164_a1.sh refused or failed (rc in the log): ${why:-read the output above}"
fi
rb_has '^launched T0=' || rb_die $RB_E_FAIL "launch_e164_a1.sh did not print its launch line: read the output above"
rb_say "E164 launched on aifoundry1 card 1 (deadline $RB_E164_DEADLINE); wait with s20_wait.sh e164 and read its smoke gate"
