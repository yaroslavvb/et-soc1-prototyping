#!/usr/bin/env bash
# E188 (Q165, the kit's dated note 1, KIT.md.dated-note-1.md, Thu 12 Nov 2026, before any E188 datum): KIT.md box step 9 v2, the session's
# launch. It is rb/s11_a3_session_e188.sh (726a6b64, which stays as committed) with ONE change, marked "note 1": the rest lines it sends to
# aifoundry3 before the launch are THE REST RULE v2 (rb/rest_rule_e188_v2.sh, verify-e188's fault 3): a real session block with no "session
# end" is counted as ended at the latest of its last line, its log's last write and its run's latest write outside the dry paths (its
# queue.out or queue-t<T0>.out, its block directories), so a session whose shell died mid-queue no longer reads as rested from its last
# log line. Everything else is v1's, line for line: the plans, the window rule, the last start and the budget before the last end, k6's
# guard, today's dry pass and (FULL) today's good build, the launch command, the T0 on the box and in RB_OUT (e188-T0.txt), which step 10
# (s20_wait_e188.sh) and step 11 (s22_collect_e188.sh) read unchanged. Its name in the runbook's log is s11_a3_session_v2_e188.
#
#   bash tools/claims-v3/e188/rb/s11_a3_session_e188_v2.sh FULL yes | PASSES no
# v1's words follow:
# E188 (Q165, the kit), KIT.md box step 9 (this file is s11): E188's card session on aifoundry3, launched detached on the box (it returns at
# once), ONLY after the day's post names aifoundry3 and steps 5-8 read clean. A port of E186's step 9 (tools/claims-v3/e186/rb/
# s11_a3_session_e186.sh, run on 9 Nov 2026; itself E182's v2) with E188's names and ONE ADDITION, THE REST RULE (rb/rest_rule_e188.sh,
# E183's kit note 4's rule in E188's words; E188.md section 6: the launch at least 40 minutes after the end of our last session on
# aifoundry3): the box reads every session log of ours in every form our kits write (build/e*/session.log, session-*.log, T*/session.log,
# T*/session-*.log: E182's, E183's session-t<T0>.log, E184's session-<arm>-t<T0>.log, E185's, E186's and E188's T<T0>/session.log) and
# refuses (10, nothing launched) within 40 minutes of the latest real session's end. FULL yes needs step 8's trains job (a3-dry-e188) ended
# rc 0 today and the train host built today (a3-build-e188 ended rc 0 with TRAIN-HOST-BUILT, E183's v2 check); PASSES no, the registered
# fallback, needs its no-trains job (a3-dry-e188-nt) or the trains job; FULL no and PASSES yes are refused (10) before any call. The window
# rule (written today for E188), the last start, the plan's budget before the last end (FULL 6,000 s, PASSES 2,400 s), the guard (no dry
# pass running, no card session of ours: k6's rb_guard_text), the rest rule, the launch command of KIT.md's box step 9, the launch marker.
# The launch records its T0 on the box (build/q141k/e188.T0) and in RB_OUT (e188-T0.txt), which steps 10 and 11 read; the rest rule's line
# goes to the runbook log.
#
#   bash tools/claims-v3/e188/rb/s11_a3_session_e188.sh FULL yes | PASSES no
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e188.sh"
rb_init s11_a3_session_v2                  # note 1: its name in the runbook's log
plan=${1:-FULL}
trains=${2:-yes}
need=$(e188_budget "$plan") || rb_die $RB_E_USAGE "E188's plan is FULL or PASSES"
case "$plan.$trains" in
  FULL.yes) JOBS="a3-dry-e188" ;;
  PASSES.no) JOBS="a3-dry-e188-nt a3-dry-e188" ;;
  *) rb_die $RB_E_USAGE "E188 runs FULL yes, or the fallback PASSES no (after step 6's builds failed); '$plan $trains' is neither" ;;
esac
e188_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e188)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan; TRAINS=$trains; JOBS='$JOBS'"
  rb_guard_text
  cat "$RB_E188_DIR/rest_rule_e188_v2.sh"     # note 1: THE REST RULE v2, before the launch (v1: rest_rule_e188.sh)
  cat <<'EOF2'
okj=""; for j in $JOBS; do job_ok_today "$j" && { okj=$j; break; }; done
[ -n "$okj" ] || { echo "REFUSED: E188's dry pass for plan $PLAN (step 8's job: $JOBS) has not ended rc 0 today"; exit 3; }
echo "dry pass: $okj ended rc 0 today"
if [ "$TRAINS" = yes ]; then
  { job_ok_today a3-build-e188 && grep -q '^TRAIN-HOST-BUILT rc=0' build/q141k/jobs/a3-build-e188.out 2>/dev/null; } ||
    { echo "REFUSED: E188's train host (s08_a3_build_e188.sh) was not built today"; exit 3; }
fi
mkdir -p build/e188 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e188.T0
E188_T0=$T0 E188_PLAN="$PLAN" E188_TRAINS="$TRAINS" E188_LATEST_START="$LAST_START" E188_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e188/session_e188.sh > build/e188/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e188 T0 $T0 $(date '+%F %T %Z') (plan $PLAN, trains $TRAINS; gates: latest start $LAST_START, deadline $LAST_END)"
tail -n 6 "build/e188/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e188, detached (plan $plan, trains $trains)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e188
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"     # E188: the rest rule
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e188 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e188-T0.txt"
rb_say "e188 launched on aifoundry3 (plan $plan, trains $trains, T0 $t0); wait with s20_wait_e188.sh (bounded), and read its smoke gate before counting it as started"
