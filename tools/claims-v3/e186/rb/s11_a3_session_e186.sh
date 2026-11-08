#!/usr/bin/env bash
# E186 (Q158, the kit), KIT.md box step 9 (this file is s11): E186's card session on aifoundry3, launched detached on the box (it returns at
# once), ONLY after the day's post names aifoundry3 and steps 5-8 read clean. A port of E182's step 9 v2
# (tools/claims-v3/e182/rb/s11_a3_session_e182_v2.sh): FULL yes needs step 8's trains job (a3-dry-e186) ended rc 0 today; PASSES no, the
# registered fallback, needs its no-trains job (a3-dry-e186-nt) or the trains job; FULL no and PASSES yes are refused (10) before any call.
# The window rule (written today for E186), the last start, the plan's budget before the last end (FULL 6,000 s, PASSES 2,400 s), the
# guard (no dry pass running, no card session of ours: k6's rb_guard_text), the launch command of KIT.md's box step 9, the launch marker.
# E186: the launch records its T0 on the box (build/q141k/e186.T0) and in RB_OUT (e186-T0.txt), which steps 10 and 11 read.
#
#   bash tools/claims-v3/e186/rb/s11_a3_session_e186.sh FULL yes | PASSES no
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e186.sh"
rb_init s11_a3_session
plan=${1:-FULL}
trains=${2:-yes}
need=$(e186_budget "$plan") || rb_die $RB_E_USAGE "E186's plan is FULL or PASSES"
case "$plan.$trains" in
  FULL.yes) JOBS="a3-dry-e186" ;;
  PASSES.no) JOBS="a3-dry-e186-nt a3-dry-e186" ;;
  *) rb_die $RB_E_USAGE "E186 runs FULL yes, or the fallback PASSES no (after step 6's builds failed); '$plan $trains' is neither" ;;
esac
e186_window
rb_need_start
rb_need_end "$need"
f=$(rb_file e186)
{ rb_prelude aifoundry3
  echo "LAST_START=$(printf '%q' "$RB_LAST_START"); LAST_END=$(printf '%q' "$RB_LAST_END"); PLAN=$plan; TRAINS=$trains; JOBS='$JOBS'"
  rb_guard_text
  cat <<'EOF2'
okj=""; for j in $JOBS; do job_ok_today "$j" && { okj=$j; break; }; done
[ -n "$okj" ] || { echo "REFUSED: E186's dry pass for plan $PLAN (step 8's job: $JOBS) has not ended rc 0 today"; exit 3; }
echo "dry pass: $okj ended rc 0 today"
mkdir -p build/e186 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e186.T0
E186_T0=$T0 E186_PLAN="$PLAN" E186_TRAINS="$TRAINS" E186_LATEST_START="$LAST_START" E186_DEADLINE="$LAST_END" setsid nohup bash tools/claims-v3/e186/session_e186.sh > build/e186/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e186 T0 $T0 $(date '+%F %T %Z') (plan $PLAN, trains $TRAINS; gates: latest start $LAST_START, deadline $LAST_END)"
tail -n 6 "build/e186/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e186, detached (plan $plan, trains $trains)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e186
t0=$(rb_val '^LAUNCHED e186 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e186-T0.txt"
rb_say "e186 launched on aifoundry3 (plan $plan, trains $trains, T0 $t0); wait with s20_wait_e186.sh (bounded), and read its smoke gate before counting it as started"
