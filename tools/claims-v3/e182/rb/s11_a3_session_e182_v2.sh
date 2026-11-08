#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1), step 11 v2: E182's card session on aifoundry3, launched detached on the box (it returns at once),
# ONLY after the day's post names aifoundry3 and steps 7-10 v2 read clean. It is v1 (rb/s11_a3_session_e182.sh, which stays as committed)
# with the dry job read by the plan (the verifier's MAJOR 1): FULL yes needs step 10 v2's trains job (a3-dry-e182) ended rc 0 today;
# PASSES no, the registered fallback, needs its no-trains job (a3-dry-e182-nt) or the trains job; FULL no and PASSES yes are refused (10)
# before any call (session_e182.sh would turn FULL no into PASSES; the runbook says so first). Everything else is v1's: the window, the
# last start and the plan's budget (FULL 6,000 s, PASSES 2,400 s), the guard (no dry pass running, no card session of ours), the launch
# command of KIT.md's box step 9, the launch marker.
#
#   bash tools/claims-v3/e182/rb/s11_a3_session_e182_v2.sh FULL yes | PASSES no
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s11_a3_session_v2
plan=${1:-FULL}
trains=${2:-yes}
need=$(e182_budget "$plan") || rb_die $RB_E_USAGE "E182's plan is FULL or PASSES"
case "$plan.$trains" in
  FULL.yes) JOBS="a3-dry-e182" ;;
  PASSES.no) JOBS="a3-dry-e182-nt a3-dry-e182" ;;
  *) rb_die $RB_E_USAGE "E182 runs FULL yes, or the fallback PASSES no (after step 8 v2's build failed); '$plan $trains' is neither" ;;
esac
rb_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e182)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan; TRAINS=$trains; JOBS='$JOBS'"
  rb_guard_text
  cat <<'EOF2'
okj=""; for j in $JOBS; do job_ok_today "$j" && { okj=$j; break; }; done
[ -n "$okj" ] || { echo "REFUSED: E182's dry pass for plan $PLAN (step 10 v2's job: $JOBS) has not ended rc 0 today"; exit 3; }
echo "dry pass: $okj ended rc 0 today"
mkdir -p build/e182 build/q141k
if [ -f build/e182/session.log ]; then wc -l < build/e182/session.log; else echo 0; fi > build/q141k/e182.log-offset
E182_T0=$(date +%s) E182_PLAN="$PLAN" E182_TRAINS="$TRAINS" E182_LATEST_START="$LAST_START" E182_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e182/session_e182.sh > build/e182/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e182 $(date '+%F %T %Z') (plan $PLAN, trains $TRAINS; gates: latest start $LAST_START, deadline $LAST_END)"
tail -n +"$(( $(cat build/q141k/e182.log-offset) + 1 ))" build/e182/session.log | tail -n 6 | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e182, detached (plan $plan, trains $trains)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e182
rb_say "e182 launched on aifoundry3 (plan $plan, trains $trains); wait with s20_wait_e182.sh (bounded), and read its smoke gate before counting it as started"
