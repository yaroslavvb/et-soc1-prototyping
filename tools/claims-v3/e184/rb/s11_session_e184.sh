#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 9: an arm's card session, launched detached on its box (it returns at
# once), ONLY after the day's post names the card and steps 5-8 read clean today. ../../e180/rb/s11_a3_session_e180_v2.sh's form, for either
# box, with the rest rule (the verifier's fault 4) made code: T0 is taken on the box once, written to build/q141k/e184<s|b>.t0 BEFORE the
# launch, passed to the session as E184_T0, and printed back ("LAUNCHED e184<s|b> T0=<epoch>"), and this step keeps it in $RB_OUT/t0-<arm>.txt;
# the session names every file it writes by that T0 (session_e184{s,b}_v2.sh), so step 10 reads only this launch's log, never an earlier one's.
#   E184_T0=<T0> E184_LATEST_START=<the round's last start> E184_DEADLINE=<the round's last end>
#     setsid nohup bash tools/claims-v3/e184/session_e184<s|b>_v2.sh > build/e184/session-<arm>-t<T0>.out 2>&1 < /dev/null &
# The session runs its own checks, the stop-path test and the smoke with its gate before any pass; its gates refuse with exit 8.
# Refused (10) before any launch: no window, fewer seconds left than the arm's budget (S 8,100, B 1,500), the build or dry job not ended rc 0
# today, a dry pass of the runbook still running there, or a card session of ours; 16 past the last start. On aifoundry1 the host's identity
# (booted before E82's firmware read) is checked by k6's guard text, and arm B never touches card 0.
#
#   bash tools/claims-v3/e184/rb/s11_session_e184.sh S|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s11_session
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s11_session_e184.sh S|B"
rb_window
rb_need_start
rb_need_end "$E184_BUDGET"
f=$(rb_file "e184$E184_LC")
{ rb_prelude "$E184_BOX"
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); ARM=$E184_ARM; LC=$E184_LC; SESS=$E184_SESS; J=$E184_J"
  rb_guard_text
  cat <<'EOF2'
job_ok_today "$J-dry-e184" || { echo "REFUSED: E184's dry pass (s10_dry_e184.sh $ARM) has not ended rc 0 today"; exit 3; }
job_ok_today "$J-build-e184" || { echo "REFUSED: E184's build and preflight (s08_build_e184.sh $ARM) have not ended rc 0 today"; exit 3; }
mkdir -p build/e184 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e184$LC.t0"
E184_T0=$T0 E184_LATEST_START="$LAST_START" E184_DEADLINE="$LAST_END" setsid nohup bash "tools/claims-v3/e184/$SESS" > "build/e184/session-$ARM-t$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e184$LC T0=$T0 $(date '+%F %T %Z') (gates: latest start $LAST_START, deadline $LAST_END)"
head -n 6 "build/e184/session-$ARM-t$T0.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$E184_BOX"
rb_remote launch "$E184_BOX" "launch e184$E184_LC, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e184$E184_LC"
t0=$(rb_val "^LAUNCHED e184$E184_LC T0=([0-9]+) .*$")      # rb_val substitutes the match: the pattern takes the whole line
case "$t0" in ''|*[!0-9]*) rb_die $RB_E_FAIL "the launch printed no T0 (read '$t0'): read the output above" ;; esac
echo "$t0" > "$RB_OUT/t0-$E184_ARM.txt"
rb_say "e184$E184_LC launched on $E184_BOX, T0 $t0; wait with s20_wait_e184.sh $E184_ARM (bounded), and read its smoke gate before counting it as started"
