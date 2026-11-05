#!/usr/bin/env bash
# E173 (Q142(kg)): the box steps for aifoundry2, run ON THE INTEL from the top of the lab tree, each remote call through the q142kg runbook (v3.1's
# rb_common.sh and rb_run.py, sourced unchanged by tools/claims-v3/q142kg-runbook/rb_common.sh): a 15 s hard-killed probe first; then the call under
# its bound (read 60 s, copy 600 s, wait 600 s, launch 60 s, which detaches on the box and returns at once); a login link kills the call, appends
# "<HH:MM:SS> aifoundry2 needs a check" to $RB_LOCK and exits 11; nothing prompts; every command is logged in $RB_OUT/runbook.log. It ports v3.1's
# aifoundry2 steps to E173: s05 (look), s14 (the tree and the preflights), s15 (the dry pass, a detached dry job), s16 (the launch, with v3.1's
# guard: no dry pass running, no session of ours, the firmware identity by host-boot continuity), s20 (the bounded wait) and s22 (the collection,
# with the C-log gate and the desk-path gate).
#
# v2 (Q142(kg) fix pass, Thu 5 Nov 2026; E173.md.dated-note-1.md): box/step_e173.sh (v1, lab 5a2a9ba0) stays as committed and is superseded for
# the card day by this file, which is v1 line for line except for three things. It sources ../../q142kg-runbook/rb_common_v2.sh, so (1) the C-log
# gate at collect reads cclist_q142kg_v2.py, the stricter list (the queue's record must be there; a session whose records show it ran a launch
# must carry a C log even when its launches.jsonl is lost: the kits' verifier's fault 7), and (2) RB_BASE defaults to the kits' commit 5a2a9ba0
# (v1: c8064454, with RB_BASE=5a2a9ba0 passed by hand); (3) its own name, step_e173_v2.sh, in its usage lines and messages, and every step's
# name carries "_q142kg2". aifoundry2's steps needed no other change: v1 already starts its dry pass through rb_job_start, and its launch already
# needs job_ok_today a2-dry-e173 and v3.1's rb_guard_text.
#
#   export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's lock file for login checks> [RB_BASE=<the kit's commit>]
#   bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>     # 0  once, from the owner's go
#   bash tools/claims-v3/e173/box/step_e173_v2.sh look              # 1  read only: et-who, who, uptime, the identity; the holder rule
#   bash tools/claims-v3/e173/box/step_e173_v2.sh tree              # 2  git pull --ff-only; ancestry of RB_BASE; clean; harness, tiles, blind8 89, GO
#   bash tools/claims-v3/e173/box/step_e173_v2.sh dry start|wait    # 3  the box's dry pass (the toy card), a detached job; wait until it ends rc 0
#                                                                # 4  the day's one post (the card lanes, under the post's lock)
#   bash tools/claims-v3/e173/box/step_e173_v2.sh launch [subset]   # 5  the slot file and the detached queue, inside the day's window
#   bash tools/claims-v3/e173/box/step_e173_v2.sh wait              # 6  one bounded wait; 17 = still running, call again
#   bash tools/claims-v3/e173/box/step_e173_v2.sh collect           # 7  at the desk: collect_e173_bounded.sh, the C-log gate, the desk-path gate
#
# Exit codes are the runbook's: 0 done; 10 refused; 11 a login link; 12 the probe got no answer; 13 past its bound; 14 non-zero (a check of C that
# did not finish, a required C log missing, a lost dry job); 15 a holder after 30 minutes; 16 a gate says stop; 17 not yet. RB_DRY=1 lists the
# exact commands and runs nothing.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q142kg-runbook/rb_common_v2.sh"
step=${1:-}
rb_init "e173_$step"
case "$step" in
  look)
    rb_probe aifoundry2
    f=$(rb_file look)
    { rb_prelude aifoundry2; cat <<'EOF'
date '+%F %T %Z'; uptime
boot=$(date -d "$(uptime -s)" +%s); fw=$(date -d '2026-10-27 13:56:26 PDT' +%s)
if [ "$boot" -lt "$fw" ]; then echo "IDENTITY-OK: the host booted $(uptime -s), before E69's firmware read of 2026-10-27 13:56:26 PDT (BL2 0.22.0 by continuity)"
else echo "IDENTITY-STOP: the host booted $(uptime -s), after E69's firmware read of 2026-10-27 13:56:26 PDT: BL2 0.22.0 is not carried"; fi
hold_read
echo "ours: $(ours_live) card sessions of ours; $(jobs_live) dry jobs of the runbook"
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && echo FREE || echo HELD)"
EOF
    } > "$f"
    rb_remote read aifoundry2 "E173 step 1: et-who, who, uptime, the identity" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the look exited $RB_RC"
    rb_identity_stop
    rb_has '^HOLDER-RULE: FREE' || rb_die $RB_E_AGAIN "aifoundry2 is held: look again later (at most 30 minutes in all, then skip the card)"
    rb_say "aifoundry2 is free (an idle login does not block)" ;;
  tree)
    rb_probe aifoundry2
    f=$(rb_file tree)
    { rb_prelude aifoundry2; cat <<EOF
GIT_TERMINAL_PROMPT=0 git pull --ff-only; echo "pull rc=\$?"
git merge-base --is-ancestor $RB_BASE HEAD; echo "ancestry rc=\$?"
echo "porcelain lines: \$(git status --porcelain -- tools/claims-v3 | wc -l)"
git log -1 --format='HEAD %h %ad' --date=format:'%F %T %z'
EOF
    } > "$f"
    rb_remote copy aifoundry2 "git pull --ff-only; ancestry of $RB_BASE; tools/claims-v3 clean" "$f"
    tree_ok=1
    rb_has '^pull rc=0$' && rb_has '^ancestry rc=0$' && rb_has '^porcelain lines: 0$' || tree_ok=0
    f=$(rb_file pre)
    { rb_prelude aifoundry2; cat <<'EOF'
python3 -B tools/claims-v3/e173/check_e173.py | tail -n 3
python3 -B tools/claims-v3/e173/e173_common.py | tail -n 3
echo "blind8 OK: $(cd tools/claims-v3/kinds/blind8 && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$')"
bash tools/claims-v3/e173/preflight_e173.sh > build/e173-preflight.txt 2>&1; echo "preflight rc=$? $(grep -m1 '^dmcmd_audit:' build/e173-preflight.txt)"
python3 -B tools/claims-v3/e173/run_e173.py --protocol tools/claims-v3/e173/protocol.json --out build/e173/list --dry --list > build/e173-list.txt 2>&1; echo "list rc=$? ($(grep -c 'BURST-' build/e173-list.txt) BURST runs listed)"
EOF
    } > "$f"
    rb_remote read aifoundry2 "E173: harness and binaries, tiles, blind8, the device-command preflight, the run list" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    pre_ok=1
    { rb_has '^HARNESS OK [0-9]+ \+ 3 binaries' && rb_has '^64 tiles; frozen inputs, Q139\(k\).s files and tiles: OK' && rb_has '^blind8 OK: 89$' \
      && rb_has 'dmcmd_audit: GO' && rb_has '\(165 BURST runs listed\)'; } || pre_ok=0
    echo "$(date '+%F %T %Z') aifoundry2 tree=$tree_ok e173=$pre_ok (1 = reads clean)" >> "$RB_OUT/a2-tree-q142kg.txt"
    [ "$tree_ok" -eq 1 ] || rb_die $RB_E_GATE "aifoundry2's tree is not at $RB_BASE or later, or not clean: read above"
    [ "$pre_ok" -eq 1 ] || rb_die $RB_E_GATE "E173 does not read clean on aifoundry2 (harness, tiles, blind8, the preflight or the run list): a dated amendment first"
    rb_say "aifoundry2 reads clean for E173 (tree at $RB_BASE or later)" ;;
  dry)
    act=${2:-}
    job=a2-dry-e173
    case "$act" in
      start)
        body=$(rb_file body)
        cat > "$body" <<'EOF'
mkdir -p build/e173
[ -e build/e173/dry ] && mv build/e173/dry build/e173/dry.before-$(date +%s)
now=$(date +%s)
printf 'SLOT E173: start %s (aifoundry2, dry) end %s \n' "$now" "$((now + 2400))" > ~/claude/work/q142-a2-e173-dry-slot.txt
python3 tools/claims-v3/e173/queue_e173.py --dry --slots ~/claude/work/q142-a2-e173-dry-slot.txt --runs build/e173/dry \
  --protocol tools/claims-v3/e173/protocol-dry.json --stoptest-board tools/claims-v3/e173/protocol-stoptest-board-dry.json \
  --stoptest-die tools/claims-v3/e173/protocol-stoptest-die-dry.json --cap 12 > build/e173/dry.out 2>&1 < /dev/null
r=$?
echo "E173 dry queue rc=$r"
grep -hE '"kind": "(smoke_check|stoptest_check|queue_halt|stop|s1_end|queue_end)"' build/e173/dry/queue.jsonl | cut -c1-260
[ "$r" -eq 0 ] && grep -q '"kind": "smoke_check".*"bad": null' build/e173/dry/queue.jsonl &&
  [ "$(grep -c '"kind": "stoptest_check".*"bad": null' build/e173/dry/queue.jsonl)" -eq 2 ] &&
  grep -q '"kind": "queue_end"' build/e173/dry/queue.jsonl
EOF
        rb_probe aifoundry2
        rb_job_start aifoundry2 "$job" "$body" 1 ;;
      wait)
        rb_probe aifoundry2
        rb_job_wait aifoundry2 "$job"; exit $? ;;
      *) rb_die $RB_E_USAGE "usage: step_e173_v2.sh dry start|wait" ;;
    esac ;;
  launch)
    plan=${2:-full}
    case "$plan" in full) slot=2880; cap=42; proto=tools/claims-v3/e173/protocol.json ;;
                    subset) slot=2040; cap=28; proto=tools/claims-v3/e173/protocol-subset.json ;;
                    *) rb_die $RB_E_USAGE "usage: step_e173_v2.sh launch [full|subset]" ;; esac
    rb_window
    rb_need_start
    rb_need_end "$slot"
    f=$(rb_file e173)
    { rb_prelude aifoundry2
      echo "SLOT=$slot; CAP=$cap; PROTO=$proto"
      rb_guard_text
      cat <<'EOF'
job_ok_today a2-dry-e173 || { echo "REFUSED: E173's dry pass has not ended rc 0 today (step_e173_v2.sh dry start, then dry wait)"; exit 3; }
[ -e build/e173/runs/queue.jsonl ] && { echo "REFUSED: build/e173/runs already holds a queue"; exit 3; }
mkdir -p build/e173 ~/claude/work
now=$(date +%s)
printf 'SLOT E173: start %s (aifoundry2) end %s \n' "$now" "$((now + SLOT))" > ~/claude/work/q142-a2-e173-slot.txt
setsid nohup python3 tools/claims-v3/e173/queue_e173.py --slots ~/claude/work/q142-a2-e173-slot.txt --runs build/e173/runs --cap "$CAP" --protocol "$PROTO" > build/e173/queue.out 2>&1 < /dev/null &
sleep 3
echo "LAUNCHED e173 $(date '+%F %T %Z') (--cap $CAP, slot $SLOT s, $PROTO)"
cat ~/claude/work/q142-a2-e173-slot.txt; tail -n 3 build/e173/queue.out | cut -c1-300
EOF
    } > "$f"
    rb_probe aifoundry2
    rb_remote launch aifoundry2 "E173's slot and detached queue (--cap $cap, $plan)" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_launched e173
    rb_say "E173's queue started (--cap $cap); wait with step_e173_v2.sh wait and read its smoke and stop-test checks" ;;
  wait)
    rb_probe aifoundry2
    f=$(rb_file wait-e173)
    { rb_prelude aifoundry2
      echo "RUN=e173; LIM=$RB_WAIT_LOOP_S"
      cat <<'EOF'
R=build/$RUN/runs
fin() { fresh "$R/status.json" && grep -qE '"state": "(ended|halted)"' "$R/status.json" 2>/dev/null; }
if ! fresh "$R/status.json" && ! pgrep -u "$(id -u)" -f "queue_$RUN\.py" > /dev/null; then
  echo "RUN-UNKNOWN $RUN: no queue process and no status.json written today"; exit 3
fi
while ! fin && [ "$SECONDS" -lt "$LIM" ]; do
  pgrep -u "$(id -u)" -f "queue_$RUN\.py" > /dev/null || { sleep 2; fin || { echo "RUN-GONE $RUN: no queue process and no end in status.json"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'; cat "$R/status.json" 2>/dev/null; echo
[ -e "$R/QUEUE-HALT" ] && { echo "QUEUE-HALT:"; cut -c1-300 "$R/QUEUE-HALT"; }
grep -hE '"kind": "(smoke_check|stoptest_check|queue_halt|give_up|stop|s[1-6]_end|queue_end)"' "$R/queue.jsonl" 2>/dev/null | cut -c1-300 | tail -n 14
tail -n 4 build/$RUN/queue.out 2>/dev/null | cut -c1-300
if fin; then echo "RUN-ENDED $RUN"; else echo "RUN-RUNNING $RUN after $t s"; fi
if [ -e "$R/QUEUE-HALT" ] || grep -qE '"kind": "give_up"' "$R/queue.jsonl" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
EOF
    } > "$f"
    rb_remote wait aifoundry2 "one bounded wait on e173" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on e173 exited $RB_RC"
    rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "e173 is not running and recorded no end: read the box's logs before anything else"
    rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "e173 ended at a gate (a smoke or stop test, QUEUE-HALT): read the lines above"
    rb_has '^RUN-ENDED' && { rb_say "e173 has ended"; exit 0; }
    rb_say "e173 still runs: call again"; exit $RB_E_AGAIN ;;
  collect)
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
    rb_say "E173 collected and scored: $D" ;;
  *) rb_die $RB_E_USAGE "usage: step_e173_v2.sh look|tree|dry start|wait|launch [full|subset]|wait|collect" ;;
esac
