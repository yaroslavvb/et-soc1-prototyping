#!/usr/bin/env bash
# E175 (Q143(g)): the box steps for aifoundry2, v3, run ON THE INTEL from the top of the lab tree. E173's box/step_e173_v2.sh (lab 34436d68) and
# box/step_e173_v3.sh (the v3 collect, E173.md.dated-note-2.md) ported to E175 in one file (tools/claims-v3/e175/E175.md, lab c50ff493): every
# remote call goes through the q142kg runbook (../../q142kg-runbook/rb_common_v3.sh, which sources rb_common_v2.sh, rb_common.sh and v3.1's
# rb_common.sh, all unchanged): a 15 s hard-killed probe first; then the call under its bound (read 60 s, copy 600 s, wait 600 s, launch 60 s,
# which detaches on the box and returns at once); a login link kills the call, appends "<HH:MM:SS> aifoundry2 needs a check" to $RB_LOCK and exits
# 11; nothing prompts; every command is logged in $RB_OUT/runbook.log. Its steps are E173's line for line with E175's names, and three things:
#   - RB_BASE defaults to E175's registration commit (c50ff493): every box tree it uses descends from it, and the kit's own bytes are checked file
#     by file by the harness check (check_e175.py), so a box that lacks the kit commit refuses there (E173's v1 rule);
#   - the launch adds E175.md's window gate: E173's queue (build/e173/runs) must have ended (status.json "ended" or "halted", written today) at
#     least 10 minutes before, or never have started today; and no queue of E173's may run (the guard's ours_live also counts it);
#   - collect is v3's: collect_e175_bounded.sh, then the C-log gate with v3's list (cclist_q142kg_v3.py), then the desk-path gate.
#
#   export RB_OUT=<a new directory for this session, outside the repo> RB_LOCK=<the round's lock file for login checks> [RB_BASE=<the kit's commit>]
#   bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>     # 0  once: the go's window
#                                                                # (E175.md: if the go names none, 2026-11-05 21:00 22:00)
#   bash tools/claims-v3/e175/box/step_e175_v3.sh look              # 1  read only: et-who, who, uptime, the identity; the holder rule
#   bash tools/claims-v3/e175/box/step_e175_v3.sh tree              # 2  git pull --ff-only; ancestry of RB_BASE; clean; harness, tiles, pool, GO
#   bash tools/claims-v3/e175/box/step_e175_v3.sh dry start|wait    # 3  the box's dry pass (the toy card), a detached job; wait until it ends rc 0
#                                                                # 4  the day's one post (the card lane, under the post's lock)
#   bash tools/claims-v3/e175/box/step_e175_v3.sh launch [subset]   # 5  the slot file and the detached queue, inside the window, after E173
#   bash tools/claims-v3/e175/box/step_e175_v3.sh wait              # 6  one bounded wait; 17 = still running, call again
#   bash tools/claims-v3/e175/box/step_e175_v3.sh collect           # 7  at the desk: collect_e175_bounded.sh, the C-log gate (v3), the desk-path gate
#
# Exit codes are the runbook's: 0 done; 10 refused; 11 a login link; 12 the probe got no answer; 13 past its bound; 14 non-zero (a check of C that
# did not finish, a required C log missing, a lost dry job); 15 a holder after 30 minutes; 16 a gate says stop; 17 not yet. RB_DRY=1 lists the
# exact commands and runs nothing.
# SPDX-License-Identifier: Apache-2.0
RB_BASE=${RB_BASE:-c50ff493}          # E175's registration (Thu 5 Nov 2026 12:16:51 PST)
. "$(dirname "${BASH_SOURCE[0]}")/../../q142kg-runbook/rb_common_v3.sh"
step=${1:-}
rb_init "e175_$step"
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
    rb_remote read aifoundry2 "E175 step 1: et-who, who, uptime, the identity" "$f"
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
python3 -B tools/claims-v3/e175/check_e175.py | tail -n 3
python3 -B tools/claims-v3/e175/e175_common.py | tail -n 3
echo "pool OK: $(cd tools/claims-v3/e175/pool && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$')"
bash tools/claims-v3/e175/preflight_e175.sh > build/e175-preflight.txt 2>&1; echo "preflight rc=$? $(grep -m1 '^dmcmd_audit:' build/e175-preflight.txt)"
python3 -B tools/claims-v3/e175/run_e175.py --protocol tools/claims-v3/e175/protocol.json --out build/e175/list --dry --list > build/e175-list.txt 2>&1; echo "list rc=$? ($(grep -c 'BURST-' build/e175-list.txt) BURST runs listed)"
EOF
    } > "$f"
    rb_remote read aifoundry2 "E175: harness and binaries, tiles, the pool, the device-command preflight, the run list" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    pre_ok=1
    { rb_has '^HARNESS OK [0-9]+ \+ 3 binaries' && rb_has '^27 tiles; frozen inputs, Q139\(k\).s files and tiles: OK' && rb_has '^pool OK: 28$' \
      && rb_has 'dmcmd_audit: GO' && rb_has '\(145 BURST runs listed\)'; } || pre_ok=0
    echo "$(date '+%F %T %Z') aifoundry2 tree=$tree_ok e175=$pre_ok (1 = reads clean)" >> "$RB_OUT/a2-tree-q142kg.txt"
    [ "$tree_ok" -eq 1 ] || rb_die $RB_E_GATE "aifoundry2's tree is not at $RB_BASE or later, or not clean: read above"
    [ "$pre_ok" -eq 1 ] || rb_die $RB_E_GATE "E175 does not read clean on aifoundry2 (harness, tiles, the pool, the preflight or the run list): a dated amendment first"
    rb_say "aifoundry2 reads clean for E175 (tree at $RB_BASE or later)" ;;
  dry)
    act=${2:-}
    job=a2-dry-e175
    case "$act" in
      start)
        body=$(rb_file body)
        cat > "$body" <<'EOF'
mkdir -p build/e175
[ -e build/e175/dry ] && mv build/e175/dry build/e175/dry.before-$(date +%s)
now=$(date +%s)
printf 'SLOT E175: start %s (aifoundry2, dry) end %s \n' "$now" "$((now + 2400))" > ~/claude/work/q143-a2-e175-dry-slot.txt
python3 tools/claims-v3/e175/queue_e175.py --dry --slots ~/claude/work/q143-a2-e175-dry-slot.txt --runs build/e175/dry \
  --protocol tools/claims-v3/e175/protocol-dry.json --stoptest-board tools/claims-v3/e175/protocol-stoptest-board-dry.json \
  --stoptest-die tools/claims-v3/e175/protocol-stoptest-die-dry.json --cap 12 > build/e175/dry.out 2>&1 < /dev/null
r=$?
echo "E175 dry queue rc=$r"
grep -hE '"kind": "(smoke_check|stoptest_check|queue_halt|stop|s1_end|queue_end)"' build/e175/dry/queue.jsonl | cut -c1-260
[ "$r" -eq 0 ] && grep -q '"kind": "smoke_check".*"bad": null' build/e175/dry/queue.jsonl &&
  [ "$(grep -c '"kind": "stoptest_check".*"bad": null' build/e175/dry/queue.jsonl)" -eq 2 ] &&
  grep -q '"kind": "queue_end"' build/e175/dry/queue.jsonl
EOF
        rb_probe aifoundry2
        rb_job_start aifoundry2 "$job" "$body" 1 ;;
      wait)
        rb_probe aifoundry2
        rb_job_wait aifoundry2 "$job"; exit $? ;;
      *) rb_die $RB_E_USAGE "usage: step_e175_v3.sh dry start|wait" ;;
    esac ;;
  launch)
    plan=${2:-full}
    case "$plan" in full) slot=2880; cap=42; proto=tools/claims-v3/e175/protocol.json ;;
                    subset) slot=1860; cap=25; proto=tools/claims-v3/e175/protocol-subset.json ;;
                    *) rb_die $RB_E_USAGE "usage: step_e175_v3.sh launch [full|subset]" ;; esac
    rb_window
    rb_need_start
    rb_need_end "$slot"
    f=$(rb_file e175)
    { rb_prelude aifoundry2
      echo "SLOT=$slot; CAP=$cap; PROTO=$proto; AFTER=600"
      rb_guard_text
      cat <<'EOF'
job_ok_today a2-dry-e175 || { echo "REFUSED: E175's dry pass has not ended rc 0 today (step_e175_v3.sh dry start, then dry wait)"; exit 3; }
# E175.md, The window: after E173, never beside it: E173's queue ended (or halted) at least AFTER s before, or it never started today
if pgrep -u "$(id -u)" -f 'queue_e173\.py' > /dev/null; then echo "REFUSED: E173's queue still runs on this box (E175 runs after it, never beside it)"; exit 3; fi
E3=build/e173/runs/status.json
if fresh "$E3"; then
  grep -qE '"state": "(ended|halted)"' "$E3" || { echo "REFUSED: E173's status.json (written today) does not read ended or halted"; exit 3; }
  age=$(( $(date +%s) - $(stat -c %Y "$E3") ))
  [ "$age" -ge "$AFTER" ] || { echo "REFUSED: E173's queue ended $age s ago; E175 waits $AFTER s after it (E175.md, The window)"; exit 3; }
  echo "after E173: its queue ended $age s ago (at least $AFTER s): ok"
else
  echo "after E173: no E173 queue record written today on this box: ok"
fi
[ -e build/e175/runs/queue.jsonl ] && { echo "REFUSED: build/e175/runs already holds a queue"; exit 3; }
mkdir -p build/e175 ~/claude/work
now=$(date +%s)
printf 'SLOT E175: start %s (aifoundry2) end %s \n' "$now" "$((now + SLOT))" > ~/claude/work/q143-a2-e175-slot.txt
setsid nohup python3 tools/claims-v3/e175/queue_e175.py --slots ~/claude/work/q143-a2-e175-slot.txt --runs build/e175/runs --cap "$CAP" --protocol "$PROTO" > build/e175/queue.out 2>&1 < /dev/null &
sleep 3
echo "LAUNCHED e175 $(date '+%F %T %Z') (--cap $CAP, slot $SLOT s, $PROTO)"
cat ~/claude/work/q143-a2-e175-slot.txt; tail -n 3 build/e175/queue.out | cut -c1-300
EOF
    } > "$f"
    rb_probe aifoundry2
    rb_remote launch aifoundry2 "E175's slot and detached queue (--cap $cap, $plan)" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_launched e175
    rb_say "E175's queue started (--cap $cap); wait with step_e175_v3.sh wait and read its smoke and stop-test checks" ;;
  wait)
    rb_probe aifoundry2
    f=$(rb_file wait-e175)
    { rb_prelude aifoundry2
      echo "RUN=e175; LIM=$RB_WAIT_LOOP_S"
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
    rb_remote wait aifoundry2 "one bounded wait on e175" "$f"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on e175 exited $RB_RC"
    rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "e175 is not running and recorded no end: read the box's logs before anything else"
    rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "e175 ended at a gate (a smoke or stop test, QUEUE-HALT): read the lines above"
    rb_has '^RUN-ENDED' && { rb_say "e175 has ended"; exit 0; }
    rb_say "e175 still runs: call again"; exit $RB_E_AGAIN ;;
  collect)
    rb_window
    D=docs/reports/data/$RB_DAY-e175-governed-aifoundry2
    RAW=$RB_OUT/e175-raw
    [ -n "$(ls -A "$RAW" 2>/dev/null)" ] && rb_die $RB_E_USAGE "$RAW is not empty: the bounded collector needs a new, empty scratch dir"
    rb_probe aifoundry2
    t_cc=$(date +%s)
    rb_local desk aifoundry2 "collect_e175_bounded.sh (its own probe, every remote call under 600 s, the C-log list, the registered scorer)" \
      bash tools/claims-v3/e175/collect_e175_bounded.sh "$RAW" "$D"
    if [ -z "${RB_DRY:-}" ] && [ "$RB_RC" -ne 0 ]; then
      rb_die $RB_E_FAIL "collect_e175_bounded.sh stopped (2 a dir; 3 a remote call; 4 no session; 5 no answer; 6 the code path; 7 the scrub or the scorer; 8 a required C log or its check missing): read the output above"
    fi
    rb_cc_gate E175 "$t_cc" "$D/aifoundry2" "$D"
    rb_nopath "$D"
    rb_say "E175 collected and scored (the C-log gate with v3's list): $D" ;;
  *) rb_die $RB_E_USAGE "usage: step_e175_v3.sh look|tree|dry start|wait|launch [full|subset]|wait|collect" ;;
esac
