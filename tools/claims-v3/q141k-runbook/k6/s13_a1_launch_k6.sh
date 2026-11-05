#!/usr/bin/env bash
# Q142(k6), step 13: E172's launch on aifoundry1 card 1 (E172's README, box step 5) through box/launch_e172.sh with the deadline quoted
# inside the remote command (the round's last end less 10 minutes, RB_E172_DEADLINE from s02_window_k6.sh), ONLY after the day's post
# carries the reservation and s12_a1_check_k6.sh wait read the box check clean today. The runbook's guard first (no dry pass, no card
# session of ours, the box check job ended rc 0 today, the identity by continuity). The launcher's refusals (2, 3, 4 and 9, whose line
# is `HARNESS DIFFERS - refusing:`) exit 10; any other failure exits 14. A port of ../v3.1/s13_a1_launch.sh.
#
#   bash tools/claims-v3/q141k-runbook/k6/s13_a1_launch_k6.sh [--drop-p2]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s13_a1_launch
opt=${1:-}
case "$opt" in ""|--drop-p2) ;; *) rb_die $RB_E_USAGE "the only option is --drop-p2 (the registered subset, chosen before the launch)" ;; esac
rb_window
rb_need_start
rb_need_end 2330        # k6: the launcher's MIN_S (1,730 s) before E172's deadline, the last end less 600 s
L=tools/claims-v3/e172/box/launch_e172.sh
[ -f "$RB_REPO/$L" ] || rb_die $RB_E_USAGE "$L is missing"
if [ -z "${RB_DRY:-}" ]; then
  [ "$(cut -d' ' -f1-2 "$RB_OUT/a1-check-clean-e172.txt" 2>/dev/null)" = "$RB_DAY clean" ] ||
    rb_die $RB_E_USAGE "s12_a1_check_k6.sh wait has not read aifoundry1's box check clean today ($RB_DAY): step 12, then 13"
else
  echo "--- gate: s12_a1_check_k6.sh wait read the box check clean today (RB_OUT/a1-check-clean-e172.txt names the window's day)"
fi
g=$(rb_file guard)
{ rb_prelude aifoundry1
  rb_guard_text
  cat <<'EOF'
job_ok_today a1-check-e172 || { echo "REFUSED: s12's box check job has not ended rc 0 today: run s12_a1_check_k6.sh start, then wait"; exit 3; }
echo "GUARD-OK: no dry pass of the runbook runs on $BOX, no card session of ours, and s12's check job ended rc 0 today"
EOF
} > "$g"
pre=""; [ "$opt" = --drop-p2 ] && pre="E172_DROP_P2=1 "
rcmd="${pre}bash -s -- '$RB_E172_DEADLINE'"
rb_probe aifoundry1
rb_remote read aifoundry1 "the runbook's guard before E172's launch (no dry pass, no session of ours, s12's check today, the identity)" "$g"
rb_identity_stop
rb_refused
[ -n "${RB_DRY:-}" ] || rb_has '^GUARD-OK' || rb_die $RB_E_FAIL "the guard read gave no reading (rc $RB_RC): nothing launched"
rb_remote launch aifoundry1 "box/launch_e172.sh, deadline $RB_E172_DEADLINE" "$RB_REPO/$L" "$rcmd"
[ -n "${RB_DRY:-}" ] && exit 0
if [ "$RB_RC" -ne 0 ]; then
  why=$(grep -m1 -E '^REFUSED|^usage|^not a date|^HARNESS DIFFERS' "$RB_CAP")    # v3.1: exit 9's line too (nit 5)
  [ -n "$why" ] && rb_die $RB_E_USAGE "launch_e172.sh refused on the box (nothing launched): $why"
  rb_die $RB_E_FAIL "launch_e172.sh failed (rc in the log): read the output above"
fi
rb_has '^launched T0=' || rb_die $RB_E_FAIL "launch_e172.sh did not print its launch line: read the output above"
rb_say "E172 launched on aifoundry1 card 1 (deadline $RB_E172_DEADLINE); wait with s20_wait_k6.sh e172 and read its smoke gate"
